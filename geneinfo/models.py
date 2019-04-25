from django.db import models
from postgres_copy import CopyManager


class Hgnc(models.Model):
    """Information of HGNC database."""

    #: HGNC identifier
    hgnc_id = models.CharField(max_length=16)
    #: Gene symbol
    symbol = models.CharField(max_length=32)
    #: Gene name
    name = models.CharField(max_length=128)
    #: Locus group
    locus_group = models.CharField(max_length=32, null=True)
    #: Locus type
    locus_type = models.CharField(max_length=32, null=True)
    #: Status of record
    status = models.CharField(max_length=32, null=True)
    #: Location on the chromosome
    location = models.CharField(max_length=64, null=True)
    #: Location on the chromosome
    location_sortable = models.CharField(max_length=64, null=True)
    #: Aliases of gene symbol
    alias_symbol = models.CharField(max_length=128, null=True)
    #: Aliases of gene name
    alias_name = models.CharField(max_length=512, null=True)
    #: Previous gene symbol
    prev_symbol = models.CharField(max_length=128, null=True)
    #: Previous gene name
    prev_name = models.CharField(max_length=1024, null=True)
    #: Gene family
    gene_family = models.CharField(max_length=256, null=True)
    #: Gene family ID
    gene_family_id = models.CharField(max_length=32, null=True)
    #: Date approved
    date_approved_reserved = models.CharField(max_length=32, null=True)
    #: Date symbol changed
    date_symbol_changed = models.CharField(max_length=32, null=True)
    #: Date name changed
    date_name_changed = models.CharField(max_length=32, null=True)
    #: Date of modification
    date_modified = models.CharField(max_length=16, null=True)
    #: Entrez ID
    entrez_id = models.CharField(max_length=16, null=True)
    #: Ensembl Gene ID
    ensembl_gene_id = models.CharField(max_length=32, null=True)
    #: Vega ID (vertebrate genomes)
    vega_id = models.CharField(max_length=32, null=True)
    #: UCSC ID
    ucsc_id = models.CharField(max_length=16, null=True)
    #: ENA ID
    ena = models.CharField(max_length=64, null=True)
    #: RefSeq Accession
    refseq_accession = models.CharField(max_length=128, null=True)
    #: CCDS ID (consensus CDS)
    ccds_id = models.CharField(max_length=256, null=True)
    #: Uniprot ID
    uniprot_ids = models.CharField(max_length=256, null=True)
    #: Pubmed ID
    pubmed_id = models.CharField(max_length=64, null=True)
    #: MGD ID (mouse genome database)
    mgd_id = models.CharField(max_length=256, null=True)
    #: RGD ID (rat genome database)
    rgd_id = models.CharField(max_length=32, null=True)
    #: LDSB ID (locus-specific database)
    lsdb = models.CharField(max_length=1024, null=True)
    #: COSMIC ID
    cosmic = models.CharField(max_length=32, null=True)
    #: OMIM ID
    omim_id = models.CharField(max_length=32, null=True)
    #: miRBase ID (microRNA database)
    mirbase = models.CharField(max_length=16, null=True)
    #: homeodb ID (homeobox gene database)
    homeodb = models.CharField(max_length=16, null=True)
    #: snornabase ID (small nucleolar RNA database)
    snornabase = models.CharField(max_length=16, null=True)
    #: Bioparadigms SLC ID (solute carrier, bioparadigms is company name)
    bioparadigms_slc = models.CharField(max_length=32, null=True)
    #: Orphanet  (rare disease database)
    orphanet = models.CharField(max_length=16, null=True)
    #: Pseudogene.org ID
    pseudogene_org = models.CharField(max_length=32, null=True)
    #: HORDE ID (Human Olfactory Data Explorer database)
    horde_id = models.CharField(max_length=16, null=True)
    #: MEROPS ID (peptidase database)
    merops = models.CharField(max_length=16, null=True)
    #: IMGT ID (international immunogenetics information system database)
    imgt = models.CharField(max_length=32, null=True)
    #: IUPHAR ID (internationl union of basic and clinical pharmacology database)
    iuphar = models.CharField(max_length=32, null=True)
    #: KZNF ID (krueppel-type zinc finger gene family catalog database (?))
    kznf_gene_catalog = models.CharField(max_length=32, null=True)
    #: Mamit tRNA ID (mammalian mitochondrial tRNA database)
    mamit_trnadb = models.CharField(max_length=16, null=True)
    #: CD ID
    cd = models.CharField(max_length=16, null=True)
    #: lncRND ID (long non-coding RNA database)
    lncrnadb = models.CharField(max_length=32, null=True)
    #: enzyme ID (enzyme database ID [BRENDA?])
    enzyme_id = models.CharField(max_length=64, null=True)
    #: Intermediate Filament ID (human intermediate filament database)
    intermediate_filament_db = models.CharField(max_length=32, null=True)
    #: RNACentral ID (rnacentral.org database)
    rna_central_ids = models.CharField(max_length=32, null=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [
            models.Index(fields=["ensembl_gene_id"]),
            models.Index(fields=["entrez_id"]),
            models.Index(fields=["symbol"]),
            models.Index(fields=["hgnc_id"]),
            models.Index(fields=["ensembl_gene_id", "entrez_id", "symbol"]),
        ]


class Mim2geneMedgen(models.Model):
    """Information to translate Entrez ID int OMIM ID."""

    #: OMIM ID
    omim_id = models.IntegerField()
    #: Entrez ID
    entrez_id = models.CharField(max_length=16, null=True)
    #: OMIM type of record
    omim_type = models.CharField(max_length=32, null=True)
    #: Record source
    source = models.CharField(max_length=32, null=True)
    #: Medgen concept identifier
    medgen_cui = models.CharField(max_length=8, null=True)
    #: Comment
    comment = models.CharField(max_length=64, null=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"])]


class Hpo(models.Model):
    """Information of the HPO database."""

    #: Database id of OMIM/DECIPHER/ORPHA
    database_id = models.CharField(max_length=16)
    #: HPO name
    name = models.CharField(max_length=1024, null=True)
    #: HPO qualifier
    qualifier = models.CharField(max_length=4, null=True)
    #: HPO identifier
    hpo_id = models.CharField(max_length=16, null=True)
    #: Cross reference to database
    reference = models.CharField(max_length=128, null=True)
    #: Evidence
    evidence = models.CharField(max_length=4, null=True)
    #: Onset
    onset = models.CharField(max_length=16, null=True)
    #: Frequency
    frequency = models.CharField(max_length=16, null=True)
    #: Sex
    sex = models.CharField(max_length=8, null=True)
    #: Modifier
    modifier = models.CharField(max_length=16, null=True)
    #: Aspect
    aspect = models.CharField(max_length=1, null=True)
    #: Curator
    biocuration = models.CharField(max_length=32, null=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["database_id"])]


class HpoName(models.Model):
    """Mapping of HPO id to name."""

    #: HPO id
    hpo_id = models.CharField(max_length=16, null=True)
    #: HPO name
    name = models.CharField(max_length=512, null=True)

    #: Allow bulk import into database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["hpo_id"])]


class NcbiGeneInfo(models.Model):
    """Store gene information taken from NCBI Gene database."""

    #: The Entrez ID of the gene.
    entrez_id = models.CharField(max_length=16, null=False)
    #: The summary text
    summary = models.TextField(null=True)

    #: Allow bulk import into database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"])]


class NcbiGeneRif(models.Model):
    """Store Gene Reference-Into-Function information taken from NCBI Gene database."""

    #: The Entrez ID of the gene.
    entrez_id = models.CharField(max_length=16, null=False)
    #: The summary text
    rif_text = models.TextField(null=False)

    #: Allow bulk import into database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"])]


class RefseqToHgnc(models.Model):
    """Refseq HGNC mapping."""

    #: Refseq (Entrez) ID
    entrez_id = models.CharField(max_length=16, null=False)
    #: HGNC ID
    hgnc_id = models.CharField(max_length=16, null=False)

    #: Allow bulk import into database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"]), models.Index(fields=["hgnc_id"])]


class Acmg(models.Model):
    """Acmg recommendation table."""

    #: Refseq/Entrez/NCBI ID
    entrez_id = models.CharField(max_length=16, null=False)
    # " EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=32, null=False)
    #: HGNC symbol
    symbol = models.CharField(max_length=32, null=False)

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"]), models.Index(fields=["ensembl_gene_id"])]
