from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField
from postgres_copy import CopyManager


class Main(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    case_id = models.CharField(max_length=512)
    frequency = models.FloatField(null=True)
    homozygous = models.IntegerField(null=True)
    effect = ArrayField(models.CharField(max_length=64, null=True))
    genotype = JSONField()
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["case_id", "frequency", "homozygous", "effect"]
            ),
            models.Index(
                fields=["chromosome", "position", "reference", "alternative"]
            ),
        ]


class Pedigree(models.Model):
    case_id = models.CharField(max_length=512)
    pedigree = JSONField()
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["case_id"])]
    
    def __str__(self):
        return self.case_id


class ImportInfo(models.Model):
    table = models.CharField(max_length=16)
    timestamp = models.DateTimeField(editable=False)
    release = models.CharField(max_length=16)
    comment = models.CharField(max_length=1024)


class Exac(models.Model):
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField(null=True)
    ac_afr = models.IntegerField(null=True)
    ac_amr = models.IntegerField(null=True)
    ac_eas = models.IntegerField(null=True)
    ac_fin = models.IntegerField(null=True)
    ac_nfe = models.IntegerField(null=True)
    ac_oth = models.IntegerField(null=True)
    ac_sas = models.IntegerField(null=True)
    an = models.IntegerField(null=True)
    an_afr = models.IntegerField(null=True)
    an_amr = models.IntegerField(null=True)
    an_eas = models.IntegerField(null=True)
    an_fin = models.IntegerField(null=True)
    an_nfe = models.IntegerField(null=True)
    an_oth = models.IntegerField(null=True)
    an_sas = models.IntegerField(null=True)
    hemi = models.IntegerField(null=True)
    hemi_afr = models.IntegerField(null=True)
    hemi_amr = models.IntegerField(null=True)
    hemi_eas = models.IntegerField(null=True)
    hemi_fin = models.IntegerField(null=True)
    hemi_nfe = models.IntegerField(null=True)
    hemi_oth = models.IntegerField(null=True)
    hemi_sas = models.IntegerField(null=True)
    hom = models.IntegerField(null=True)
    hom_afr = models.IntegerField(null=True)
    hom_amr = models.IntegerField(null=True)
    hom_eas = models.IntegerField(null=True)
    hom_fin = models.IntegerField(null=True)
    hom_nfe = models.IntegerField(null=True)
    hom_oth = models.IntegerField(null=True)
    hom_sas = models.IntegerField(null=True)
    popmax = models.CharField(max_length=8)
    ac_popmax = models.IntegerField(null=True)
    an_popmax = models.IntegerField(null=True)
    af_popmax = models.FloatField(null=True)
    hemi_popmax = models.IntegerField(null=True)
    hom_popmax = models.IntegerField(null=True)
    af = models.FloatField(null=True)
    af_afr = models.FloatField(null=True)
    af_amr = models.FloatField(null=True)
    af_eas = models.FloatField(null=True)
    af_fin = models.FloatField(null=True)
    af_nfe = models.FloatField(null=True)
    af_oth = models.FloatField(null=True)
    af_sas = models.FloatField(null=True)
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["chromosome", "position", "reference", "alternative"]
            )
        ]


class Annotation(models.Model):
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    effect = ArrayField(models.CharField(max_length=64, null=True))
    impact = models.CharField(max_length=64, null=True)
    gene_name = models.CharField(max_length=64, null=True)
    gene_id = models.CharField(max_length=64, null=True)
    feature_type = models.CharField(max_length=64, null=True)
    feature_id = models.CharField(max_length=64, null=True)
    transcript_biotype = models.CharField(max_length=64, null=True)
    rank = models.CharField(max_length=64, null=True)
    hgvs_c = models.CharField(max_length=512, null=True)
    hgvs_p = models.CharField(max_length=512, null=True)
    cdna_pos_length = models.CharField(max_length=64, null=True)
    cds_pos_length = models.CharField(max_length=64, null=True)
    aa_pos_length = models.CharField(max_length=64, null=True)
    distance = models.CharField(max_length=64, null=True)
    errors = models.CharField(max_length=512, null=True)
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["chromosome", "position", "reference", "alternative"]
            )
        ]


class Hgnc(models.Model):
    hgnc_id = models.CharField(max_length=16)
    symbol = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    locus_group = models.CharField(max_length=32, null=True)
    locus_type = models.CharField(max_length=32, null=True)
    status = models.CharField(max_length=32, null=True)
    location = models.CharField(max_length=64, null=True)
    location_sortable = models.CharField(max_length=64, null=True)
    alias_symbol = models.CharField(max_length=128, null=True)
    alias_name = models.CharField(max_length=512, null=True)
    prev_symbol = models.CharField(max_length=128, null=True)
    prev_name = models.CharField(max_length=1024, null=True)
    gene_family = models.CharField(max_length=256, null=True)
    gene_family_id = models.CharField(max_length=32, null=True)
    date_approved_reserved = models.CharField(max_length=32, null=True)
    date_symbol_changed = models.CharField(max_length=32, null=True)
    date_name_changed = models.CharField(max_length=32, null=True)
    date_modified = models.CharField(max_length=16, null=True)
    entrez_id = models.IntegerField(null=True)
    ensembl_gene_id = models.CharField(max_length=32, null=True)
    vega_id = models.CharField(max_length=32, null=True)
    ucsc_id = models.CharField(max_length=16, null=True)
    ena = models.CharField(max_length=64, null=True)
    refseq_accession = models.CharField(max_length=128, null=True)
    ccds_id = models.CharField(max_length=256, null=True)
    uniprot_ids = models.CharField(max_length=256, null=True)
    pubmed_id = models.CharField(max_length=64, null=True)
    mgd_id = models.CharField(max_length=256, null=True)
    rgd_id = models.CharField(max_length=32, null=True)
    lsdb = models.CharField(max_length=1024, null=True)
    cosmic = models.CharField(max_length=32, null=True)
    omim_id = models.CharField(max_length=32, null=True)
    mirbase = models.CharField(max_length=16, null=True)
    homeodb = models.CharField(max_length=16, null=True)
    snornabase = models.CharField(max_length=16, null=True)
    bioparadigms_slc = models.CharField(max_length=32, null=True)
    orphanet = models.CharField(max_length=16, null=True)
    pseudogene_org = models.CharField(max_length=32, null=True)
    horde_id = models.CharField(max_length=16, null=True)
    merops = models.CharField(max_length=16, null=True)
    imgt = models.CharField(max_length=32, null=True)
    iuphar = models.CharField(max_length=32, null=True)
    kznf_gene_catalog = models.CharField(max_length=32, null=True)
    namit_trnadb = models.CharField(max_length=16, null=True)
    cd = models.CharField(max_length=16, null=True)
    lncrnadb = models.CharField(max_length=32, null=True)
    enzyme_id = models.CharField(max_length=64, null=True)
    intermediate_filament_db = models.CharField(max_length=32, null=True)
    rna_central_ids = models.CharField(max_length=32, null=True)
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["ensembl_gene_id"])]


class Mim2gene(models.Model):
    omim_id = models.IntegerField()
    omim_type = models.CharField(max_length=32, null=True)
    entrez_id = models.IntegerField(null=True)
    symbol = models.CharField(max_length=32, null=True)
    ensembl_gene_id = models.CharField(max_length=32, null=True)
    objects = CopyManager()


class Mim2geneMedgen(models.Model):
    omim_id = models.IntegerField()
    entrez_id = models.IntegerField(null=True)
    omim_type = models.CharField(max_length=32, null=True)
    source = models.CharField(max_length=32, null=True)
    medgen_cui = models.CharField(max_length=8, null=True)
    comment = models.CharField(max_length=64, null=True)
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"])]


class Hpo(models.Model):
    db = models.CharField(max_length=8)
    db_object_id = models.IntegerField()
    name = models.CharField(max_length=1024, null=True)
    qualifier = models.CharField(max_length=4, null=True)
    hpo_id = models.CharField(max_length=16, null=True)
    db_reference = models.CharField(max_length=128, null=True)
    evidence = models.CharField(max_length=4, null=True)
    onset = models.CharField(max_length=16, null=True)
    frequency = models.CharField(max_length=16, null=True)
    sex = models.CharField(max_length=8, null=True)
    modifier = models.CharField(max_length=16, null=True)
    aspect = models.CharField(max_length=1, null=True)
    date = models.DateField(null=True)
    assigned_by = models.CharField(max_length=32, null=True)
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(fields=["db_object_id"]),
            models.Index(fields=["db"]),
        ]
