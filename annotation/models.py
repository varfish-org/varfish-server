from django.db import models
from django.contrib.postgres.fields import ArrayField
from postgres_copy import CopyManager


class Annotation(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    database = models.CharField(max_length=8, null=True)
    effect = ArrayField(models.CharField(max_length=64, null=True))
    gene_id = models.CharField(max_length=64, null=True)
    transcript_id = models.CharField(max_length=64, null=True)
    transcript_coding = models.NullBooleanField()
    hgvs_c = models.CharField(max_length=512, null=True)
    hgvs_p = models.CharField(max_length=512, null=True)
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "position",
            "reference",
            "alternative",
            "transcript_id",
        )
        indexes = [
            models.Index(
                fields=["release", "chromosome", "position", "reference", "alternative", "gene_id"]
            )
        ]
