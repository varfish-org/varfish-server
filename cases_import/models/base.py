import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.db import models
from django.urls import reverse
from projectroles.models import Project

from cases_import.proto import get_case_name_from_family_payload
from varfish.utils import JSONField


class CaseImportAction(models.Model):
    """Stores the necessary information for importing a case."""

    ACTION_CREATE = "create"
    ACTION_UPDATE = "update"
    ACTION_DELETE = "delete"

    ACTION_CHOICES = (
        (ACTION_CREATE, ACTION_CREATE),
        (ACTION_UPDATE, ACTION_UPDATE),
        (ACTION_DELETE, ACTION_DELETE),
    )

    STATE_DRAFT = "draft"
    STATE_SUBMITTED = "submitted"
    STATE_RUNNING = "running"
    STATE_FAILED = "failed"
    STATE_SUCCESS = "success"

    STATE_CHOICES = (
        (STATE_DRAFT, STATE_DRAFT),
        (STATE_SUBMITTED, STATE_SUBMITTED),
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FAILED, STATE_FAILED),
        (STATE_SUCCESS, STATE_SUCCESS),
    )

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The project that the import is related to.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    #: The action to perform.
    action = models.CharField(
        max_length=32, null=False, blank=False, choices=ACTION_CHOICES, default=ACTION_CREATE
    )
    #: The import action's current state.
    state = models.CharField(
        max_length=32, null=False, blank=False, choices=STATE_CHOICES, default=STATE_DRAFT
    )
    #: The JSON serialization of the phenopacket that is to be used in the action.
    payload = JSONField()

    #: Whether or not to overwrite changes in the disease and phenotype terms.
    #:
    #: These are commonly curated by users so we do not want to override them with potentially
    #: empty or wrong lists.
    overwrite_terms = models.BooleanField(default=False)

    def get_case_name(self):
        """Return case name from ``self.payload`` as family ID."""
        return get_case_name_from_family_payload(self.payload)

    class Meta:
        #: Order by date of last modification (most recent first).
        ordering = ("-date_modified",)


class CaseImportBackgroundJobManager(models.Manager):
    """Custom manager class that allows to create a ``CaseImportBackgroundJob``
    together with the backing ``BackgroundJob``.
    """

    def create_full(self, *, caseimportaction, project, user):
        case_name = caseimportaction.get_case_name()
        bg_job = BackgroundJob.objects.create(
            name=f"Import of case '{case_name}'",
            project=project,
            job_type=CaseImportBackgroundJob.spec_name,
            user=user,
        )
        instance = super().create(project=project, bg_job=bg_job, caseimportaction=caseimportaction)
        return instance


class CaseImportBackgroundJob(JobModelMessageMixin, models.Model):
    """Background job for importing cases with the ``cases_import`` app."""

    # We use a custom manager that provides creation together with the ``BackgroundJob``.
    objects = CaseImportBackgroundJobManager()

    #: Task description for logging.
    task_desc = "Case Import"

    #: String identifying model in BackgroundJob.
    spec_name = "cases_import.importcasebgjob"

    #: The SODAR UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4,
        unique=True,
    )
    #: The project that this background job belong to.
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    #: The background job for state management etc.
    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        related_name="caseimportbackgroundjob",
        help_text="Background job for state etc.",
        on_delete=models.CASCADE,
    )
    #: The case import action to perform.
    caseimportaction = models.ForeignKey(CaseImportAction, on_delete=models.CASCADE, null=False)

    def get_human_readable_type(self):
        return "Import a case into VarFish"

    def get_absolute_url(self):
        return reverse(
            "cases_import:ui-caseimportbackgroundjob-detail",
            kwargs={"caseimportbackgroundjob": self.sodar_uuid},
        )
