"""Models and model helper code provided by the ``bgjobs`` app.

The central class is ``BackgroundJob`` that stores the core information about a background job.  You can "subclass"
this class by creating your own models in your apps and having a ``bg_job`` field referencing ``BackgroundJob``
through a ``OneToOneField``.

Further, the ``BackgroundJobLogEntry`` model allows to manage background log entries for your background jobs.  Use
the ``JobModelMessageMixin`` for adding helper functions for applying state changes and adding log messages.
"""

import uuid as uuid_object

from django.conf import settings
from django.db import models

from projectroles.models import Project


#: Access Django user model
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


# Levels to use in ``BackgroundJobLogEntry``.

#: Debug log message.
LOG_LEVEL_DEBUG = "debug"
#: Info log message.
LOG_LEVEL_INFO = "info"
#: Warning log message.
LOG_LEVEL_WARNING = "warning"
#: Error log message.
LOG_LEVEL_ERROR = "error"

#: Choices to use in ``CharField`` for log level.
LOG_LEVEL_CHOICES = (
    (LOG_LEVEL_DEBUG, "debug"),
    (LOG_LEVEL_INFO, "info"),
    (LOG_LEVEL_WARNING, "warning"),
    (LOG_LEVEL_ERROR, "error"),
)


# The possible states of ``BackgroundJob`` objects and their labels.

#: Job has been created but not started.
JOB_STATE_INITIAL = "initial"
#: Job is running.
JOB_STATE_RUNNING = "running"
#: Job succeeded.
JOB_STATE_DONE = "done"
#: Job failed.
JOB_STATE_FAILED = "failed"

#: Choices to use in the ``CharField``.
JOB_STATE_CHOICES = (
    (JOB_STATE_INITIAL, "initial"),
    ("running", "running"),
    ("done", "done"),
    ("failed", "failed"),
)


class BackgroundJob(models.Model):
    """Common background job information."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: The UUID for this job.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="BG Job SODAR UUID"
    )
    #: The project that this job belongs to.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")
    #: The user initiating the job.
    user = models.ForeignKey(AUTH_USER_MODEL, null=False, related_name="background_jobs")

    #: Specializing string of the job.
    job_type = models.CharField(max_length=512, null=False, help_text="Type of the job")

    #: A human-readable name for this job.
    name = models.CharField(max_length=512)
    #: An optional, extend description for this job.
    description = models.TextField()
    #: The job status.
    status = models.CharField(max_length=50, choices=JOB_STATE_CHOICES, default=JOB_STATE_INITIAL)

    def get_human_readable_type(self):
        """Also implement in your sub classes to show human-readable type in the views."""
        return "(generic job)"

    def add_log_entry(self, message, level=LOG_LEVEL_INFO):
        """Add and return a new ``BackgroundJobLogEntry``."""
        return self.log_entries.create(level=level, message=message)

    def __str__(self):
        return self.name


class BackgroundJobLogEntry(models.Model):
    """Log entry for background job"""

    #: Creation time of log entry.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")

    #: The ``BackgroundJob`` that the log entry is for.
    job = models.ForeignKey(
        BackgroundJob, related_name="log_entries", help_text="Owning background job"
    )

    #: The entry's log level.
    level = models.CharField(
        max_length=50, choices=LOG_LEVEL_CHOICES, help_text="Level of log entry"
    )
    #: The message contained by the log entry.
    message = models.TextField(help_text="Log level's message")

    class Meta:
        ordering = ["date_created"]


class JobModelMessageMixin:
    """Mixin with shortcuts for marking job state and adding log entry.

    Use this in your ``BackgroundJob`` "subclasses" (sub classing meaning ``OneToOneField`` specializations).
    """

    task_desc = None

    def mark_start(self):
        """Mark the export job as started."""
        self.bg_job.status = JOB_STATE_RUNNING
        self.bg_job.add_log_entry("%s started" % self.task_desc)
        self.bg_job.save()

    def mark_error(self, msg):
        """Mark the export job as complete successfully."""
        self.bg_job.status = JOB_STATE_FAILED
        self.bg_job.add_log_entry("{} file failed: {}".format(self.task_desc, msg))
        self.bg_job.save()

    def mark_success(self):
        """Mark the export job as complete successfully."""
        self.bg_job.status = JOB_STATE_DONE
        self.bg_job.add_log_entry("%s succeeded" % self.task_desc)
        self.bg_job.save()

    def add_log_entry(self, *args, **kwargs):
        """Add a log entry through the related ``BackgroundJob``."""
        return self.bg_job.add_log_entry(*args, **kwargs)
