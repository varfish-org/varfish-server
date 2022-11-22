"""The structural variant records for the database."""

import uuid as uuid_object

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from postgres_copy import CopyManager

from varfish.utils import JSONField
from variants.models import Case

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

#: Structural variant type "deletion"
SV_TYPE_DEL = "DEL"
#: Structural variant type "duplication"
SV_TYPE_DUP = "DUP"
#: Structural variant type "insertion"
SV_TYPE_INS = "INS"
#: Structural variant type "inversion"
SV_TYPE_INV = "INV"
#: Structural variant type "breakend"
SV_TYPE_BND = "BND"
#: Structural variant type "copy number variation"
SV_TYPE_CNV = "CNV"

#: The choices for structural variant types.
SV_TYPE_CHOICES = (
    (SV_TYPE_DEL, "deletion"),
    (SV_TYPE_DUP, "duplication"),
    (SV_TYPE_INS, "insertion"),
    (SV_TYPE_INV, "inversion"),
    (SV_TYPE_BND, "breakend"),
    (SV_TYPE_CNV, "copy number variation"),
)

#: Generic deletion
SV_SUB_TYPE_DEL = "DEL"
#: Mobile element deletion
SV_SUB_TYPE_DEL_ME = "DEL:ME"
#: SVA mobile element deletion
SV_SUB_TYPE_DEL_ME_SVA = "DEL:ME:SVA"
#: LINE1 mobile element deletion
SV_SUB_TYPE_DEL_ME_L1 = "DEL:ME:L1"
#: ALU mobile element deletion
SV_SUB_TYPE_DEL_ME_ALU = "DEL:ME:ALU"
#: Generic duplication
SV_SUB_TYPE_DUP = "DUP"
#: Tandem duplication
SV_SUB_TYPE_DUP_TANDEM = "DUP:TANDEM"
#: Generic inversion
SV_SUB_TYPE_INV = "INV"
#: Generic insertion
SV_SUB_TYPE_INS = "INS"
#: mobile element insertion
SV_SUB_TYPE_INS_ME = "INS:ME"
#: SVA mobile element insertion
SV_SUB_TYPE_INS_ME_SVA = "INS:ME:SVA"
#: LINE1 mobile element insertion
SV_SUB_TYPE_INS_ME_L1 = "INS:ME:L1"
#: ALU mobile element insertion
SV_SUB_TYPE_INS_ME_ALU = "INS:ME:ALU"
#: Generic Breakend
SV_SUB_TYPE_BND = "BND"
#: Generic CNV
SV_SUB_TYPE_CNV = "CNV"

#: The choices for structural variant sub types.
SV_SUB_TYPE_CHOICES = (
    (SV_SUB_TYPE_DEL, "deletion"),
    (SV_SUB_TYPE_DEL_ME, "mobile element deletion"),
    (SV_SUB_TYPE_DEL_ME_SVA, "mobile element deletion (SVA)"),
    (SV_SUB_TYPE_DEL_ME_L1, "mobile element deletion (LINE1)"),
    (SV_SUB_TYPE_DEL_ME_ALU, "mobile element deletion (ALU)"),
    (SV_SUB_TYPE_DUP, "duplication"),
    (SV_SUB_TYPE_DUP_TANDEM, "tandem duplication"),
    (SV_SUB_TYPE_INV, "inversion"),
    (SV_SUB_TYPE_INS, "insertion"),
    (SV_SUB_TYPE_INS_ME, "mobile_element insertion"),
    (SV_SUB_TYPE_INS_ME_SVA, "mobile element deletion (SVA)"),
    (SV_SUB_TYPE_INS_ME_L1, "mobile element deletion (LINE1)"),
    (SV_SUB_TYPE_INS_ME_ALU, "mobile element deletion (ALU)"),
    (SV_SUB_TYPE_INV, "inversion"),
    (SV_SUB_TYPE_BND, "breakend"),
    (SV_SUB_TYPE_CNV, "copy number variation"),
)

#: The key to use for "background carriers".
INFO_KEY_BACKGROUND_CARRIERS = "BACKGROUND_CARRIERS"
#: The key to use for "affected carriers".
INFO_KEY_AFFECTED_CARRIERS = "AFFECTED_CARRIERS "
#: The key to use for "unaffected carriers".
INFO_KEY_UNAFFECTED_CARRIERS = "UNAFFECTED_CARRIERS"


class StructuralVariantSet(models.Model):
    """A set of structural variants associated with a case.

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


class StructuralVariant(models.Model):
    """Represent a structural variant call with its genomic coordinates, genotype calls in a ``Case``, and other
    properties.

    Note that at this level, only the variant and its genotypes in the individuals of the case is described.  The
    description of its impact on genome features is done in ``StructuralVariantFeatureAnnotation``.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: The bin for indexing in case of linear SVs, in case of non-linear SVs the bin of pos.
    bin = models.IntegerField()
    #: Variant coordinates - chromosome of end position (equal to ``chromosome`` for linear variants)
    chromosome2 = models.CharField(max_length=32, null=True)
    #: Chromosome as number - of end position (equal to ``chromosome_no`` for linear variants)
    chromosome_no2 = models.IntegerField(null=True)
    #: In case of non-linear variants, the bin of end, otherwise equal to ``bin``.
    bin2 = models.IntegerField(null=True)

    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Paired-end orientation of SV, one of "3to3", "3to5", "5to3", or "5to5", or None.
    pe_orientation = models.CharField(max_length=32, null=True, blank=True)

    #: Left boundary of CI of ``start``.
    start_ci_left = models.IntegerField()
    #: Right boundary of CI of ``start``.
    start_ci_right = models.IntegerField()
    #: Left boundary of CI of ``end``.
    end_ci_left = models.IntegerField()
    #: Right boundary of CI of ``end``.
    end_ci_right = models.IntegerField()

    #: Foreign key to case ID
    case_id = models.IntegerField()
    #: The StructuralVariantSet ID
    set_id = models.IntegerField()

    #: UUID used for identification.
    sv_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Structural variant UUID"
    )

    #: Identifier of the caller (includes version)
    caller = models.CharField(max_length=128)
    #: Type of structural variant
    sv_type = models.CharField(max_length=32, choices=SV_TYPE_CHOICES)
    #: Sub type of structural variant
    sv_sub_type = models.CharField(max_length=32, choices=SV_SUB_TYPE_CHOICES)

    #: Further description of mobile element as JSON
    #:
    #: - gt  -- genotype
    #: - gq  -- genotype quality
    #: - pec -- paired end coverage
    #: - pev -- paired end variant
    #: - src -- split read coverage
    #: - srv -- split read variants
    #: - ft  -- array of filter strings
    info = JSONField(default=dict, help_text="Further information of the structural variant")

    #: Number of homozygous alternative genotypes.
    num_hom_alt = models.IntegerField(null=True)
    #: Number of homozygous reference genotypes.
    num_hom_ref = models.IntegerField(null=True)
    #: Number of heterozygous genotypes.
    num_het = models.IntegerField(null=True)
    #: Number of hemizygous alternative genotypes
    num_hemi_alt = models.IntegerField(null=True)
    #: Number of hemizygous reference occurences.
    num_hemi_ref = models.IntegerField(null=True)

    #: Genotype calls and genotype-related information
    genotype = JSONField()

    #: Allow bulk import
    objects = CopyManager()

    def get_variant_description(self):
        return "({}) chr{}:{}-{}".format(self.sv_type, self.chromosome, self.start, self.end)

    class Meta:
        indexes = (
            models.Index(fields=["case_id"]),
            models.Index(fields=["set_id"]),
            models.Index(fields=["case_id", "release", "chromosome", "bin"]),
            models.Index(
                fields=["case_id", "release", "chromosome", "bin", "sv_type", "sv_sub_type"]
            ),
        )
        managed = settings.IS_TESTING
        db_table = "svs_structuralvariant"


class StructuralVariantGeneAnnotation(models.Model):
    """Annotation of a ``StructuralVariant`` and its impact on genes (such as the coding region).

    This model describes the impact of a structural variant on one gene.  The description of the structural variant
    itself is done in ``StructuralVariant``.
    """

    #: Foreign key to case ID
    case_id = models.IntegerField()
    #: The StructuralVariantSet ID
    set_id = models.IntegerField()

    #: Foreign key into ``StructuralVariant.sodar_uuid``.
    sv_uuid = models.UUIDField(
        default=uuid_object.uuid4, help_text="Structural variant UUID foreign key"
    )

    #: RefSeq gene ID
    refseq_gene_id = models.CharField(max_length=16, null=True)
    #: RefSeq transcript ID
    refseq_transcript_id = models.CharField(max_length=16, null=True)
    #: Flag RefSeq transcript coding
    refseq_transcript_coding = models.BooleanField(null=True)
    #: RefSeq variant effect list
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=32, null=True)
    #: Flag EnsEMBL transcript coding
    ensembl_transcript_coding = models.BooleanField(null=True)
    #: EnsEMBL variant effect list
    ensembl_effect = ArrayField(models.CharField(max_length=64, null=True))

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = (models.Index(fields=["sv_uuid"]), models.Index(fields=["set_id"]))
        managed = settings.IS_TESTING
        db_table = "svs_structuralvariantgeneannotation"


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
    _ = kwargs
    if sender == Case:
        # TODO: delete with SQL alchemy...
        uuids = [obj.sv_uuid for obj in StructuralVariant.objects.filter(case_id=instance.id)]
        for uuid in uuids:
            StructuralVariantGeneAnnotation.objects.filter(sv_uuid=uuid).delete()
        StructuralVariant.objects.filter(case_id=instance.id).delete()
