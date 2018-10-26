import uuid as uuid_object

from django.db import models

from projectroles.models import Project


#: The possible states of background jobs and their labels.
JOB_STATE_INITIAL = "initial"
JOB_STATE_RUNNING = "running"
JOB_STATE_DONE = "done"
JOB_STATE_FAILED = "failed"
JOB_STATE_CHOICES = (
    (JOB_STATE_INITIAL, "initial"),
    ("running", "running"),
    ("done", "done"),
    ("failed", "failed"),
)


LOG_LEVEL_DEBUG = "debug"
LOG_LEVEL_INFO = "info"
LOG_LEVEL_WARNING = "warning"
LOG_LEVEL_ERROR = "error"
LOG_LEVEL_CHOICES = (
    (LOG_LEVEL_DEBUG, "debug"),
    (LOG_LEVEL_INFO, "info"),
    (LOG_LEVEL_WARNING, "warning"),
    (LOG_LEVEL_ERROR, "error"),
)


class BackgroundJob(models.Model):
    """Common background job information."""

    #: DateTime of creation
    # created_at = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="BG Job SODAR UUID"
    )
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")
    job_type = models.CharField(max_length=512, null=False, help_text="Type of the job")

    name = models.CharField(max_length=512)
    description = models.TextField()
    status = models.CharField(max_length=50, choices=JOB_STATE_CHOICES, default=JOB_STATE_INITIAL)

    def add_log_entry(self, message, level=LOG_LEVEL_INFO):
        """Add and return a new ``BackgroundJobLogEntry``."""
        return self.log_entries.create(level=level, message=message)

    def __str__(self):
        return self.name


class BackgroundJobLogEntry(models.Model):
    """Log entry for background job"""

    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    job = models.ForeignKey(
        BackgroundJob, related_name="log_entries", help_text="Owning background job"
    )

    level = models.CharField(
        max_length=50, choices=LOG_LEVEL_CHOICES, help_text="Level of log entry"
    )
    message = models.TextField(help_text="Log level's message")

    class Meta:
        ordering = ["date_created"]
