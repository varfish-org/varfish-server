import uuid as uuid_object
from datetime import datetime, timedelta

import aldjemy
from bgjobs.models import BackgroundJob, JobModelMessageMixin
from postgres_copy import CopyManager

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils import timezone
from projectroles.models import Project
from projectroles.plugins import get_backend_api
from sqlalchemy import and_

from variants.models import Case, VARIANT_RATING_CHOICES, VariantImporterBase
from variants.helpers import SQLALCHEMY_ENGINE


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
    case = models.ForeignKey(Case, null=False, help_text="The case that this set is for")
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
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()

    #: The bin for indexing.
    bin = models.IntegerField()

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
    info = JSONField(default={}, help_text="Further information of the structural variant")
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
    refseq_transcript_coding = models.NullBooleanField()
    #: RefSeq variant effect list
    refseq_effect = ArrayField(models.CharField(max_length=64), null=True)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=32, null=True)
    #: Flag EnsEMBL transcript coding
    ensembl_transcript_coding = models.NullBooleanField()
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
    if sender == Case:
        # TODO: delete with SQL alchemy...
        uuids = [obj.sv_uuid for obj in StructuralVariant.objects.filter(case_id=instance.id)]
        for uuid in uuids:
            StructuralVariantGeneAnnotation.objects.filter(sv_uuid=uuid).delete()
        StructuralVariant.objects.filter(case_id=instance.id).delete()


class _UserAnnotation(models.Model):
    """Common attributes for structural variant comments and flags"""

    #: Annotation UUID
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Annotation UUID"
    )
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: The bin for indexing.
    bin = models.IntegerField()

    #: The genome release of the SV
    release = models.CharField(max_length=32)
    #: The chromosome of the SV
    chromosome = models.CharField(max_length=32)
    #: The start position of the SV
    start = models.IntegerField()
    #: The end position of the SV
    end = models.IntegerField()
    #: The SV type
    sv_type = models.CharField(max_length=32)
    #: The SV sub type
    sv_sub_type = models.CharField(max_length=32)

    def get_variant_description(self):
        return "({}) chr{}:{}-{}".format(self.sv_type, self.chromosome, self.start, self.end)

    class Meta:
        abstract = True
        indexes = (models.Index(fields=["case", "release", "bin"]),)


class StructuralVariantComment(_UserAnnotation):
    """Model for commenting on a ``StructuralVariant``."""

    #: User who created the comment.
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="structural_variant_comments",
        help_text="User who created the comment",
    )

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="structural_variant_comments",
        help_text="Case that this SV is commented on",
    )

    #: The comment text.
    text = models.TextField(help_text="The comment text", null=False, blank=False)

    def shortened_text(self, max_chars=50):
        """Shorten ``text`` to ``max_chars`` characters if longer."""
        if len(self.text) > max_chars:
            return self.text[:max_chars] + "..."
        else:
            return self.text

    def get_absolute_url(self):
        return self.case.get_absolute_url() + "#comment-%s" % self.sodar_uuid


class StructuralVariantFlags(_UserAnnotation):
    """Model for flagging structural variants.

    Structural variants are generally not as clear-cut as small variants because of ambiguities in their start
    and end points.  We can thus not prevent flagging a variant more than once ad we do not attempt to.
    """

    #: The related case.
    case = models.ForeignKey(
        Case,
        null=False,
        related_name="structural_variant_flags",
        help_text="Case that this SV is flagged in",
    )

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

    #: Molecular flag.
    flag_molecular = models.CharField(
        max_length=32, choices=VARIANT_RATING_CHOICES, default="empty", null=False
    )
    #: Visual inspection flag.
    flag_visual = models.CharField(
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
                self.flag_molecular != "empty",
                self.flag_visual != "empty",
                self.flag_validation != "empty",
                self.flag_phenotype_match != "empty",
                self.flag_summary != "empty",
            )
        )


class ImportStructuralVariantBgJob(JobModelMessageMixin, models.Model):
    """Background job for importing structural variants."""

    #: Task description for logging.
    task_desc = "Import variants"

    #: String identifying model in BackgroundJob.
    spec_name = "svs.import"

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: UUID of the job
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Job UUID")
    #: The project that the job belongs to.
    project = models.ForeignKey(Project, help_text="Project that is imported to")

    #: The background job that is specialized.
    bg_job = models.ForeignKey(
        BackgroundJob,
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
    #: The path to the variant feature effects TSV.
    path_feature_effects = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to feature_effects TSV file"
        )
    )
    #: The path to the db-info TSV file.
    path_db_info = ArrayField(
        models.CharField(
            max_length=4096, blank=False, null=False, help_text="Path to db-info TSV file"
        )
    )

    def get_human_readable_type(self):
        return "Import SVs into VarFish"

    def get_absolute_url(self):
        return reverse(
            "svs:import-job-detail",
            kwargs={"project": self.project.sodar_uuid, "job": self.sodar_uuid},
        )


class VariantImporter(VariantImporterBase):
    """Helper class for importing structural variants"""

    variant_set_attribute = "structuralvariantset_set"
    table_names = ("svs_structuralvariant", "svs_structuralvariantgeneannotation")

    def _perform_import(self, variant_set):
        self._import_table(variant_set, "SVs", "path_genotypes", StructuralVariant)
        self._import_table(
            variant_set,
            "SV-gene annotation",
            "path_feature_effects",
            StructuralVariantGeneAnnotation,
        )


def cleanup_variant_sets(min_age_hours=12):
    """Cleanup old variant sets."""
    variant_sets = list(
        StructuralVariantSet.objects.filter(
            state__ne="active", entered__gte=datetime.now() - timedelta(hours=min_age_hours)
        )
    )
    table_names = ("svs_structuralvariant", "svs_structuralvariantgeneannotation")
    for table_name in table_names:
        table = aldjemy.core.get_meta().tables[table_name]
        for variant_set in variant_sets:
            SQLALCHEMY_ENGINE.execute(
                table.delete().where(
                    and_(table.c.set_id == variant_set.id, table.c.case_id == variant_set.case.id)
                )
            )
    variant_set.delete()


def run_import_structural_variants_bg_job(pk):
    timeline = get_backend_api("timeline_backend")
    import_job = ImportStructuralVariantBgJob.objects.get(pk=pk)
    started = timezone.now()
    with import_job.marks():
        VariantImporter(import_job).run()
        if timeline:
            elapsed = timezone.now() - started
            timeline.add_event(
                project=import_job.project,
                app_name="svs",
                user=import_job.bg_job.user,
                event_name="case_import",
                description='Import of SVs for case case "%s" finished in %.2fs.'
                % (import_job.case_name, elapsed.total_seconds()),
                status_type="OK",
            )
