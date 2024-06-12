"""Models and supporting code for importing structural variants"""

import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from projectroles.models import Project
from projectroles.plugins import get_backend_api

from svs.models.records import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    StructuralVariantSet,
)
from variants.models import Case, VariantImporterBase


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


class SvAnnotationReleaseInfo(models.Model):
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
    case = models.ForeignKey(Case, on_delete=models.CASCADE)
    #: Link to variant set
    variant_set = models.ForeignKey(StructuralVariantSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("genomebuild", "table", "variant_set")


class VariantImporter(VariantImporterBase):
    """Helper class for importing structural variants"""

    variant_set_attribute = "structuralvariantset_set"
    table_names = (
        ("svs_structuralvariant", "set_id"),
        ("svs_structuralvariantgeneannotation", "set_id"),
    )
    latest_set = "latest_structural_variant_set"
    release_info = SvAnnotationReleaseInfo

    def _perform_import(self, variant_set):
        self._import_annotation_release_info(variant_set)
        self._import_table(variant_set, "SVs", "path_genotypes", StructuralVariant)
        self._import_table(
            variant_set,
            "SV-gene annotation",
            "path_feature_effects",
            StructuralVariantGeneAnnotation,
        )

    def _post_import(self, variant_set):
        pass


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
