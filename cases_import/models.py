import uuid as uuid_object

from django.db import models
from projectroles.models import Project

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

    class Meta:
        #: Order by date of last modification (most recent first).
        ordering = ("-date_modified",)
