from django.db import models
from postgres_copy import CopyManager


class Dbsnp(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    rsid = models.CharField(max_length=16)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
        )
        indexes = [models.Index(fields=["release", "chromosome", "position", "reference", "alternative"])]

