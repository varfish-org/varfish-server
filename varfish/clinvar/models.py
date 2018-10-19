from django.db import models
from django.contrib.postgres.fields import ArrayField
from postgres_copy import CopyManager


class Clinvar(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    start = models.IntegerField()
    stop = models.IntegerField()
    strand = models.CharField(max_length=1, null=True)
    variation_type = models.CharField(max_length=16, null=True)
    variation_id = models.IntegerField(null=True)
    rcv = models.CharField(max_length=16, null=True)
    scv = ArrayField(models.CharField(max_length=16, null=True))
    allele_id = models.IntegerField(null=True)
    symbol = models.CharField(max_length=16, null=True)
    hgvs_c = models.CharField(max_length=512, null=True)
    hgvs_p = models.CharField(max_length=512, null=True)
    molecular_consequence = models.CharField(max_length=1024, null=True)
    clinical_significance = models.CharField(max_length=64)
    clinical_significance_ordered = ArrayField(models.CharField(max_length=512))
    pathogenic = models.IntegerField()
    likely_pathogenic = models.IntegerField()
    uncertain_significance = models.IntegerField()
    likely_benign = models.IntegerField()
    benign = models.IntegerField()
    review_status = models.CharField(max_length=64, null=True)
    review_status_ordered = ArrayField(models.CharField(max_length=64, null=True))
    last_evaluated = models.DateField(null=True)
    all_submitters = ArrayField(models.CharField(max_length=512, null=True))
    submitters_ordered = ArrayField(models.CharField(max_length=512, null=True))
    all_traits = ArrayField(models.CharField(max_length=512))
    all_pmids = ArrayField(models.IntegerField(null=True))
    inheritance_modes = models.CharField(max_length=32, null=True)
    age_of_onset = models.CharField(max_length=32, null=True)
    prevalence = models.CharField(max_length=32, null=True)
    disease_mechanism = models.CharField(max_length=32, null=True)
    origin = ArrayField(models.CharField(max_length=16, null=True))
    xrefs = ArrayField(models.CharField(max_length=16, null=True))
    dates_ordered = ArrayField(models.DateField(null=True))
    multi = models.IntegerField()
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(fields=["release", "chromosome", "position", "reference", "alternative"])
        ]
