from django.db import models
from django.contrib.postgres.fields import ArrayField
from postgres_copy import CopyManager
from django.conf import settings


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
    #: Strand information
    strand = models.CharField(max_length=1, null=True)
    #: Type of variation
    variation_type = models.CharField(max_length=16, null=True)
    #: ClinVar identifier for the variant
    variation_id = models.IntegerField(null=True)
    #: Reference accession number
    rcv = models.CharField(max_length=16, null=True)
    #: Accession number
    scv = ArrayField(models.CharField(max_length=16, null=True))
    #: ClinVar identifier for an individual change
    allele_id = models.IntegerField(null=True)
    #: Gene symbol
    symbol = models.CharField(max_length=16, null=True)
    #: HGVS coding DNA sequence
    hgvs_c = models.CharField(max_length=512, null=True)
    #: HGVS protein sequence
    hgvs_p = models.CharField(max_length=512, null=True)
    #: Calculated result of the indicated allele based on difference relative to reference
    molecular_consequence = models.CharField(max_length=1024, null=True)
    #: Clinical significance reported by submitters
    clinical_significance = models.CharField(max_length=64)
    #: Clinical significance reported by submitters
    clinical_significance_ordered = ArrayField(models.CharField(max_length=512))
    #: Pathogenic or not (1|0)
    pathogenic = models.IntegerField()
    #: Likely pathogenic or not (1|0)
    likely_pathogenic = models.IntegerField()
    #: Uncertain significance or not (1|0)
    uncertain_significance = models.IntegerField()
    #: Likely benign or not (1|0)
    likely_benign = models.IntegerField()
    #: Benign or not (1|0)
    benign = models.IntegerField()
    #: Review status of the record
    review_status = models.CharField(max_length=64, null=True)
    #: List of review status of the record
    review_status_ordered = ArrayField(models.CharField(max_length=64, null=True))
    #: Date of last evaluation
    last_evaluated = models.DateField(null=True)
    #: List of all submitters
    all_submitters = ArrayField(models.CharField(max_length=512, null=True))
    #: List of all submitters
    submitters_ordered = ArrayField(models.CharField(max_length=512, null=True))
    #: List of trait identifiers
    all_traits = ArrayField(models.CharField(max_length=512))
    #: List of PubMed identifiers
    all_pmids = ArrayField(models.IntegerField(null=True))
    #: Modes of inheritance
    inheritance_modes = models.CharField(max_length=32, null=True)
    #: Age of onset
    age_of_onset = models.CharField(max_length=32, null=True)
    #: Prevalence
    prevalence = models.CharField(max_length=32, null=True)
    #: Disease mechanism
    disease_mechanism = models.CharField(max_length=32, null=True)
    #: Origin of the variant allele
    origin = ArrayField(models.CharField(max_length=16, null=True))
    #: List of cross references
    xrefs = ArrayField(models.CharField(max_length=16, null=True))
    #: List of ordered dates of what?
    dates_ordered = ArrayField(models.DateField(null=True))
    #: Indicator if ClinVar entry comes from multi or single variant database
    multi = models.IntegerField()

    #: Allows bulk import
    objects = CopyManager()

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
