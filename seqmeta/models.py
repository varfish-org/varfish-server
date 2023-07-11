import uuid as uuid_object

from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse


class EnrichmentKit(models.Model):
    """A category of gene panels"""

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: Identifier of the enrichment kit.
    identifier = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text="Identifier of the enrichment kit, e.g., 'agilent-all-exon-v4'.",
        validators=[
            RegexValidator(
                regex=r"^[\w_-]+$",
                message="Identifier may only contain alphanumeric characters, hyphens, and underscores.",
            ),
        ],
    )
    #: Title of the enrichment kit.
    title = models.CharField(
        max_length=128, null=False, blank=False, help_text="Title of the category"
    )
    #: Description of the enrichment kit.
    description = models.TextField(
        null=True, blank=True, help_text="Optional description of the category"
    )

    def __str__(self):
        return f"EnrichmentKit '{self.title}'"

    def get_absolute_url(self):
        return reverse("seqmeta:enrichmentkit-detail", kwargs={"category": self.sodar_uuid})

    class Meta:
        # Order by identifier.
        ordering = ("identifier",)


class TargetBedFile(models.Model):
    """An file belonging to an enrichment kit."""

    #: Constant for GRCh37
    GRCH37 = "grch37"
    #: Constant for GRCh38
    GRCH38 = "grch38"
    #: Options for field genome_release
    GENOME_RELEASE_CHOICES = [
        (GRCH37, "GRCh37"),
        (GRCH38, "GRCh38"),
    ]

    #: Record UUID.
    sodar_uuid = models.UUIDField(
        default=uuid_object.uuid4, unique=True, help_text="Record SODAR UUID"
    )
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")

    #: The panel (version) that this entry is part of
    enrichmentkit = models.ForeignKey(
        EnrichmentKit,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
        help_text="The enrichment kit that this file belongs to.",
    )
    #: The file's URI.
    file_uri = models.URLField(
        null=False,
        blank=False,
        max_length=512,
        help_text="The file's URI.",
    )
    #: The genome release.
    genome_release = models.CharField(
        null=False,
        blank=False,
        max_length=16,
        choices=GENOME_RELEASE_CHOICES,
        default=GRCH37,
        help_text="The file's reference genome.",
    )

    class Meta:
        # Order by genome release.
        ordering = ("genome_release", "file_uri")
