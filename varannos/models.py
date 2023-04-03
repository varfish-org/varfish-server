import uuid as uuid_object

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from projectroles.models import Project


class VarAnnoSet(models.Model):
    """Represent a set of variant annotations."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    #: The variant annotation set's project.
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    #: The variant annotation set's title.
    title = models.CharField(
        max_length=100, null=False, blank=False, help_text="The variant annotation set's title."
    )
    #: The description of the variant annotation set.
    description = models.TextField(
        null=True, blank=True, help_text="An optional description for the variant annotation set."
    )
    #: The genome build of the variant annotation set.
    release = models.CharField(
        max_length=16,
        null=False,
        blank=False,
        help_text="Genome build of the variant annotation set.",
        choices=(("GRCh37", "GRCh37"), ("GRCh38", "GRCh38")),
    )
    #: A list of allowed field names for the entries' payload.
    fields = ArrayField(
        models.CharField(max_length=64, null=False, blank=False),
        null=False,
        blank=False,
        help_text="The allowed fields in the entries.",
    )

    def get_absolute_url(self):
        """Return absolute URL for the detail view of this case."""
        return reverse(
            "varannos:varannoset-detail",
            kwargs={"varannoset": self.sodar_uuid},
        )

    def days_since_modification(self):
        return (timezone.now() - self.date_modified).days

    class Meta:
        ordering = ("title",)


class VarAnnoSetEntry(models.Model):
    """An entry in a ``VarAnnoSet``."""

    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Cohort SODAR UUID"
    )

    #: The variant anno set this entry belongs to.
    varannoset = models.ForeignKey(VarAnnoSet, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: The actual entry as a JSON dictionary.
    payload = models.JSONField(
        null=False,
        blank=False,
        help_text="The annotation's data with fields defined in the variant annotation set.",
    )

    def get_project(self):
        """Return varannoset's project."""
        return self.varannoset.project

    class Meta:
        ordering = ("release", "chromosome", "start", "reference", "alternative")

        # Manually define index on the chromosomal position to join with ``SmallVariant``.
        indexes = [
            models.Index(
                fields=["release", "chromosome", "start", "reference", "alternative"],
            ),
        ]
