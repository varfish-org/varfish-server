from enum import Enum
import typing
import uuid as uuid_object

import django
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django_pydantic_field import SchemaField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import pydantic

from cases_analysis.models import CaseAnalysisSession
from variants.models.case import Case
from variants.models.projectroles import Project

#: User model.
User = get_user_model()


class FrequencySettingsBase(models.Model):
    """Abstract model for storing frequency-related settings."""

    gnomad_exomes_enabled = models.BooleanField(default=False, null=False, blank=False)
    gnomad_exomes_frequency = models.FloatField(null=True, blank=True)
    gnomad_exomes_homozygous = models.IntegerField(null=True, blank=True)
    gnomad_exomes_heterozygous = models.IntegerField(null=True, blank=True)
    gnomad_exomes_hemizygous = models.IntegerField(null=True, blank=True)

    gnomad_genomes_enabled = models.BooleanField(default=False, null=False, blank=False)
    gnomad_genomes_frequency = models.FloatField(null=True, blank=True)
    gnomad_genomes_homozygous = models.IntegerField(null=True, blank=True)
    gnomad_genomes_heterozygous = models.IntegerField(null=True, blank=True)
    gnomad_genomes_hemizygous = models.IntegerField(null=True, blank=True)

    helixmtdb_enabled = models.BooleanField(default=False, null=False, blank=False)
    helixmtdb_heteroplasmic = models.IntegerField(null=True, blank=True)
    helixmtdb_homoplasmic = models.IntegerField(null=True, blank=True)
    helixmtdb_frequency = models.FloatField(null=True, blank=True)

    inhouse_enabled = models.BooleanField(default=False, null=False, blank=False)
    inhouse_carriers = models.IntegerField(null=True, blank=True)
    inhouse_homozygous = models.IntegerField(null=True, blank=True)
    inhouse_heterozygous = models.IntegerField(null=True, blank=True)
    inhouse_hemizygous = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class VariantTypeChoice(str, Enum):
    """The type of a variant."""

    #: Single nucleotide variant.
    SNV = "snv"
    #: Insertion/deletion.
    INDEL = "indel"
    #: Multi-nucleotide variant.
    MNV = "mnv"
    #: Complex substitution.
    COMPLEX_SUBSTITUTION = "complex_substitution"


class TranscriptTypeChoice(str, Enum):
    """The type of a transcript."""

    #: Coding transcript.
    CODING = "coding"
    #: Non-coding transcript.
    NON_CODING = "non_coding"


class VariantConsequenceChoice(str, Enum):
    """The variant consequence."""

    # high impact

    # skipped chromosome_number_variation
    # skipped exon_loss_variant
    #: Frameshift variant
    FRAMESHIFT_VARIANT = "frameshift_variant"
    #: Rare amino acid variant
    RARE_AMINO_ACID_VARIANT = "rare_amino_acid_variant"
    #: Splice acceptor variant
    SPLICE_ACCEPTOR_VARIANT = "splice_acceptor_variant"
    #: Splice donor variant
    SPLICE_DONOR_VARIANT = "splice_donor_variant"
    #: Start lost
    START_LOST = "start_lost"
    #: Stop gained
    STOP_GAINED = "stop_gained"
    #: Stop lost
    STOP_LOST = "stop_lost"
    # skipped transcript_ablation

    # moderate impact

    # 3' UTR truncation
    THREE_PRIME_UTR_TRUNCATION = "3_prime_UTR_truncation"
    # 5' UTR truncation
    FIVE_PRIME_UTR_TRUNCATION = "5_prime_UTR_truncation"
    #: Conservative inframe deletion
    CONSERVATIVE_INFRAME_DELETION = "conservative_inframe_deletion"
    #: Conservative inframe insertion
    CONSERVATIVE_INFRAME_INSERTION = "conservative_inframe_insertion"
    #: Disruptive inframe deletion
    DISRUPTIVE_INFRAME_DELETION = "disruptive_inframe_deletion"
    #: Disruptive inframe insertion
    DISRUPTIVE_INFRAME_INSERTION = "disruptive_inframe_insertion"
    #: Missense variant
    MISSENSE_VARIANT = "missense_variant"
    #: skipped regulatory_region_ablation
    #: Splice region variant
    SPLICE_REGION_VARIANT = "splice_region_variant"
    # skipped TFBS_ablation

    # low impact

    # skipped 5_prime_UTR_premature_start_codon_gain_variant
    #: Initiator codon variant
    INITIATOR_CODON_VARIANT = "initiator_codon_variant"
    #: Start retained
    START_RETAINED = "start_retained"
    #: Stop retained variant
    STOP_RETAINED_VARIANT = "stop_retained_variant"
    #: Synonymous variant
    SYNONYMOUS_VARIANT = "synonymous_variant"

    # modifier

    # skipped 3_prime_UTR_variant
    # skipped 5_prime_UTR_variant
    # skipped coding_sequence_variant
    # skipped conserved_intergenic_variant
    # skipped conserved_intron_variant
    #: Downstream gene variant
    DOWNSTREAM_GENE_VARIANT = "downstream_gene_variant"
    # skipped exon_variant
    # skipped feature_elongation
    # skipped feature_truncation
    # skipped gene_variant
    # skipped intergenic_variant
    #: Intron variant.
    INTRON_VARIANT = "intron_variant"
    # skipped mature_miRNA_variant
    # skipped miRNA
    # skipped NMD_transcript_variant
    #: Non-coding transcript exon variant
    NON_CODING_TRANSCRIPT_EXON_VARIANT = "non_coding_transcript_exon_variant"
    #: Non-coding transcript intron variant
    NON_CODING_TRANSCRIPT_INTRON_VARIANT = "non_coding_transcript_intron_variant"
    #: 5' UTR variant
    FIVE_PRIME_UTR_VARIANT = "5_prime_UTR_variant"
    #: Coding sequence variant
    CODING_SEQUENCE_VARIANT = "coding_sequence_variant"
    # skipped regulatory_region_amplification
    # skipped regulatory_region_variant
    # skipped TF_binding_site_variant
    # skipped TFBS_amplification
    # skipped transcript_amplification
    # skipped transcript_variant
    #: Upstream gene variant
    UPSTREAM_GENE_VARIANT = "upstream_gene_variant"

    #: EXTRA, not directly written by Mehari: 3' UTR variant + exon variant
    THREE_PRIME_UTR_VARIANT_EXON_VARIANT = "3_prime_UTR_variant-exon_variant"
    #: EXTRA, not directly written by Mehari: 5' UTR variant + exon variant
    FIVE_PRIME_UTR_VARIANT_EXON_VARIANT = "5_prime_UTR_variant-exon_variant"
    #: EXTRA, not directly written by Mehari: 3' UTR variant + intron_variant
    THREE_PRIME_UTR_VARIANT_INTRON_VARIANT = "3_prime_UTR_variant-intron_variant"
    #: EXTRA, not directly written by Mehari: 5' UTR variant + intron_variant
    FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT = "5_prime_UTR_variant-intron_variant"


class ConsequenceSettingsBase(models.Model):
    """Abstract model for storing consequence-related settings."""

    #: The variant types.
    variant_types = SchemaField(schema=list[VariantTypeChoice], default=list)
    #: The transcript types.
    transcript_types = SchemaField(schema=list[TranscriptTypeChoice], default=list)
    #: The variant consequences.
    variant_consequences = SchemaField(schema=list[VariantConsequenceChoice], default=list)
    #: Maximal distance to next exon.
    max_distance_to_exon = models.IntegerField(null=True, blank=True)

    class Meta:
        abstract = True


class Gene(pydantic.BaseModel):
    """Representation of a gene to query for."""

    #: The HGNC identifier used as stable ID.
    hgnc_id: str
    #: The HGNC gene symbol (informative for the user).
    symbol: str
    #: Optionally, the gene name (informative for the user).
    name: typing.Optional[str] = None
    #: Optionally, the NCBI Entrez GeneID (informative for the user).
    entrez_id: typing.Optional[int] = None
    #: Optionally, the Ensembl gene ID (informative for the user).
    ensembl_id: typing.Optional[str] = None


class GenePanelSource(str, Enum):
    """The source of a gene panel."""

    #: PanelApp.
    PANELAPP = "panelapp"
    #: Internal to varfish intance.
    INTERNAL = "internal"


class GenePanel(pydantic.BaseModel):
    """Representation of a gene panel to use in the query."""

    #: The source of the gene panel.
    source: GenePanelSource
    #: The panel ID (number for PanelApp, UUID for internal).
    panel_id: str
    #: The panel name.
    name: str
    #: The panel version.
    version: str


class OneBasedRange(pydantic.BaseModel):
    """Representation of a 1-based range."""

    #: The 1-based start position.
    start: int
    #: The 1-based end position.
    end: int


class GenomeRegion(pydantic.BaseModel):
    """Representation of a genomic region to query for."""

    #: The chromosome name.
    chromosome: str
    #: The optional range.
    range: typing.Optional[OneBasedRange] = None


class LocusSettingsBase(models.Model):
    """Abstract model for storing locus-related settings."""

    #: Optional list of gene symbols to filter for.
    genes = SchemaField(schema=list[Gene], default=list)
    #: Optional ilst of gene panels to use in the query.
    gene_panels = SchemaField(schema=list[GenePanel], default=list)
    #: Optional list of genomic regions to filter for.
    genome_regions = SchemaField(schema=list[GenomeRegion], default=list)

    class Meta:
        abstract = True


class Term(pydantic.BaseModel):
    """Representation of a condition (phenotype / disease) term."""

    #: CURIE-style identifier, e.g., with prefixes "HP:0000001", "OMIM:123456", "ORPHA:123456
    term_id: str
    #: An optional label for the term.
    label: typing.Optional[str]


class TermPresence(pydantic.BaseModel):
    """Representation of a term with optional presence (default is not excluded)."""

    #: The condition term.
    term: Term
    #: Whether the term is excluded.
    excluded: typing.Optional[bool] = None


class PhenotypePrioSettingsBase(models.Model):
    """Abstract model for storing phenotype priorization--related settings."""

    #: Whether to enable phenotype-based priorization.
    phenotype_prio_enabled = models.BooleanField(default=False, null=False, blank=False)
    #: The algorithm to use for priorization.
    phenotype_prio_algorithm = models.CharField(max_length=128, null=True, blank=True)
    #: The phenotype terms to use.
    terms = SchemaField(schema=list[TermPresence], default=list)

    class Meta:
        abstract = True


class VariantPrioService(pydantic.BaseModel):
    """Representation of a variant pathogenicity service."""

    #: The name of the service.
    name: str
    #: The version of the service.
    version: str


class VariantPrioSettingsBase(models.Model):
    """Abstract model for storing variant priorization--related settings.

    Note that this refers to external APIs that provide variant pathogenicity scores
    that are not annotated by the worker already (i.e., not precomputed).
    """

    #: Whether to enable variant-based priorization.
    variant_prio_enabled = models.BooleanField(default=False, null=False, blank=False)
    #: The enabled services.
    services = SchemaField(schema=list[VariantPrioService], default=list)

    class Meta:
        abstract = True


class ClinvarGermlineAggregateDescription(str, Enum):
    """The aggregate description for germline variants in ClinVar."""

    #: Pathogenic
    PATHOGENIC = "pathogenic"
    #: Likely pathogenic
    LIKELY_PATHOGENIC = "likely_pathogenic"
    #: Uncertain significance
    UNCERTAIN_SIGNIFICANCE = "uncertain_significance"
    #: Likely benign
    LIKELY_BENIGN = "likely_benign"
    #: Benign
    BENIGN = "benign"


class ClinvarSettingsBase(models.Model):
    """Abstract model for storing clinvar-related settings."""

    #: Whether to require presence in ClinVar priorization.
    clinvar_presence_required = models.BooleanField(default=False, null=False, blank=False)
    #: The aggregate description for germline variants.
    clinvar_germline_aggregate_description = SchemaField(
        schema=list[ClinvarGermlineAggregateDescription], default=list
    )
    #: Whether to allow for conflicting interpretations of pathogenicity.
    allow_conflicting_interpretations = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        abstract = True


class ColumnConfig(pydantic.BaseModel):
    """Configuration for a single column in the result table."""

    #: The column name.
    name: str
    #: The column label.
    label: str
    #: The column description.
    description: typing.Optional[str] = None
    #: The column width.
    width: int
    #: The column visibility.
    visible: bool


class ColumnsSettingsBase(models.Model):
    """Abstract model for storing column-related settings."""

    #: List of columns with their widths.
    column_settings = SchemaField(schema=list[ColumnConfig], default=list)

    class Meta:
        abstract = True


class BaseModel(models.Model):
    """Base model with sodar_uuid and creation/update time."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)
    #: DateTime of creation
    date_created = models.DateTimeField(auto_now_add=True)
    #: DateTime of last modification
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LabeledSortableBaseModel(BaseModel):
    """Base class for models with a rank, label, and description."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: Label of the presets.
    label = models.CharField(max_length=128)
    #: Description of the presets.
    description = models.TextField(null=True)

    class Meta:
        ordering = ["rank"]
        abstract = True


class QueryPresetsSet(LabeledSortableBaseModel, ClusterableModel):
    """Configured presets for a given project.

    We inherit from ``ClusterableModel`` so we can create presets sets and owned version /
    presets without storing them in the database for the factory defaults.
    """

    #: The owning ``Project``.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="seqvarpresetsset", null=True, blank=True
    )

    @transaction.atomic
    def clone_with_latest_version(self) -> "QueryPresetsSet":
        # Get label of presets set to create.
        for i in range(1, 100):
            label = f"{self.label} (copy {i})"
            if not QueryPresetsSet.objects.filter(project=self.project, label=label).exists():
                break
        # Compute rank.
        rank = QueryPresetsSet.objects.filter(project=self.project).count() + 1

        result = QueryPresetsSet.objects.create(
            label=label,
            rank=rank,
            description=self.description,
            project=self.project,
        )
        if self.versions.exists():
            self.versions.first().clone_with_presetsset(result)
        return result

    def __str__(self):
        return f"QueryPresetsSet '{self.sodar_uuid}'"


class QueryPresetsSetVersion(BaseModel, ClusterableModel):
    """One version of query presets set.

    It is assumed that there is at most one active version and at most one draft version.
    """

    #: The version is active.
    STATUS_ACTIVE = "active"
    #: The version is in draft state.
    STATUS_DRAFT = "draft"
    #: The version has been retired.
    STATUS_RETIRED = "retired"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, STATUS_ACTIVE),
        (STATUS_DRAFT, STATUS_DRAFT),
        (STATUS_RETIRED, STATUS_RETIRED),
    )

    #: The owning ``QueryPresetsSet``.
    presetsset = ParentalKey(QueryPresetsSet, on_delete=models.CASCADE, related_name="versions")
    #: The major version.
    version_major = models.IntegerField(default=1)
    #: The minor version.
    version_minor = models.IntegerField(default=0)
    #: The current status.
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    #: The user who signed off the presets.
    signed_off_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )

    @transaction.atomic
    def clone_with_presetsset(self, presetsset: QueryPresetsSet) -> "QueryPresetsSetVersion":
        result = QueryPresetsSetVersion.objects.create(
            presetsset=presetsset,
            version_major=1,
            version_minor=0,
            status=self.STATUS_DRAFT,
        )

        old_uuid_to_new_obj = {}
        for key in (
            "querypresetsfrequency_set",
            "querypresetsvariantprio_set",
            "querypresetsclinvar_set",
            "querypresetscolumns_set",
            "querypresetslocus_set",
            "querypresetsconsequence_set",
            "querypresetsquality_set",
            "querypresetsphenotypeprio_set",
            "predefinedquery_set",
        ):
            for obj in getattr(self, key, []).all():
                obj.pk = None
                obj.id = None
                obj._state.adding = True
                obj.sodar_uuid = uuid_object.uuid4()
                obj.presetssetversion = result
                obj.save()

        return result

    def __str__(self):
        return f"QueryPresetsSetVersion '{self.sodar_uuid}'"

    class Meta:
        unique_together = [("presetsset", "version_major", "version_minor")]
        ordering = ["-version_major", "-version_minor"]


class QueryPresetsBase(LabeledSortableBaseModel):
    """Base presets."""

    #: The owning ``QueryPresetsSetVersion``.
    presetssetversion = ParentalKey(QueryPresetsSetVersion, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class QueryPresetsQuality(QueryPresetsBase):
    """Presets for quality settings within a ``QueryPresetsSetVersion``.

    This is copied into ``QuerySettingsQuality.sample_quality_filters`` for
    each sample in the family when creating filter settings.
    """

    #: Drop whole variant on failure.
    filter_active = models.BooleanField(default=False, null=False, blank=False)
    #: Minimal depth for het. variants.
    min_dp_het = models.IntegerField(null=True, blank=True)
    #: Minimal depth for hom. variants.
    min_dp_hom = models.IntegerField(null=True, blank=True)
    #: Minimal allele balance for het. variants.
    min_ab_het = models.FloatField(null=True, blank=True)
    #: Minimal genotype quality.
    min_gq = models.IntegerField(null=True, blank=True)
    #: Minimal alternate allele read depth.
    min_ad = models.IntegerField(null=True, blank=True)
    #: Maximal alternate allele read depth.
    max_ad = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"QueryPresetsQuality '{self.sodar_uuid}'"


class QueryPresetsFrequency(FrequencySettingsBase, QueryPresetsBase):
    """Presets for frequency settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsFrequency '{self.sodar_uuid}'"


class QueryPresetsConsequence(ConsequenceSettingsBase, QueryPresetsBase):
    """Presets for consequence-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsConsequence '{self.sodar_uuid}'"


class QueryPresetsLocus(LocusSettingsBase, QueryPresetsBase):
    """Presets for locus-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsLocus '{self.sodar_uuid}'"


class QueryPresetsPhenotypePrio(PhenotypePrioSettingsBase, QueryPresetsBase):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsPhenotypePrio '{self.sodar_uuid}'"


class QueryPresetsVariantPrio(VariantPrioSettingsBase, QueryPresetsBase):
    """Presets for variant pathogenicity--related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsVariantPrio '{self.sodar_uuid}'"


class QueryPresetsClinvar(ClinvarSettingsBase, QueryPresetsBase):
    """Presets for clinvar-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsClinvar '{self.sodar_uuid}'"


class QueryPresetsColumns(ColumnsSettingsBase, QueryPresetsBase):
    """Presets for columns presets within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"QueryPresetsColumns '{self.sodar_uuid}'"


class GenotypePresetChoice(str, Enum):
    """Presets value for the chosen genotype."""

    #: No restriction on genotypes.
    ANY = "any"
    #: De novo inheritance.
    DE_NOVO = "de_novo"
    #: Dominant inheritance.
    DOMINANT = "dominant"
    #: Recessive inheritance.
    HOMOZYGOUS_RECESSIVE = "homozygous_recessive"
    #: Compound heterozygous inheritance.
    COMPOUND_HETEROZYGOUS_RECESSIVE = "compound_heterozygous_recessive"
    #: Autosomal recessive inheritance.
    RECESSIVE = "recessive"
    #: X-linked dominant inheritance.
    X_RECESSIVE = "x_recessive"
    #: All carriers are affected.
    AFFECTED_CARRIERS = "affected_carriers"


class GenotypePresets(pydantic.BaseModel):
    """Configuration for a single column in the result table."""

    #: The genotype prests choice.
    choice: typing.Optional[GenotypePresetChoice] = None


class PredefinedQuery(QueryPresetsBase):
    """A choice of presets from a ``PresetsSet`` in each category."""

    #: Whether this predefined query shall be run as part of an SOP.
    included_in_sop = models.BooleanField(default=False, null=False, blank=False)

    #: The chosen genotype presets.
    genotype = SchemaField(schema=typing.Optional[GenotypePresets], default=GenotypePresets())

    #: The chosen quality presets.
    quality = models.ForeignKey(
        QueryPresetsQuality, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen frequency presets.
    frequency = models.ForeignKey(
        QueryPresetsFrequency, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen consequence presets.
    consequence = models.ForeignKey(
        QueryPresetsConsequence, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen locus presets.
    locus = models.ForeignKey(QueryPresetsLocus, on_delete=models.SET_NULL, null=True, blank=True)
    #: The chosen phenotype priorization presets.
    phenotypeprio = models.ForeignKey(
        QueryPresetsPhenotypePrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen variant priorization presets.
    variantprio = models.ForeignKey(
        QueryPresetsVariantPrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen clinvar presets.
    clinvar = models.ForeignKey(
        QueryPresetsClinvar, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen columns presets.
    columns = models.ForeignKey(
        QueryPresetsColumns, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"PredefinedQuery '{self.sodar_uuid}'"


class QuerySettings(BaseModel):
    """The query settings for a case."""

    #: The owning ``CaseAnalysisSession``.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)

    #: The presets set version that this ``QuerySettings`` is based on.
    #:
    #: This information is used for computing differences between the presets and the
    #: effective query settings.
    presetssetversion = models.ForeignKey(
        QueryPresetsSetVersion, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"QuerySettings '{self.sodar_uuid}'"


class QuerySettingsCategoryBase(BaseModel):
    """Base class for concrete category query settings."""

    class Meta:
        abstract = True


class GenotypeChoice(str, Enum):
    """Store genotype choice of a ``SampleGenotype``."""

    #: Any.
    ANY = "any"
    #: Reference (wild type, homozygous/hemizygous reference) genotype.
    REF = "ref"
    #: Heterozygous genotype.
    HET = "het"
    #: Homozygous alternative genotype (or hemizygous alt for chrX / male).
    HOM = "hom"
    #: Non-homozygous.
    NON_HOM = "non-hom"
    #: Variant.
    VARIANT = "variant"
    #: Compound heterozygous index.
    COMPHET_INDEX = "comphet_index"
    #: Recessive index.
    RECESSIVE_INDEX = "recessive_index"
    #: Recessive parent.
    RECESSIVE_PARENT = "recessive_parent"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SampleGenotypeChoice(pydantic.BaseModel):
    """Store the genotype of a sample."""

    #: The sample identifier.
    sample: str
    #: The genotype.
    genotype: GenotypeChoice


class QuerySettingsGenotype(QuerySettingsCategoryBase):
    """Query settings for per-sample genotype filtration."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="genotype"
    )

    #: Per-sample genotype choice.
    sample_genotype_choices = SchemaField(schema=list[SampleGenotypeChoice], default=list)

    def __str__(self):
        return f"QuerySettingsGenotype '{self.sodar_uuid}'"


class SampleQualityFilter(pydantic.BaseModel):
    """Stores per-sample quality filter settings for a particular query."""

    #: Name of the sample.
    sample: str

    #: Whether the filter is active.
    filter_active: bool = False
    #: Minimal depth for het. variants.
    min_dp_het: typing.Optional[int] = None
    #: Minimal depth for hom. variants.
    min_dp_hom: typing.Optional[int] = None
    #: Minimal allele balance for het. variants.
    min_ab_het: typing.Optional[float] = None
    #: Minimal genotype quality.
    min_gq: typing.Optional[int] = None
    #: Minimal alternate allele read depth.
    min_ad: typing.Optional[int] = None
    #: Maximal alternate allele read depth.
    max_ad: typing.Optional[int] = None


class QuerySettingsQuality(QuerySettingsCategoryBase):
    """Query settings for per-sample quality filtration."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="quality"
    )

    #: Per-sample quality settings.
    sample_quality_filters = SchemaField(schema=list[SampleQualityFilter], default=list)

    def __str__(self):
        return f"QuerySettingsQuality '{self.sodar_uuid}'"


class QuerySettingsConsequence(ConsequenceSettingsBase, QuerySettingsCategoryBase):
    """Presets for consequence-related settings within a ``QuerySettingsSet``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="consequence"
    )

    def __str__(self):
        return f"QuerySettingsConsequence '{self.sodar_uuid}'"


class QuerySettingsLocus(LocusSettingsBase, QuerySettingsCategoryBase):
    """Presets for locus-related settings within a ``QuerySettingsSet``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="locus"
    )

    def __str__(self):
        return f"QuerySettingsLocus '{self.sodar_uuid}'"


class QuerySettingsFrequency(FrequencySettingsBase, QuerySettingsCategoryBase):
    """Query settings in the frequency category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="frequency"
    )

    def __str__(self):
        return f"QuerySettingsFrequency '{self.sodar_uuid}'"


class QuerySettingsPhenotypePrio(PhenotypePrioSettingsBase, QuerySettingsCategoryBase):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSetVersion``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="phenotypeprio"
    )

    def __str__(self):
        return f"QuerySettingsPhenotypePrio '{self.sodar_uuid}'"


class QuerySettingsVariantPrio(VariantPrioSettingsBase, QuerySettingsCategoryBase):
    """Query settings in the variant priorization category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="variantprio"
    )

    def __str__(self):
        return f"QuerySettingsVariantPrio '{self.sodar_uuid}'"


class QuerySettingsClinvar(ClinvarSettingsBase, QuerySettingsCategoryBase):
    """Query settings in the variant priorization category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        QuerySettings, on_delete=models.CASCADE, related_name="clinvar"
    )

    def __str__(self):
        return f"QuerySettingsClinvar '{self.sodar_uuid}'"


class QueryColumnsConfig(ColumnsSettingsBase, BaseModel):
    """Per-query (not execution) configuration of columns.

    This will be copied over from the presets to the query and not the query
    settings.  Thus, it will not be persisted by query execution but is
    editable after query execution.
    """

    def __str__(self):
        return f"QueryColumnsConfig '{self.sodar_uuid}'"


class Query(BaseModel):
    """Allows users to prepare seqvar queries for execution and execute them."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: The label of the query.
    label = models.CharField(max_length=128)

    #: Owning/containing session.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)
    #: Query settings to be edited in the next query execution.
    settings = models.OneToOneField(QuerySettings, on_delete=models.PROTECT)
    #: The columns configuration of the query.
    columnsconfig = models.OneToOneField(QueryColumnsConfig, on_delete=models.PROTECT)

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"Query '{self.sodar_uuid}'"


class QueryExecution(BaseModel):
    """Hold the state, query settings, and results for running one seqvar query."""

    #: Initial status.
    STATE_INITIAL = "initial"
    #: Queued and waiting for execution.
    STATE_QUEUED = "queued"
    #: Currently being executed.
    STATE_RUNNING = "running"
    #: Completed with failure.
    STATE_FAILED = "failed"
    #: Completed after being canceled by user.
    STATE_CANCELED = "canceled"
    #: Completed with success.
    STATE_DONE = "done"
    #: Choices for the ``state`` field.
    STATE_CHOICES = (
        (STATE_INITIAL, STATE_INITIAL),
        (STATE_QUEUED, STATE_QUEUED),
        (STATE_RUNNING, STATE_RUNNING),
        (STATE_FAILED, STATE_FAILED),
        (STATE_CANCELED, STATE_CANCELED),
        (STATE_DONE, STATE_DONE),
    )

    #: State of the query execution.
    state = models.CharField(max_length=64, choices=STATE_CHOICES)
    #: Estimate for completion, if given.
    complete_percent = models.IntegerField(null=True)
    #: The start time.
    start_time = models.DateTimeField(null=True)
    #: The end time.
    end_time = models.DateTimeField(null=True)
    #: The elapsed seconds.
    elapsed_seconds = models.FloatField(null=True)

    #: The owning/containing query.
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    #: Effective query settings of execution.
    querysettings = models.ForeignKey(QuerySettings, on_delete=models.PROTECT)

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.query.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"QueryExecution '{self.sodar_uuid}'"


class DataSourceInfo(pydantic.BaseModel):
    """Describes the version version of a given datasource."""

    #: The name.
    name: str
    #: The version.
    version: str


class DataSourceInfos(pydantic.BaseModel):
    """Container for ``DataSourceInfo`` records."""

    #: Information about the used datasources.
    infos: list[DataSourceInfo]


class ResultSet(BaseModel):
    """Store result rows and version information about the query."""

    #: The owning query execution.
    queryexecution = models.ForeignKey(QueryExecution, on_delete=models.CASCADE)
    #: The number of rows in the result.
    result_row_count = models.IntegerField(null=False, blank=False)
    #: Information about the data sources and versions used in the query, backed by
    #: pydantic model ``DataSourceInfos``.
    datasource_infos = SchemaField(schema=typing.Optional[DataSourceInfos])

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.queryexecution.case
        except AttributeError:
            return None

    def get_absolute_url(self) -> str:
        return f"/seqvars/api/resultset/{self.case.sodar_uuid}/{self.sodar_uuid}/"

    def __str__(self):
        return f"ResultSet '{self.sodar_uuid}'"


class ResultRowPayload(pydantic.BaseModel):
    """Payload for one result row of a seqvar query."""

    # TODO: implement me / infer from protobuf schema
    foo: int


class ResultRow(models.Model):
    """One entry in the result set."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)

    #: The owning result set.
    resultset = models.ForeignKey(ResultSet, on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Chromosome as number
    chromosome_no = models.IntegerField()
    #: Variant coordinates - start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    stop = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    #: The payload of the result row, backed by pydantic model
    #: ``ResultRowPayload``.
    payload = SchemaField(schema=typing.Optional[ResultRowPayload])

    def __str__(self):
        return (
            f"ResultRow '{self.sodar_uuid}' '{self.release}-{self.chromosome}-"
            f"{self.start}-{self.reference}-{self.alternative}'"
        )
