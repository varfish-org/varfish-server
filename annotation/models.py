from django.db import models
from django.contrib.postgres.fields import ArrayField
from postgres_copy import CopyManager


class Annotation(models.Model):
    """Stores the annotated information of a variant."""

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordiantes - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: Transcript database (refseq or ensembl)
    database = models.CharField(max_length=8, null=True)
    #: Variant effect, multiple allowed
    effect = ArrayField(models.CharField(max_length=64, null=True))
    #: Gene ID according to transcript database
    gene_id = models.CharField(max_length=64, null=True)
    #: Transcript ID according to transcript database
    transcript_id = models.CharField(max_length=64, null=True)
    #: Information if transcript is coding
    transcript_coding = models.NullBooleanField()
    #: HGVS coding DNA sequence
    hgvs_c = models.CharField(max_length=512, null=True)
    #: HGVS protein sequence
    hgvs_p = models.CharField(max_length=512, null=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        unique_together = (
            "release",
            "chromosome",
            "start",
            "reference",
            "alternative",
            "transcript_id",
        )
        indexes = [
            models.Index(
                fields=["release", "chromosome", "start", "reference", "alternative", "gene_id"]
            )
        ]
