from django.db import models
from postgres_copy import CopyManager


class EnsemblToKegg(models.Model):
    gene_id = models.CharField(max_length=32)
    kegginfo_id = models.IntegerField()
    objects = CopyManager()

    class Meta:
        unique_together = ["gene_id", "kegginfo_id"]
        indexes = [models.Index(fields=["gene_id"])]


class RefseqToKegg(models.Model):
    gene_id = models.CharField(max_length=32)
    kegginfo_id = models.IntegerField()
    objects = CopyManager()

    class Meta:
        unique_together = ["gene_id", "kegginfo_id"]
        indexes = [models.Index(fields=["gene_id"])]


class KeggInfo(models.Model):
    kegg_id = models.CharField(max_length=16)
    name = models.CharField(max_length=512)
    objects = CopyManager()
