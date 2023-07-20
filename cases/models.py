import uuid as uuid_object

from django.db import models

from seqmeta.models import EnrichmentKit
from variants.models import Case


class Pedigree(models.Model):
    """A pedigree related to a case."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    #: The related case.
    case = models.OneToOneField(
        Case,
        on_delete=models.CASCADE,
        # TODO: remove related_name when the pedigree UUID is not used any more
        related_name="pedigree_obj",
    )


class Individual(models.Model):
    """An individual in a pedigree."""

    KARYOTYPE_UNKNOWN = "unknown"
    KARYOTYPE_XX = "XX"
    KARYOTYPE_XY = "XY"
    KARYOTYPE_XO = "XO"
    KARYOTYPE_XXY = "XXY"
    KARYOTYPE_XXX = "XXX"
    KARYOTYPE_XXYY = "XXYY"
    KARYOTYPE_XXXY = "XXXY"
    KARYOTYPE_XXXX = "XXXX"
    KARYOTYPE_XYY = "XYY"
    KARYOTYPE_OTHER = "other"

    KARYOTYPE_CHOICES = (
        (KARYOTYPE_UNKNOWN, KARYOTYPE_UNKNOWN),
        (KARYOTYPE_XX, KARYOTYPE_XX),
        (KARYOTYPE_XY, KARYOTYPE_XY),
        (KARYOTYPE_XO, KARYOTYPE_XO),
        (KARYOTYPE_XXY, KARYOTYPE_XXY),
        (KARYOTYPE_XXX, KARYOTYPE_XXX),
        (KARYOTYPE_XXYY, KARYOTYPE_XXYY),
        (KARYOTYPE_XXXY, KARYOTYPE_XXXY),
        (KARYOTYPE_XXXX, KARYOTYPE_XXXX),
        (KARYOTYPE_XYY, KARYOTYPE_XYY),
        (KARYOTYPE_OTHER, KARYOTYPE_OTHER),
    )

    SEX_UNKNOWN = "unknown"
    SEX_MALE = "male"
    SEX_FEMALE = "female"
    SEX_OTHER = "other"

    SEX_CHOICES = (
        (SEX_UNKNOWN, SEX_UNKNOWN),
        (SEX_MALE, SEX_MALE),
        (SEX_FEMALE, SEX_FEMALE),
        (SEX_OTHER, SEX_OTHER),
    )

    ASSAY_PANEL = "panel_seq"
    ASSAY_WES = "wes"
    ASSAY_WGS = "wgs"

    ASSAY_CHOICES = (
        (ASSAY_PANEL, ASSAY_PANEL),
        (ASSAY_WES, ASSAY_WES),
        (ASSAY_WGS, ASSAY_WGS),
    )

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    #: The related pedigree.
    pedigree = models.ForeignKey(Pedigree, on_delete=models.CASCADE)

    #: The name of the individual.
    name = models.CharField(max_length=128)
    #: The "sex assigned at birth" of the individual.
    sex = models.CharField(max_length=128, choices=SEX_CHOICES)
    #: The karyotypic sex.
    karyotypic_sex = models.CharField(max_length=128, choices=KARYOTYPE_CHOICES)

    #: The assay used or None for no assay.
    assay = models.CharField(max_length=128, choices=ASSAY_CHOICES, null=True, blank=True)
    #: When sequenced, the used enrichment kit to specify targets.
    enrichmentkit = models.ForeignKey(
        EnrichmentKit, on_delete=models.PROTECT, null=True, blank=True
    )


class TermCore(models.Model):
    """Abstract model used for terms associated with an ``Individual``."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    #: The related individual.
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE)

    #: The term ID.
    term_id = models.CharField(max_length=128, blank=False, null=False)
    #: The term label.
    term_label = models.CharField(max_length=128, blank=False, null=False)
    #: Whether the disease was excluded.
    excluded = models.BooleanField(default=False)

    class Meta:
        unique_together = (("individual", "term_id"),)
        abstract = True


class Disease(TermCore):
    """Disease associated with an ``Individual``."""


class PhenotypicFeature(TermCore):
    """Phenotypic feature associated with an ``Individual``."""
