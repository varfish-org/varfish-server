from django.db import models
from postgres_copy import CopyManager


class KnowngeneAA(models.Model):
    """Information of KnownGeneExonAA track from UCSC genome browser."""

    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=16)
    #: Variant coordinates - start
    start = models.IntegerField()
    #: Variant coordinates - end
    end = models.IntegerField()
    #: Transcript ID in UCSC format
    transcript_id = models.CharField(max_length=16)
    #: Multiple AA alignment of 100 species (multiz)
    alignment = models.CharField(max_length=100)

    #: Allows bulk import
    objects = CopyManager()

    class Meta:
        unique_together = ("chromosome", "start", "end", "transcript_id")

        indexes = [models.Index(fields=["chromosome", "start", "end"])]
