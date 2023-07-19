import uuid as uuid_object

from django.db import models

from cases_import.proto import FileDesignation


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

    #: The file's path relative to the internal or project's external storage base URI.  That is,
    #: the path will not start with a slash.
    path = models.CharField(max_length=1024, null=False, blank=False, unique=True)

    #: The checksum of the file.
    checksum = models.CharField(max_length=128)
    #: The designation of the file.
    designation = models.CharField(max_length=128, null=False, choices=FILE_DESIGNATION_CHOICES)
    #: The genome assembly, if any.
    genomebuild = models.CharField(max_length=128, null=True, choices=GENOMEBUILD_CHOICES)
    #: The file format as MIME type.
    mimetype = models.CharField(max_length=128)

    class Meta:
        abstract = True


class ExternalFile(AbstractFile):
    """Reference to file on external storage.

    Such files are either used for import (and then conversion to internal files)
    before being used in queries etc., or they are used for redisplay only.
    """


class InternalFile(AbstractFile):
    """Reference to a file on internal storage.

    Such files are used for queries etc.
    """
