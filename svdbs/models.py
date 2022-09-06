"""Models for ``svdb``, storage of structural variant databases.
"""
from postgres_copy import CopyManager

__author__ = "Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>"

from django.contrib.postgres.fields import ArrayField
from django.db import models

#: "gain" in DGV
DGV_SV_SUB_TYPE_GAIN = "gain"
#: "loss" in DGV
DGV_SV_SUB_TYPE_LOSS = "loss"
#: "loss" in DGV
DGV_SV_SUB_TYPE_GAIN_LOSS = "gain+loss"
#: "insertion" in DGV
DGV_SV_SUB_TYPE_INS = "insertion"
#: "novel sequence insertion" in DGV
DGV_SV_SUB_TYPE_NOVEL_INS = "novel sequence insertion"
#: "deletion" in DGV
DGV_SV_SUB_TYPE_DELETION = "deletion"
#: "complex" in DGV
DGV_SV_SUB_TYPE_COMPLEX = "complex"
#: "sequence alteration" in DGV
DGV_SV_SUB_TYPE_SEQ_ALTERATION = "sequence alteration"
#: Choices for ``DgvGoldStandard.cnv_type``.
DGV_SV_SUB_TYPE_CHOICES = (
    (DGV_SV_SUB_TYPE_GAIN, "gain"),
    (DGV_SV_SUB_TYPE_LOSS, "loss"),
    (DGV_SV_SUB_TYPE_GAIN_LOSS, "gain+loss"),
    (DGV_SV_SUB_TYPE_INS, "insertion"),
    (DGV_SV_SUB_TYPE_NOVEL_INS, "novel sequence insertion"),
    (DGV_SV_SUB_TYPE_DELETION, "deletion"),
    (DGV_SV_SUB_TYPE_COMPLEX, "complex"),
    (DGV_SV_SUB_TYPE_SEQ_ALTERATION, "sequence alteration"),
)


class DgvGoldStandardSvs(models.Model):
    """SVs from DGV (database of genomic variation) GS (gold standard) build.

    This model was designed for record from the file ``DGV.GS.March2016.50percent.GainLossSep.Final.hg19.gff3``.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - outer start position
    start_outer = models.IntegerField()
    #: Variant coordinates - inner start position
    start_inner = models.IntegerField()
    #: Variant coordinates - inner end position
    end_inner = models.IntegerField()
    #: Variant coordinates - outer end position
    end_outer = models.IntegerField()

    #: Interval bin from ``start_outer`` to ``end_outer``, automatically set
    #: in ``save()``.
    bin = models.IntegerField(default=0)

    #: Identifier of the variant
    accession = models.CharField(max_length=32)
    #: SV type (always ``"CNV"``)
    sv_type = models.CharField(max_length=8)
    #: SV sub type
    sv_sub_type = models.CharField(max_length=32, choices=DGV_SV_SUB_TYPE_CHOICES)

    #: Number of studies
    num_studies = models.IntegerField()
    #: Studies
    studies = ArrayField(models.CharField(max_length=128))
    #: Number of platforms
    num_platforms = models.IntegerField()
    #: Platforms
    platforms = ArrayField(models.CharField(max_length=128))
    #: Number of algorithms
    num_algorithms = models.IntegerField()
    #: Algorithms
    algorithms = ArrayField(models.CharField(max_length=128))
    #: Number of variants
    num_variants = models.IntegerField()
    #: Number of carrying samples
    num_carriers = models.IntegerField()
    #: Number of unique samples
    num_unique_samples = models.IntegerField()

    #: Number of carriers from African population.
    num_carriers_african = models.IntegerField()
    #: Number of carriers from Asian population.
    num_carriers_asian = models.IntegerField()
    #: Number of carriers from European population.
    num_carriers_european = models.IntegerField()
    #: Number of carriers from Mexican population.
    num_carriers_mexican = models.IntegerField()
    #: Number of carriers from MiddleEast population.
    num_carriers_middle_east = models.IntegerField()
    #: Number of carriers from NativeAmerican population.
    num_carriers_native_american = models.IntegerField()
    #: Number of carriers from NorthAmerican population.
    num_carriers_north_american = models.IntegerField()
    #: Number of carriers from Oceania population.
    num_carriers_oceania = models.IntegerField()
    #: Number of carriers from SouthAmerican population.
    num_carriers_south_american = models.IntegerField()
    #: Number of carriers from Admixed population.
    num_carriers_admixed = models.IntegerField()
    #: Number of carriers from Unknown population.
    num_carriers_unknown = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]


class DgvSvs(models.Model):
    """SVs from DGV (database of genomic variation).

    This model was designed for record from the files:

    - ``GRCh37_hg19_variants_2016-05-15.txt``
    - ``GRCh38_hg38_variants_2016-08-31.txt``
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()

    #: Interval bin from ``start`` to ``end``, automatically set in ``save()``.
    bin = models.IntegerField(default=0)

    #: Identifier of the variant
    accession = models.CharField(max_length=32)
    #: SV type (always ``"CNV"``)
    sv_type = models.CharField(max_length=32)
    #: SV sub type
    sv_sub_type = models.CharField(max_length=32, choices=DGV_SV_SUB_TYPE_CHOICES)

    #: Study name
    study = models.CharField(max_length=128)
    #: Platform
    platform = ArrayField(models.CharField(max_length=128))

    #: Sample size
    num_samples = models.IntegerField()
    #: Observed gains
    observed_gains = models.IntegerField()
    #: Observed losses
    observed_losses = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]


#: "deletion" in ExAC
EXAC_SV_TYPE_DELETION = "deletion"
#: "duplication" in ExAC
EXAC_SV_TYPE_DUPLICATION = "duplication"
#: ExAC choices for variant types
EXAC_SV_TYPE_CHOICES = (
    (EXAC_SV_TYPE_DELETION, "deletion"),
    (EXAC_SV_TYPE_DUPLICATION, "duplication"),
)

#: Populations in ExAC
EXAC_POP_CHOICES = (
    ("AFR", "African"),
    ("AMR", "American"),
    ("EAS", "East Asian"),
    ("FIN", "Finnish"),
    ("NFE", "Non-Finish European"),
    ("OTH", "Other"),
    ("SAS", "South Asian"),
)


class ExacCnv(models.Model):
    """CNVs from the ExAC project.

    Note that this table stores individual CNVs that are mapped to the population that the carriers are samples
    from.  While the data is stored as BED files in the ExAC downloads, the coordinates used in the database are
    one-based.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()

    #: Interval bin from ``start`` to ``end``, automatically set in ``save()``.
    bin = models.IntegerField(default=0)

    #: SV type (always ``"CNV"``)
    sv_type = models.CharField(max_length=32)
    #: Population of individual
    population = models.CharField(max_length=3, choices=EXAC_POP_CHOICES)
    #: Phred score of the variant
    phred_score = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]


#: Mobile element insertion of ALU
G1K_SVTYPE_INS_ALU = "ALU"
#: Mobile element insertion of LINE1
G1K_SVTYPE_INS_LINE1 = "LINE1"
#: Mobile element insertion of SVA
G1K_SVTYPE_INS_SVA = "SVA"
#: Nuclear mitochondrial insertion
G1K_SVTYPE_INS_MT = "INS"
#: Bi-allelic deletion
G1K_SVTYPE_DEL = "DEL"
#: Bi-allelic duplication
G1K_SVTYPE_DUP = "DUP"
#: Bi-allelic incversion
G1K_SVTYPE_INV = "INV"
#: Multi-allelic copy-number variant
G1K_SVTYPE_CNV = "CNV"
#: Mobile element deletion of ALU
G1K_SVTYPE_DEL_ALU = "DEL_ALU"
#: Mobile element deletion of LINE1
G1K_SVTYPE_DEL_LINE1 = "DEL_LINE1"
#: Mobile element deletion of SVA
G1K_SVTYPE_DEL_SVA = "DEL_SVA"

#: Choices for Thousand Genomes sv_type
G1K_SVTYPE_CHOICES = (
    (G1K_SVTYPE_CNV, G1K_SVTYPE_CNV),
    (G1K_SVTYPE_DEL_ALU, G1K_SVTYPE_DEL_ALU),
    (G1K_SVTYPE_DEL, G1K_SVTYPE_DEL),
    (G1K_SVTYPE_DEL_LINE1, G1K_SVTYPE_DEL_LINE1),
    (G1K_SVTYPE_DEL_SVA, G1K_SVTYPE_DEL_SVA),
    (G1K_SVTYPE_DUP, G1K_SVTYPE_DUP),
    (G1K_SVTYPE_INS_ALU, G1K_SVTYPE_INS_ALU),
    (G1K_SVTYPE_INS_LINE1, G1K_SVTYPE_INS_LINE1),
    (G1K_SVTYPE_INS_MT, G1K_SVTYPE_INS_MT),
    (G1K_SVTYPE_INS_SVA, G1K_SVTYPE_INS_SVA),
    (G1K_SVTYPE_INV, G1K_SVTYPE_INV),
)


#: Alu element insertion call set from the University of Maryland (MELT algorithm)
G1K_CALLSET_ALU_UMARY = "ALU_umary"
#: Line1 transposable element insertion from the University of Maryland (MELT algorithm)
G1K_CALLSET_L1_UMARY = "L1_umary"
#: SVA element insertion from the University of Maryland (MELT algorithm)
G1K_CALLSET_SVA_UMARY = "SVA_umary"
#: Nuclear mitochondrial insertion from the University of Michigan (NumtS algorithm)
G1K_CALLSET_NUMT_UMICH = "NUMT_umich"
#: Union deletions genotypted by GenomeSTRiP and variant sites identified by GenomeSTRiP, Breakdancer,
#: CNVnator, Delly and Variation Hunter.
G1K_CALLSET_DEL_UNION = "DEL_union"
#: Small deletions (<1kbp) from Washington University (Pindel algorithm)
G1K_CALLSET_DEL_PINDEL = "DEL_pindel"
#: Bi-allelic simple inversions from EMBL (Delly algorithm)
G1K_CALLSET_INV_DELLY = "INV_delly"
#: Bi-allelic complex inversions from EMBL (Delly algorithm)
G1K_CALLSET_CINV_DELLY = "CINV_delly"
#: Bi-allelic duplications and copy-number variants from Broad Institute (GenomeSTRiP algorithm)
G1K_CALLSET_DUP_GS = "DUP_gs"
#: Bi-allelic tandem duplications from EMBL (Delly algorithm)
G1K_CALLSET_DUP_DELLY = "DUP_delly"
#: Bi-allelic deletions, duplications and copy-number variants from University of Washington (SSF algorithm)
G1K_CALLSET_DUP_UWASH = "DUP_uwash"

#: Choices for Thousand Genomes call set
G1K_CALLSET_CHOICES = (
    (G1K_CALLSET_ALU_UMARY, G1K_CALLSET_ALU_UMARY),
    (G1K_CALLSET_CINV_DELLY, G1K_CALLSET_CINV_DELLY),
    (G1K_CALLSET_DEL_PINDEL, G1K_CALLSET_DEL_PINDEL),
    (G1K_CALLSET_DEL_UNION, G1K_CALLSET_DEL_UNION),
    (G1K_CALLSET_DUP_DELLY, G1K_CALLSET_DUP_DELLY),
    (G1K_CALLSET_DUP_GS, G1K_CALLSET_DUP_GS),
    (G1K_CALLSET_DUP_UWASH, G1K_CALLSET_DUP_UWASH),
    (G1K_CALLSET_INV_DELLY, G1K_CALLSET_INV_DELLY),
    (G1K_CALLSET_L1_UMARY, G1K_CALLSET_L1_UMARY),
    (G1K_CALLSET_NUMT_UMICH, G1K_CALLSET_NUMT_UMICH),
    (G1K_CALLSET_SVA_UMARY, G1K_CALLSET_SVA_UMARY),
)


class ThousandGenomesSv(models.Model):
    """Thousand Genomes Project Phase 3 structural variants.

    All coordinates are one-based.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()

    #: Interval bin from ``start`` to ``end``, automatically set in ``save()``.
    bin = models.IntegerField(default=0)

    #: Left boundary of CI of ``start``.
    start_ci_left = models.IntegerField()
    #: Right boundary of CI of ``start``.
    start_ci_right = models.IntegerField()
    #: Left boundary of CI of ``end``.
    end_ci_left = models.IntegerField()
    #: Right boundary of CI of ``end``.
    end_ci_right = models.IntegerField()

    #: Type of structural variant
    sv_type = models.CharField(max_length=32, choices=G1K_SVTYPE_CHOICES)
    #: Call set from which the variant originates
    source_call_set = models.CharField(max_length=32, choices=G1K_CALLSET_CHOICES)

    #: Additional information regarding mobile elements, if any
    mobile_element_info = ArrayField(
        models.CharField(max_length=32, null=True, blank=True), null=True, blank=True
    )

    #: Number of samples with data
    num_samples = models.IntegerField()
    #: Number of alleles
    num_alleles = models.IntegerField()
    #: Number of alleles carrying variant
    num_var_alleles = models.IntegerField()

    #: Number of alleles in AFR population.
    num_alleles_afr = models.IntegerField()
    #: Number of variant alleles in AFR population.
    num_var_alleles_afr = models.IntegerField()
    #: Number of alleles in AMR population.
    num_alleles_amr = models.IntegerField()
    #: Number of variant alleles in AMR population.
    num_var_alleles_amr = models.IntegerField()
    #: Number of alleles in EAS population.
    num_alleles_eas = models.IntegerField()
    #: Number of variant alleles in EAS population.
    num_var_alleles_eas = models.IntegerField()
    #: Number of alleles in EUR population.
    num_alleles_eur = models.IntegerField()
    #: Number of variant alleles in EUR population.
    num_var_alleles_eur = models.IntegerField()
    #: Number of alleles in SAS population.
    num_alleles_sas = models.IntegerField()
    #: Number of variant alleles in SAS population.
    num_var_alleles_sas = models.IntegerField()

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]


class DbVarSv(models.Model):
    """dbVar structural variants.

    All coordinates are one-based.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()

    #: Interval bin from ``start`` to ``end``, automatically set ``save()``.
    bin = models.IntegerField(default=0)

    #: Number of observations
    num_carriers = models.IntegerField()
    #: Variant type TODO this should be an array of charfields.
    sv_type = models.CharField(max_length=1024)
    #: Detection method TODO this should be an array of charfields.
    method = models.CharField(max_length=1024)
    #: Detection analysis TODO this should be an array of charfields.
    analysis = models.CharField(max_length=1024)
    #: Detection platform TODO this should be an array of charfields.
    platform = models.CharField(max_length=1024)
    #: Study TODO this should be an array of charfields.
    study = models.CharField(max_length=1024)
    # Variant identifiers are not imported
    #: Clinical assertion
    clinical_assertions = ArrayField(models.CharField(max_length=1024))
    #: Clinvar accessions
    clinvar_accessions = ArrayField(models.CharField(max_length=1024))
    #: Bin size
    bin_size = models.CharField(max_length=32)
    #: Minimal insertion length
    min_ins_length = models.IntegerField(null=True, blank=True)
    #: Maximal insertion length
    max_ins_length = models.IntegerField(null=True, blank=True)

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]


class GnomAdSv(models.Model):
    """gnomAD structural variants.

    Coordinates are one-based.
    """

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - start position (1-based)
    start = models.IntegerField()
    #: Variant coordinates - end position (1-based)
    end = models.IntegerField()

    #: Interval bin from ``start`` to ``end``, automatically set ``save()``.
    bin = models.IntegerField(default=0)

    #: REF allele
    ref = models.CharField(max_length=64, default="N")
    #: ALT alleles
    alt = ArrayField(models.CharField(max_length=64), default=list)

    #: SV name in gnomAD SV.
    name = ArrayField(models.CharField(max_length=64))
    #: Type of the SV.
    svtype = models.CharField(max_length=64)
    #: Length of the SV
    svlen = models.IntegerField()
    #: Filter value.
    filter = ArrayField(models.CharField(max_length=64))
    #: Evidence for SV
    evidence = ArrayField(models.CharField(max_length=8))
    #: Algorithms used for SV
    algorithms = ArrayField(models.CharField(max_length=32))
    #: Second chromosome for non-linear events
    chr2 = models.CharField(max_length=32, null=True, blank=True)
    #: Complex type
    cpx_type = models.CharField(max_length=32, null=True, blank=True)
    #: Complex intervals
    cpx_intervals = ArrayField(models.CharField(max_length=64), null=True, blank=True)
    #: Source
    source = models.CharField(max_length=64, null=True, blank=True)
    #: Strand
    strands = models.CharField(max_length=2, null=True, blank=True)
    #: Type of unresolved event
    unresolved_type = models.CharField(max_length=64, null=True, blank=True)
    #: Whether deleted in samples with PCR enrichment
    pcrplus_depleted = models.BooleanField()
    #: Overdispersion
    pesr_gt_overdispersion = models.BooleanField()
    #: Protein coding LOF genes
    protein_coding_lof = ArrayField(models.CharField(max_length=64))
    #: Protein coding LOF duplication genes
    protein_coding_dup_lof = ArrayField(models.CharField(max_length=64))
    #: Protein coding copy gain
    protein_coding_copy_gain = ArrayField(models.CharField(max_length=64))
    #: Protein coding partiaul duplication
    protein_coding_dup_partial = ArrayField(models.CharField(max_length=64))
    #: Protein coding exon overlap
    protein_coding_msv_exon_ovr = ArrayField(models.CharField(max_length=64))
    #: Protein coding intronic variant
    protein_coding_intronic = ArrayField(models.CharField(max_length=64))
    #: Protein coding in inversion
    protein_coding_inv_span = ArrayField(models.CharField(max_length=64))
    #: Protein coding with UTR affected
    protein_coding_utr = ArrayField(models.CharField(max_length=64))
    #: Protein coding gene with nearest TSS
    protein_coding_nearest_tss = ArrayField(models.CharField(max_length=64))
    #: Protein coding gene intergenic
    protein_coding_intergenic = models.BooleanField()
    #: Protein coding gene promoter
    protein_coding_promoter = ArrayField(models.CharField(max_length=64))
    #: Allele number
    an = models.IntegerField()
    #: Observed non-reference alleles
    ac = ArrayField(models.IntegerField())
    #: Allele frequencies
    af = ArrayField(models.FloatField())
    #: Number of biallelic genotypes
    n_bi_genos = models.IntegerField()
    #: Number of hom. ref. genotypes
    n_homref = models.IntegerField()
    #: Number of het. genotypes
    n_het = models.IntegerField()
    #: Numbe of hom. alt. genotypes
    n_homalt = models.IntegerField()
    #: Frequency of hom. ref.
    freq_homref = models.FloatField()
    #: Frequency of het.
    freq_het = models.FloatField()
    #: Frequency of hom. alt.
    freq_homalt = models.FloatField()
    #: AF in POPMAX
    popmax_af = models.FloatField()
    #: Observed total alleles in AFR
    afr_an = models.IntegerField()
    #: Observed alternative alleles in AFR
    afr_ac = ArrayField(models.IntegerField())
    #: Alternate allele frequency in AFR
    afr_af = ArrayField(models.FloatField())
    #: Total number of biallelic genomes in AFR
    afr_n_bi_genos = models.IntegerField()
    #: Number of hom. ref. genomes in AFR
    afr_n_homref = models.IntegerField()
    #: Number of het. genomes in AFR
    afr_n_het = models.IntegerField()
    #: Number of hom. alt. genomes in AFR
    afr_n_homalt = models.IntegerField()
    #: Frequency of hom. ref. in AFR
    afr_freq_homref = models.FloatField()
    #: Frequency of het. in AFR
    afr_freq_het = models.FloatField()
    #: Frequency of hom. alt. in AFR
    afr_freq_homalt = models.FloatField()
    #: Observed total alleles in AMR
    amr_an = models.IntegerField()
    #: Alternate allele frequency in AMR
    amr_ac = ArrayField(models.IntegerField())
    #: Alternate allele frequency in AMR
    amr_af = ArrayField(models.FloatField())
    #: Total number of biallelic genomes in AMR
    amr_n_bi_genos = models.IntegerField()
    #: Frequency of hom. ref. in AMR
    amr_n_homref = models.IntegerField()
    #: Number of het. genomes in AMR
    amr_n_het = models.IntegerField()
    #: Number of hom. alt. genomes in AMR
    amr_n_homalt = models.IntegerField()
    #: Frequency of hom. ref. in AMR
    amr_freq_homref = models.FloatField()
    #: Frequency of het. in AMR
    amr_freq_het = models.FloatField()
    #: Frequency of hom. alt. in AMR
    amr_freq_homalt = models.FloatField()
    #: Observed total alleles in EAS
    eas_an = models.IntegerField()
    #: Alternate allele frequency in EAS
    eas_ac = ArrayField(models.IntegerField())
    #: Alternate allele frequency in EAS
    eas_af = ArrayField(models.FloatField())
    #: Total number of biallelic genomes in EAS
    eas_n_bi_genos = models.IntegerField()
    #: Frequency of hom. ref. in EAS
    eas_n_homref = models.IntegerField()
    #: Number of het. genomes in EAS
    eas_n_het = models.IntegerField()
    #: Number of hom. alt. genomes in EAS
    eas_n_homalt = models.IntegerField()
    #: Frequency of hom. ref. in EAS
    eas_freq_homref = models.FloatField()
    #: Frequency of het. in EAS
    eas_freq_het = models.FloatField()
    #: Frequency of hom. alt. in EAS
    eas_freq_homalt = models.FloatField()
    #: Observed total alleles in EUR
    eur_an = models.IntegerField()
    #: Alternate allele frequency in EUR
    eur_ac = ArrayField(models.IntegerField())
    #: Alternate allele frequency in EUR
    eur_af = ArrayField(models.FloatField())
    #: Total number of biallelic genomes in EUR
    eur_n_bi_genos = models.IntegerField()
    #: Frequency of hom. ref. in EUR
    eur_n_homref = models.IntegerField()
    #: Number of het. genomes in EUR
    eur_n_het = models.IntegerField()
    #: Number of hom. alt. genomes in EUR
    eur_n_homalt = models.IntegerField()
    #: Frequency of hom. ref. in EUR
    eur_freq_homref = models.FloatField()
    #: Frequency of het. in EUR
    eur_freq_het = models.FloatField()
    #: Frequency of hom. alt. in EUR
    eur_freq_homalt = models.FloatField()
    #: Observed total alleles in OTH
    oth_an = models.IntegerField()
    #: Alternate allele frequency in OTH
    oth_ac = ArrayField(models.IntegerField())
    #: Alternate allele frequency in OTH
    oth_af = ArrayField(models.FloatField())
    #: Total number of biallelic genomes in OTH
    oth_n_bi_genos = models.IntegerField()
    #: Frequency of hom. ref. in OTH
    oth_n_homref = models.IntegerField()
    #: Number of het. genomes in OTH
    oth_n_het = models.IntegerField()
    #: Number of hom. alt. genomes in OTH
    oth_n_homalt = models.IntegerField()
    #: Frequency of hom. ref. in OTH
    oth_freq_homref = models.FloatField()
    #: Frequency of het. in OTH
    oth_freq_het = models.FloatField()
    #: Frequency of hom. alt. in OTH
    oth_freq_homalt = models.FloatField()

    #: Allow bulk import
    objects = CopyManager()

    class Meta:
        indexes = [models.Index(fields=["release", "chromosome", "bin"])]
