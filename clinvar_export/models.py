"""Models for the ``clinvar_export`` app.

The design is such that the individuals and families (aka cases) in ``clinvar_export`` **can** be linked to the
records in ``variants``.
"""

import logging
import uuid as uuid_object

from django.contrib.postgres.fields import ArrayField
from django.db import models, transaction
from django.conf import settings
from projectroles.models import Project

from varfish.utils import JSONField
from variants.models import CaseAwareProject, Case

logger = logging.getLogger(__name__)

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

#: Map pedigree value for "sex" to value for models.
SEX_MAP = {
    0: "unknown",
    1: "male",
    2: "female",
}

#: Map pedigree value for "affected" to value for models.
AFFECTED_MAP = {
    0: "unknown",
    1: "no",
    2: "yes",
}


class FamilyManager(models.Manager):
    """Custom ``Manager`` that allows to easily get or create a ``Family`` from a project with a given name."""

    def get_or_create_in_project(self, project, case=None, case_name=None):
        """Get or create a ``Family`` for the given ``Case`` in the given ``Project`` or by name of the ``Case``.

        The creation is done in a transaction so no conflict should occur.  Raises a ``Case.DoesNotExist`` if
        there is no such corresponding case by this name (if ``case_name`` is given).
        """
        if (not case) == (not case_name):
            raise ValueError("You have to specify exactly one of case and case_name.")
        with transaction.atomic():
            case = case or project.case_set.get(name=case_name)  # Case.DoesNotExist not caught
            family, _ = Family.objects.get_or_create(
                project=project,
                case_name=case.name,
                defaults={"case": case, "case_name": case.name, "pedigree": case.pedigree},
            )
            return family


class Family(models.Model):
    """Stub to link case in VarFish to family in ClinVar."""

    objects = FamilyManager()

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: ClinvarFamily UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The project that this family is to be stored in.
    project = models.ForeignKey(CaseAwareProject, on_delete=models.CASCADE)

    #: Foreign key to the ``Case``.  This is nullable and we will not delete the ``ClinvarFamily`` even if the
    #: case is being deleted.
    case = models.ForeignKey(Case, null=True, blank=True, on_delete=models.SET_NULL)
    #: The name of the ``Case`` for the case where it is deleted.
    case_name = models.TextField(max_length=128)
    #: Pedigree information.
    pedigree = JSONField(null=True, blank=True, default=list, help_text="Pedigree information.")

    class Meta:
        unique_together = (("case_name", "project"),)
        ordering = ("date_created",)


class IndividualManager(models.Manager):
    """Provides helper methods to safely create ``Individual`` objects for entries corresponding to ``Case.pedigree`."""

    def get_or_create_in_project(
        self, project, name, family=None, case=None, case_name=None, **kwargs
    ):
        """Create new ``Individual`` with the given ``name`` in the case specified by ``case`` or ``case_name``; the
        corresponding ``family`` can also be specified directly.

        If no corresponding case by case_name can be found then ``Case.DoesNotExist`` will be raised.
        """
        if sum(map(lambda x: int(not not x), (family, case, case_name))) != 1:  # pragma: no cover
            raise ValueError("Exactly one of family, case, case_name must be set.")
        with transaction.atomic():
            family = family or Family.objects.get_or_create_in_project(
                project, case=case, case_name=case_name
            )
            indiv, _ = Individual.objects.get_or_create(family=family, name=name, defaults=kwargs)
            return indiv


class Individual(models.Model):
    """Stub to link individual in Varfish to individual in ClinVar."""

    objects = IndividualManager()

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The family that this individual belongs to.
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    #: Name of the individual in the Case.
    name = models.TextField(max_length=128)

    #: The NCBI taxonomy ID of the sample, 9606 is homo sapiens.
    taxonomy_id = models.IntegerField(default=9606)
    #: The sex of the sample.  One of [unknown, male, female].
    sex = models.TextField(max_length=100, blank=False, null=False, default="unknown")
    #: Whether or not the individual is affected.
    affected = models.TextField(max_length=100, blank=False, null=False, default="unknown")

    def get_project(self):
        return self.family.project

    class Meta:
        ordering = ("date_created",)


def create_families_and_individuals(project: Project) -> None:
    """Create missing families and individuals for the given ``project``."""
    with transaction.atomic():
        for case in Case.objects.filter(project=project):
            family = Family.objects.get_or_create_in_project(project, case=case)
            for entry in case.pedigree:
                Individual.objects.get_or_create_in_project(
                    project,
                    entry["patient"],
                    family=family,
                    sex=SEX_MAP.get(entry.get("sex", 0), "unknown"),
                    affected=AFFECTED_MAP.get(entry.get("affected", 0), "unknown"),
                )


class SubmissionIndividual(models.Model):
    """Participation of an individual in a submission."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: Sort order within the SubmissionSet.
    sort_order = models.IntegerField()

    #: Foreign key to the individual that was submitted.
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE)
    #: Foreign key to the submission that this individidual was included in.
    submission = models.ForeignKey(
        "Submission", on_delete=models.CASCADE, related_name="submission_individuals"
    )
    #: As list of object with keys "term_id", and "term_name", e.g.,
    #: ``[{"term_id": "HP:1234567", "term_name": "Something"}]``
    phenotypes = JSONField(blank=True, null=True, default=list)

    #: The origin of the variant.  one of [germline, somatic, de novo, unknown, not provided, inherited, maternal,
    #: paternal, uniparental, biparental, not-reported, tested-inconclusive, not applicable, experimentally
    #: generated].
    variant_origin = models.TextField(
        max_length=100, blank=False, null=False, default="not-reported"
    )
    #: The variant allele count.
    variant_allele_count = models.IntegerField(blank=True, null=True, default=None)
    #: The variant zygosity, one of [Homozygote, Single heterozygote, Compound heterozygote, Hemizygote, not provide].
    variant_zygosity = models.TextField(
        max_length=100, blank=True, null=True, default="not provided"
    )
    #: The method the individual was recruited from, one of [curation, literature only, provider interpretation,
    #: phenotyping only, case-control, clinical testing, in vitro, in vivo, research, not provided].
    source = models.TextField(max_length=100, blank=False, null=False)
    #: List of citations, e.g. ``["PMID:12345"]]``.
    citations = ArrayField(models.TextField(max_length=100), blank=True, null=True, default=list)
    #: The tissue type of the sample.
    tissue = models.TextField(max_length=100, blank=True, null=True)

    def get_project(self):
        return self.individual.get_project()

    class Meta:
        ordering = ("sort_order",)
        unique_together = (("individual", "submission"),)


class AssertionMethod(models.Model):
    """An assertion method."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: Whether or not the assertion method is builtin and cannot be modified by the user.
    is_builtin = models.BooleanField(default=False)
    #: Title of the assertion method.
    title = models.TextField(max_length=200)
    #: The reference of the assertion number, can be a ``PMID:12345`` or a URL.
    reference = models.TextField(max_length=200)

    class Meta:
        ordering = ("reference",)


class Submitter(models.Model):
    """Description of a submitting user.

    These must be created through the web interface anyway, so we only store a stub.
    """

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The submitter ID as stored in ClinVar.
    clinvar_id = models.IntegerField()
    #: A descriptive name, not exported as meta data is updated through ClinVar web UI.
    name = models.TextField()

    class Meta:
        ordering = ("name",)


class Organisation(models.Model):
    """Description of a submitting organisation.

    These must be created through the web interface anyway, so we only store a stub.
    """

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Cohort UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The organisation ID as stored in ClinVar.
    clinvar_id = models.IntegerField()
    #: A descriptive name, not exported as meta data is updated through ClinVar web UI.
    name = models.TextField()

    class Meta:
        ordering = ("clinvar_id",)


class SubmissionSet(models.Model):
    """Model for a Clinvar submission set."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Submission set UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")
    #: The project that this family is to be stored in.
    project = models.ForeignKey(CaseAwareProject, on_delete=models.CASCADE)

    #: The submitter
    submitter = models.ForeignKey(
        Submitter, related_name="submission_sets", null=True, on_delete=models.CASCADE
    )
    #: Submitting organisations.
    organisations = models.ManyToManyField(Organisation, through="SubmittingOrg")

    #: State of the submission as tracked in VarFish.  One of [pending, submitted, released, rejected].
    state = models.TextField(max_length=32)
    #: title of the submission set.
    title = models.TextField()

    class Meta:
        ordering = ("date_created",)


class SubmittingOrg(models.Model):
    """Information on a submitting organisation."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Sort order within the SubmissionSet.
    sort_order = models.IntegerField()

    #: Submitting organisation UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")
    #: The submitting organisation.
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    #: The submission set that this organisation belongs to.
    submission_set = models.ForeignKey(
        SubmissionSet, on_delete=models.CASCADE, related_name="submitting_orgs"
    )

    class Meta:
        ordering = ("sort_order",)
        unique_together = (("organisation", "submission_set"),)


class Submission(models.Model):
    """Model for a clinvar variant submission (for one variant, maybe multiple individuals)."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Submission UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="SODAR UUID")

    #: The submission set.
    submission_set = models.ForeignKey(
        SubmissionSet, related_name="submissions", on_delete=models.CASCADE
    )

    #: Sort order within the SubmissionSet.
    sort_order = models.IntegerField()

    #: Status of the record, one of [novel, update, delete]
    record_status = models.TextField(max_length=32, default="novel")
    #: Release status of the record, one of [public, hold until published].
    release_status = models.TextField(max_length=32, default="public")

    #: Significance status of the record, e.g. "criteria provided, single submitter"
    significance_status = models.TextField(max_length=100)
    #: Description fo the significance.
    significance_description = models.TextField(max_length=100)
    #: Last evaluation of significance.
    significance_last_evaluation = models.DateField()

    #: The used assertion method.
    assertion_method = models.ForeignKey(AssertionMethod, on_delete=models.CASCADE,)
    #: Mode of Inheritance
    inheritance = models.TextField(max_length=100, blank=True, null=True)
    #: Age of onset
    age_of_onset = models.TextField(max_length=100, blank=True, null=True)

    #: The individual that this variant was observed in.
    individuals = models.ManyToManyField(Individual, through=SubmissionIndividual)

    #: The variant assembly.
    variant_assembly = models.TextField(max_length=64)
    #: The variant chromosome.
    variant_chromosome = models.TextField(max_length=64)
    #: The variant type.
    variant_type = models.TextField(max_length=100, blank=False, null=False, default="Variation")
    #: The 1-based variant start coordinate.
    variant_start = models.IntegerField(blank=True, null=True)
    #: The 1-based variant stop coordinate.
    variant_stop = models.IntegerField(blank=True, null=True)
    #: The reference variant allele.
    variant_reference = models.TextField(blank=True, null=True)
    #: The alternative variant allele.
    variant_alternative = models.TextField(blank=True, null=True)
    #: The affected genes with their preferred name.
    variant_gene = ArrayField(models.TextField(max_length=64))
    #: The HGV annotation of the variant for each gene (for display only, not submitted to ClinVAr).
    variant_hgvs = ArrayField(models.TextField())

    #: Disease information.
    diseases = JSONField(blank=True, null=True, default=list)

    def get_project(self):
        return self.submission_set.project

    class Meta:
        ordering = ("sort_order",)


def refresh_individual_sex_affected():
    """Update the ``Individual.sex`` field from the upstream case.

    This is done regularly in a related task.
    """
    for family in Family.objects.select_related("case").prefetch_related("individual_set").all():
        if family.case:
            ped_entries = {entry["patient"]: entry for entry in family.case.pedigree}
            for individual in family.individual_set.all():
                if individual.name not in ped_entries:
                    logger.info(f"{individual.name} not in pedigree for case {family.case}")
                else:
                    related_ped_entry = ped_entries[individual.name]
                    individual.sex = SEX_MAP.get(related_ped_entry["sex"], "unknown")
                    individual.affected = AFFECTED_MAP.get(related_ped_entry["affected"], "unknown")
                    individual.save()
