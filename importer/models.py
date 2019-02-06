from django.db import models


class ImportInfo(models.Model):
    """Store information about data import."""

    #: Name of imported table
    table = models.CharField(max_length=16)
    #: Timestamp of import
    timestamp = models.DateTimeField(editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Further comments
    comment = models.CharField(max_length=1024)

    class Meta:
        unique_together = ("table", "release")
