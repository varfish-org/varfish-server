"""Code for storing the small variants themselves"""

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from postgres_copy import CopyManager
from sqlalchemy import and_

from varfish.utils import JSONField
from variants.helpers import get_engine, get_meta


class SmallVariant(models.Model):
    """Information of a single variant, knows its case."""

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
    #: Miscellaneous information as JSONB.
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
    #: Total ExAC homozygous count
    exac_homozygous = models.IntegerField(null=True)
    #: Total ExAC heterozygous count
    exac_heterozygous = models.IntegerField(null=True)
    #: Total ExAC hemizygous count
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
        # IMPORTANT ---------------------------------------------------------
        #
        # The SmallVariant model has Meta.managed=False outside of testing!
        # The reason is that we use table partitioning here.  We maintain a
        # list of indices here for documentation purposes, but they are
        # actually created manually in the migrations.
        #
        # IMPORTANT ---------------------------------------------------------
        indexes = [
            # For query: select all variants for a case.
            models.Index(fields=["case_id"], name="variants_sm_case_id_6f9d8c_idx"),
            # For locating variants by coordiante.
            models.Index(
                fields=["case_id", "chromosome", "bin"], name="variants_sm_case_id_3efbb1_idx"
            ),
            # For locating variants directly.
            models.Index(
                fields=["case_id", "release", "chromosome", "start", "reference", "alternative"],
                name="variants_sm_case_id_coords",
            ),
            # Filter query: the most important thing is to reduce the variants for a case quickly. It's questionable
            # how much adding homozygous/frequency really adds here.  Adding them back should only be done when we
            # know that it helps.
            GinIndex(fields=["case_id", "refseq_effect"], name="variants_sm_case_id_a529e8_gin"),
            GinIndex(fields=["case_id", "ensembl_effect"], name="variants_sm_case_id_071d6b_gin"),
            models.Index(fields=["case_id", "in_clinvar"], name="variants_sm_case_id_423a80_idx"),
            # Fast allow-list queries of gene.
            models.Index(
                fields=["case_id", "ensembl_gene_id"], name="variants_sm_case_id_5d52f6_idx"
            ),
            models.Index(
                fields=["case_id", "refseq_gene_id"], name="variants_sm_case_id_1f4f31_idx"
            ),
            # For mitochondrial frequency join
            models.Index(fields=["case_id", "chromosome_no"], name="variants_sm_case_id_chr_no"),
            # For selecting all variants of a set of a case (used for gathering variant stats).
            models.Index(fields=["case_id", "set_id"], name="variants_sm_case_id_set_id"),
            # For selecting all variants within a bin quickly.
            models.Index(
                fields=["case_id", "release", "chromosome", "bin"],
                name="variants_sm_case_id_for_bin",
            ),
        ]
        managed = settings.IS_TESTING
        db_table = "variants_smallvariant"


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
        "Case", on_delete=models.CASCADE, null=False, help_text="The case that this set is for"
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
    """Model to track the database releases used during annotation of a case."""

    #: Release of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: Name of imported table
    table = models.CharField(max_length=512)
    #: Timestamp of import
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Link to case
    case = models.ForeignKey(
        "Case",
        on_delete=models.CASCADE,
    )
    #: Link to variant set
    variant_set = models.ForeignKey(
        SmallVariantSet,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ("genomebuild", "table", "variant_set")
