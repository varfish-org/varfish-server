from django.db import models


class ImportInfo(models.Model):
    """Store information about data import."""

    #: Releas of genomebuild
    genomebuild = models.CharField(max_length=32, default="GRCh37")
    #: Name of imported table
    table = models.CharField(max_length=16)
    #: Timestamp of import
    timestamp = models.DateTimeField(auto_now_add=True, editable=False)
    #: Data release
    release = models.CharField(max_length=512)
    #: Further comments
    comment = models.CharField(max_length=1024)

    class Meta:
        unique_together = ("genomebuild", "table", "release")
