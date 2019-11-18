from django.contrib.postgres.fields import ArrayField
from django.db import models, connection, transaction
from django.conf import settings
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
    #: OMIM IDs (can be multiple, separated by | and in quotes)
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
    #: OMIM ID
    omim_id = models.IntegerField(null=True)
    #: Decipher ID
    decipher_id = models.IntegerField(null=True)
    #: Orpha ID
    orpha_id = models.IntegerField(null=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["database_id"]), models.Index(fields=["omim_id"])]


class HpoName(models.Model):
    """Mapping of HPO id to name."""

    #: HPO id
    hpo_id = models.CharField(max_length=16, null=True)
    #: HPO name
    name = models.CharField(max_length=512, null=True)

    #: Allow bulk import into database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["hpo_id"]), models.Index(fields=["name"])]


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
    #: The pubmed ids.
    pubmed_ids = ArrayField(models.CharField(max_length=16, null=False), default=[])

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
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=32, null=False)
    #: HGNC symbol
    symbol = models.CharField(max_length=32, null=False)

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"]), models.Index(fields=["ensembl_gene_id"])]


class GnomadConstraints(models.Model):
    """Gnomad Constraints table."""

    #: HGNC symbol
    symbol = models.CharField(max_length=32)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=16)
    obs_mis = models.IntegerField(null=True)
    exp_mis = models.FloatField(null=True)
    oe_mis = models.FloatField(null=True)
    mu_mis = models.FloatField(null=True)
    possible_mis = models.IntegerField(null=True)
    obs_mis_pphen = models.IntegerField(null=True)
    exp_mis_pphen = models.FloatField(null=True)
    oe_mis_pphen = models.FloatField(null=True)
    possible_mis_pphen = models.IntegerField(null=True)
    obs_syn = models.IntegerField(null=True)
    exp_syn = models.FloatField(null=True)
    oe_syn = models.FloatField(null=True)
    mu_syn = models.FloatField(null=True)
    possible_syn = models.IntegerField(null=True)
    obs_lof = models.IntegerField(null=True)
    mu_lof = models.FloatField(null=True)
    possible_lof = models.IntegerField(null=True)
    exp_lof = models.FloatField(null=True)
    pLI = models.FloatField(null=True)
    pNull = models.FloatField(null=True)
    pRec = models.FloatField(null=True)
    oe_lof = models.FloatField(null=True)
    oe_syn_lower = models.FloatField(null=True)
    oe_syn_upper = models.FloatField(null=True)
    oe_mis_lower = models.FloatField(null=True)
    oe_mis_upper = models.FloatField(null=True)
    oe_lof_lower = models.FloatField(null=True)
    oe_lof_upper = models.FloatField(null=True)
    constraint_flag = models.CharField(max_length=64, null=True)
    syn_z = models.FloatField(null=True)
    mis_z = models.FloatField(null=True)
    lof_z = models.FloatField(null=True)
    oe_lof_upper_rank = models.IntegerField(null=True)
    oe_lof_upper_bin = models.IntegerField(null=True)
    oe_lof_upper_bin_6 = models.IntegerField(null=True)
    n_sites = models.IntegerField(null=True)
    classic_caf = models.FloatField(null=True)
    max_af = models.FloatField(null=True)
    no_lofs = models.IntegerField(null=True)
    obs_het_lof = models.IntegerField(null=True)
    obs_hom_lof = models.IntegerField(null=True)
    defined = models.IntegerField(null=True)
    p = models.FloatField(null=True)
    exp_hom_lof = models.FloatField(null=True)
    classic_caf_afr = models.FloatField(null=True)
    classic_caf_amr = models.FloatField(null=True)
    classic_caf_asj = models.FloatField(null=True)
    classic_caf_eas = models.FloatField(null=True)
    classic_caf_fin = models.FloatField(null=True)
    classic_caf_nfe = models.FloatField(null=True)
    classic_caf_oth = models.FloatField(null=True)
    classic_caf_sas = models.FloatField(null=True)
    p_afr = models.FloatField(null=True)
    p_amr = models.FloatField(null=True)
    p_asj = models.FloatField(null=True)
    p_eas = models.FloatField(null=True)
    p_fin = models.FloatField(null=True)
    p_nfe = models.FloatField(null=True)
    p_oth = models.FloatField(null=True)
    p_sas = models.FloatField(null=True)
    transcript_type = models.CharField(max_length=16, null=True)
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    transcript_level = models.IntegerField(null=True)
    cds_length = models.IntegerField(null=True)
    num_coding_exons = models.IntegerField(null=True)
    gene_type = models.CharField(max_length=16, null=True)
    gene_length = models.IntegerField(null=True)
    exac_pLI = models.FloatField(null=True)
    exac_obs_lof = models.IntegerField(null=True)
    exac_exp_lof = models.FloatField(null=True)
    exac_oe_lof = models.FloatField(null=True)
    brain_expression = models.CharField(max_length=16, null=True)
    chromosome = models.CharField(max_length=32, null=True)
    start_position = models.IntegerField(null=True)
    end_position = models.IntegerField(null=True)

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["ensembl_gene_id"])]


class ExacConstraints(models.Model):
    """Exac Constraints table."""

    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=16)
    #: HGNC symbol
    symbol = models.CharField(max_length=32)
    chromosome = models.CharField(max_length=32)
    n_exons = models.IntegerField()
    cds_start = models.IntegerField()
    cds_end = models.IntegerField()
    bp = models.IntegerField()
    mu_syn = models.FloatField()
    mu_mis = models.FloatField()
    mu_lof = models.FloatField()
    n_syn = models.IntegerField()
    n_mis = models.IntegerField()
    n_lof = models.IntegerField()
    exp_syn = models.FloatField()
    exp_mis = models.FloatField()
    exp_lof = models.FloatField()
    syn_z = models.FloatField()
    mis_z = models.FloatField()
    lof_z = models.FloatField()
    pLI = models.FloatField()
    pRec = models.FloatField()
    pNull = models.FloatField()

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["ensembl_transcript_id"])]


class EnsemblToRefseq(models.Model):
    """Ensembl gene ID and transcript ID to Entrez ID."""

    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=16)
    #: Entrez ID
    entrez_id = models.CharField(max_length=16, null=True)

    #: Allow bulk import info database.
    objects = CopyManager()


class RefseqToEnsembl(models.Model):
    """Entrez ID to Ensembl gene ID and transcript ID."""

    #: Entrez ID
    entrez_id = models.CharField(max_length=16)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16, null=True)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=16, null=True)

    #: Allow bulk import info database.
    objects = CopyManager()


class GeneIdToInheritance(models.Model):
    """Mode of inheritance to EnsEMBL/RefSeq gene id as materialized view.
    The modes of inheritance are derived from the following HPO terms. While this table is detached
    from the HPO terms, the generation of the materialized view is not. Please look into
    ``migrations/0010_geneidtoinheritance.py`` to learn how the view is created.
    - HP:0000006: ad
    - HP:0000007: ar
    - HP:0001417: x
    - HP:0001419: xr
    - HP:0001423: xd
    Modes of inheritance in HPO: https://hpo.jax.org/app/browse/term/HP:0000005
    """

    AR = "AR"
    AD = "AD"
    X = "X-linked"
    XR = "XR"
    XD = "XD"

    MODES_OF_INHERITANCE = (
        (AR, "Autosomal recessive"),
        (AD, "Autosomal dominant"),
        (X, "X-linked"),
        (XR, "X-linked recessive"),
        (XD, "X-linked dominant"),
    )

    #: RefSeq gene ID (the view requires entrez id not to be null.)
    entrez_id = models.CharField(max_length=16, null=False)
    #: EnsEMBL gene ID (the view joins via entrez id, so entrez id is never null, but ensembl might be.)
    ensembl_gene_id = models.CharField(max_length=32)
    #: Mode of inheritance
    mode_of_inheritance = models.CharField(choices=MODES_OF_INHERITANCE, default=AR, max_length=8)

    class Meta:
        managed = settings.IS_TESTING
        db_table = "geneinfo_geneidtoinheritance"


def refresh_geneinfo_geneidtoinheritance():
    """Refresh the ``GeneIdToInheritance`` materialized view."""
    with connection.cursor() as cursor:
        with transaction.atomic():
            cursor.execute("REFRESH MATERIALIZED VIEW geneinfo_geneidtoinheritance")


class MgiHomMouseHumanSequence(models.Model):
    """Model for mouse to human mapping. One record (row) can be either mouse or human.
    Mapping of a gene is accomplished via ``HomoloGene ID`` column, which contains the same ID in the homologous entries
    of mouse and human, respectively.
    """

    #: HomoloGene ID
    homologene_id = models.IntegerField(null=False)
    #: Common Organism Name ('human' or 'mouse, laboratory')
    common_organism_name = models.CharField(max_length=32, null=False)
    #: NCBI Taxon ID (9606 for human, 10090 for mouse)
    ncbi_taxon_id = models.CharField(max_length=16, null=False)
    #: Gene Symbol (seems to differ in capitalization between mouse gene and human homolog)
    symbol = models.CharField(max_length=32, null=False)
    #: Entrez Gene ID (differs between mouse gene and human homolog)
    entrez_id = models.CharField(max_length=16, null=False)
    #: Mouse MGI ID (only set in mouse record)
    mgi_id = models.CharField(max_length=16, null=True)
    #: HGNC ID (only set in human record)
    hgnc_id = models.CharField(max_length=16, null=True)
    #: OMIM Gene ID (only set in human record)
    omim_id = models.CharField(max_length=32, null=True)
    #: Genetic Location
    location = models.CharField(max_length=64, null=True)
    #: Genomic Coordinates
    coordinates = models.CharField(max_length=128, null=True)
    #: Nucleotide RefSeq IDs
    nucleotide_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: Protein RefSeq IDs
    protein_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: SwissProt IDs
    swissprot_ids = ArrayField(models.CharField(max_length=16))

    #: Allow bulk import info database.
    objects = CopyManager()


class MgiMapping(models.Model):
    """Materialized view model for easy mapping of MGI ids to various human gene attributes."""

    #: HGNC ID (only set in human record)
    hgnc_id = models.CharField(max_length=16, null=True)
    #: OMIM Gene ID (only set in human record)
    omim_id = models.CharField(max_length=32, null=True)
    #: coordinates Human
    human_coordinates = models.CharField(max_length=128, null=True)
    #: entrez_id Human
    human_entrez_id = models.CharField(max_length=16, null=True)
    #: Nucleotide RefSeq IDs Human
    human_nucleotide_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: Protein RefSeq IDs Human
    human_protein_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: SwissProt IDs Human
    human_swissprot_ids = ArrayField(models.CharField(max_length=16))
    #: MGI ID
    mgi_id = models.CharField(max_length=16, null=True)
    #: coordinates Mouse
    mouse_coordinates = models.CharField(max_length=128, null=True)
    #: entrez_id Mouse
    mouse_entrez_id = models.CharField(max_length=16, null=True)
    #: Nucleotide RefSeq IDs Mouse
    mouse_nucleotide_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: Protein RefSeq IDs Mouse
    mouse_protein_refseq_ids = ArrayField(models.CharField(max_length=16))
    #: SwissProt IDs Mouse
    mouse_swissprot_ids = ArrayField(models.CharField(max_length=16))

    class Meta:
        managed = settings.IS_TESTING
        db_table = "geneinfo_mgimapping"


class RefseqToGeneSymbol(models.Model):
    """Model to map entrez id to gene symbol."""

    #: Entrez ID
    entrez_id = models.CharField(max_length=16, null=True)
    #: Gene symbol
    gene_symbol = models.CharField(max_length=32)

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["entrez_id"])]


class EnsemblToGeneSymbol(models.Model):
    """Model to map ensembl gene id to gene symbol."""

    #: Ensembl Gene ID
    ensembl_gene_id = models.CharField(max_length=32, null=True)
    #: Gene symbol
    gene_symbol = models.CharField(max_length=32)

    #: Allow bulk import info database.
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["ensembl_gene_id"])]


def refresh_geneinfo_mgimapping():
    """Refresh the ``SmallVariantSummary`` materialized view."""
    with connection.cursor() as cursor:
        with transaction.atomic():
            cursor.execute("REFRESH MATERIALIZED VIEW geneinfo_mgimapping")
