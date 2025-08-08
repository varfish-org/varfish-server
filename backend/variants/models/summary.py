"""Code for small variant summary (aka in-house table)."""

from django.conf import settings
from django.db import models


class SmallVariantSummary(models.Model):
    """Summary counts for the small variants.

    In the database, this is a materialized view.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: Number of hom. ref. genotypes.
    count_hom_ref = models.IntegerField()
    #: Number of heterozygous genotypes.
    count_het = models.IntegerField()
    #: Number of hom. alt. genotypes.
    count_hom_alt = models.IntegerField()
    #: Number of hemi ref. genotypes.
    count_hemi_ref = models.IntegerField()
    #: Number of hemi alt. genotypes.
    count_hemi_alt = models.IntegerField()

    class Meta:
        managed = settings.IS_TESTING
        db_table = "variants_smallvariantsummary"
