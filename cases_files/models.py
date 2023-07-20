import enum
import uuid as uuid_object

from django.db import models

from cases.models import Individual, Pedigree
from cases_import.proto import FileDesignation
from variants.models import Case


@enum.unique
class MimeTypes(enum.Enum):
    BAM = "application/x-bam"


class AbstractFile(models.Model):
    """Abstract model for file reference."""

    GENOMEBUILD_GRCH37 = "grch37"
    GENOMEBUILD_GRCH38 = "grch38"

    GENOMEBUILD_CHOICES = (
        (GENOMEBUILD_GRCH37, GENOMEBUILD_GRCH37),
        (GENOMEBUILD_GRCH38, GENOMEBUILD_GRCH38),
    )

    FILE_DESIGNATION_CHOICES = tuple(((val, val) for val in FileDesignation.all_values()))

    #: Record UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation.
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification.
    date_modified = models.DateTimeField(auto_now=True)

    #: The case that the file belongs to.
    case = models.ForeignKey(
        Case,
        null=False,
        on_delete=models.CASCADE,
    )

    #: The file's path relative to the internal or project's external storage base URI.  That is,
    #: the path will not start with a slash.
    path = models.CharField(max_length=1024, null=False, blank=False, unique=True)

    #: The designation of the file.
    designation = models.CharField(max_length=128, null=False, choices=FILE_DESIGNATION_CHOICES)
    #: The genome assembly, if any.
    genomebuild = models.CharField(max_length=128, null=True, choices=GENOMEBUILD_CHOICES)
    #: The file format as MIME type.
    mimetype = models.CharField(max_length=256)

    class Meta:
        abstract = True


class ExternalFile(AbstractFile):
    """Reference to file on external storage.

    Such files are either used for import (and then conversion to internal files)
    before being used in queries etc., or they are used for redisplay only.
    """

    #: Whether or not the file was available on the last check.
    available = models.BooleanField(default=False)
    #: Date of the last check.
    last_checked = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class InternalFile(AbstractFile):
    """Reference to a file on internal storage.

    Such files are used for queries etc.
    """

    #: The checksum of the file.
    checksum = models.CharField(max_length=128, null=True)

    class Meta:
        abstract = True


class IndividualExternalFile(ExternalFile):
    """Reference to a file on external storage for an individual."""

    #: The individual that the file belongs to.
    individual = models.ForeignKey(
        Individual,
        null=False,
        on_delete=models.CASCADE,
    )


class IndividualInternalFile(InternalFile):
    """Reference to a file on internal storage for an individual."""

    #: The individual that the file belongs to.
    individual = models.ForeignKey(
        Individual,
        null=False,
        on_delete=models.CASCADE,
    )


class PedigreeExternalFile(ExternalFile):
    """Reference to a file on external storage for a pedigree."""

    #: The pedigree that the file belongs to.
    pedigree = models.ForeignKey(
        Pedigree,
        null=False,
        on_delete=models.CASCADE,
    )


class PedigreeInternalFile(InternalFile):
    """Reference to a file on internal storage for a pedigree."""

    #: The pedigree that the file belongs to.
    pedigree = models.ForeignKey(
        Pedigree,
        null=False,
        on_delete=models.CASCADE,
    )
