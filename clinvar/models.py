from django.conf import settings
from django.db import models, connection, transaction
from django.contrib.postgres.fields import ArrayField
from postgres_copy import CopyManager

from varfish.utils import JSONField
from .clinvar_models import ClinVarSet


class Clinvar(models.Model):
    """Model for the clinvar information

    For more information on the fields, check out:
    https://www.ncbi.nlm.nih.gov/clinvar/docs/help/
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)
    #: ClinVar version
    clinvar_version = models.CharField(max_length=512, null=True)
    #: Type of the set
    set_type = models.CharField(max_length=32, null=True)
    #: Type of variation
    variation_type = models.CharField(max_length=16)
    #: The symbols.
    symbols = ArrayField(base_field=models.CharField(max_length=32), size=None)
    #: The HGNC IDs.
    hgnc_ids = ArrayField(base_field=models.CharField(max_length=32), size=None)
    #: The variant accession
    vcv = models.CharField(max_length=32)
    #: Summary (ClinVar style) - review status label
    summary_clinvar_review_status_label = models.CharField(max_length=512, null=True)
    #: Summary (ClinVar style) - pathogenicity label
    summary_clinvar_pathogenicity_label = models.CharField(max_length=512, null=True)
    #: Summary (ClinVar style) - pathogenicities
    summary_clinvar_pathogenicity = ArrayField(
        base_field=models.CharField(max_length=32), size=None, null=True
    )
    #: Summary (ClinVar style) - gold stars for VCV
    summary_clinvar_gold_stars = models.IntegerField(null=True)
    #: Summary (paranoid style) - review status label
    summary_paranoid_review_status_label = models.CharField(max_length=512, null=True)
    #: Summary (paranoid style) - pathogenicity label
    summary_paranoid_pathogenicity_label = models.CharField(max_length=512, null=True)
    #: Summary (paranoid style) - pathogenicities
    summary_paranoid_pathogenicity = ArrayField(
        base_field=models.CharField(max_length=32), size=None, null=True
    )
    #: Summary (paranoid style) - gold stars for VCV
    summary_paranoid_gold_stars = models.IntegerField(null=True)
    #: The structured Details information.
    details = JSONField()

    #: Allows bulk import
    objects = CopyManager()

    @property
    def clinvar_sets(self):
        if not hasattr(self, "_clinvar_sets"):
            self._clinvar_sets = tuple([ClinVarSet.from_json(elem) for elem in self.details])
        return self._clinvar_sets

    class Meta:
        indexes = [
            models.Index(fields=["release", "chromosome", "start", "reference", "alternative"])
        ]


class ClinvarPathogenicGenes(models.Model):
    symbol = models.CharField(max_length=16)
    entrez_id = models.CharField(max_length=16, null=True)
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    pathogenic_count = models.IntegerField()
    likely_pathogenic_count = models.IntegerField()

    class Meta:
        managed = settings.IS_TESTING
        db_table = "clinvar_clinvarpathogenicgenes"


def refresh_clinvar_clinvarpathogenicgenes():
    """Refresh the ``ClinvarPathogenicGenes`` materialized view."""
    with connection.cursor() as cursor:
        with transaction.atomic():
            cursor.execute("REFRESH MATERIALIZED VIEW clinvar_clinvarpathogenicgenes")
