from enum import Enum
import typing
import uuid as uuid_object

import django
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django_pydantic_field.v2.fields import PydanticSchemaField as SchemaField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import pydantic

from cases_analysis.models import CaseAnalysisSession
from variants.models.case import Case
from variants.models.projectroles import Project

#: User model.
User = get_user_model()


class GnomadNuclearFrequencySettings(pydantic.BaseModel):
    """Settings for gnomAD nuclear frequency filtering."""

    enabled: bool = False
    homozygous: int | None = None
    heterozygous: int | None = None
    hemizygous: int | None = None
    frequency: float | None = None


class GnomadMitochondrialFrequencySettings(pydantic.BaseModel):
    """Settings for gnomAD mitochondrial frequency filtering."""

    enabled: bool = False
    heteroplasmic: int | None = None
    homoplasmic: int | None = None
    frequency: float | None = None


class HelixmtDbFrequencySettings(pydantic.BaseModel):
    """Settings for HelixMtDb frequency filtering."""

    enabled: bool = False
    heteroplasmic: int | None = None
    homoplasmic: int | None = None
    frequency: float | None = None


class InhouseFrequencySettings(pydantic.BaseModel):
    """Settings for in-house frequency filtering."""

    enabled: bool = False
    heterozygous: int | None = None
    homozygous: int | None = None
    hemizygous: int | None = None
    carriers: int | None = None


class SeqvarsFrequencySettingsBase(models.Model):
    """Abstract model for storing frequency-related settings."""

    gnomad_exomes = SchemaField(
        schema=typing.Optional[GnomadNuclearFrequencySettings],
        blank=True,
        null=True,
        default=None,
    )
    gnomad_genomes = SchemaField(
        schema=typing.Optional[GnomadNuclearFrequencySettings], blank=True, null=True, default=None
    )
    gnomad_mitochondrial = SchemaField(
        schema=typing.Optional[GnomadMitochondrialFrequencySettings],
        blank=True,
        null=True,
        default=None,
    )
    helixmtdb = SchemaField(
        schema=typing.Optional[HelixmtDbFrequencySettings], blank=True, null=True, default=None
    )
    inhouse = SchemaField(
        schema=typing.Optional[InhouseFrequencySettings], blank=True, null=True, default=None
    )

    class Meta:
        abstract = True


class SeqvarsVariantTypeChoice(str, Enum):
    """The type of a variant."""

    #: Single nucleotide variant.
    SNV = "snv"
    #: Insertion/deletion.
    INDEL = "indel"
    #: Multi-nucleotide variant.
    MNV = "mnv"
    #: Complex substitution.
    COMPLEX_SUBSTITUTION = "complex_substitution"


class SeqvarsTranscriptTypeChoice(str, Enum):
    """The type of a transcript."""

    #: Coding transcript.
    CODING = "coding"
    #: Non-coding transcript.
    NON_CODING = "non_coding"


class SeqvarsVariantConsequenceChoice(str, Enum):
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


class SeqvarsConsequenceSettingsBase(models.Model):
    """Abstract model for storing consequence-related settings."""

    #: The variant types.
    variant_types = SchemaField(schema=list[SeqvarsVariantTypeChoice], default=list)
    #: The transcript types.
    transcript_types = SchemaField(schema=list[SeqvarsTranscriptTypeChoice], default=list)
    #: The variant consequences.
    variant_consequences = SchemaField(schema=list[SeqvarsVariantConsequenceChoice], default=list)
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


class SeqvarsLocusSettingsBase(models.Model):
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


class SeqvarsPhenotypePrioSettingsBase(models.Model):
    """Abstract model for storing phenotype priorization--related settings."""

    #: Whether to enable phenotype-based priorization.
    phenotype_prio_enabled = models.BooleanField(default=False, null=False, blank=False)
    #: The algorithm to use for priorization.
    phenotype_prio_algorithm = models.CharField(max_length=128, null=True, blank=True)
    #: The phenotype terms to use.
    terms = SchemaField(schema=list[TermPresence], default=list)

    class Meta:
        abstract = True


class SeqvarsPrioService(pydantic.BaseModel):
    """Representation of a variant pathogenicity service."""

    #: The name of the service.
    name: str
    #: The version of the service.
    version: str


class SeqvarsVariantPrioSettingsBase(models.Model):
    """Abstract model for storing variant priorization--related settings.

    Note that this refers to external APIs that provide variant pathogenicity scores
    that are not annotated by the worker already (i.e., not precomputed).
    """

    #: Whether to enable variant-based priorization.
    variant_prio_enabled = models.BooleanField(default=False, null=False, blank=False)
    #: The enabled services.
    services = SchemaField(schema=list[SeqvarsPrioService], default=list)

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


class SeqvarsClinvarSettingsBase(models.Model):
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


class SeqvarsColumnConfig(pydantic.BaseModel):
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


class SeqvarsColumnsSettingsBase(models.Model):
    """Abstract model for storing column-related settings."""

    #: List of columns with their widths.
    column_settings = SchemaField(schema=list[SeqvarsColumnConfig], default=list)

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


class SeqvarsQueryPresetsSet(LabeledSortableBaseModel, ClusterableModel):
    """Configured presets for a given project.

    We inherit from ``ClusterableModel`` so we can create presets sets and owned version /
    presets without storing them in the database for the factory defaults.
    """

    #: The owning ``Project``.
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="seqvarspresetsset", null=True, blank=True
    )

    @transaction.atomic
    def clone_with_latest_version(self) -> "SeqvarsQueryPresetsSet":
        # Get label of presets set to create.
        for i in range(1, 100):
            label = f"{self.label} (copy {i})"
            if not SeqvarsQueryPresetsSet.objects.filter(
                project=self.project, label=label
            ).exists():
                break
        # Compute rank.
        rank = SeqvarsQueryPresetsSet.objects.filter(project=self.project).count() + 1

        result = SeqvarsQueryPresetsSet.objects.create(
            label=label,
            rank=rank,
            description=self.description,
            project=self.project,
        )
        if self.versions.exists():
            self.versions.first().clone_with_presetsset(result)
        return result

    def __str__(self):
        return f"SeqvarsQueryPresetsSet '{self.sodar_uuid}'"


class SeqvarsQueryPresetsSetVersion(BaseModel, ClusterableModel):
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
    presetsset = ParentalKey(
        SeqvarsQueryPresetsSet, on_delete=models.CASCADE, related_name="versions"
    )
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
    def clone_with_presetsset(
        self, presetsset: SeqvarsQueryPresetsSet
    ) -> "SeqvarsQueryPresetsSetVersion":
        result = SeqvarsQueryPresetsSetVersion.objects.create(
            presetsset=presetsset,
            version_major=1,
            version_minor=0,
            status=self.STATUS_DRAFT,
        )

        old_uuid_to_new_obj = {}
        for key in (
            "seqvarsquerypresetsfrequency_set",
            "seqvarsquerypresetsvariantprio_set",
            "seqvarsquerypresetsclinvar_set",
            "seqvarsquerypresetscolumns_set",
            "seqvarsquerypresetslocus_set",
            "seqvarsquerypresetsconsequence_set",
            "seqvarsquerypresetsquality_set",
            "seqvarsquerypresetsphenotypeprio_set",
            "seqvarspredefinedquery_set",
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
        return f"SeqvarsQueryPresetsSetVersion '{self.sodar_uuid}'"

    class Meta:
        unique_together = [("presetsset", "version_major", "version_minor")]
        ordering = ["-version_major", "-version_minor"]


class SeqvarsQueryPresetsBase(LabeledSortableBaseModel):
    """Base presets."""

    #: The owning ``QueryPresetsSetVersion``.
    presetssetversion = ParentalKey(SeqvarsQueryPresetsSetVersion, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class SeqvarsQueryPresetsQuality(SeqvarsQueryPresetsBase):
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
        return f"SeqvarsQueryPresetsQuality '{self.sodar_uuid}'"


class SeqvarsQueryPresetsFrequency(SeqvarsFrequencySettingsBase, SeqvarsQueryPresetsBase):
    """Presets for frequency settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsFrequency '{self.sodar_uuid}'"


class SeqvarsQueryPresetsConsequence(SeqvarsConsequenceSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for consequence-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsConsequence '{self.sodar_uuid}'"


class SeqvarsQueryPresetsLocus(SeqvarsLocusSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for locus-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsLocus '{self.sodar_uuid}'"


class SeqvarsQueryPresetsPhenotypePrio(SeqvarsPhenotypePrioSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsPhenotypePrio '{self.sodar_uuid}'"


class SeqvarsQueryPresetsVariantPrio(SeqvarsVariantPrioSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for variant pathogenicity--related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsVariantPrio '{self.sodar_uuid}'"


class SeqvarsQueryPresetsClinvar(SeqvarsClinvarSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for clinvar-related settings within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsClinvar '{self.sodar_uuid}'"


class SeqvarsQueryPresetsColumns(SeqvarsColumnsSettingsBase, SeqvarsQueryPresetsBase):
    """Presets for columns presets within a ``QueryPresetsSetVersion``."""

    def __str__(self):
        return f"SeqvarsQueryPresetsColumns '{self.sodar_uuid}'"


class SeqvarsGenotypePresetChoice(str, Enum):
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


class SeqvarsGenotypePresets(pydantic.BaseModel):
    """Configuration for a single column in the result table."""

    #: The genotype prests choice.
    choice: typing.Optional[SeqvarsGenotypePresetChoice] = None


class SeqvarsPredefinedQuery(SeqvarsQueryPresetsBase):
    """A choice of presets from a ``PresetsSet`` in each category."""

    #: Whether this predefined query shall be run as part of an SOP.
    included_in_sop = models.BooleanField(default=False, null=False, blank=False)

    #: The chosen genotype presets.
    genotype = SchemaField(
        schema=typing.Optional[SeqvarsGenotypePresets], default=SeqvarsGenotypePresets()
    )

    #: The chosen quality presets.
    quality = models.ForeignKey(
        SeqvarsQueryPresetsQuality, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen frequency presets.
    frequency = models.ForeignKey(
        SeqvarsQueryPresetsFrequency, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen consequence presets.
    consequence = models.ForeignKey(
        SeqvarsQueryPresetsConsequence, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen locus presets.
    locus = models.ForeignKey(
        SeqvarsQueryPresetsLocus, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen phenotype priorization presets.
    phenotypeprio = models.ForeignKey(
        SeqvarsQueryPresetsPhenotypePrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen variant priorization presets.
    variantprio = models.ForeignKey(
        SeqvarsQueryPresetsVariantPrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen clinvar presets.
    clinvar = models.ForeignKey(
        SeqvarsQueryPresetsClinvar, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen columns presets.
    columns = models.ForeignKey(
        SeqvarsQueryPresetsColumns, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"SeqvarsPredefinedQuery '{self.sodar_uuid}'"


class SeqvarsQuerySettings(BaseModel):
    """The query settings for a case."""

    #: The owning ``CaseAnalysisSession``.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)

    #: The presets set version that this ``QuerySettings`` is based on.
    #:
    #: This information is used for computing differences between the presets and the
    #: effective query settings.
    presetssetversion = models.ForeignKey(
        SeqvarsQueryPresetsSetVersion, on_delete=models.PROTECT, null=True, blank=True
    )

    def __str__(self):
        return f"SeqvarsQuerySettings '{self.sodar_uuid}'"


class SeqvarsQuerySettingsCategoryBase(BaseModel):
    """Base class for concrete category query settings."""

    class Meta:
        abstract = True


class SeqvarsGenotypeChoice(str, Enum):
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


class SeqvarsSampleGenotypeChoice(pydantic.BaseModel):
    """Store the genotype of a sample."""

    #: The sample identifier.
    sample: str
    #: The genotype.
    genotype: SeqvarsGenotypeChoice


class SeqvarsQuerySettingsGenotype(SeqvarsQuerySettingsCategoryBase):
    """Query settings for per-sample genotype filtration."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="genotype"
    )

    #: Per-sample genotype choice.
    sample_genotype_choices = SchemaField(schema=list[SeqvarsSampleGenotypeChoice], default=list)

    def __str__(self):
        return f"SeqvarsQuerySettingsGenotype '{self.sodar_uuid}'"


class SeqvarsSampleQualityFilter(pydantic.BaseModel):
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


class SeqvarsQuerySettingsQuality(SeqvarsQuerySettingsCategoryBase):
    """Query settings for per-sample quality filtration."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="quality"
    )

    #: Per-sample quality settings.
    sample_quality_filters = SchemaField(schema=list[SeqvarsSampleQualityFilter], default=list)

    def __str__(self):
        return f"SeqvarsQuerySettingsQuality '{self.sodar_uuid}'"


class SeqvarsQuerySettingsConsequence(
    SeqvarsConsequenceSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Presets for consequence-related settings within a ``QuerySettingsSet``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="consequence"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsConsequence '{self.sodar_uuid}'"


class SeqvarsQuerySettingsLocus(SeqvarsLocusSettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Presets for locus-related settings within a ``QuerySettingsSet``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="locus"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsLocus '{self.sodar_uuid}'"


class SeqvarsQuerySettingsFrequency(SeqvarsFrequencySettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Query settings in the frequency category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="frequency"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsFrequency '{self.sodar_uuid}'"


class SeqvarsQuerySettingsPhenotypePrio(
    SeqvarsPhenotypePrioSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSetVersion``."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="phenotypeprio"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsPhenotypePrio '{self.sodar_uuid}'"


class SeqvarsQuerySettingsVariantPrio(
    SeqvarsVariantPrioSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Query settings in the variant priorization category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="variantprio"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsVariantPrio '{self.sodar_uuid}'"


class SeqvarsQuerySettingsClinvar(SeqvarsClinvarSettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Query settings in the variant priorization category."""

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="clinvar"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsClinvar '{self.sodar_uuid}'"


class SeqvarsQueryColumnsConfig(SeqvarsColumnsSettingsBase, BaseModel):
    """Per-query (not execution) configuration of columns.

    This will be copied over from the presets to the query and not the query
    settings.  Thus, it will not be persisted by query execution but is
    editable after query execution.
    """

    def __str__(self):
        return f"SeqvarsQueryColumnsConfig '{self.sodar_uuid}'"


class SeqvarsQuery(BaseModel):
    """Allows users to prepare seqvar queries for execution and execute them."""

    #: An integer rank for manual sorting in UI.
    rank = models.IntegerField()
    #: The label of the query.
    label = models.CharField(max_length=128)

    #: Owning/containing session.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)
    #: Query settings to be edited in the next query execution.
    settings = models.OneToOneField(SeqvarsQuerySettings, on_delete=models.PROTECT)
    #: The columns configuration of the query.
    columnsconfig = models.OneToOneField(SeqvarsQueryColumnsConfig, on_delete=models.PROTECT)

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"SeqvarsQuery '{self.sodar_uuid}'"


class SeqvarsQueryExecution(BaseModel):
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
    query = models.ForeignKey(SeqvarsQuery, on_delete=models.CASCADE)
    #: Effective query settings of execution.
    querysettings = models.ForeignKey(SeqvarsQuerySettings, on_delete=models.PROTECT)

    @property
    def case(self) -> typing.Optional[Case]:
        try:
            return self.query.session.caseanalysis.case
        except AttributeError:
            return None

    def __str__(self):
        return f"SeqvarsQueryExecution '{self.sodar_uuid}'"


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


class SeqvarsResultSet(BaseModel):
    """Store result rows and version information about the query."""

    #: The owning query execution.
    queryexecution = models.ForeignKey(SeqvarsQueryExecution, on_delete=models.CASCADE)
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
        return f"SeqvarsResultSet '{self.sodar_uuid}'"


class SeqvarsResultRowPayload(pydantic.BaseModel):
    """Payload for one result row of a seqvar query."""

    # TODO: implement me / infer from protobuf schema
    foo: int


class SeqvarsResultRow(models.Model):
    """One entry in the result set."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)

    #: The owning result set.
    resultset = models.ForeignKey(SeqvarsResultSet, on_delete=models.CASCADE)

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
    payload = SchemaField(schema=typing.Optional[SeqvarsResultRowPayload])

    def __str__(self):
        return (
            f"SeqvarsResultRow '{self.sodar_uuid}' '{self.release}-{self.chromosome}-"
            f"{self.start}-{self.reference}-{self.alternative}'"
        )
