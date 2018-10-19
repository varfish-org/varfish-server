from django.db import models
from postgres_copy import CopyManager


class KnowngeneAA(models.Model):
    chromosome = models.CharField(max_length=16)
    start = models.IntegerField()
    end = models.IntegerField()
    transcript_id = models.CharField(max_length=16)
    alignment = models.CharField(max_length=100)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "chromosome",
            "start",
            "end",
            "transcript_id",
        )

        indexes = [
            models.Index(fields=["chromosome", "start", "end"])
        ]
