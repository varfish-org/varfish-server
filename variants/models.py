import contextlib
import itertools
import os
import shlex
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timedelta
import json
from collections import defaultdict

import binning
import wrapt
from itertools import chain
import math
import re
import requests

from varfish.utils import JSONField
from variants.helpers import get_engine
from bgjobs.plugins import BackgroundJobsPluginPoint
from django.contrib.auth import get_user_model
from django.forms import model_to_dict
from django.utils.html import strip_tags
from sqlalchemy import select, func, and_, delete
import uuid as uuid_object

from postgres_copy import CopyManager

from django.db import models, transaction, connection, utils
from django.db.models import Q
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import pre_delete
from django.utils import timezone

from projectroles.models import Project
from bgjobs.models import (
    BackgroundJob,
    JobModelMessageMixin,
    LOG_LEVEL_CHOICES,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_INFO,
)
from projectroles.plugins import get_backend_api

from geneinfo.models import Hgnc, EnsemblToGeneSymbol

from genomicfeatures.models import GeneInterval

#: The SQL Alchemy engine to use
from importer.management.helpers import open_file, tsv_reader

from variants.helpers import get_meta
from projectroles.app_settings import AppSettingAPI


app_settings = AppSettingAPI()

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

#: The User model to use.
User = get_user_model()

#: Threshold for hom/het ratio for identifying sex.
CHRX_HET_HOM_THRESH = 0.45
#: Threshold for relatedness between parent and children.
THRESH_PARENT = 0.6
#: Threshold for relatedness between siblings.
THRESH_SIBLING = 0.6

#: Pedigree value for male.
PED_MALE = 1
#: Pedigree value for female.
PED_FEMALE = 2

#: Create mapping for chromosome as string to chromosome as integer
CHROMOSOME_STR_TO_CHROMOSOME_INT = {
    b: a for a, b in enumerate(list(map(str, range(1, 23))) + ["X", "Y", "MT"], 1)
}


def only_source_name(full_name):
    """Helper function that strips SNAPPY suffixes for samples."""
    if full_name.count("-") >= 3:
        tokens = full_name.split("-")
        return "-".join(tokens[:-3])
    else:
        return full_name


class CaseAwareProject(Project):
    """A project that is aware of its cases"""

    class Meta:
        proxy = True

    def indices(self, _user=None):
        """Return all registered indices."""
        return [p.index for p in self.get_active_smallvariant_cases()]

    def pedigree(self, _user=None):
        """Concatenate the pedigrees of project's cases."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.pedigree:
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_filtered_pedigree_with_samples(self, _user=None):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = []
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result.append(line)
                seen.add((case.name, line["patient"]))
        return result

    def get_family_with_filtered_pedigree_with_samples(self, _user=None):
        """Concatenate the pedigrees of project's cases that have samples."""
        result = defaultdict(list)
        seen = set()
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.get_filtered_pedigree_with_samples():
                if line["patient"] not in seen:
                    result[case.name].append(line)
                seen.add((case.name, line["patient"]))
        return dict(result)

    def sample_to_case(self):
        """Compute sample-to-case mapping."""
        result = {}
        # Only select cases that have an active variant set.
        # TODO Perspectively, we need to distinguish between Small and Structural VariantSets.
        for case in self.get_active_smallvariant_cases():
            for line in case.pedigree:
                if line["patient"] not in result:
                    result[line["patient"]] = case
        return result

    def chrx_het_hom_ratio(self, sample):
        """Forward to appropriate case"""
        case = self.sample_to_case().get(sample)
        if not case:
            return 0.0
        else:
            return case.chrx_het_hom_ratio(sample)

    def sex_errors(self):
        """Concatenate all contained case's sex errors dicts"""
        result = {}
        disable_sex_check = app_settings.get_app_setting(
            "variants", "disable_pedigree_sex_check", project=self
        )
        if disable_sex_check:
            return result
        for case in self.case_set.all():
            result.update(case.sex_errors(disable_sex_check))
        return result

    def sex_errors_to_fix(self):
        for case in self.case_set.all():
            fix_case = case.sex_errors_variant_stats(lambda x: x)
            if fix_case:
                return True
        return False

    def get_case_pks(self):
        """Return PKs for cases."""
        return [case.pk for case in self.case_set.all()]

    def get_members(self):
        """Return concatenated list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.get_filtered_pedigree_with_samples()])

    def get_active_smallvariant_cases(self):
        """Return activate cases."""
        return list(self.case_set.filter(smallvariantset__state="active"))

    def num_small_vars(self):
        """Return total number of small vars in a project."""
        return sum(
            case.num_small_vars for case in self.case_set.all() if case.num_small_vars is not None
        )

    def has_variants_and_variant_sets(self):
        return all(case.has_variants_and_variant_set() for case in self.case_set.all())

    def casealignmentstats(self):
        stats = []
        for case in self.case_set.all():
            variant_set = case.latest_variant_set
            if variant_set:
                stats.append(variant_set.casealignmentstats)
        return stats

    def get_annotation_count(self):
        return sum(case.get_annotation_count() for case in self.case_set.all())

    def sample_variant_stats(self):
        stats = []
        for case in self.case_set.all():
            variant_set = case.latest_variant_set
            if variant_set:
                for sample in variant_set.variant_stats.sample_variant_stats.all():
                    stats.append(sample)
        return stats


class SmallVariant(models.Model):
    """"Information of a single variant, knows its case."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - chromosome (numeric)
    chromosome_no = models.IntegerField()
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Variant type
    var_type = models.CharField(max_length=8)
    # #: Link to Case ID.
    case_id = models.IntegerField()
    #: Link to VariantSet ID.
    set_id = models.IntegerField()
    #: Miscalleneous information as JSONB.
    info = JSONField(default=dict)
    #: Genotype information as JSONB
    genotype = JSONField()
    #: Number of hom. alt. genotypes
    num_hom_alt = models.IntegerField(default=0)
    #: Number of hom. ref. genotypes
    num_hom_ref = models.IntegerField(default=0)
    #: Number of het. genotypes
    num_het = models.IntegerField(default=0)
    #: Number of hemi alt. genotypes
    num_hemi_alt = models.IntegerField(default=0)
    #: Number of hemi ref. genotypes
    num_hemi_ref = models.IntegerField(default=0)
    #: Flag if in clinvar
    in_clinvar = models.BooleanField(null=True)
    #: Total ExAC allele frequency
    exac_frequency = models.FloatField(null=True)
    #: Total ExAC homoyzgous count
    exac_homozygous = models.IntegerField(null=True)
    #: Total ExAC heterozygous count
    exac_heterozygous = models.IntegerField(null=True)
    #: Total ExAC hemizgous count
    exac_hemizygous = models.IntegerField(null=True)
    #: Total thousand genomes frequency count
    thousand_genomes_frequency = models.FloatField(null=True)
    #: Total thousand genomes homozygous count
    thousand_genomes_homozygous = models.IntegerField(null=True)
    #: Total thousand genomes heterozygous count
    thousand_genomes_heterozygous = models.IntegerField(null=True)
    #: Total thousand genomes hemizygous count
    thousand_genomes_hemizygous = models.IntegerField(null=True)
    #: Total gnomAD exomes frequency
    gnomad_exomes_frequency = models.FloatField(null=True)
    #: Total gnomAD exomes homozygous count
    gnomad_exomes_homozygous = models.IntegerField(null=True)
    #: Total gnomAD exomes heterozygous count
    gnomad_exomes_heterozygous = models.IntegerField(null=True)
    #: Total gnomAD exomes hemizygous count
    gnomad_exomes_hemizygous = models.IntegerField(null=True)
    #: Total gnomAD genomes frequency
    gnomad_genomes_frequency = models.FloatField(null=True)
    #: Total gnomAD genomes homozygous count
    gnomad_genomes_homozygous = models.IntegerField(null=True)
    #: Total gnomAD genomes heterozygous count
    gnomad_genomes_heterozygous = models.IntegerField(null=True)
    #: Total gnomAD genomes hemizygous count
    gnomad_genomes_hemizygous = models.IntegerField(null=True)
    #: RefSeq gene ID
    refseq_gene_id = models.CharField(max_length=16, null=True)
    #: RefSeq transcript ID
    refseq_transcript_id = models.CharField(max_length=16, null=True)
    #: Flag RefSeq transcript coding
    refseq_transcript_coding = models.BooleanField(null=True)
    #: RefSeq HGVS coding sequence
    refseq_hgvs_c = models.CharField(max_length=512, null=True)
    #: RefSeq HGVS protein sequence
    refseq_hgvs_p = models.CharField(max_length=512, null=True)
    #: RefSeq variant effect list
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    #: Distance to next RefSeq exon.
    refseq_exon_dist = models.IntegerField(null=True)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=32, null=True)
    #: Flag EnsEMBL transcript coding
    ensembl_transcript_coding = models.BooleanField(null=True)
    #: EnsEMBL HGVS coding sequence
    ensembl_hgvs_c = models.CharField(max_length=512, null=True)
    #: EnsEMBL HGVS protein sequence
    ensembl_hgvs_p = models.CharField(max_length=512, null=True)
    #: EnsEMBL variant effect list
    ensembl_effect = ArrayField(models.CharField(max_length=64, null=True))
    #: Distance to next ENSEMBL exon.
    ensembl_exon_dist = models.IntegerField(null=True)

    #: Allow bulk import
    objects = CopyManager()

    def get_description(self):
        """Return simple string description of variant"""
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def human_readable(self):
        return "{}:{}-{:,}-{}-{}".format(
            self.release, self.chromosome, self.start, self.reference, self.alternative
        )

    def __repr__(self):
        return "-".join(
            map(
                str,
                (
                    self.set_id,
                    self.release,
                    self.chromosome,
                    self.start,
                    self.reference,
                    self.alternative,
                ),
            )
        )

    class Meta:
        indexes = [
            # For query: select all variants for a case.
            models.Index(fields=["case_id"]),
            # For locating variants by coordiante.
            models.Index(fields=["case_id", "chromosome", "bin"]),
            # Filter query: the most important thing is to reduce the variants for a case quickly. It's questionable
            # how much adding homozygous/frequency really adds here.  Adding them back should only done when we
            # know that it helps.
            GinIndex(fields=["case_id", "refseq_effect"]),
            GinIndex(fields=["case_id", "ensembl_effect"]),
            models.Index(fields=["case_id", "in_clinvar"]),
            # Fast allow-list queries of gene.
            models.Index(fields=["case_id", "ensembl_gene_id"]),
            models.Index(fields=["case_id", "refseq_gene_id"]),
            # For mitochondrial frequency join
            models.Index(fields=["case_id", "chromosome_no"]),
            # For selecting all variants of a set of a case (used for gathering variant stats).
            models.Index(fields=["case_id", "set_id"]),
        ]
        managed = settings.IS_TESTING
        db_table = "variants_smallvariant"


class SmallVariantSummary(models.Model):
    """Summary counts for the small variants.

    In the database, this is a materialized view.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: Number of hom. ref. genotypes.
    count_hom_ref = models.IntegerField()
    #: Number of heterozygous genotypes.
    count_het = models.IntegerField()
    #: Number of hom. alt. genotypes.
    count_hom_alt = models.IntegerField()
    #: Number of hemi ref. genotypes.
    count_hemi_ref = models.IntegerField()
    #: Number of hemi alt. genotypes.
    count_hemi_alt = models.IntegerField()

    class Meta:
        managed = settings.IS_TESTING
        db_table = "variants_smallvariantsummary"


def refresh_variants_smallvariantsummary():
    """Refresh the ``SmallVariantSummary`` materialized view."""

    with transaction.atomic():
        bg_job = BackgroundJob.objects.create(
            name='Refreshing small variant summaries (aka "in-house database")',
            project=None,
            job_type=RefreshSmallVariantSummaryBgJob.spec_name,
            user=User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER),
        )
        refresh_job = RefreshSmallVariantSummaryBgJob.objects.create(bg_job=bg_job)
    with refresh_job.marks():
        with connection.cursor() as cursor:
            try:
                # This will fail if the materialized view is empty.
                with transaction.atomic():
                    cursor.execute(
                        "REFRESH MATERIALIZED VIEW CONCURRENTLY variants_smallvariantsummary"
                    )
            except utils.NotSupportedError:
                with transaction.atomic():
                    cursor.execute("REFRESH MATERIALIZED VIEW variants_smallvariantsummary")


class CaseManager(models.Manager):
    """Manager for custom table-level Case queries"""

    # TODO: properly test searching..

    def find(self, search_terms, _keywords=None):
        """
        Return objects or links matching the query.
        :param search_terms: Search terms (list of string)
        :param _keywords: Optional search keywords as key/value pairs (dict)
        :return: Python list of BaseFilesfolderClass objects
        """
        objects = super().get_queryset().order_by("name")
        term_query = Q()
        for t in search_terms:
            term_query.add(Q(name__iexact=t), Q.OR)
            term_query.add(Q(search_tokens__icontains=t), Q.OR)
        return objects.filter(term_query)


CASE_STATUS_CHOICES = (
    ("initial", "initial"),
    ("active", "active"),
    ("closed-unsolved", "closed as unsolved"),
    ("closed-uncertain", "closed as uncertain"),
    ("closed-solved", "closed as solved"),
)


class CoreCase(models.Model):
    """Abstract base class for Case core fields."""

    #: Genome build
    release = models.CharField(max_length=32, null=True, default="GRCh37")
    #: Name of the case.
    name = models.CharField(max_length=512)
    #: Identifier of the index in ``pedigree``.
    index = models.CharField(max_length=512)
    #: Pedigree information, ``list`` of ``dict`` with the information.
    pedigree = JSONField()
    #: Note field to summarize the current status
    notes = models.TextField(default="", null=True, blank=True)
    #: Status field
    status = models.CharField(max_length=32, default="initial", choices=CASE_STATUS_CHOICES)
    #: Tags field
    tags = ArrayField(models.CharField(max_length=32), default=list, null=True, blank=True)

    class Meta:
        unique_together = (("project", "name"),)
        abstract = True


class Case(CoreCase):
    """Stores information about a (germline) case."""

    class Meta:
        ordering = ("-date_modified",)
        indexes = [models.Index(fields=["name"])]

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: The number of small variants, ``None`` if no small variants have been imported.
    num_small_vars = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name="Small variants",
        help_text="Number of small variants, empty if no small variants have been imported",
    )
    #: The number of structural variants, ``None`` if no structural variants have been imported.
    num_svs = models.IntegerField(
        default=None,
        null=True,
        blank=True,
        verbose_name="Structural variants",
        help_text="Number of structural variants, empty if no structural variants have been imported",
    )

    #: The project containing this case.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    #: Case manager with custom queries, supporting ``find()`` for the search.
    objects = CaseManager()
    #: List of additional tokens to search for, for aiding search
    search_tokens = ArrayField(
        models.CharField(max_length=128, blank=True),
        default=list,
        db_index=True,
        help_text="Search tokens",
    )

    latest_variant_set = models.ForeignKey(
        "SmallVariantSet",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="case_of_latest_variant_set",
    )

    latest_structural_variant_set = models.ForeignKey(
        "svs.StructuralVariantSet",
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True,
        related_name="case_of_latest_structuralvariant_set",
    )

    def latest_variant_set_id(self):
        variant_set = self.latest_variant_set
        if variant_set:
            return variant_set.id
        else:
            return -1

    def has_variants_and_variant_set(self):
        return bool(self.latest_variant_set) and bool(self.num_small_vars)

    def latest_structural_variant_set_id(self):
        structural_variant_set = self.latest_structural_variant_set
        if structural_variant_set:
            return structural_variant_set.id
        else:
            return -1

    def has_svs_and_structural_variant_set(self):
        return bool(self.latest_structural_variant_set) and bool(self.num_svs)

    def days_since_modification(self):
        return (timezone.now() - self.date_modified).days

    def save(self, *args, **kwargs):
        """Override save() to automatically update ``self.search_tokens``"""
        self._update_search_tokens()
        super().save(*args, **kwargs)

    def _update_search_tokens(self):
        """Force-update ``self.search_tokens``, will enable ``.save()`` call to always save."""
        # Get all IDs
        self.search_tokens = [self.name] + [x["patient"] for x in self.pedigree if x.get("patient")]
        # Remove -N1-DNA1-WES1 etc.
        self.search_tokens = [
            re.sub(r"-\S+\d+-\S+\d+-[^-]+\d+$", "", x) for x in self.search_tokens
        ]
        # Convert to lower case
        self.search_tokens = [x.lower() for x in self.search_tokens]
        # Strip non-alphanumeric characters
        self.search_tokens = [re.sub(r"[^a-zA-Z0-9]", "", x) for x in self.search_tokens]

    def get_sex(self, sample):
        """Return ``int``-value sex for the given ``sample`` in ``pedigree``."""
        for line in self.pedigree:
            if line["patient"] == sample:
                return line["sex"]

    def get_absolute_url(self):
        """Return absolute URL for the detail view of this case."""
        return reverse(
            "variants:case-detail",
            kwargs={"project": self.project.sodar_uuid, "case": self.sodar_uuid},
        )

    def get_filter_url(self):
        """Return absolute URL for the filtration view of this case."""
        return reverse(
            "variants:case-filter",
            kwargs={"project": self.project.sodar_uuid, "case": self.sodar_uuid},
        )

    def get_background_jobs(self):
        """Return list of ``BackgroundJob`` objects."""
        # TODO: need to be more dynamic here?
        return BackgroundJob.objects.filter(
            Q(variants_exportfilebgjob_related__case=self)
            | Q(cadd_submission_bg_job__case=self)
            | Q(distiller_submission_bg_job__case=self)
            | Q(spanr_submission_bg_job__case=self)
            | Q(filter_bg_job__case=self)
        )

    def get_members(self):
        """Return list of members in ``pedigree``."""
        return sorted([x["patient"] for x in self.pedigree])

    def get_filtered_pedigree_with_samples(self):
        """Return filtered pedigree lines with members with ``has_gt_entries``."""
        # TODO: unit test me
        return [x for x in self.pedigree if x["has_gt_entries"]]

    def get_family_with_filtered_pedigree_with_samples(self):
        """Concatenate the pedigrees of project's cases that have samples."""
        return {self.name: self.get_filtered_pedigree_with_samples()}

    def get_members_with_samples(self):
        """Returns names of members that genotype information / samples in imported VCF file."""
        # TODO: unit test me
        return sorted([x["patient"] for x in self.get_filtered_pedigree_with_samples()])

    def get_trio_roles(self):
        """Returns a dict with keys mapping ``index``, ``mother``, ``father`` to pedigree member names if present.
        """
        result = {"index": self.index}
        for member in self.pedigree:
            if member["patient"] == self.index:
                if member["father"] != "0":
                    result["father"] = member["father"]
                if member["mother"] != "0":
                    result["mother"] = member["mother"]
        return result

    def sex_errors_pedigree(self):
        """Return dict of sample to error messages indicating sex assignment errors that can be derived from the
        pedigree information.

        Inconsistencies can be determined from father/mother name and sex.
        """
        fathers = set([m["father"] for m in self.pedigree])
        mothers = set([m["mother"] for m in self.pedigree])
        result = {}
        for m in self.pedigree:
            if m["patient"] in fathers and m["sex"] != PED_MALE:
                result[m["patient"]] = ["used as father in pedigree but not male"]
            if m["patient"] in mothers and m["sex"] != PED_FEMALE:
                result[m["patient"]] = ["used as mother in pedigree not female"]
        return result

    def chrx_het_hom_ratio(self, sample):
        """Return het./hom. ratio on chrX for ``sample``."""
        try:
            variant_set = self.latest_variant_set
            if not variant_set:
                return -1
            else:
                sample_stats = variant_set.variant_stats.sample_variant_stats.get(
                    sample_name=sample
                )
                return sample_stats.chrx_het_hom
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return -1.0

    def sex_errors_variant_stats(self, reporter):
        """Return dict of sample to error messages indicating sex assignment errors that can be derived from
        het/hom ratio on chrX.
        """
        import_job = ImportVariantsBgJob.objects.filter(case_name=self.name).order_by(
            "-date_created"
        )
        if import_job and not import_job[0].bg_job.status == "done":
            return {}

        try:
            ped_sex = {m["patient"]: m["sex"] for m in self.pedigree}
            result = {}
            variant_set = self.latest_variant_set
            if variant_set:
                for sample_stats in variant_set.variant_stats.sample_variant_stats.all():
                    sample = sample_stats.sample_name
                    stats_sex = 1 if sample_stats.chrx_het_hom < CHRX_HET_HOM_THRESH else 2
                    if stats_sex != ped_sex[sample]:
                        result[sample] = reporter(stats_sex)
            return result
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return {}

    def sex_errors_to_fix(self):
        return self.sex_errors_variant_stats(lambda x: x)

    def sex_errors(self, disable_pedigree_sex_check=None):
        """Returns dict mapping sample to error messages from both pedigree and variant statistics."""

        result = {}

        if disable_pedigree_sex_check is None:
            disable_pedigree_sex_check = app_settings.get_app_setting(
                "variants", "disable_pedigree_sex_check", project=self.project
            )

        if disable_pedigree_sex_check:
            return result

        for sample, msgs in chain(
            self.sex_errors_pedigree().items(),
            self.sex_errors_variant_stats(
                lambda x: [
                    "sex from pedigree conflicts with one derived from het/hom ratio on chrX"
                ]
            ).items(),
        ):
            result.setdefault(sample, [])
            result[sample] += msgs
        return result

    def rel_errors(self):
        """Returns dict mapping sample to list of relationship errors."""
        ped_entries = {m["patient"]: m for m in self.pedigree}
        result = {}
        import_job = ImportVariantsBgJob.objects.filter(case_name=self.name).order_by(
            "-date_created"
        )
        if import_job and not import_job[0].bg_job.status == "done":
            return result

        try:
            variant_set = self.latest_variant_set
            if variant_set:
                for rel_stats in variant_set.variant_stats.relatedness.all():
                    relationship = "other"
                    if (
                        ped_entries[rel_stats.sample1]["father"]
                        == ped_entries[rel_stats.sample2]["father"]
                        and ped_entries[rel_stats.sample1]["mother"]
                        == ped_entries[rel_stats.sample2]["mother"]
                        and ped_entries[rel_stats.sample1]["father"] != "0"
                        and ped_entries[rel_stats.sample1]["mother"] != "0"
                    ):
                        relationship = "sibling-sibling"
                    elif (
                        ped_entries[rel_stats.sample1]["father"] == rel_stats.sample2
                        or ped_entries[rel_stats.sample1]["mother"] == rel_stats.sample2
                        or ped_entries[rel_stats.sample2]["father"] == rel_stats.sample1
                        or ped_entries[rel_stats.sample2]["mother"] == rel_stats.sample1
                    ):
                        relationship = "parent-child"
                    if (
                        relationship == "sibling-sibling"
                        and rel_stats.relatedness() < THRESH_SIBLING
                    ) or (
                        relationship == "parent-child" and rel_stats.relatedness() < THRESH_PARENT
                    ):
                        for sample in (rel_stats.sample1, rel_stats.sample2):
                            result.setdefault(sample, []).append(
                                (
                                    "pedigree shows {} relation for {} and {} but variants show low degree "
                                    "of relatedness"
                                ).format(
                                    relationship,
                                    only_source_name(rel_stats.sample1),
                                    only_source_name(rel_stats.sample2),
                                )
                            )
            return result
        except SmallVariantSet.variant_stats.RelatedObjectDoesNotExist:
            return {}

    def shortened_notes_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.notes) > max_chars:
            return self.notes[:max_chars] + "..."
        else:
            return self.notes

    def get_annotation_sv_count(self):
        variants = set()
        for record in self.structural_variant_comments.all():
            variants.add((record.chromosome, record.start, record.end, record.sv_type))
        for record in self.structural_variant_flags.all():
            variants.add((record.chromosome, record.start, record.end, record.sv_type))
        return len(variants)

    def get_annotation_small_variant_count(self):
        variants = set()
        for record in self.small_variant_flags.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        for record in self.small_variant_comments.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        for record in self.acmg_ratings.all():
            variants.add((record.chromosome, record.start, record.reference, record.alternative))
        return len(variants)

    def get_annotation_count(self):
        """Return annotation count."""
        return self.get_annotation_sv_count() + self.get_annotation_small_variant_count()

    def update_terms(self, terms):
        """Given a dict of individual names to list of terms, ensure that the appropriate ``CasePhenotypeTerms``
        records exist.
        """
        with transaction.atomic():
            self.phenotype_terms.all().delete()
            for name, lst in terms.items():
                self.phenotype_terms.create(individual=name, terms=lst)

    def __str__(self):
        """Return case name as human-readable description."""
        return self.name


class CasePhenotypeTerms(models.Model):
    """Phenotype annotation for an individual in a case."""

    #: The case that this belongs to.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="phenotype_terms",
        help_text="Case for this annotation",
    )

    #: The name of the individual that this belongs to.
    individual = models.CharField(max_length=128, null=False, blank=False, help_text="Individual")

    #: A list of HPO, Orphanet, and OMIM terms that the case has been annotated with.
    terms = ArrayField(
        models.CharField(max_length=128, blank=False),
        default=list,
        help_text="Phenotype annotation terms with HPO, Orphanet, and OMIM terms",
    )

    class Meta:
        unique_together = (("case", "individual"),)
        ordering = ("individual",)


@receiver(pre_delete)
def delete_case_cascaded(sender, instance, **kwargs):
    """Signal handler when attempting to delete a case

    Bulk deletes are atomic transactions, including pre/post delete signals.
    Comment From their code base in `contrib/contenttypes/fields.py`:

    ```
    if bulk:
        # `QuerySet.delete()` creates its own atomic block which
        # contains the `pre_delete` and `post_delete` signal handlers.
        queryset.delete()
    ```
    """
    if sender == Case:
        SmallVariant.objects.filter(case_id=instance.id).delete()
        for plugin in BackgroundJobsPluginPoint.get_plugins():
            for _, klass in plugin.job_specs.items():
                bgjobs = []
                if hasattr(klass, "case_id"):
                    bgjobs = klass.objects.filter(case_id=instance.id)
                elif hasattr(klass, "case_name"):
                    bgjobs = klass.objects.filter(project=instance.project, case_name=instance.name)
                for bgjob in bgjobs:
                    bgjob.bg_job.delete()


class CaseComments(models.Model):
    """Comments associated with a case."""

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Case for the comment
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="case_comments",
        help_text="Case for this comment",
    )
    #: User who created the comment
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="case_comments",
        help_text="User who created the comment",
    )
    #: User
    comment = models.TextField()

    class Meta:
        ordering = ["date_created"]

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.comment) > max_chars:
            return self.comment[:max_chars] + "..."
        else:
            return self.comment

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


class SmallVariantSet(models.Model):
    """A set of small variants associated with a case.

    This additional step of redirection is created such that a new set of variants can be imported into the database
    without affecting existing variants and without using transactions.
    """

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: The case that the variants are for.
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case that this set is for"
    )
    #: Genome build
    release = models.CharField(max_length=32, null=True, default="GRCh37")
    #: The state of the variant set.
    state = models.CharField(
        max_length=16,
        choices=(("importing", "importing"), ("active", "active"), ("deleting", "deleting")),
        null=False,
        blank=False,
    )


def cleanup_variant_sets(min_age_hours=12):
    """Cleanup old variant sets."""
    variant_sets = list(
        SmallVariantSet.objects.filter(
            date_created__lte=datetime.now() - timedelta(hours=min_age_hours)
        ).exclude(state="active")
    )
    smallvariant_table = get_meta().tables["variants_smallvariant"]
    for variant_set in variant_sets:
        get_engine().execute(
            smallvariant_table.delete().where(
                and_(
                    smallvariant_table.c.set_id == variant_set.id,
                    smallvariant_table.c.case_id == variant_set.case.id,
                )
            )
        )
        variant_set.delete()


class AnnotationReleaseInfo(models.Model):
    """Model to track the database releases used during annotation of a case.
    """

    #: Release of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: Name of imported table
    table = models.CharField(max_length=512)
    #: Timestamp of import
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Link to case
    case = models.ForeignKey(Case, on_delete=models.CASCADE,)
    #: Link to variant set
    variant_set = models.ForeignKey(SmallVariantSet, on_delete=models.CASCADE,)

    class Meta:
        unique_together = ("genomebuild", "table", "variant_set")


class CaseAlignmentStats(models.Model):
    """Store alignment information about alignment statistics for a case."""

    #: Reference to the case.
    case = models.ForeignKey(Case, on_delete=models.CASCADE, null=False)
    #: Reference to the small variant set.
    variant_set = models.OneToOneField(SmallVariantSet, on_delete=models.CASCADE, null=False)
    #: The BAM statistics information.  On the top level, there is one entry for each sample.  Below this are the keys
    #: bamstats, idxstats, min_cov_targets, min_cov_bases.  Below bamstats, there is an entry from "samtools stats"
    #: metric (as retrieved by ``grep '^SN'`` to the metric value.  Below idxstats, the contig name is mapped to
    #: a dict with "mapped" and "unmapped" entries.  Below min_cov_targets is a dict mapping coverage to the percentage
    #: of targets having a minimal coverage of the key value.  Below min_cov_bases is a dict mapping coverage to
    #: the percentage of *bases* having a minimal coverage of the key value.
    bam_stats = JSONField(default=dict, null=False)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = (models.Index(fields=["case"]),)


#: File type choices for ``ExportFileBgJob``.
EXPORT_TYPE_CHOICE_TSV = "tsv"
EXPORT_TYPE_CHOICE_XLSX = "xlsx"
EXPORT_TYPE_CHOICE_VCF = "vcf"
EXPORT_FILE_TYPE_CHOICES = (
    (EXPORT_TYPE_CHOICE_TSV, "TSV File"),
    (EXPORT_TYPE_CHOICE_XLSX, "Excel File (XLSX)"),
    (EXPORT_TYPE_CHOICE_VCF, "VCF File"),
)


class ExportFileBgJobBase(JobModelMessageMixin, models.Model):
    """Base class for background file export jobs."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    #: The query arguments.
    query_args = JSONField(null=False, help_text="(Validated) query parameters")
    #: The file type to create.
    file_type = models.CharField(
        max_length=32, choices=EXPORT_FILE_TYPE_CHOICES, help_text="File types for exported file"
    )

    class Meta:
        ordering = ("-date_created",)
        abstract = True


class ExportFileBgJob(ExportFileBgJobBase):
    """Background job for exporting query results for a single case as a file."""

    # TODO: rename to reflect single-case purpose

    #: Task description for logging.
    task_desc = "Exporting single case to file"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.export_file_bg_job"

    #: The case to export.
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to export"
    )

    def get_human_readable_type(self):
        return "Single-case File Export"

    def get_absolute_url(self):
        return reverse(
            "variants:export-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ExportFileJobResult(models.Model):
    """Result of ``ExportFileBgJob``."""

    job = models.OneToOneField(
        ExportFileBgJob,
        on_delete=models.CASCADE,
        related_name="export_result",
        null=False,
        help_text="Related file export job",
    )
    expiry_time = models.DateTimeField(help_text="Time at which the file download expires")
    payload = models.BinaryField(help_text="Resulting exported file")


class ExportProjectCasesFileBgJob(ExportFileBgJobBase):
    """Background job for exporting query results for all cases in a project as a file."""

    # TODO: rename to reflect single-case purpose

    #: Task description for logging.
    task_desc = "Exporting all project cases to file"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.project_cases_export_file_bg_job"

    #: Cohort to export
    cohort = models.ForeignKey("cohorts.Cohort", on_delete=models.CASCADE, null=True)

    def get_human_readable_type(self):
        return "Project-wide Case File Export"

    def get_absolute_url(self):
        return reverse(
            "variants:project-cases-export-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ExportProjectCasesFileBgJobResult(models.Model):
    """Result of ``ExportProjectCasesFileBgJob``."""

    job = models.OneToOneField(
        ExportProjectCasesFileBgJob,
        on_delete=models.CASCADE,
        related_name="export_result",
        null=False,
        help_text="Related file export job",
    )
    expiry_time = models.DateTimeField(help_text="Time at which the file download expires")
    payload = models.BinaryField(help_text="Resulting exported file")


class DistillerSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to MutationDistiller."""

    #: Task description for logging.
    task_desc = "Submission to MutationDistiller"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.distiller_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="distiller_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    distiller_project_id = models.CharField(
        max_length=100,
        null=True,
        help_text="The project ID that MutationDistiller assigned on submission",
    )

    def get_human_readable_type(self):
        return "MutationDistiller Submission"

    def get_distiller_project_url(self):
        """Returns URL to MutationDistiller project if ``distiller_project_id`` is set.

        Returns ``None`` otherwise.
        """
        if self.distiller_project_id:
            return (
                "https://www.mutationdistiller.org/temp/QE/vcf_%s/progress.html"
                % self.distiller_project_id
            )
        else:
            return None

    def get_absolute_url(self):
        return reverse(
            "variants:distiller-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class CaddSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to CADD."""

    #: Task description for logging.
    task_desc = "Submission to CADD"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.cadd_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="cadd_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    cadd_version = models.CharField(
        max_length=100, help_text="The CADD version used for the annotation"
    )

    cadd_job_id = models.CharField(
        max_length=100, null=True, help_text="The project ID that CADD assigned on submission",
    )

    def get_human_readable_type(self):
        return "CADD Submission"

    def get_cadd_result_url(self):
        """Returns URL to CADD result download if ``cadd_job_id`` is set.

        Returns ``None`` otherwise.
        """
        if self.cadd_job_id:
            return "https://cadd.gs.washington.edu/check_avail/%s_anno_%s.tsv.gz" % (
                self.cadd_version,
                self.cadd_job_id,
            )
        else:
            return None

    def get_absolute_url(self):
        return reverse(
            "variants:cadd-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SpanrSubmissionBgJob(JobModelMessageMixin, models.Model):
    """Background job for submitting variants to SPANR."""

    #: Task description for logging.
    task_desc = "Submission to SPANR"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.spanr_submission_bg_job"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="spanr_submission_bg_job",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to export"
    )
    query_args = JSONField(null=False, help_text="(Validated) query parameters")

    spanr_job_url = models.CharField(max_length=100, null=True, help_text="The SPANR job URL")

    def get_human_readable_type(self):
        return "SPANR Submission"

    def get_absolute_url(self):
        return reverse(
            "variants:spanr-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SmallVariantComment(models.Model):
    """Model for commenting on a ``SmallVariant``."""

    #: User who created the comment.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="small_variant_comments",
        help_text="User who created the comment",
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: Chromosome as Integer for proper odering
    chromosome_no = models.IntegerField(default=0)
    #: The 1-based start position of the small variant coordinate.
    start = models.IntegerField()
    #: The end position of the small variant coordinate.
    end = models.IntegerField()
    #: The UCSC bin.
    bin = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_comments",
        help_text="Case that this variant is flagged in",
    )

    #: The comment text.
    text = models.TextField(null=False, blank=False)

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_gene_symbols(self):
        """Query for overlapping genes."""
        # TODO: could be made much nicer with join in DB via SQL Alchemy
        bins = binning.containing_bins(self.start - 1, self.end)
        gene_intervals = list(
            GeneInterval.objects.filter(
                database="ensembl",
                release=self.release,
                chromosome=self.chromosome,
                bin__in=bins,
                start__lte=self.end,
                end__gte=self.start,
            )
        )
        gene_ids = [itv.gene_id for itv in gene_intervals]
        symbols1 = {
            o.gene_symbol for o in EnsemblToGeneSymbol.objects.filter(ensembl_gene_id__in=gene_ids)
        }
        symbols2 = {o.symbol for o in Hgnc.objects.filter(ensembl_gene_id__in=gene_ids)}
        return sorted(symbols1 | symbols2)

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            start=self.start,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    def save(self, *args, **kwargs):
        """Save chromosome as integer for proper ordering."""
        self.chromosome_no = CHROMOSOME_STR_TO_CHROMOSOME_INT.get(self.chromosome, 0)
        super().save(*args, **kwargs)

    class Meta:
        indexes = (
            models.Index(
                fields=["release", "chromosome", "start", "end", "reference", "alternative", "case"]
            ),
        )
        ordering = ["chromosome_no", "start", "end"]

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.text) > max_chars:
            return self.text[:max_chars] + "..."
        else:
            return self.text

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


#: Choices for visual inspect, wet-lab validation, or clinical/phenotype flag statuses.
VARIANT_RATING_CHOICES = (
    ("positive", "positive"),
    ("uncertain", "uncertain"),
    ("negative", "negative"),
    ("empty", "empty"),
)


class SmallVariantFlags(models.Model):
    """Small variant flag models, at most one per variant of each model."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Small variant flags UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: The genome release of the small variant coordinate.
    release = models.CharField(max_length=32)
    #: The chromosome of the small variant coordinate.
    chromosome = models.CharField(max_length=32)
    #: Chromosome as Integer for proper odering
    chromosome_no = models.IntegerField(default=0)
    #: The 1-based start position of the small variant coordinate.
    start = models.IntegerField()
    #: The end position of the small variant coordiantes
    end = models.IntegerField()
    #: The UCSC bin.
    bin = models.IntegerField()
    #: The reference bases of the small variant coordinate.
    reference = models.CharField(max_length=512)
    #: The alternative bases of the small variant coordinate.
    alternative = models.CharField(max_length=512)

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_flags",
        help_text="Case that this variant is flagged in",
    )

    # Boolean fields for checking

    #: Bookmarked: saved for later
    flag_bookmarked = models.BooleanField(default=False, null=False)
    #: Candidate variant
    flag_candidate = models.BooleanField(default=False, null=False)
    #: Finally selected causative variant
    flag_final_causative = models.BooleanField(default=False, null=False)
    #: Selected for wet-lab validation
    flag_for_validation = models.BooleanField(default=False, null=False)
    #: Gene affected by this variant has no known disease association
    flag_no_disease_association = models.BooleanField(default=False, null=False)
    #: Variant does segregate
    flag_segregates = models.BooleanField(default=False, null=False)
    #: Variant does not segregate
    flag_doesnt_segregate = models.BooleanField(default=False, null=False)

    # Choice fields for gradual rating

    #: Visual inspection flag.
    flag_visual = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Molecular flag.
    flag_molecular = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Wet-lab validation flag.
    flag_validation = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Phenotype/clinic suitability flag
    flag_phenotype_match = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Summary/colour code flag
    flag_summary = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )

    def get_gene_symbols(self):
        """Query for overlapping genes."""
        # TODO: could be made much nicer with join in DB via SQL Alchemy
        bins = binning.containing_bins(self.start - 1, self.end)
        gene_intervals = list(
            GeneInterval.objects.filter(
                database="ensembl",
                release=self.release,
                chromosome=self.chromosome,
                bin__in=bins,
                start__lte=self.end,
                end__gte=self.start,
            )
        )
        gene_ids = [itv.gene_id for itv in gene_intervals]
        symbols1 = {
            o.gene_symbol for o in EnsemblToGeneSymbol.objects.filter(ensembl_gene_id__in=gene_ids)
        }
        symbols2 = {o.symbol for o in Hgnc.objects.filter(ensembl_gene_id__in=gene_ids)}
        return sorted(symbols1 | symbols2)

    def human_readable(self):
        """Return human-redable version of flags"""
        if self.no_flags_set():
            return "no flags set"
        else:
            flag_desc = []
            for name in ("bookmarked", "for_validation", "candidate", "final causative"):
                if getattr(self, "flag_%s" % name.replace(" ", "_")):
                    flag_desc.append(name)
            for name in ("visual", "validation", "molecular", "phenotype_match", "summary"):
                field = getattr(self, "flag_%s" % name)
                if field and field != "empty":
                    flag_desc.append("%s rating is %s" % (name.split("_")[0], field))
            return ", ".join(flag_desc)

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#flags-" + self.get_variant_description()

    def no_flags_set(self):
        """Return true if no flags are set and the model can be deleted."""
        # TODO: unit test me
        return not any(
            (
                self.flag_bookmarked,
                self.flag_candidate,
                self.flag_final_causative,
                self.flag_for_validation,
                self.flag_no_disease_association,
                self.flag_segregates,
                self.flag_doesnt_segregate,
                self.flag_molecular != "empty",
                self.flag_visual != "empty",
                self.flag_validation != "empty",
                self.flag_phenotype_match != "empty",
                self.flag_summary != "empty",
            )
        )

    def clean(self):
        """Make sure that the case has such a variant"""
        # TODO: unit test me
        small_vars = SmallVariant.objects.filter(
            case_id=self.case.pk,
            release=self.release,
            chromosome=self.chromosome,
            start=self.start,
            reference=self.reference,
            alternative=self.alternative,
        )
        if not small_vars.exists():
            raise ValidationError("No corresponding variant in case")

    def save(self, *args, **kwargs):
        """Save chromosome as integer for proper ordering."""
        self.chromosome_no = CHROMOSOME_STR_TO_CHROMOSOME_INT.get(self.chromosome, 0)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "start",
            "end",
            "reference",
            "alternative",
            "case",
        )
        indexes = (
            models.Index(
                fields=["release", "chromosome", "start", "end", "reference", "alternative", "case"]
            ),
        )
        ordering = ["chromosome_no", "start", "end"]


class SmallVariantQueryBase(models.Model):
    """Base class for models storing queries to the ``SmallVariant`` model.

    Saving the query settings is implemented as a JSON plus a version field.  This design was chosen to allow for
    less rigid upgrade paths of the form schema itself.  Further, we will need a mechanism for upgrading the form
    "schemas" automatically and then storing the user settings.
    """

    #: DateTime of query.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: Query UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Small variant flags SODAR UUID"
    )

    #: User who created the query.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="%(app_label)s_%(class)s_related",
        help_text="User who created the query",
    )

    #: The identifier of the form
    form_id = models.CharField(max_length=100, null=False, help_text="Identifier of the form")

    #: The version of the form when saving.
    form_version = models.IntegerField(null=False, help_text="Version of form when saving")

    #: The query settings as JSON.
    query_settings = JSONField(null=False, help_text="The query settings")

    #: Many-to-Many relationship with SmallVariant to store query results for faster future retrieval
    query_results = models.ManyToManyField(SmallVariant)

    #: Optional, user-assign query name.
    name = models.CharField(
        max_length=100, null=True, default=None, help_text="Optional user-assigned name"
    )

    #: Flag for being public or not.
    public = models.BooleanField(
        null=False, default=False, help_text="Case is flagged as public or not"
    )

    class Meta:
        abstract = True
        ordering = ("-date_created",)

    def is_prioritization_enabled(self):
        """Return whether prioritization is enabled in this query."""
        return all(
            (
                self.query_settings.get("prio_enabled"),
                self.query_settings.get("prio_algorithm"),
                self.query_settings.get("prio_hpo_terms", []),
            )
        )

    def query_type(self):
        raise NotImplementedError("Implement me!")


class SmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of single-case queries to the ``SmallVariant`` model.
    """

    # TODO: rename to reflect single-case

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_queries",
        help_text="The case that the query relates to",
    )

    def query_type(self):
        return "smallvariantquery"


class ProjectCasesSmallVariantQuery(SmallVariantQueryBase):
    """Allow saving of whole-project queries to the ``SmallVariant`` model.

    """

    #: The related case.
    project = models.ForeignKey(
        CaseAwareProject,
        on_delete=models.CASCADE,
        null=False,
        related_name="small_variant_queries",
        help_text="The project that the query relates to",
    )

    def query_type(self):
        return "projectcasessmallvariantquery"


class SmallVariantQueryGeneScores(models.Model):
    """Annotate ``SmallVariantQuery`` with gene scores (if configured to do so)."""

    #: The query to annotate.
    query = models.ForeignKey(SmallVariantQuery, on_delete=models.CASCADE)

    #: The Entrez gene ID.
    gene_id = models.CharField(max_length=64, null=False, blank=False, help_text="Entrez gene ID")

    #: The gene symbol.
    gene_symbol = models.CharField(
        max_length=128, null=False, blank=False, help_text="The gene symbol"
    )

    #: The priority type.
    priority_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The priority type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The gene score")


class SmallVariantQueryVariantScores(models.Model):
    """Annotate ``SmallVariantQuery`` with pathogenicity score."""

    #: The query to annotate.
    query = models.ForeignKey(SmallVariantQuery, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - 1-based start position.
    start = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - end position.
    end = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - UCSC bin.
    bin = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - reference
    reference = models.CharField(max_length=512, null=False, blank=False)

    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512, null=False, blank=False)

    #: The score type.
    score_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The score type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The variant score")

    #: Further information.
    info = JSONField(default=dict)

    def variant_key(self):
        return "-".join(
            map(str, [self.release, self.chromosome, self.start, self.reference, self.alternative])
        )


class ProjectCasesSmallVariantQueryVariantScores(models.Model):
    """Annotate ``ProjectCasesSmallVariantQuery`` with pathogenicity score."""

    #: The query to annotate.
    query = models.ForeignKey(ProjectCasesSmallVariantQuery, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - 1-based start position.
    start = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - end position.
    end = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - UCSC bin.
    bin = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - reference
    reference = models.CharField(max_length=512, null=False, blank=False)

    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512, null=False, blank=False)

    #: The score type.
    score_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The score type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The variant score")

    #: Further information.
    info = JSONField(default=dict)

    def variant_key(self):
        return "-".join(
            map(str, [self.release, self.chromosome, self.start, self.reference, self.alternative])
        )


class FilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing single case filter query and storing query results in table SmallVariantQueryBase."""

    #: Task description for logging.
    task_desc = "Single case filter query and store results"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="filter_bg_job",
        help_text="Background job for filtering and storing query results",
        on_delete=models.CASCADE,
    )

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to filter"
    )

    #: Link to the smallvariantquery object. Holds query arguments and results
    smallvariantquery = models.ForeignKey(
        SmallVariantQuery, on_delete=models.CASCADE, null=False, help_text="Query that is executed."
    )

    def get_human_readable_type(self):
        return "Single-case query results"

    def get_absolute_url(self):
        return reverse(
            "variants:filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class ProjectCasesFilterBgJob(JobModelMessageMixin, models.Model):
    """Background job for processing joint project filter query and storing query results in table SmallVariantQueryBase."""

    #: Task description for logging.
    task_desc = "Joint project filter query and store results."

    #: String identifying model in BackgroundJob.
    spec_name = "variants.project_cases_filter_bg_job"

    #: Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="project_cases_filter_bg_job",
        help_text="Background job for filtering joint project and storing query results.",
        on_delete=models.CASCADE,
    )

    #: Link to the ProjectCaseSmallVariantQuery object. Holds query arguments and results.
    projectcasessmallvariantquery = models.ForeignKey(
        ProjectCasesSmallVariantQuery,
        on_delete=models.CASCADE,
        null=False,
        help_text="Query that is executed.",
    )

    cohort = models.ForeignKey(
        "cohorts.Cohort",
        on_delete=models.CASCADE,
        null=True,
        related_name="project_cases_filter_bg_job",
    )

    def get_human_readable_type(self):
        return "Joint project query results"

    def get_absolute_url(self):
        return reverse(
            "variants:project-cases-filter-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class CaseVariantStats(models.Model):
    """Statistics on various aspects of variants of a case:

    - Ts/Tv ratio
    """

    #: The related ``SmallVariantSet``.
    variant_set = models.OneToOneField(
        SmallVariantSet,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this variant set",
        on_delete=models.CASCADE,
    )


class SampleVariantStatistics(models.Model):
    """Single-number variant statistics for donors in a ``Case`` via ``CaseVariantStats``."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="sample_variant_stats",
        help_text="Single-value variant statistics for one individual",
        on_delete=models.CASCADE,
    )

    #: The name of the donor.
    sample_name = models.CharField(max_length=200, null=False)

    #: The number of on-target transitions (A <-> G, C <-> T).
    ontarget_transitions = models.IntegerField(null=False)
    #: The number of on-target transversions.
    ontarget_transversions = models.IntegerField(null=False)

    #: The number of on-target SNVs
    ontarget_snvs = models.IntegerField(null=False)
    #: The number of on-target Indels
    ontarget_indels = models.IntegerField(null=False)
    #: The number of on-target MNVs
    ontarget_mnvs = models.IntegerField(null=False)

    #: Counts for the different variant effects
    ontarget_effect_counts = JSONField(null=False)

    #: Histogram of indel sizes.
    ontarget_indel_sizes = JSONField(null=False)
    #: Histogram of read depths.
    ontarget_dps = JSONField(null=False)
    #: 5-value summary of on-target read depths.
    ontarget_dp_quantiles = ArrayField(models.FloatField(), size=5)

    #: Overall het ratio.
    het_ratio = models.FloatField(null=False)
    #: Hom/het ratio on chrX in PAR1 and PAR2, for sex checking.
    chrx_het_hom = models.FloatField(null=False)

    def ontarget_ts_tv_ratio(self):
        """Compute Ts/Tv ratio."""
        if not self.ontarget_transversions:
            return 0.0
        else:
            return self.ontarget_transitions / self.ontarget_transversions

    class Meta:
        ordering = ("sample_name",)


class BaseRelatedness(models.Model):
    """Shared functionality of relatedness of individuals in a collective.

    This could be a pedigree or a project.
    """

    #: First sample.
    sample1 = models.CharField(max_length=200, null=False)
    #: Second sample.
    sample2 = models.CharField(max_length=200, null=False)

    #: The Het_1_2 statistic
    het_1_2 = models.IntegerField(null=False)
    #: The Het_1 statistic
    het_1 = models.IntegerField(null=False)
    #: The Het_2 statistic
    het_2 = models.IntegerField(null=False)
    #: The N_IBS0 statistic
    n_ibs0 = models.IntegerField(null=False)
    #: The N_IBS1 statistic
    n_ibs1 = models.IntegerField(null=False)
    #: The N_IBS2 statistic
    n_ibs2 = models.IntegerField(null=False)

    def relatedness(self):
        """Return relatedness following Pedersen and Quinlan (2017)."""
        if self.het_1 * self.het_2:
            return (self.het_1_2 - 2 * self.n_ibs0) * 2 / math.sqrt(self.het_1 * self.het_2)
        else:
            return 0.0

    class Meta:
        abstract = True
        ordering = ("sample1", "sample2")


class PedigreeRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a pedigree/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        CaseVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
        on_delete=models.CASCADE,
    )


class ProjectVariantStats(models.Model):
    """Statistics on various aspects of variants of all cases in a project."""

    #: The related ``Project``.
    project = models.OneToOneField(
        Project,
        null=False,
        related_name="variant_stats",
        help_text="The variant statistics object for this projects",
        on_delete=models.CASCADE,
    )


class ProjectRelatedness(BaseRelatedness):
    """Store relatedness information between two donors in a case/``Case``.."""

    #: The related ``CaseVariantStats``.
    stats = models.ForeignKey(
        ProjectVariantStats,
        null=False,
        related_name="relatedness",
        help_text="Pedigree relatedness information",
        on_delete=models.CASCADE,
    )


class ComputeProjectVariantsStatsBgJob(JobModelMessageMixin, models.Model):
    """Background job for computing project variants statistics."""

    #: Task description for logging.
    task_desc = "Compute project-wide variants statistics"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.compute_project_variants_stats"

    # Fields required by SODAR
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Job Specialization SODAR UUID"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="compute_project_variants_stats",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    def get_human_readable_type(self):
        return "Project-wide Variant Statistics Computation"

    def get_absolute_url(self):
        return reverse(
            "variants:project-stats-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class PathogenicityScoreCacheBase(models.Model):
    """Base model class for the pathogenicity scoring caches to store the API results."""

    #: Date of last retrieval
    last_retrieved = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    class Meta:
        abstract = True


class CaddPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the CADD pathogenicity API results."""

    #: Info dictionary
    info = JSONField()
    #: Tuple of returned scores
    scores = ArrayField(models.FloatField(), size=2)


class UmdPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the UMD predictor API results."""

    #: Amino acid wildtype
    aa_wildtype = models.CharField(max_length=512)
    #: Amino acid mutant
    aa_mutant = models.CharField(max_length=512)
    #: Gene symbol
    gene_name = models.CharField(max_length=512)
    #: Conclusion
    conclusion = models.CharField(max_length=512)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=32)
    #: Pathogenicity score
    pathogenicity_score = models.IntegerField()
    #: Transcript position
    transcript_position = models.IntegerField()


class MutationTasterPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the MutationTaster API results."""

    #: Ensembl transcript id
    transcript_stable = models.CharField(max_length=32, null=True)
    #: Entrez ID
    ncbi_geneid = models.CharField(max_length=16, null=True)
    #: Pathogenicity prediction
    prediction = models.CharField(max_length=32, null=True)
    #: Model used for predicition
    model = models.CharField(max_length=32, null=True)
    #: Probability from bayes classifier
    bayes_prob_dc = models.IntegerField(null=True)
    #: Further information
    note = models.CharField(max_length=512, null=True)
    #: Splicesite
    splicesite = models.CharField(max_length=32, null=True)
    #: Distance from splicesite
    distance_from_splicesite = models.IntegerField(null=True)
    #: Disease database this mutation is registered in (e.g. ClinVar)
    disease_mutation = models.CharField(max_length=32, null=True)
    #: Polymorphism database this mutation is registered in (e.g. ExAC)
    polymorphism = models.CharField(max_length=32, null=True)


# TODO: Improve wrapper so we can assign obj.phenotype_rank and score
class RowWithPhenotypeScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for phenotype score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_phenotype_rank = None
        self._self_phenotype_score = -1

    @property
    def phenotype_rank(self):
        return self._self_phenotype_rank

    @property
    def phenotype_score(self):
        return self._self_phenotype_score

    def __getitem__(self, key):
        if key == "phenotype_rank":
            return self.phenotype_rank
        elif key == "phenotype_score":
            return self.phenotype_score
        else:
            return self.__wrapped__.__getitem__(key)


def annotate_with_phenotype_scores(rows, gene_scores):
    """Annotate the results in ``rows`` with phenotype scores stored in ``small_variant_query``.

    Variants are ranked by the gene scors, automatically ranking them by gene.
    """
    rows = [RowWithPhenotypeScore(row) for row in rows]
    for row in rows:
        row._self_phenotype_score = gene_scores.get(row.entrez_id, -1)
    rows.sort(key=lambda row: (row._self_phenotype_score, row.entrez_id or ""), reverse=True)
    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].phenotype_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.phenotype_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_gene_score = row.phenotype_score
            prev_gene = row.entrez_id
        row._self_phenotype_rank = rank
    return rows


# TODO: Improve wrapper so we can assign obj.pathogenicity_rank and score
class RowWithPathogenicityScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for pathogenicity score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_pathogenicity_rank = None
        self._self_pathogenicity_score = -1
        self._self_pathogenicity_score_info = {}

    @property
    def pathogenicity_rank(self):
        return self._self_pathogenicity_rank

    @property
    def pathogenicity_score(self):
        return self._self_pathogenicity_score

    @property
    def pathogenicity_score_info(self):
        return self._self_pathogenicity_score_info

    def __getitem__(self, key):
        if key == "pathogenicity_rank":
            return self.pathogenicity_rank
        elif key == "pathogenicity_score":
            return self.pathogenicity_score
        elif key == "pathogenicity_score_info":
            return self.pathogenicity_score_info
        else:
            return self.__wrapped__.__getitem__(key)

    def variant_key(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )


def annotate_with_pathogenicity_scores(rows, variant_scores):
    """Annotate the results in ``rows`` with pathogenicity scores stored in ``small_variant_query``.

    Variants are score independently but grouped by gene (the highest score of each variant in
    each gene is used for ranking).
    """
    # Get list of rows and assign pathogenicity scores.
    rows = [RowWithPathogenicityScore(row) for row in rows]
    for row in rows:
        key = row.variant_key()
        score = variant_scores.get(key)
        if score:
            row._self_pathogenicity_score = score[0]
            row._self_pathogenicity_score_info = score[1]
    # Get highest score for each gene.
    gene_scores = {}
    for row in rows:
        gene_scores[row.entrez_id] = max(
            gene_scores.get(row.entrez_id, 0), row.pathogenicity_score or 0.0
        )

    # Sort variant by gene score now.
    def gene_score(row):
        if row.entrez_id:
            return (gene_scores[row.entrez_id], row.pathogenicity_score or 0.0)
        else:
            return (0.0, 0.0)  # no gene => lowest score

    rows.sort(key=gene_score, reverse=True)

    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].pathogenicity_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.pathogenicity_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            # We get the score of the first variant of a gene, they are ordered by score and thus the first variant is
            # the highest, representing the gene score.
            prev_gene_score = row.pathogenicity_score
            prev_gene = row.entrez_id
        row._self_pathogenicity_rank = rank
    return rows


# TODO: Improve wrapper so we can assign obj.pathogenicity_rank and score
class RowWithJointScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for joint score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_joint_rank = None
        self._self_joint_score = -1

    @property
    def joint_rank(self):
        return self._self_joint_rank

    @property
    def joint_score(self):
        return self._self_joint_score

    def __getitem__(self, key):
        if key == "joint_rank":
            return self.joint_rank
        elif key == "joint_score":
            return self.joint_score
        else:
            return self.__wrapped__.__getitem__(key)


def annotate_with_joint_scores(rows):
    """Annotate the results in ``rows`` with joint scores stored in ``small_variant_query``.

    Variants are score independently but grouped by gene (the highest score of each variant in
    each gene is used for ranking).
    """
    # Get list of rows and assign joint scores.
    rows = [RowWithJointScore(row) for row in rows]
    for row in rows:
        key = "-".join(
            map(str, [row["chromosome"], row["start"], row["reference"], row["alternative"]])
        )
        row._self_joint_score = (row.phenotype_score or 0) * (row.pathogenicity_score or 0)
    # Get highest score for each gene.
    gene_scores = {}
    for row in rows:
        gene_scores[row.entrez_id] = max(gene_scores.get(row.entrez_id, 0), row.joint_score or 0)

    # Sort variant by gene score now.
    def gene_score(row):
        if row.entrez_id:
            return gene_scores[row.entrez_id]
        else:
            return 0.0  # no gene => lowest score

    rows.sort(key=gene_score, reverse=True)

    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].joint_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.joint_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_gene_score = row.joint_score
            prev_gene = row.entrez_id
        row._self_joint_rank = rank
    return rows


def prioritize_genes(entrez_ids, hpo_terms, prio_algorithm):
    """Perform gene prioritization query.

    Yield quadruples (gene id, gene symbol, score, priority type) for the given gene list and query settings.
    """
    # TODO: properly test
    if not settings.VARFISH_ENABLE_EXOMISER_PRIORITISER or not entrez_ids or not hpo_terms:
        return

    try:
        algo_params = {
            "hiphive": ("hiphive", ["human", "mouse", "fish", "ppi"]),
            "hiphive-human": ("hiphive", ["human"]),
            "hiphive-mouse": ("hiphive", ["human", "mouse"]),
        }
        prio_algorithm, prio_params = algo_params.get(prio_algorithm, (prio_algorithm, []))
        res = requests.post(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            json={
                "phenotypes": sorted(set(hpo_terms)),
                "genes": sorted(set(entrez_ids)),
                "prioritiser": prio_algorithm,
                "prioritiser-params": ",".join(prio_params),
            },
        )
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, strip_tags(re.sub("<head>.*</head>", "", res.text))
                )
            )
    except requests.ConnectionError:
        raise ConnectionError(
            "ERROR: Server {} not responding.".format(settings.VARFISH_EXOMISER_PRIORITISER_API_URL)
        )

    for entry in res.json().get("results", ()):
        yield entry["geneId"], entry["geneSymbol"], entry["score"], entry["priorityType"]


class VariantScoresFactory:
    """Factory class for variant scorers."""

    def get_scorer(self, genomebuild, score_type, variants, user=None):
        if score_type == "umd":
            return VariantScoresUmd(genomebuild, variants, score_type, user)
        elif score_type == "cadd":
            return VariantScoresCadd(genomebuild, variants, score_type)
        elif score_type == "mutationtaster":
            return VariantScoresMutationTaster(genomebuild, variants, score_type)


class VariantScoresBase:
    """Variant scoring base class."""

    #: Set PathogenicityCache model (required in child classes)
    cache_model = None

    def __init__(self, genomebuild, variants, score_type, user=None):
        self.genomebuild = genomebuild
        self.variants = list(set(variants))
        self.user = user
        self.score_type = score_type

    def score(self):
        raise NotImplementedError("Implement me!")

    def get_cache_model(self):
        if not self.cache_model:
            raise NotImplementedError("Please set ``cache_model``")
        return self.cache_model

    def _get_cached_and_uncached_variants(self):
        cached = []
        uncached = []
        for variant in self.variants:
            res = self.get_cache_model().objects.filter(
                chromosome=variant[0],
                start=variant[1],
                reference=variant[2],
                alternative=variant[3],
            )
            if res:
                cached.append(res.first())
            else:
                uncached.append(variant)
        return cached, uncached

    def _cache_results(self, results):
        self.get_cache_model().objects.bulk_create(results)

    def _build_yield_dict(self, record, score, info):
        yield_dict = {
            k: record[k]
            for k in ("release", "chromosome", "start", "end", "bin", "reference", "alternative")
        }
        yield_dict["score"] = score
        yield_dict["info"] = info
        yield_dict["score_type"] = self.score_type
        return yield_dict


class VariantScoresUmd(VariantScoresBase):
    """Variant scoring class for UMD Predictor."""

    #: Set PathogenicityCache model (required)
    cache_model = UmdPathogenicityScoreCache

    def score(self):
        if not self.variants or not self.user:
            return

        token = app_settings.get_app_setting("variants", "umd_predictor_api_token", user=self.user)

        if not token:
            return

        cached, uncached = self._get_cached_and_uncached_variants()

        try:
            res = requests.get(
                settings.VARFISH_UMD_REST_API_URL,
                params=dict(
                    batch=",".join(["_".join(map(str, var)) for var in uncached]), token=token
                ),
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(settings.VARFISH_UMD_REST_API_URL)
            )

        # Exit if error is reported
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )

        # UMD API results do not contain header, so manually assign header information from their web page legend.
        header = [
            "chromosome",
            "position",
            "gene_name",
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "transcript_position",
            "reference",
            "alternative",
            "aa_wildtype",
            "aa_mutant",
            "pathogenicity_score",
            "conclusion",
        ]
        # Yield cached results
        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(item, item["pathogenicity_score"], {})
        # Yield API results
        result = []
        for line in res.text.split("\n"):
            if not line:
                continue
            if not line.startswith("chr"):
                continue
            record = dict(zip(header, line.split("\t")))
            record["release"] = "GRCh37"
            record["chromosome"] = record["chromosome"][3:]
            record["start"] = int(record.pop("position"))
            record["end"] = record["start"] + len(record["reference"]) - 1
            record["bin"] = binning.assign_bin(record["start"] - 1, record["end"])
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(record, record["pathogenicity_score"], {})
        # Store API results in cache
        self._cache_results(result)


class VariantScoresMutationTaster(VariantScoresBase):
    """Variant scoring class for Mutation Taster."""

    #: Set PathogenicityCache model (required)
    cache_model = MutationTasterPathogenicityScoreCache

    def score(self):
        if not self.variants:
            return

        cached, uncached = self._get_cached_and_uncached_variants()

        if len(uncached) > settings.VARFISH_MUTATIONTASTER_MAX_VARS:
            raise ConnectionError(
                "ERROR: Too many variants to score. Got {}, limit is {}.".format(
                    len(uncached), settings.VARFISH_MUTATIONTASTER_MAX_VARS
                )
            )

        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(
                item,
                _variant_scores_mutationtaster_score(item),
                _variant_scores_mutationtaster_info(item),
            )

        for i in range(len(uncached)):
            if i % settings.VARFISH_MUTATIONTASTER_BATCH_VARS == 0:
                yield from self._variant_scores_mutationtaster_loop(
                    uncached[i : i + settings.VARFISH_MUTATIONTASTER_BATCH_VARS]
                )

    def _variant_scores_mutationtaster_loop(self, batch):
        batch_str = ",".join("{}:{}{}>{}".format(*var) for var in batch)
        try:
            res = requests.post(
                settings.VARFISH_MUTATIONTASTER_REST_API_URL,
                dict(format="tsv", debug="0", variants=batch_str),
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(
                    settings.VARFISH_MUTATIONTASTER_REST_API_URL
                )
            )

        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )

        error_response = "Content-Type: text/plain\n\nERROR: "
        if res.text.startswith(error_response):
            raise ConnectionError(
                "ERROR: Server responded with: {}".format(res.text[len(error_response) :])
            )

        result = []
        lines = res.text.split("\n")
        if not lines or len(lines) < 2:
            return
        head = lines.pop(0).lower().split("\t")
        for line in lines:
            if not line:
                continue
            line = line.split("\t")
            record = dict(zip(head, line))
            # Remove id column as it would collide with the postgres id column. It's not required anyway.
            record.pop("id")
            # Convert chromosome identifiers
            record["chromosome"] = record.pop("chr")
            if record["chromosome"] == "23":
                record["chromosome"] = "X"
            elif record["chromosome"] == "24":
                record["chromosome"] = "Y"
            elif record["chromosome"] == "0":
                record["chromosome"] = "MT"
            # Re-label columns and convert data types to match postgres columns.
            record["release"] = "GRCh37"
            record["start"] = int(record.pop("pos"))
            record["end"] = record["start"] + len(record["ref"]) - 1
            record["bin"] = binning.assign_bin(record["start"] - 1, record["end"])
            record["reference"] = record.pop("ref")
            record["alternative"] = record.pop("alt")
            # This looks a bit complicated but is required as int() can't be casted on an empty string.
            record["bayes_prob_dc"] = (
                int(record["bayes_prob_dc"]) if record["bayes_prob_dc"] else None
            )
            record["distance_from_splicesite"] = (
                int(record["distance_from_splicesite"])
                if record["distance_from_splicesite"]
                else None
            )
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(
                record,
                _variant_scores_mutationtaster_score(record),
                _variant_scores_mutationtaster_info(record),
            )
        result_ = [(r.chromosome, r.start, r.reference, r.alternative) for r in result]
        # Create empty record for variants that weren't scored by mutationtaster
        # (and thus do not show up in the results and would be queried all over again)
        for variant in batch:
            if variant not in result_:
                chromosome, start, reference, alternative = variant
                record = {
                    "release": "GRCh37",
                    "chromosome": chromosome,
                    "start": start,
                    "end": start + len(reference) - 1,
                    "bin": binning.assign_bin(start - 1, start + len(reference) - 1),
                    "reference": reference,
                    "alternative": alternative,
                    "transcript_stable": None,
                    "ncbi_geneid": None,
                    "prediction": None,
                    "model": None,
                    "bayes_prob_dc": None,
                    "note": "error",
                    "splicesite": None,
                    "distance_from_splicesite": None,
                    "disease_mutation": None,
                    "polymorphism": None,
                }
                result.append(self.get_cache_model()(**record))
                yield self._build_yield_dict(
                    record,
                    _variant_scores_mutationtaster_score(record),
                    _variant_scores_mutationtaster_info(record),
                )

        # Store API results in cache
        self._cache_results(result)


def _variant_scores_mutationtaster_score(record):
    if record.get("note") == "error":
        return -1
    model_rank = _variant_scores_mutationtaster_rank_model(record)
    return model_rank + int(record.get("bayes_prob_dc")) / 10000


def _variant_scores_mutationtaster_info(record):
    return {
        "model": record["model"],
        "prediction": record["prediction"],
        "splicesite": record["splicesite"],
        "bayes_prob_dc": record["bayes_prob_dc"],
        "note": record["note"],
    }


def _variant_scores_mutationtaster_rank_model(record):
    model_rank = 0
    if record.get("prediction") == "disease causing (automatic)":
        model_rank = 4
    elif record.get("prediction") in ("disease causing", "disease causing - long InDel"):
        if record.get("model") in ("simple_aae", "complex_aae"):
            model_rank = 3
        elif record.get("model") == "without_aae":
            if record.get("splicesite") in ("splice site", "splicing impaired"):
                model_rank = 2
            else:
                model_rank = 1
    return model_rank


class VariantScoresCadd(VariantScoresBase):
    """Variant scoring class for CADD."""

    #: Set PathogenicityCache model (required)
    cache_model = CaddPathogenicityScoreCache

    def score(self):
        if not settings.VARFISH_ENABLE_CADD or not self.variants:
            return

        cached, uncached = self._get_cached_and_uncached_variants()
        uncached = uncached[: settings.VARFISH_CADD_MAX_VARS]

        # TODO: properly test
        cadd_release = "%s-%s" % (self.genomebuild, settings.VARFISH_CADD_REST_API_CADD_VERSION)
        try:
            res = requests.post(
                settings.VARFISH_CADD_REST_API_URL + "/annotate/",
                json={
                    "genome_build": self.genomebuild,
                    "cadd_release": cadd_release,
                    "variant": ["-".join(map(str, var)) for var in uncached],
                },
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(settings.VARFISH_CADD_REST_API_URL)
            )

        # Exit if error is reported
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )
        bgjob_uuid = res.json().get("uuid")
        while True:
            try:
                res = requests.post(
                    settings.VARFISH_CADD_REST_API_URL + "/result/", json={"bgjob_uuid": bgjob_uuid}
                )
            except requests.ConnectionError:
                raise ConnectionError(
                    "ERROR: Server {} not responding.".format(settings.VARFISH_CADD_REST_API_URL)
                )

            if not res.status_code == 200:
                raise ConnectionError(
                    "ERROR: Server responded with status {} and message {}".format(
                        res.status_code, res.text
                    )
                )
            if res.json().get("status") == "active":
                time.sleep(2)
            elif res.json().get("status") == "failed":
                raise ConnectionError(
                    "Job failed, leaving the following message: {}".format(res.json().get("result"))
                )
            else:  # status == finished
                break

        # Yield cached results
        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(item, item["scores"][1], {})

        result = []
        for var, scores in res.json().get("scores", {}).items():
            chrom, pos, ref, alt = var.split("-")
            start = int(pos)
            end = start + len(ref) - 1
            record = {
                "release": "GRCh37",
                "chromosome": chrom,
                "start": start,
                "end": end,
                "bin": binning.assign_bin(start - 1, end),
                "reference": ref,
                "alternative": alt,
                "info": res.json().get("info"),
                "scores": scores,
            }
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(record, record["scores"][1], {})
        self._cache_results(result)


# TODO: Improve wrapper
class RowWithClinvarMax(wrapt.ObjectProxy):
    """Wrap a result row and add members for clinvar max status and max significance."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_max_clinvar_status = None
        self._self_max_significance = None
        self._self_max_all_traits = None

    @property
    def max_clinvar_status(self):
        return self._self_max_clinvar_status

    @property
    def max_significance(self):
        return self._self_max_significance

    @property
    def max_all_traits(self):
        return self._self_max_all_traits

    def __getitem__(self, key):
        if key == "max_clinvar_status":
            return self.max_clinvar_status
        elif key == "max_significance":
            return self.max_significance
        elif key == "max_all_traits":
            return self.max_all_traits
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithAffectedCasesPerGene(wrapt.ObjectProxy):
    """Wrap a result row and add number of families per gene."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_affected_cases_per_gene = None

    @property
    def affected_cases_per_gene(self):
        return self._self_affected_cases_per_gene

    def __getitem__(self, key):
        if key == "affected_cases_per_gene":
            return self.affected_cases_per_gene
        else:
            return self.__wrapped__.__getitem__(key)


class AcmgCriteriaRating(models.Model):
    """Store criteria rating given by the ACMG guidelines.

    "Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the
    American College of Medical Genetics and Genomics and Association for Molecular Pathology (2015)."

    Choices are coded as follows:

    - -1 = [reserved for auto-selected as being the case]
    - 0 = user did not tick checkbox
    - 1 = [reserved for auto-selected as not being the case]
    - 2 = user tick checkbox
    """

    #: User who created the rating
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="acmg_ratings",
        help_text="User creating the original rating",
    )

    #: The related case.
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        null=False,
        related_name="acmg_ratings",
        help_text="Case that this rating was given for",
    )

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    pvs1 = models.IntegerField(
        default=0,
        verbose_name="PVS1",
        help_text=(
            "null variant (nonsense, frameshift, canonical ±1 or 2 splice sites, initiation codon, single or "
            "multiexon deletion) in a gene where LOF is a known mechanism of disease",
        ),
    )

    ps1 = models.IntegerField(
        default=0,
        verbose_name="PS1",
        help_text=(
            "Same amino acid change as a previously established pathogenic variant regardless of nucleotide change"
        ),
    )
    ps2 = models.IntegerField(
        default=0,
        verbose_name="PS2",
        help_text=(
            "De novo (both maternity and paternity confirmed) in a patient with the disease and no family history"
        ),
    )
    ps3 = models.IntegerField(
        default=0,
        verbose_name="PS3",
        help_text=(
            "Well-established in vitro or in vivo functional studies supportive of a damaging effect on the gene or "
            "gene product"
        ),
    )
    ps4 = models.IntegerField(
        default=0,
        verbose_name="PS4",
        help_text=(
            "The prevalence of the variant in affected individuals is significantly increased compared with the "
            "prevalence in controls"
        ),
    )

    pm1 = models.IntegerField(
        default=0,
        verbose_name="PM1",
        help_text=(
            "Located in a mutational hot spot and/or critical and well-established functional domain (e.g., active "
            "site of an enzyme) without benign variation"
        ),
    )
    pm2 = models.IntegerField(
        default=0,
        verbose_name="PM2",
        help_text=(
            "Absent from controls (or at extremely low frequency if recessive) in Exome Sequencing Project, 1000 "
            "Genomes Project, or Exome Aggregation Consortium"
        ),
    )
    pm3 = models.IntegerField(
        default=0,
        verbose_name="PM3",
        help_text="For recessive disorders, detected in trans with a pathogenic variant",
    )
    pm4 = models.IntegerField(
        default=0,
        verbose_name="PM4",
        help_text=(
            "Protein length changes as a result of in-frame deletions/insertions in a nonrepeat region or stop-loss "
            "variants"
        ),
    )
    pm5 = models.IntegerField(
        default=0,
        verbose_name="PM5",
        help_text=(
            "Novel missense change at an amino acid residue where a different missense change determined to be "
            "pathogenic has been seen before"
        ),
    )
    pm6 = models.IntegerField(
        default=0,
        verbose_name="PM6",
        help_text="Assumed de novo, but without confirmation of paternity and maternity",
    )

    pp1 = models.IntegerField(
        default=0,
        verbose_name="PP1",
        help_text=(
            "Cosegregation with disease in multiple affected family members in a gene definitively known to cause "
            "the disease"
        ),
    )
    pp2 = models.IntegerField(
        default=0,
        verbose_name="PP2",
        help_text=(
            "Missense variant in a gene that has a low rate of benign missense variation and in which missense "
            "variants are: a common mechanism of disease"
        ),
    )
    pp3 = models.IntegerField(
        default=0,
        verbose_name="PP3",
        help_text=(
            "Multiple lines of computational evidence support a deleterious effect on the gene or gene product "
            "(conservation, evolutionary, splicing impact, etc.)"
        ),
    )
    pp4 = models.IntegerField(
        default=0,
        verbose_name="PP4",
        help_text=(
            "Patient's phenotype or family history is highly specific for a disease with a single genetic etiology"
        ),
    )
    pp5 = models.IntegerField(
        default=0,
        verbose_name="PP5",
        help_text=(
            "Reputable source recently reports variant as pathogenic, but the evidence is not available to the "
            "laboratory to perform an independent evaluation"
        ),
    )

    ba1 = models.IntegerField(
        default=0,
        verbose_name="BA1",
        help_text=(
            "Allele frequency is >5% in Exome Sequencing Project, 1000 Genomes Project, or Exome Aggregation "
            "Consortium"
        ),
    )

    bs1 = models.IntegerField(
        default=0,
        verbose_name="BS1",
        help_text="Allele frequency is greater than expected for disorder (see Table 6)",
    )
    bs2 = models.IntegerField(
        default=0,
        verbose_name="BS2",
        help_text=(
            "Observed in a healthy adult individual for a recessive (homozygous), dominant (heterozygous), or "
            "X-linked (hemizygous) disorder, with full penetrance expected at an early age"
        ),
    )
    bs3 = models.IntegerField(
        default=0,
        verbose_name="BS3",
        help_text=(
            "Well-established in vitro or in vivo functional studies show no damaging effect on protein function "
            "or splicing"
        ),
    )
    bs4 = models.IntegerField(
        default=0,
        verbose_name="BS4",
        help_text="BS4: Lack of segregation in affected members of a family",
    )

    bp1 = models.IntegerField(
        default=0,
        verbose_name="BP1",
        help_text="Missense variant in a gene for which primarily truncating variants are known to cause disease",
    )
    bp2 = models.IntegerField(
        default=0,
        verbose_name="BP2",
        help_text=(
            "Observed in trans with a pathogenic variant for a fully penetrant dominant gene/disorder or observed in "
            "cis with a pathogenic variant in any inheritance pattern"
        ),
    )
    bp3 = models.IntegerField(
        default=0,
        verbose_name="BP3",
        help_text="In-frame deletions/insertions in a repetitive region without a known function",
    )
    bp4 = models.IntegerField(
        default=0,
        verbose_name="BP4",
        help_text=(
            "Multiple lines of computational evidence suggest no impact on gene or gene product (conservation, "
            "evolutionary, splicing impact, etc.)"
        ),
    )
    bp5 = models.IntegerField(
        default=0,
        verbose_name="BP5",
        help_text="Variant found in a case with an alternate molecular basis for disease",
    )
    bp6 = models.IntegerField(
        default=0,
        verbose_name="BP6",
        help_text=(
            "Reputable source recently reports variant as benign, but the evidence is not available to the "
            "laboratory to perform an independent evaluation"
        ),
    )
    bp7 = models.IntegerField(
        default=0,
        verbose_name="BP7",
        help_text=(
            "A synonymous (silent) variant for which splicing prediction algorithms predict no impact to the splice "
            "consensus sequence nor the creation of a new splice site AND the nucleotide is not highly conserved"
        ),
    )

    class_auto = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="ACMG Classification",
        help_text="Result of the ACMG classification",
    )

    class_override = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name="Class Override",
        help_text="Use this field to override the auto-computed class assignment",
    )

    @property
    def acmg_class(self):
        return self.class_override or self.class_auto

    get_gene_symbols = SmallVariantComment.get_gene_symbols

    def save(self, *args, **kwargs):
        self.bin = binning.assign_bin(self.start, self.end - 1)
        return super().save(*args, **kwargs)

    def get_variant_description(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )

    def get_human_readable(self):
        """Return human-readable ACMG rating values."""

        def yesno(key):
            if getattr(self, key) and getattr(self, key) > 0:
                return "Y"
            else:
                return "N"

        keys = (
            "pvs1",
            "ps1",
            "ps2",
            "ps3",
            "ps4",
            "pm1",
            "pm2",
            "pm3",
            "pm4",
            "pm5",
            "pm6",
            "pp1",
            "pp2",
            "pp3",
            "pp4",
            "pp5",
            "ba1",
            "bs1",
            "bs2",
            "bs3",
            "bs4",
            "bp1",
            "bp2",
            "bp3",
            "bp4",
            "bp5",
            "bp6",
            "bp7",
        )
        result = ", ".join(["%s: %s" % (key.upper(), yesno(key)) for key in keys])
        result += ", ACMG classification: %s" % self.class_auto
        if self.class_override:
            result += ", ACMG class. override: %s" % self.class_override
        return result


class SyncCaseListBgJob(JobModelMessageMixin, models.Model):
    """Background job for syncing project with remote site."""

    #: Task description for logging.
    task_desc = "Synchronise project cases with upstream"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.sync_project_upstream"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")

    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is to be synced"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    def get_human_readable_type(self):
        return "Synchronise with upstream SODAR"

    def get_absolute_url(self):
        return reverse(
            "variants:sync-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class SyncCaseResultMessage(models.Model):
    """A part of the case list synchronisation."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the message.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Message UUID")
    #: The project that the message belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project for the message"
    )

    #: The entry's log level.
    level = models.CharField(
        max_length=50, choices=LOG_LEVEL_CHOICES, help_text="Level of log entry"
    )

    #: The message contained by the log entry.
    message = models.TextField(help_text="Log level's message")


class ImportVariantsBgJob(JobModelMessageMixin, models.Model):
    """Background job for importing variants."""

    #: Task description for logging.
    task_desc = "Import variants"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.import"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")
    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is imported to"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    #: The case name.
    case_name = models.CharField(max_length=128, blank=False, null=False, help_text="The case name")
    #: The index name.
    index_name = models.CharField(
        max_length=128, blank=False, null=False, help_text="The index name"
    )
    #: The path to the PED file.
    path_ped = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to PED file"
    )
    #: The path to the variant genotype calls TSV.
    path_genotypes = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to variants TSV file"
        )
    )
    #: The path to the db-info TSV file.
    path_db_info = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to db-info TSV file"
        )
    )
    #: The path to the bam-qc TSV file.
    path_bam_qc = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to bam-qc TSV file"
        ),
        default=list,
    )

    def get_human_readable_type(self):
        return "Import (small) variants into VarFish"

    def get_absolute_url(self):
        return reverse(
            "variants:import-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )

    def get_case(self):
        latest_case = self.project.case_set.filter(name=self.case_name).order_by("-date_created")
        if latest_case:
            return latest_case[0]
        return None


class KioskAnnotateBgJob(JobModelMessageMixin, models.Model):
    """Background job for annotating vcf in kiosk mode."""

    #: Task description for logging.
    task_desc = "Kiosk annotate"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.kiosk"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")
    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project that is imported to"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        on_delete=models.CASCADE,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
    )

    #: Path to the temporary vcf file.
    path_vcf = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to the vcf file to annotate"
    )
    #: Path to the db info file.
    path_db_info = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Output path to the db info file"
    )
    #: Path to the gts variant file.
    path_gts = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Output path to the gts file"
    )
    #: Path to the tmp dir everything is stored.
    path_tmp_dir = models.CharField(
        max_length=4096, blank=False, null=False, help_text="Path to the tmp dir"
    )

    def get_human_readable_type(self):
        return "Annotate small variants in kiosk mode"

    def get_absolute_url(self):
        return reverse(
            "variants:kiosk-annotate-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class DeleteCaseBgJob(JobModelMessageMixin, models.Model):
    """Background job for deleting cases."""

    #: Task description for logging.
    task_desc = "Delete case"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.delete_case"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")

    #: The project that the job belongs to.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this object belongs"
    )

    #: Case that will be deleted
    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to delete"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    def get_human_readable_type(self):
        return "Delete case"

    def get_absolute_url(self):
        return reverse(
            "variants:case-delete-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class VariantImporterBase:
    """Base class for variant importer helper classes."""

    variant_set_attribute = None
    table_names = None
    latest_set = None
    #: Fill this with ``field_name: default_tsv_value`` in your sub class to ensure the fields are present.
    default_values = {}
    release_info = None

    def __init__(self, import_job):
        self.import_job = import_job

    def run(self):
        """Perform the variant import."""
        pedigree = list(self._yield_pedigree())
        # Create new case or get existing one.
        with transaction.atomic():
            case, case_created = Case.objects.get_or_create(
                name=self.import_job.case_name,
                project=self.import_job.project,
                defaults={"index": self.import_job.index_name, "pedigree": pedigree,},
            )
            # Create new variant set for case.
            variant_set = getattr(case, self.variant_set_attribute).create(state="importing")
        try:
            self._perform_import(variant_set)
        except Exception as e:
            self.import_job.add_log_entry("Problem during variant import: %s" % e, LOG_LEVEL_ERROR)
            self.import_job.add_log_entry("Rolling back variant set...")
            self._purge_variant_set(variant_set)
            raise RuntimeError("Problem during variant import ") from e
        with transaction.atomic():
            variant_set.state = "active"
            variant_set.save()
            if not case_created:  # Case needs to be updated.
                case.index = self.import_job.index_name
                case.pedigree = pedigree
            setattr(case, self.latest_set, variant_set)
            case.save()
            update_variant_counts(variant_set.case)
            self._post_import(variant_set)
        if variant_set.state == "active":
            self._clear_old_variant_sets(case, variant_set)
        else:
            self.import_job.add_log_entry("Problem during variant import", LOG_LEVEL_ERROR)
            self.import_job.add_log_entry("Rolling back variant set...")
            self._purge_variant_set(variant_set)
            raise RuntimeError("Problem during variant import")

    def _perform_import(self, variant_set):
        raise NotImplementedError("Override me!")

    def _post_import(self, variant_set):
        raise NotImplementedError("Override me!")

    def _purge_variant_set(self, variant_set):
        variant_set.__class__.objects.filter(pk=variant_set.id).update(state="deleting")
        for table_name, variant_set_attr in self.table_names:
            table = get_meta().tables[table_name]
            get_engine().execute(
                table.delete().where(
                    and_(
                        getattr(table.c, variant_set_attr) == variant_set.id,
                        table.c.case_id == variant_set.case.id,
                    )
                )
            )
        variant_set.__class__.objects.filter(pk=variant_set.id).delete()

    def _yield_pedigree(self):
        samples_in_genotypes = self._get_samples_in_genotypes()
        seen_index = False
        with open(self.import_job.path_ped, "rt") as pedf:
            for line in pedf:
                line = line.strip()
                _, patient, father, mother, sex, affected = line.split("\t")
                seen_index = seen_index or patient == self.import_job.index_name
                sex = int(sex)
                affected = int(affected)
                yield {
                    "patient": patient,
                    "father": father,
                    "mother": mother,
                    "sex": sex,
                    "affected": affected,
                    "has_gt_entries": patient in samples_in_genotypes,
                }
        if not seen_index:
            raise RuntimeError("Index {} not seen in pedigree!".format(self.import_job.index_name))

    def _get_samples_in_genotypes(self):
        """Return names from samples present in genotypes column."""
        with open_file(self.import_job.path_genotypes[0], "rt") as tsv:
            header = tsv.readline()[:-1].split("\t")
            first = tsv.readline()[:-1].replace('"""', '"').split("\t")
            values = dict(zip(header, first))
            return list(json.loads(values["genotype"]).keys())

    def _clear_old_variant_sets(self, case, keep_variant_set):
        self.import_job.add_log_entry("Starting to purge old variants")
        before = timezone.now()
        for variant_set in keep_variant_set.__class__.objects.filter(
            case=case, state="active", date_created__lt=keep_variant_set.date_created
        ):
            if variant_set.id != keep_variant_set.id:
                self._purge_variant_set(variant_set)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished purging old variants in %.2f s" % elapsed.total_seconds()
        )

    def _import_table(self, variant_set, token, path_attr, model_class):
        before = timezone.now()
        self.import_job.add_log_entry("Creating temporary %s file..." % token)
        with tempfile.NamedTemporaryFile("w+t") as tempf:
            for i, path_genotypes in enumerate(getattr(self.import_job, path_attr)):
                with open_file(path_genotypes, "rt") as inputf:
                    header = inputf.readline().strip()
                    header_arr = header.split("\t")
                    try:
                        case_idx = header_arr.index("case_id")
                        set_idx = header_arr.index("set_id")
                    except ValueError as e:
                        raise RuntimeError(
                            "Column 'case_id' or 'set_id' not found in %s TSV" % token
                        ) from e
                    # Extend header for fields in self.default_values and build suffix to append to every line.
                    default_suffix = []
                    for field, value in self.default_values.items():
                        if field not in header_arr:
                            header += "\t%s" % field
                            default_suffix.append(str(value))
                    if i == 0:
                        tempf.write(header)
                        tempf.write("\n")
                    while True:
                        line = inputf.readline().strip()
                        if not line:
                            break
                        arr = line.split("\t")
                        arr[case_idx] = str(variant_set.case.pk)
                        arr[set_idx] = str(variant_set.pk)
                        tempf.write("\t".join(arr + default_suffix))
                        tempf.write("\n")
            tempf.flush()
            elapsed = timezone.now() - before
            self.import_job.add_log_entry("Wrote file in %.2f s" % elapsed.total_seconds())

            before = timezone.now()
            self.import_job.add_log_entry("Importing %s file..." % token)
            model_class.objects.from_csv(
                tempf.name,
                delimiter="\t",
                null=".",
                ignore_conflicts=True,
                drop_constraints=False,
                drop_indexes=False,
            )
            elapsed = timezone.now() - before
            self.import_job.add_log_entry(
                "Finished importing %s in %.2f s" % (token, elapsed.total_seconds())
            )

    def _import_annotation_release_info(self, variant_set):
        before = timezone.now()
        self.import_job.add_log_entry("Importing annotation release info...")
        for path_db_info in self.import_job.path_db_info:
            for entry in tsv_reader(path_db_info):
                self._get_release_info().objects.get_or_create(
                    genomebuild=entry["genomebuild"],
                    table=entry["db_name"],
                    case=variant_set.case,
                    variant_set=variant_set,
                    defaults={"release": entry["release"]},
                )
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing annotation release info in %.2f s" % elapsed.total_seconds()
        )

    def _get_release_info(self):
        if not self.release_info:
            raise NotImplementedError("Please set release_info!")
        return self.release_info


class VariantImporter(VariantImporterBase):
    """Helper class for importing variants."""

    variant_set_attribute = "smallvariantset_set"
    table_names = (
        ("variants_smallvariant", "set_id"),
        ("variants_casealignmentstats", "variant_set_id"),
    )
    latest_set = "latest_variant_set"
    # Ensure that the info and {refseq,ensembl}_exon_dist fields are present with default values.  This snippet
    # can go away once we are certain all TSV files have been created with varfish-annotator >=0.10
    default_values = {"info": "{}", "refseq_exon_dist": ".", "ensembl_exon_dist": "."}
    release_info = AnnotationReleaseInfo

    def _perform_import(self, variant_set):
        self._import_annotation_release_info(variant_set)
        self._import_alignment_stats(variant_set)
        self._import_table(variant_set, "genotypes", "path_genotypes", SmallVariant)

    def _post_import(self, variant_set):
        self._rebuild_small_variants_stats(variant_set)

    def _rebuild_small_variants_stats(self, variant_set):
        """Rebuild small variant statistics."""
        # This must be imported here to circumvent cyclic dependencies
        from .variant_stats import rebuild_case_variant_stats  # noqa

        before = timezone.now()
        self.import_job.add_log_entry("Computing variant statistics...")
        rebuild_case_variant_stats(get_engine(), variant_set, logger=self.import_job.add_log_entry)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished computing variant statistics in %.2f s" % elapsed.total_seconds()
        )

    def _import_alignment_stats(self, variant_set):
        before = timezone.now()
        self.import_job.add_log_entry("Importing alignment statistics...")
        for path_bam_qc in self.import_job.path_bam_qc:
            self.import_job.add_log_entry("... importing from %s" % path_bam_qc)
            # Enumerate is bad because empty iterator and iterator with one element result in the same count
            lineno = 0
            for entry in tsv_reader(path_bam_qc):
                case_stats, created = CaseAlignmentStats.objects.get_or_create(
                    variant_set=variant_set,
                    defaults={
                        "case": variant_set.case,
                        "bam_stats": json.loads(entry["bam_stats"].replace('"""', '"')),
                    },
                )
                if created:
                    self.import_job.add_log_entry(
                        "created entry for case '%s' with id %d and variant set id %d"
                        % (variant_set.case.name, variant_set.case.id, variant_set.id)
                    )
                else:  # needs update
                    case_stats.bam_stats = json.loads(entry["bam_stats"].replace('"""', '"'))
                    case_stats.case = variant_set.case
                    case_stats.save()
                    self.import_job.add_log_entry(
                        "updated entry (found stats entry for variant set id %d)" % variant_set.id
                    )
                lineno += 1
            self.import_job.add_log_entry("imported %d entries" % lineno)
        elapsed = timezone.now() - before
        self.import_job.add_log_entry(
            "Finished importing alignment statistics in %.2f s" % elapsed.total_seconds()
        )


def run_import_variants_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    import_job = ImportVariantsBgJob.objects.get(pk=pk)
    started = timezone.now()
    with import_job.marks():
        VariantImporter(import_job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=import_job.project,
                app_name="variants",
                user=import_job.bg_job.user,
                event_name="case_import",
                description='Import of small variants for case "%s" finished in %.2fs.'
                % (import_job.case_name, elapsed.total_seconds()),
                status_type="OK",
            )


class KioskAnnotate:
    def __init__(self, job):
        self.job = job

    def run(self):
        """Perform the variant annotation."""
        try:
            process = subprocess.Popen(
                """
                {set_x}
                . {conda_path}
                conda activate varfish-annotator
                set -euo pipefail
                vcf=$(dirname {input_vcf})/sorted-$(basename {input_vcf})
                vcf=${{vcf%.gz}}
                vcf=${{vcf%.vcf}}
                vcf=$vcf.vcf.gz
                bcftools sort -m 10M -Oz -o $vcf {input_vcf}
                tabix -f $vcf
                varfish-annotator \
                    -XX:MaxHeapSize=10g \
                    -XX:+UseConcMarkSweepGC \
                    annotate \
                    --db-path {db_path} \
                    --ensembl-ser-path {ensembl_ser_path} \
                    --refseq-ser-path {refseq_ser_path} \
                    --input-vcf $vcf \
                    --output-db-info >(gzip > {output_db_info}) \
                    --output-gts >(awk -F$'\t' 'BEGIN{{OFS=FS}}{{if(NR>1){{sub(/^chrM/,"MT",$2);sub(/^chr/,"",$2)}}print}}' | gzip > {output_gts}) \
                    --ref-path {reference_path} \
                    --release {release}
                """.format(
                    set_x="set -x" if settings.DEBUG else "",
                    conda_path=settings.KIOSK_CONDA_PATH,
                    db_path=settings.KIOSK_VARFISH_ANNOTATOR_DB_PATH,
                    ensembl_ser_path=settings.KIOSK_VARFISH_ANNOTATOR_ENSEMBL_SER_PATH,
                    refseq_ser_path=settings.KIOSK_VARFISH_ANNOTATOR_REFSEQ_SER_PATH,
                    input_vcf=shlex.quote(self.job.path_vcf),
                    output_db_info=shlex.quote(self.job.path_db_info),
                    output_gts=shlex.quote(self.job.path_gts),
                    reference_path=settings.KIOSK_VARFISH_ANNOTATOR_REFERENCE_PATH,
                    release=settings.KIOSK_VARFISH_ANNOTATOR_RELEASE,
                ),
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                shell=True,
                executable="/bin/bash",
            )
            # Get live output from bash job
            while True:
                line = process.stdout.readline()
                if line is not None:
                    self.job.add_log_entry(line.decode("utf-8").strip(), LOG_LEVEL_INFO)
                if process.poll() is not None:
                    while True:
                        line = process.stdout.readline()
                        if line:
                            self.job.add_log_entry(line.decode("utf-8").strip(), LOG_LEVEL_INFO)
                        else:
                            break
                    if not process.poll() == 0:
                        raise subprocess.CalledProcessError(process.poll(), "annotation")
                    break
        except subprocess.CalledProcessError as e:
            self.job.add_log_entry("Problem during kiosk annotation: %s" % e, LOG_LEVEL_ERROR)
            raise e

    def clear(self):
        shutil.rmtree(self.job.path_tmp_dir, ignore_errors=True)
        self.job.add_log_entry("Removing directory %s" % self.job.path_tmp_dir, LOG_LEVEL_INFO)


def run_kiosk_annotate_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    job = KioskAnnotateBgJob.objects.get(pk=pk)
    started = timezone.now()
    with job.marks():
        KioskAnnotate(job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=job.project,
                app_name="variants",
                user=job.bg_job.user,
                event_name="kiosk_annotate",
                description='Annotation of VCF file "%s" finished in %.2fs.'
                % (os.path.basename(job.path_vcf), elapsed.total_seconds()),
                status_type="OK",
            )


class DeleteCase:
    def __init__(self, job):
        self.job = job

    def run(self):
        from variants.queries import DeleteSmallVariantsQuery, DeleteStructuralVariantsQuery  # noqa

        case = self.job.case
        try:
            self.job.add_log_entry(
                "Deleting small and structural variants of case %s" % case.name, LOG_LEVEL_INFO
            )
            for query in itertools.chain(
                DeleteSmallVariantsQuery(get_engine()).run(case_id=case.id),
                DeleteStructuralVariantsQuery(get_engine()).run(case_id=case.id),
            ):
                with contextlib.closing(query):
                    pass
            self.job.add_log_entry("Deleting case %s" % case.name, LOG_LEVEL_INFO)
            case.delete()
        except Exception as e:
            self.job.add_log_entry("Problem during case deletion: %s" % e, LOG_LEVEL_ERROR)
            raise RuntimeError("Problem during case deletion") from e


def run_delete_case_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    job = DeleteCaseBgJob.objects.get(pk=pk)
    started = timezone.now()
    with job.marks():
        DeleteCase(job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=job.project,
                app_name="variants",
                user=job.bg_job.user,
                event_name="delete_case",
                description='Deletion of case "%s" finished in %.2fs.'
                % (job.case.name, elapsed.total_seconds()),
                status_type="OK",
            )


def run_clear_kiosk_bg_job(pk):
    job = KioskAnnotateBgJob.objects.get(pk=pk)
    KioskAnnotate(job).clear()


def clear_old_kiosk_cases():
    """Clear out cases that are older than a week."""

    # Do nothing if kiosk mode isn't enabled.
    if not settings.KIOSK_MODE:
        return

    # Find the correct category
    cat = Project.objects.get(type="CATEGORY", title=settings.KIOSK_CAT)
    # Define allowed period (~2 months)
    time_threshold = timezone.now() - timedelta(weeks=8)
    # Find the correct project within the category and within cases that are older than threshold
    cases = Case.objects.filter(
        project__type="PROJECT", project__parent_id=cat.id, date_created__lte=time_threshold
    )
    projects = []
    # Delete cases and associated variants
    for case in cases:
        projects.append(case.project)
        # Delete all small variants.
        with contextlib.closing(
            get_engine().execute(
                delete(SmallVariant.sa.table).where(SmallVariant.sa.case_id == case.id)
            )
        ):
            pass
        # Delete case
        case.delete()
    # Delete projects as every case has its own project and is not required anymore
    for project in set(projects):
        project.delete()


def update_variant_counts(case, kind=None, logger=lambda _: None):
    """Update the variant counts for the given case.

    This is done without changing the ``date_modified`` field.
    """
    from svs import models as sv_models  # noqa
    from importer.models import CaseVariantType  # noqa

    if not kind or kind == CaseVariantType.SMALL.name:
        logger("Updating variant counts for small variants ...")
        variant_set = case.latest_variant_set
        if variant_set:
            set_id = variant_set.pk
            logger("... found variant set with id %d" % set_id)
            stmt = (
                select([func.count()])
                .select_from(SmallVariant.sa.table)
                .where(and_(SmallVariant.sa.set_id == set_id, SmallVariant.sa.case_id == case.pk))
            )
            num_small_vars = get_engine().scalar(stmt)
            logger("... variant set has %d variants" % num_small_vars)
        else:
            logger("... no variant set found")
            num_small_vars = None
        case.num_small_vars = num_small_vars
        case.save()

    if not kind or kind == CaseVariantType.STRUCTURAL.name:
        logger("Updating variant counts for structural variants ...")
        structural_variant_set = case.latest_structural_variant_set
        if structural_variant_set:
            set_id = structural_variant_set.pk
            logger("... found variant set with id %d" % set_id)
            stmt = (
                select([func.count()])
                .select_from(sv_models.StructuralVariant.sa.table)
                .where(
                    and_(
                        sv_models.StructuralVariant.sa.set_id == set_id,
                        sv_models.StructuralVariant.sa.case_id == case.pk,
                    )
                )
            )
            num_svs = get_engine().scalar(stmt)
            logger("... variant set has %d variants" % num_svs)
        else:
            logger("... no variant set found")
            num_svs = None
        case.num_svs = num_svs
        case.save()

    logger("... num_small_vars is now %s" % case.num_small_vars)
    logger("... num_svs is now %s" % case.num_svs)


class SiteBgJobBase(JobModelMessageMixin, models.Model):
    """Base class for global (site-wide) background jobs of the Variants module."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="%(app_label)s_%(class)s_related",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )

    def get_human_readable_type(self):
        return "Site-wide Maintenance"

    class Meta:
        ordering = ("-date_created",)
        abstract = True


class ClearExpiredExportedFilesBgJob(SiteBgJobBase):
    """Background job for clearing expired exported files."""

    #: Task description for logging.
    task_desc = "Clearing expired exported files"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_expired_exported_files_bg_job"

    def get_absolute_url(self):
        return reverse("variants:clear-expired-job-detail", kwargs={"job": self.sodar_uuid},)


class ClearInactiveVariantSetsBgJob(SiteBgJobBase):
    """Background job for clearing inactive variant sets."""

    #: Task description for logging.
    task_desc = "Clearing inactive variant sets"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_inactive_variant_sets_bg_job"

    def get_absolute_url(self):
        return reverse("variants:clear-inactive-variant-set-job", kwargs={"job": self.sodar_uuid},)


class ClearOldKioskCasesBgJob(SiteBgJobBase):
    """Background job for clearing old Kiosk cases."""

    #: Task description for logging.
    task_desc = "Clearing old (and expired) Varfish Kiosk cases"

    #: String identifying model in BackgroundJob.
    spec_name = "variants.clear_old_kiosk_cases_bg_job"

    def get_absolute_url(self):
        return reverse(
            "variants:clear-old-kiosk-cases-job-detail", kwargs={"job": self.sodar_uuid},
        )


class RefreshSmallVariantSummaryBgJob(SiteBgJobBase):
    """Background job for refreshing small variant summaries."""

    #: Task description for logging.
    task_desc = 'Refreshing small variant summaries (aka "in-house database")'

    #: String identifying model in BackgroundJob.
    spec_name = "variants.refresh_small_variant_summaries"

    def get_absolute_url(self):
        return reverse(
            "variants:refresh-small-variant-summaries-job-detail", kwargs={"job": self.sodar_uuid},
        )
