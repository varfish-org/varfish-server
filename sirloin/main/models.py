from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import JSONField


class Main(models.Model):
    release = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    case_id = models.CharField(max_length=512)
    frequency = models.FloatField()
    homozygous = models.IntegerField()
    effect = ArrayField(models.CharField(max_length=64))

    class Meta:
        indexes = [
            models.Index(fields=['case_id', 'frequency', 'homozygous', 'effect']),
            models.Index(fields=['chromosome', 'position', 'reference', 'alternative'])
        ]


class Pedigree(models.Model):
    case_id = models.CharField(max_length=512)
    pedigree = JSONField()

    class Meta:
        indexes = [
            models.Index(fields=['case_id'])
        ]


class Exac(models.Model):
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    ac = models.IntegerField()
    ac_afr = models.IntegerField()
    ac_amr = models.IntegerField()
    ac_eas = models.IntegerField()
    ac_fin = models.IntegerField()
    ac_nfe = models.IntegerField()
    ac_oth = models.IntegerField()
    ac_sas = models.IntegerField()
    an = models.IntegerField()
    an_afr = models.IntegerField()
    an_amr = models.IntegerField()
    an_eas = models.IntegerField()
    an_fin = models.IntegerField()
    an_nfe = models.IntegerField()
    an_oth = models.IntegerField()
    an_sas = models.IntegerField()
    hemi = models.IntegerField()
    hemi_afr = models.IntegerField()
    hemi_amr = models.IntegerField()
    hemi_eas = models.IntegerField()
    hemi_fin = models.IntegerField()
    hemi_nfe = models.IntegerField()
    hemi_oth = models.IntegerField()
    hemi_sas = models.IntegerField()
    hom = models.IntegerField()
    hom_afr = models.IntegerField()
    hom_amr = models.IntegerField()
    hom_eas = models.IntegerField()
    hom_fin = models.IntegerField()
    hom_nfe = models.IntegerField()
    hom_oth = models.IntegerField()
    hom_sas = models.IntegerField()
    popmax = models.CharField(max_length=8)
    ac_popmax = models.IntegerField()
    an_popmax = models.IntegerField()
    af_popmax = models.FloatField()
    hemi_popmax = models.IntegerField()
    hom_popmax = models.IntegerField()
    af = models.FloatField()
    af_afr = models.FloatField()
    af_amr = models.FloatField()
    af_eas = models.FloatField()
    af_fin = models.FloatField()
    af_nfe = models.FloatField()
    af_oth = models.FloatField()
    af_sas = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['chromosome', 'position', 'reference', 'alternative'])
        ]


class Annotation(models.Model):
    chromosome = models.CharField(max_length=32)
    position = models.IntegerField()
    reference = models.CharField(max_length=512)
    alternative = models.CharField(max_length=512)
    effect = ArrayField(models.CharField(max_length=64))
    impact = models.CharField(max_length=64)
    gene_name = models.CharField(max_length=64)
    gene_id = models.CharField(max_length=64)
    feature_type = models.CharField(max_length=64)
    feature_id = models.CharField(max_length=64)
    transcript_biotype = models.CharField(max_length=64)
    rank = models.CharField(max_length=64)
    hgvs_c = models.CharField(max_length=512)
    hgvs_p = models.CharField(max_length=512)
    cdna_pos_length = models.CharField(max_length=64)
    cds_pos_length = models.CharField(max_length=64)
    aa_pos_length = models.CharField(max_length=64)
    distance = models.CharField(max_length=64)
    errors = models.CharField(max_length=512)

    class Meta:
        indexes = [
            models.Index(fields=['chromosome', 'position', 'reference', 'alternative'])
        ]


class Hgnc(models.Model):
    hgnc_id = models.CharField(max_length=16)
    symbol = models.CharField(max_length=32)
    name = models.CharField(max_length=128)
    locus_group = models.CharField(max_length=32)
    locus_type = models.CharField(max_length=32)
    status = models.CharField(max_length=32)
    location = models.CharField(max_length=64)
    location_sortable = models.CharField(max_length=64)
    alias_symbol = models.CharField(max_length=128)
    alias_name = models.CharField(max_length=512)
    prev_symbol = models.CharField(max_length=128)
    prev_name = models.CharField(max_length=1024)
    gene_family = models.CharField(max_length=256)
    gene_family_id = models.CharField(max_length=32)
    date_approved_reserved = models.CharField(max_length=32)
    date_symbol_changed = models.CharField(max_length=32)
    date_name_changed = models.CharField(max_length=32)
    date_modified = models.CharField(max_length=16)
    entrez_id = models.IntegerField()
    ensembl_gene_id = models.CharField(max_length=32)
    vega_id = models.CharField(max_length=32)
    ucsc_id = models.CharField(max_length=16)
    ena = models.CharField(max_length=64)
    refseq_accession = models.CharField(max_length=128)
    ccds_id = models.CharField(max_length=256)
    uniprot_ids = models.CharField(max_length=256)
    pubmed_id = models.CharField(max_length=64)
    mgd_id = models.CharField(max_length=256)
    rgd_id = models.CharField(max_length=32)
    lsdb = models.CharField(max_length=1024)
    cosmic = models.CharField(max_length=32)
    omim_id = models.CharField(max_length=32)
    mirbase = models.CharField(max_length=16)
    homeodb = models.CharField(max_length=16)
    snornabase = models.CharField(max_length=16)
    bioparadigms_slc = models.CharField(max_length=32)
    orphanet = models.CharField(max_length=16)
    pseudogene_org = models.CharField(max_length=32)
    horde_id = models.CharField(max_length=16)
    merops = models.CharField(max_length=16)
    imgt = models.CharField(max_length=32)
    iuphar = models.CharField(max_length=32)
    kznf_gene_catalog = models.CharField(max_length=32)
    namit_trnadb = models.CharField(max_length=16)
    cd = models.CharField(max_length=16)
    lncrnadb = models.CharField(max_length=32)
    enzyme_id = models.CharField(max_length=64)
    intermediate_filament_db = models.CharField(max_length=32)
    rna_central_ids = models.CharField(max_length=32)

    class Meta:
        indexes = [
            models.Index(fields=['ensembl_gene_id'])
        ]


class Mim2gene(models.Model):
    omim_id = models.IntegerField()
    omim_type = models.CharField(max_length=32)
    entrez_id = models.IntegerField()
    symbol = models.CharField(max_length=32)
    ensembl_gene_id = models.CharField(max_length=32)


class Mim2geneMedgen(models.Model):
    omim_id = models.IntegerField()
    entrez_id = models.IntegerField()
    omim_type = models.CharField(max_length=32)
    source = models.CharField(max_length=32)
    medgen_cui = models.CharField(max_length=8)
    comment = models.CharField(max_length=64)

    class Meta:
        indexes = [
            models.Index(fields=['entrez_id'])
        ]



class Hpo(models.Model):
    db = models.CharField(max_length=8)
    db_object_id = models.IntegerField()
    name = models.CharField(max_length=1024)
    qualifier = models.CharField(max_length=4)
    hpo_id = models.CharField(max_length=16)
    db_reference = models.CharField(max_length=128)
    evidence = models.CharField(max_length=4)
    onset = models.CharField(max_length=16)
    frequency = models.CharField(max_length=16)
    sex = models.CharField(max_length=8)
    modifier = models.CharField(max_length=16)
    aspect = models.CharField(max_length=1)
    date = models.DateField()
    assigned_by = models.CharField(max_length=32)

    class Meta:
        indexes = [
            models.Index(fields=['db_object_id']),
            models.Index(fields=['db'])
        ]
