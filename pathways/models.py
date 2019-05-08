from django.db import models
from postgres_copy import CopyManager


class KeggInfo(models.Model):
    """Kegg information."""

    #: Kegg ID
    kegg_id = models.CharField(max_length=16)
    #: Kegg name
    name = models.CharField(max_length=512)

    #: Allow bulk import
    objects = CopyManager()


class EnsemblToKegg(models.Model):
    """Linking ensembl gene id and kegg id."""

    #: Ensembl gene ID
    gene_id = models.CharField(max_length=32)
    #: Kegg info ID
    kegginfo_id = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    @property
    def kegginfo(self):
        return KeggInfo.objects.get(id=self.kegginfo_id)

    class Meta:
        unique_together = ["gene_id", "kegginfo_id"]
        indexes = [models.Index(fields=["gene_id"])]


class RefseqToKegg(models.Model):
    """Linking refseq id and kegg id."""

    #: Refseq ID
    gene_id = models.CharField(max_length=32)
    #: Kegg info ID
    kegginfo_id = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    @property
    def kegginfo(self):
        return KeggInfo.objects.get(id=self.kegginfo_id)

    class Meta:
        unique_together = ["gene_id", "kegginfo_id"]
        indexes = [models.Index(fields=["gene_id"])]
