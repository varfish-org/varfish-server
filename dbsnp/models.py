from django.db import models
from postgres_copy import CopyManager


class Dbsnp(models.Model):
    """Information of the DBSNP database."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - position
    position = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: DbSNPs RsID
    rsid = models.CharField(max_length=16)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        unique_together = ("release", "chromosome", "position", "reference", "alternative")
        indexes = [
            models.Index(fields=["release", "chromosome", "position", "reference", "alternative"])
        ]
