import uuid as uuid_object

from django.db import models
from django.conf import settings
from django.urls import reverse
from projectroles.models import Project

#: Django user model.
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class ReportTemplate(models.Model):
    """A report template."""

    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: UUID used for identification throughout SODAR.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Case SODAR UUID"
    )

    #: The project containing this case.
    project = models.ForeignKey(Project, help_text="Project in which this objects belongs")

    #: Title of the report.
    title = models.CharField(max_length=512)
    #: File name of the report.
    filename = models.CharField(max_length=512)

    #: File size in bytes.
    filesize = models.IntegerField(default=0)
    #: File hash.
    filehash = models.CharField(max_length=128)

    class Meta:
        unique_together = (("project", "filename"),)
        ordering = ("title",)

    def get_absolute_url(self):
        return reverse(
            "reports:template-view",
            kwargs={"project": self.project.sodar_uuid, "template": self.sodar_uuid},
        )
