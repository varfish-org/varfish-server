"""Models of the ``seqvars`` app.

Broadly, we have two different types of models: Django models based and Pydantic based.

Django models are used for storing records in the database.  Pydantic models are used
for storing compound information in JSONB fields in the database.  The trade-off of having
denormalized data was chosen for keeping certain complexity at bay at the cost of
denormalized database schemas and related potential issues.

All models are expected to be eventually exposed to the REST API.  Here, we need globally
unique names, thus the ``Seqvars`` prefix was used to support this.  The enums used have
the suffix ``Choice`` in some cases for disambiguation of names and in others for
consistency.  The Pydantic models have the suffix ``Pydantic`` (again) in some cases for
disambiguation and otherwise for consistency.

We are aware that there is some redundancy in the models.
"""

import datetime
from enum import Enum
import typing
import uuid as uuid_object

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django_pydantic_field.v2.fields import PydanticSchemaField as SchemaField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
import pydantic

from cases.models import Individual, Pedigree
from cases_analysis.models import CaseAnalysisSession
from variants.models.case import Case
from variants.models.projectroles import Project

#: Express "ExtendsBaseModel extends pydantic.BaseModel"
ExtendsBaseModel = typing.TypeVar("ExtendsBaseModel", bound=pydantic.BaseModel)


def copy_model(value: typing.Optional[ExtendsBaseModel]) -> typing.Optional[ExtendsBaseModel]:
    """Call ``model_dump()`` on ``value`` unless it is ``None``."""
    if value is None:
        return None
    else:
        return value.model_copy()


def copy_list(values: list[ExtendsBaseModel]) -> list[ExtendsBaseModel]:
    """Return ``model_dump()` result on each item of ``values``."""
    return [item.model_copy() for item in values]


#: User model.
User = get_user_model()


class GnomadNuclearFrequencySettingsPydantic(pydantic.BaseModel):
    """Settings for gnomAD nuclear frequency filtering."""

    enabled: bool = False
    heterozygous: int | None = None
    homozygous: int | None = None
    hemizygous: int | None = None
    frequency: float | None = None


class GnomadMitochondrialFrequencySettingsPydantic(pydantic.BaseModel):
    """Settings for gnomAD mitochondrial frequency filtering."""

    enabled: bool = False
    heteroplasmic: int | None = None
    homoplasmic: int | None = None
    frequency: float | None = None


class HelixmtDbFrequencySettingsPydantic(pydantic.BaseModel):
    """Settings for HelixMtDb frequency filtering."""

    enabled: bool = False
    heteroplasmic: int | None = None
    homoplasmic: int | None = None
    frequency: float | None = None


class InhouseFrequencySettingsPydantic(pydantic.BaseModel):
    """Settings for in-house frequency filtering."""

    enabled: bool = False
    heterozygous: int | None = None
    homozygous: int | None = None
    hemizygous: int | None = None
    carriers: int | None = None


class SeqvarsFrequencySettingsBase(models.Model):
    """Abstract model for storing frequency-related settings."""

    gnomad_exomes = SchemaField(
        schema=typing.Optional[GnomadNuclearFrequencySettingsPydantic],
        blank=True,
        null=True,
        default=None,
    )
    gnomad_genomes = SchemaField(
        schema=typing.Optional[GnomadNuclearFrequencySettingsPydantic],
        blank=True,
        null=True,
        default=None,
    )
    gnomad_mitochondrial = SchemaField(
        schema=typing.Optional[GnomadMitochondrialFrequencySettingsPydantic],
        blank=True,
        null=True,
        default=None,
    )
    helixmtdb = SchemaField(
        schema=typing.Optional[HelixmtDbFrequencySettingsPydantic],
        blank=True,
        null=True,
        default=None,
    )
    inhouse = SchemaField(
        schema=typing.Optional[InhouseFrequencySettingsPydantic],
        blank=True,
        null=True,
        default=None,
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

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsTranscriptTypeChoice(str, Enum):
    """The type of a transcript."""

    #: Coding transcript.
    CODING = "coding"
    #: Non-coding transcript.
    NON_CODING = "non_coding"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsVariantConsequenceChoice(str, Enum):
    """The variant consequence."""

    # high impact

    #: Transcript ablation.
    TRANSCRIPT_ABLATION = "transcript_ablation"
    #: Exon loss variant.
    EXON_LOSS_VARIANT = "exon_loss_variant"
    #: Splice acceptor variant
    SPLICE_ACCEPTOR_VARIANT = "splice_acceptor_variant"
    #: Splice donor variant
    SPLICE_DONOR_VARIANT = "splice_donor_variant"
    #: Stop gained
    STOP_GAINED = "stop_gained"
    #: Frameshift variant
    FRAMESHIFT_VARIANT = "frameshift_variant"
    #: Stop lost
    STOP_LOST = "stop_lost"
    #: Start lost
    START_LOST = "start_lost"
    #: Transcript amplification
    TRANSCRIPT_AMPLIFICATION = "transcript_amplification"

    # moderate impact

    #: Disruptive inframe insertion
    DISRUPTIVE_INFRAME_INSERTION = "disruptive_inframe_insertion"
    #: Disruptive inframe deletion
    DISRUPTIVE_INFRAME_DELETION = "disruptive_inframe_deletion"
    #: Conservative inframe insertion
    CONSERVATIVE_INFRAME_INSERTION = "conservative_inframe_insertion"
    #: Conservative inframe deletion
    CONSERVATIVE_INFRAME_DELETION = "conservative_inframe_deletion"
    #: In-frame indel.
    IN_FRAME_INDEL = "inframe_indel"
    #: Missense variant
    MISSENSE_VARIANT = "missense_variant"

    # low impact

    #: Splice donor 5th base variant.
    SPLICE_DONOR_5TH_BASE_VARIANT = "splice_donor_5th_base_variant"
    #: Splice region variant.
    SPLICE_REGION_VARIANT = "splice_region_variant"
    #: Splice donor region variant.
    SPLICE_DONOR_REGION_VARIANT = "splice_donor_region_variant"
    #: Splice polypyrimidine tract variant.
    SPLICE_POLYPYRIMIDINE_TRACT_VARIANT = "splice_polypyrimidine_tract_variant"
    #: Start retained variant.
    START_RETAINED_VARIANT = "start_retained_variant"
    #: Stop retained variant.
    STOP_RETAINED_VARIANT = "stop_retained_variant"
    #: Synonymous variant.
    SYNONYMOUS_VARIANT = "synonymous_variant"

    # modifier

    #: Coding sequence variant.
    CODING_SEQUENCE_VARIANT = "coding_sequence_variant"
    # #: Mature miRNA variant.
    # MATURE_MIRNA_VARIANT = "mature_miRNA_variant"
    #: 5' UTR exon variant.
    FIVE_PRIME_UTR_EXON_VARIANT = "5_prime_UTR_exon_variant"
    #: 5' UTR intron variant.
    FIVE_PRIME_UTR_INTRON_VARIANT = "5_prime_UTR_intron_variant"
    #: 3' UTR exon variant.
    THREE_PRIME_UTR_EXON_VARIANT = "3_prime_UTR_exon_variant"
    #: 3' UTR intron variant.
    THREE_PRIME_UTR_INTRON_VARIANT = "3_prime_UTR_intron_variant"
    #: Non-coding transcript exon variant.
    NON_CODING_TRANSCRIPT_EXON_VARIANT = "non_coding_transcript_exon_variant"
    #: Non-coding transcript intron variant.
    NON_CODING_TRANSCRIPT_INTRON_VARIANT = "non_coding_transcript_intron_variant"
    #: Upstream gene variant.
    UPSTREAM_GENE_VARIANT = "upstream_gene_variant"
    #: Downstream gene variant.
    DOWNSTREAM_GENE_VARIANT = "downstream_gene_variant"
    # #: TFBS ablation.
    # TFBS_ABLATION = "TFBS_ablation"
    # #: TFBS amplification.
    # TFBS_AMPLIFICATION = "TFBS_amplification"
    # #: TF binding site variant.
    # TF_BINDING_SITE_VARIANT = "TF_binding_site_variant"
    # #: Regulatory region ablation.
    # REGULATORY_REGION_ABLATION = "regulatory_region_ablation"
    # #: Regulatory region amplification.
    # REGULATORY_REGION_AMPLIFICATION = "regulatory_region_amplification"
    # #: Regulatory region variant.
    # REGULATORY_REGION_VARIANT = "regulatory_region_variant"
    #: Intergenic variant.
    INTERGENIC_VARIANT = "intergenic_variant"
    #: Intron variant.
    INTRON_VARIANT = "intron_variant"
    # #: Gene variant.
    # GENE_VARIANT = "gene_variant"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


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


class GenePydantic(pydantic.BaseModel):
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


class GenePanelSourceChoice(str, Enum):
    """The source of a gene panel."""

    #: PanelApp.
    PANELAPP = "panelapp"
    #: Internal to varfish intance.
    INTERNAL = "internal"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class GenePanelPydantic(pydantic.BaseModel):
    """Representation of a gene panel to use in the query."""

    #: The source of the gene panel.
    source: GenePanelSourceChoice
    #: The panel ID (number for PanelApp, UUID for internal).
    panel_id: str
    #: The panel name.
    name: str
    #: The panel version.
    version: str


class OneBasedRangePydantic(pydantic.BaseModel):
    """Representation of a 1-based range."""

    #: The 1-based start position.
    start: int
    #: The 1-based end position.
    end: int


class GenomeRegionPydantic(pydantic.BaseModel):
    """Representation of a genomic region to query for."""

    #: The chromosome name.
    chromosome: str
    #: The optional range.
    range: typing.Optional[OneBasedRangePydantic] = None


class SeqvarsLocusSettingsBase(models.Model):
    """Abstract model for storing locus-related settings."""

    #: Optional list of gene symbols to filter for.
    genes = SchemaField(schema=list[GenePydantic], default=list)
    #: Optional ilst of gene panels to use in the query.
    gene_panels = SchemaField(schema=list[GenePanelPydantic], default=list)
    #: Optional list of genomic regions to filter for.
    genome_regions = SchemaField(schema=list[GenomeRegionPydantic], default=list)

    class Meta:
        abstract = True


class TermPydantic(pydantic.BaseModel):
    """Representation of a condition (phenotype / disease) term."""

    #: CURIE-style identifier, e.g., with prefixes "HP:0000001", "OMIM:123456", "ORPHA:123456
    term_id: str
    #: An optional label for the term.
    label: typing.Optional[str]


class TermPresencePydantic(pydantic.BaseModel):
    """Representation of a term with optional presence (default is not excluded)."""

    #: The condition term.
    term: TermPydantic
    #: Whether the term is excluded.
    excluded: typing.Optional[bool] = None


class SeqvarsPhenotypePrioSettingsBase(models.Model):
    """Abstract model for storing phenotype priorization--related settings."""

    #: Whether to enable phenotype-based priorization.
    phenotype_prio_enabled = models.BooleanField(default=False, null=False, blank=False)
    #: The algorithm to use for priorization.
    phenotype_prio_algorithm = models.CharField(max_length=128, null=True, blank=True)
    #: The phenotype terms to use.
    terms = SchemaField(schema=list[TermPresencePydantic], default=list)

    class Meta:
        abstract = True


class SeqvarsPrioServicePydantic(pydantic.BaseModel):
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
    services = SchemaField(schema=list[SeqvarsPrioServicePydantic], default=list)

    class Meta:
        abstract = True


class ClinvarGermlineAggregateDescriptionChoice(str, Enum):
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

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsClinvarSettingsBase(models.Model):
    """Abstract model for storing clinvar-related settings."""

    #: Whether to require presence in ClinVar priorization.
    clinvar_presence_required = models.BooleanField(default=False, null=False, blank=False)
    #: The aggregate description for germline variants.
    clinvar_germline_aggregate_description = SchemaField(
        schema=list[ClinvarGermlineAggregateDescriptionChoice], default=list
    )
    #: Whether to allow for conflicting interpretations of pathogenicity.
    allow_conflicting_interpretations = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        abstract = True


class SeqvarsColumnConfigPydantic(pydantic.BaseModel):
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
    column_settings = SchemaField(schema=list[SeqvarsColumnConfigPydantic], default=list)

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
    def clone_with_latest_version(
        self, *, project: Project, label: typing.Optional[str] = None
    ) -> "SeqvarsQueryPresetsSet":
        """Clone the presets set with the latest version into the given ``project``."""
        # Get label of presets set to create (use given label by default).
        for i in range(0, 100):
            if i == 0 and not label:
                # first try label from argument if given
                continue
            elif i > 0:
                # else, try to find a unique label
                label = f"{self.label} (copy {i})"
            if not SeqvarsQueryPresetsSet.objects.filter(project=project, label=label).exists():
                break
        # Compute rank.
        rank = SeqvarsQueryPresetsSet.objects.filter(project=self.project).count() + 1

        result = SeqvarsQueryPresetsSet.objects.create(
            label=label,
            rank=rank,
            description=self.description,
            project=project,
        )
        if self.versions.exists():
            self.versions.first().clone_with_presetsset(presetsset=result)
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
        self,
        *,
        presetsset: SeqvarsQueryPresetsSet,
    ) -> "SeqvarsQueryPresetsSetVersion":
        result = SeqvarsQueryPresetsSetVersion.objects.create(
            presetsset=presetsset,
            version_major=self.version_major,
            version_minor=self.version_minor + 1,
            status=self.STATUS_DRAFT,
        )

        # First, handle the "normal" presets categories.  A side-effect of the
        # code below is that the UUIDs of the presets are changed and we rely
        # on this when createing the predefined queries.
        for key in (
            "seqvarsquerypresetsfrequency_set",
            "seqvarsquerypresetsvariantprio_set",
            "seqvarsquerypresetsclinvar_set",
            "seqvarsquerypresetscolumns_set",
            "seqvarsquerypresetslocus_set",
            "seqvarsquerypresetsconsequence_set",
            "seqvarsquerypresetsquality_set",
            "seqvarsquerypresetsphenotypeprio_set",
        ):
            for obj in getattr(self, key, []).all():
                obj.pk = None
                obj.id = None
                obj._state.adding = True
                new_uuid = uuid_object.uuid4()
                obj.sodar_uuid = new_uuid
                obj.presetssetversion = result
                obj.save()

        # Then, handle the predefined queries, using the UUID mapping built above.
        for obj in self.seqvarspredefinedquery_set.all():
            obj.pk = None
            obj.id = None
            obj._state.adding = True
            obj.sodar_uuid = uuid_object.uuid4()
            obj.presetssetversion = result
            obj.quality = SeqvarsQueryPresetsQuality.objects.get(
                sodar_uuid=obj.quality.sodar_uuid,
            )
            obj.frequency = SeqvarsQueryPresetsFrequency.objects.get(
                sodar_uuid=obj.frequency.sodar_uuid,
            )
            obj.consequence = SeqvarsQueryPresetsConsequence.objects.get(
                sodar_uuid=obj.consequence.sodar_uuid,
            )
            obj.locus = SeqvarsQueryPresetsLocus.objects.get(
                sodar_uuid=obj.locus.sodar_uuid,
            )
            obj.phenotypeprio = SeqvarsQueryPresetsPhenotypePrio.objects.get(
                sodar_uuid=obj.phenotypeprio.sodar_uuid,
            )
            obj.variantprio = SeqvarsQueryPresetsVariantPrio.objects.get(
                sodar_uuid=obj.variantprio.sodar_uuid,
            )
            obj.clinvar = SeqvarsQueryPresetsClinvar.objects.get(
                sodar_uuid=obj.clinvar.sodar_uuid,
            )
            obj.columns = SeqvarsQueryPresetsColumns.objects.get(
                sodar_uuid=obj.columns.sodar_uuid,
            )
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

    This is copied into ``SevarsQuerySettingsQuality.sample_quality_filters`` for
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

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsGenotypePresetsPydantic(pydantic.BaseModel):
    """Configuration for a single column in the result table."""

    #: The genotype prests choice.
    choice: typing.Optional[SeqvarsGenotypePresetChoice] = None


class SeqvarsPredefinedQuery(SeqvarsQueryPresetsBase):
    """A choice of presets from a ``PresetsSet`` in each category."""

    #: Whether this predefined query shall be run as part of an SOP.
    included_in_sop = models.BooleanField(default=False, null=False, blank=False)

    #: The chosen genotype presets.
    genotype = SchemaField(
        schema=typing.Optional[SeqvarsGenotypePresetsPydantic],
        default=SeqvarsGenotypePresetsPydantic(),
        null=True,
        blank=True,
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


class SeqvarsQuerySettingsManager(models.Manager):
    """Manager for ``SeqvarsQuerySettings``."""

    @transaction.atomic
    def from_predefinedquery(
        self,
        *,
        session: CaseAnalysisSession,
        predefinedquery: SeqvarsPredefinedQuery,
    ) -> "SeqvarsQuerySettings":
        querysettings = super().create(
            session=session,
            presetssetversion=predefinedquery.presetssetversion,
            predefinedquery=predefinedquery,
            # foreign keys / references to category presets
            genotypepresets=predefinedquery.genotype,
            qualitypresets=predefinedquery.quality,
            frequencypresets=predefinedquery.frequency,
            consequencepresets=predefinedquery.consequence,
            locuspresets=predefinedquery.locus,
            phenotypepriopresets=predefinedquery.phenotypeprio,
            variantpriopresets=predefinedquery.variantprio,
            clinvarpresets=predefinedquery.clinvar,
            columnspresets=predefinedquery.columns,
        )
        # create related records
        SeqvarsQuerySettingsGenotype.objects.from_presets(
            pedigree=session.case.pedigree_obj,
            querysettings=querysettings,
            genotypepresets=predefinedquery.genotype,
        )
        SeqvarsQuerySettingsQuality.objects.from_presets(
            pedigree=session.case.pedigree_obj,
            querysettings=querysettings,
            qualitypresets=predefinedquery.quality,
        )
        SeqvarsQuerySettingsFrequency.objects.from_presets(
            querysettings=querysettings, frequencypresets=predefinedquery.frequency
        )
        SeqvarsQuerySettingsConsequence.objects.from_presets(
            querysettings=querysettings, consequencepresets=predefinedquery.consequence
        )
        SeqvarsQuerySettingsLocus.objects.from_presets(
            querysettings=querysettings, locuspresets=predefinedquery.locus
        )
        SeqvarsQuerySettingsPhenotypePrio.objects.from_presets(
            querysettings=querysettings, phenotypepriopresets=predefinedquery.phenotypeprio
        )
        SeqvarsQuerySettingsVariantPrio.objects.from_presets(
            querysettings=querysettings, variantpriopresets=predefinedquery.variantprio
        )
        SeqvarsQuerySettingsClinvar.objects.from_presets(
            querysettings=querysettings, clinvarpresets=predefinedquery.clinvar
        )
        return querysettings


class SeqvarsQuerySettings(BaseModel):
    """The query settings for a case."""

    #: Custom manager with ``from_predefinedquery()``.
    objects = SeqvarsQuerySettingsManager()

    #: The owning ``CaseAnalysisSession``.
    session = models.ForeignKey(CaseAnalysisSession, on_delete=models.CASCADE)

    #: The presets set version that this ``QuerySettings`` is based on.
    #:
    #: This information is used for computing differences between the presets and the
    #: effective query settings (together with ``predefinedquery``).
    presetssetversion = models.ForeignKey(
        SeqvarsQueryPresetsSetVersion, on_delete=models.PROTECT, null=True, blank=True
    )

    #: The predefined query that this ``QuerySettings`` is based on.
    predefinedquery = models.ForeignKey(
        SeqvarsPredefinedQuery, on_delete=models.PROTECT, null=True, blank=True
    )

    #: The chosen genotype presets.
    genotypepresets = SchemaField(
        schema=typing.Optional[SeqvarsGenotypePresetsPydantic],
        default=SeqvarsGenotypePresetsPydantic(),
        null=True,
        blank=True,
    )
    #: The chosen quality presets.
    qualitypresets = models.ForeignKey(
        SeqvarsQueryPresetsQuality, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen frequency presets.
    frequencypresets = models.ForeignKey(
        SeqvarsQueryPresetsFrequency, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen consequence presets.
    consequencepresets = models.ForeignKey(
        SeqvarsQueryPresetsConsequence, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen locus presets.
    locuspresets = models.ForeignKey(
        SeqvarsQueryPresetsLocus, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen phenotype priorization presets.
    phenotypepriopresets = models.ForeignKey(
        SeqvarsQueryPresetsPhenotypePrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen variant priorization presets.
    variantpriopresets = models.ForeignKey(
        SeqvarsQueryPresetsVariantPrio, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen clinvar presets.
    clinvarpresets = models.ForeignKey(
        SeqvarsQueryPresetsClinvar, on_delete=models.SET_NULL, null=True, blank=True
    )
    #: The chosen columns presets.
    columnspresets = models.ForeignKey(
        SeqvarsQueryPresetsColumns, on_delete=models.SET_NULL, null=True, blank=True
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
    #: Non-heterozygous.
    NON_HET = "non_het"
    #: Non-homozygous.
    NON_HOM = "non_hom"
    #: Variant.
    VARIANT = "variant"
    #: Recessive index.
    RECESSIVE_INDEX = "recessive_index"
    #: Recessive father.
    RECESSIVE_FATHER = "recessive_father"
    #: Recessive mother.
    RECESSIVE_MOTHER = "recessive_mother"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsSampleGenotypePydantic(pydantic.BaseModel):
    """Store the genotype of a sample."""

    #: The sample identifier.
    sample: str
    #: The genotype.
    genotype: SeqvarsGenotypeChoice
    #: Include no-call genotype, will disable quality filter.
    include_no_call: bool = False
    #: Whether the genotype choice is enabled.
    enabled: bool = True


#: Mapping from presets choice to recessive mode.
PRESETS_CHOICE_TO_RECESSIVE_MODE: dict[SeqvarsGenotypePresetChoice, str] = {
    SeqvarsGenotypePresetChoice.ANY: "disabled",
    SeqvarsGenotypePresetChoice.DE_NOVO: "disabled",
    SeqvarsGenotypePresetChoice.DOMINANT: "disabled",
    SeqvarsGenotypePresetChoice.HOMOZYGOUS_RECESSIVE: "homozygous_recessive",
    SeqvarsGenotypePresetChoice.COMPOUND_HETEROZYGOUS_RECESSIVE: "comphet_recessive",
    SeqvarsGenotypePresetChoice.RECESSIVE: "recessive",
    SeqvarsGenotypePresetChoice.X_RECESSIVE: "recessive",
    SeqvarsGenotypePresetChoice.AFFECTED_CARRIERS: "disabled",
}


class SeqvarsQuerySettingsGenotypeManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    @classmethod
    def _compute_founder_path_lengths(
        cls,
        *,
        pedigree: Pedigree,
    ) -> dict[str, int]:
        """Compute mapping from sample name to length of longest path to a founder."""
        result = {}
        members: list[Individual] = list(pedigree.individual_set.all())
        member_names = {member.name for member in members}

        # Detect the case where we would make no progress - father/mother set but unknown.
        for member in members:
            if (member.father not in (None, "", "0") and member.father not in member_names) or (
                member.mother not in (None, "", "0") and member.mother not in member_names
            ):
                raise ValueError("Unknown father/mother set but not in pedigree")

        # Process all pedigree members, building a map of member name to longest path.
        iteration = 0
        to_process = set(member_names)
        while len(result) < len(members):
            iteration += 1
            if iteration > len(members):
                raise ValueError("Infinite loop over pedigree members detected")

            to_remove = set()
            for member_name in to_process:
                member_obj = next((m for m in members if m.name == member_name), None)
                if not member_obj:
                    raise ValueError(f"Could not find member {member_name}")
                if (not member_obj.father or member_obj.father == "0") and (
                    not member_obj.mother or member_obj.mother == "0"
                ):
                    result[member_name] = 0
                    to_remove.add(member_name)
                elif (
                    member_obj.father
                    and result.get(member_obj.father) is not None
                    and member_obj.mother
                    and result.get(member_obj.mother) is not None
                ):
                    result[member_name] = (
                        max(
                            result.get(member_obj.father),
                            result.get(member_obj.mother),
                        )
                        + 1
                    )
                    to_remove.add(member_name)
            for member in to_remove:
                to_process.remove(member)

        return result

    @classmethod
    def _pick_index_from_pedigree(cls, *, pedigree: Pedigree) -> typing.Optional[str]:
        """Pick index from the pedigree.

        The following heuristic is used. In the case of more than one match, use the first one found.

        - Compute the longest path of the individual to a founder (individual without any parents).
        - Pick affected individual with the longest path.
        - If there are no affected individual, pick first unaffected with the longest path.
        """
        founder_path_lengths = cls._compute_founder_path_lengths(pedigree=pedigree)
        if not founder_path_lengths:
            raise ValueError("No individual in pedigree")

        longest_path_length = max(founder_path_lengths.values())
        first_longest_found: typing.Optional[str] = None
        for individual in typing.cast(typing.Iterable[Individual], pedigree.individual_set.all()):
            member_name = individual.name
            path_length = founder_path_lengths.get(member_name)
            if path_length == longest_path_length:
                if first_longest_found is None:
                    first_longest_found = member_name
                if individual.affected:
                    return member_name
        return first_longest_found

    @classmethod
    def _preset_choice_to_genotype_choice(
        cls,
        *,
        pedigree: Pedigree,
        genotypepresets: SeqvarsGenotypePresetsPydantic,
    ) -> list[SeqvarsSampleGenotypePydantic]:
        """Compute the genotype choice (for input to query engine) from pedigree and genotype
        presets choice.
        """

        members: list[Individual] = list(pedigree.individual_set.all())
        member_names = [m.name for m in members]
        is_affected: dict[str, bool] = {m.name: m.affected for m in members}
        index_name = cls._pick_index_from_pedigree(pedigree=pedigree)
        index = next((m for m in members if m.name == index_name), None)
        if not index:
            raise ValueError("Could not find index in pedigree")
        father_name = next(
            (m.name for m in members if m.name == index.father),
            None,
        )
        mother_name = next(
            (m.name for m in members if m.name == index.mother),
            None,
        )

        if genotypepresets.choice == SeqvarsGenotypePresetChoice.ANY:
            return [
                SeqvarsSampleGenotypePydantic(
                    sample=sample_name,
                    genotype=SeqvarsGenotypeChoice.ANY,
                    enabled=True,
                    include_no_call=False,
                )
                for sample_name in member_names
            ]
        elif genotypepresets.choice == SeqvarsGenotypePresetChoice.DE_NOVO:
            return [
                SeqvarsSampleGenotypePydantic(
                    sample=sample_name,
                    genotype=(
                        SeqvarsGenotypeChoice.VARIANT
                        if sample_name == index_name
                        else SeqvarsGenotypeChoice.REF
                    ),
                    enabled=True,
                    include_no_call=False,
                )
                for sample_name in member_names
            ]
        elif genotypepresets.choice == SeqvarsGenotypePresetChoice.DOMINANT:
            return [
                SeqvarsSampleGenotypePydantic(
                    sample=sample_name,
                    genotype=(
                        SeqvarsGenotypeChoice.HET
                        if is_affected.get(sample_name, False)
                        else SeqvarsGenotypeChoice.REF
                    ),
                    enabled=True,
                    include_no_call=False,
                )
                for sample_name in member_names
            ]
        elif genotypepresets.choice in [
            SeqvarsGenotypePresetChoice.HOMOZYGOUS_RECESSIVE,
            SeqvarsGenotypePresetChoice.COMPOUND_HETEROZYGOUS_RECESSIVE,
            SeqvarsGenotypePresetChoice.RECESSIVE,
            SeqvarsGenotypePresetChoice.X_RECESSIVE,
        ]:
            result = []
            for member_name in member_names:
                if member_name == index_name:
                    result.append(
                        SeqvarsSampleGenotypePydantic(
                            sample=member_name,
                            genotype=SeqvarsGenotypeChoice.RECESSIVE_INDEX,
                            enabled=True,
                            include_no_call=False,
                        )
                    )
                elif member_name == father_name:
                    result.append(
                        SeqvarsSampleGenotypePydantic(
                            sample=member_name,
                            genotype=SeqvarsGenotypeChoice.RECESSIVE_FATHER,
                            enabled=True,
                            include_no_call=False,
                        )
                    )
                elif member_name == mother_name:
                    result.append(
                        SeqvarsSampleGenotypePydantic(
                            sample=member_name,
                            genotype=SeqvarsGenotypeChoice.RECESSIVE_MOTHER,
                            enabled=True,
                            include_no_call=False,
                        )
                    )
                else:
                    result.append(
                        SeqvarsSampleGenotypePydantic(
                            sample=member_name,
                            genotype=SeqvarsGenotypeChoice.ANY,
                            enabled=True,
                            include_no_call=False,
                        )
                    )
            return result
        elif genotypepresets.choice == SeqvarsGenotypePresetChoice.AFFECTED_CARRIERS:
            return [
                SeqvarsSampleGenotypePydantic(
                    sample=sample_name,
                    genotype=(
                        SeqvarsGenotypeChoice.VARIANT
                        if is_affected.get(sample_name, False)
                        else SeqvarsGenotypeChoice.REF
                    ),
                    enabled=True,
                    include_no_call=False,
                )
                for sample_name in member_names
            ]
        else:
            raise ValueError(f"Unknown genotype presets choice: {genotypepresets.choice}")

    def from_presets(
        self,
        *,
        pedigree: Pedigree,
        querysettings: SeqvarsQuerySettings,
        genotypepresets: SeqvarsGenotypePresetsPydantic,
    ) -> "SeqvarsQuerySettingsGenotype":
        recessive_mode = (
            PRESETS_CHOICE_TO_RECESSIVE_MODE.get(
                genotypepresets.choice, SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_DISABLED
            ),
        )
        sample_genotype_choices = self.__class__._preset_choice_to_genotype_choice(
            pedigree=pedigree,
            genotypepresets=genotypepresets,
        )
        return super().create(
            querysettings=querysettings,
            recessive_mode=recessive_mode,
            sample_genotype_choices=sample_genotype_choices,
        )


class SeqvarsQuerySettingsGenotype(SeqvarsQuerySettingsCategoryBase):
    """Query settings for per-sample genotype filtration."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsGenotypeManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="genotype"
    )

    RECESSIVE_MODE_DISABLED = "disabled"
    RECESSIVE_MODE_COMPHET_RECESSIVE = "comphet_recessive"
    RECESSIVE_MODE_HOMOZYGOUS_RECESSIVE = "homozygous_recessive"
    RECESSIVE_MODE_RECESSIVE = "recessive"

    RECESSIVE_MODE_CHOICES = (
        (RECESSIVE_MODE_DISABLED, RECESSIVE_MODE_DISABLED),
        (RECESSIVE_MODE_COMPHET_RECESSIVE, RECESSIVE_MODE_COMPHET_RECESSIVE),
        (RECESSIVE_MODE_HOMOZYGOUS_RECESSIVE, RECESSIVE_MODE_HOMOZYGOUS_RECESSIVE),
        (RECESSIVE_MODE_RECESSIVE, RECESSIVE_MODE_RECESSIVE),
    )

    #: The recessive mode.
    recessive_mode = models.CharField(
        max_length=128,
        choices=RECESSIVE_MODE_CHOICES,
        default=RECESSIVE_MODE_DISABLED,
        null=False,
        blank=False,
    )

    #: Per-sample genotype choice.
    sample_genotype_choices = SchemaField(schema=list[SeqvarsSampleGenotypePydantic], default=list)

    def __str__(self):
        return f"SeqvarsQuerySettingsGenotype '{self.sodar_uuid}'"


class SeqvarsSampleQualityFilterPydantic(pydantic.BaseModel):
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


class SeqvarsQuerySettingsQualityManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        pedigree: Pedigree,
        querysettings: SeqvarsQuerySettings,
        qualitypresets: SeqvarsQueryPresetsQuality,
    ) -> "SeqvarsQuerySettingsQuality":
        return super().create(
            querysettings=querysettings,
            sample_quality_filters=[
                SeqvarsSampleQualityFilterPydantic(
                    sample=individual.name,
                    filter_active=qualitypresets.filter_active,
                    min_dp_het=qualitypresets.min_dp_het,
                    min_dp_hom=qualitypresets.min_dp_hom,
                    min_ab_het=qualitypresets.min_ab_het,
                    min_gq=qualitypresets.min_gq,
                    min_ad=qualitypresets.min_ad,
                    max_ad=qualitypresets.max_ad,
                )
                for individual in typing.cast(
                    typing.Iterable[Individual], pedigree.individual_set.all()
                )
            ],
        )


class SeqvarsQuerySettingsQuality(SeqvarsQuerySettingsCategoryBase):
    """Query settings for per-sample quality filtration."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsQualityManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="quality"
    )

    #: Per-sample quality settings.
    sample_quality_filters = SchemaField(
        schema=list[SeqvarsSampleQualityFilterPydantic], default=list
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsQuality '{self.sodar_uuid}'"


class SeqvarsQuerySettingsConsequenceManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        querysettings: SeqvarsQuerySettings,
        consequencepresets: SeqvarsQueryPresetsConsequence,
    ) -> "SeqvarsQuerySettingsConsequence":
        return super().create(
            querysettings=querysettings,
            variant_types=list(consequencepresets.variant_types),
            transcript_types=list(consequencepresets.transcript_types),
            variant_consequences=list(consequencepresets.variant_consequences),
            max_distance_to_exon=consequencepresets.max_distance_to_exon,
        )


class SeqvarsQuerySettingsConsequence(
    SeqvarsConsequenceSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Presets for consequence-related settings within a ``QuerySettingsSet``."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsConsequenceManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="consequence"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsConsequence '{self.sodar_uuid}'"


class SeqvarsQuerySettingsLocusManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        querysettings: SeqvarsQuerySettings,
        locuspresets: SeqvarsQueryPresetsLocus,
    ) -> "SeqvarsQuerySettingsLocus":
        return super().create(
            querysettings=querysettings,
            genes=copy_list(locuspresets.genes),
            gene_panels=copy_list(locuspresets.gene_panels),
            genome_regions=copy_list(locuspresets.genome_regions),
        )


class SeqvarsQuerySettingsLocus(SeqvarsLocusSettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Presets for locus-related settings within a ``QuerySettingsSet``."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsLocusManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="locus"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsLocus '{self.sodar_uuid}'"


class SeqvarsQuerySettingsFrequencyManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self, *, querysettings: SeqvarsQuerySettings, frequencypresets: SeqvarsQueryPresetsFrequency
    ) -> "SeqvarsQuerySettingsFrequency":
        return super().create(
            querysettings=querysettings,
            gnomad_exomes=copy_model(frequencypresets.gnomad_exomes),
            gnomad_genomes=copy_model(frequencypresets.gnomad_genomes),
            gnomad_mitochondrial=copy_model(frequencypresets.gnomad_mitochondrial),
            helixmtdb=copy_model(frequencypresets.helixmtdb),
            inhouse=copy_model(frequencypresets.inhouse),
        )


class SeqvarsQuerySettingsFrequency(SeqvarsFrequencySettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Query settings in the frequency category."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsFrequencyManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="frequency"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsFrequency '{self.sodar_uuid}'"


class SeqvarsQuerySettingsPhenotypePrioManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        querysettings: SeqvarsQuerySettings,
        phenotypepriopresets: SeqvarsQueryPresetsPhenotypePrio,
    ) -> "SeqvarsQuerySettingsPhenotypePrio":
        return super().create(
            querysettings=querysettings,
            phenotype_prio_enabled=phenotypepriopresets.phenotype_prio_enabled,
            phenotype_prio_algorithm=phenotypepriopresets.phenotype_prio_algorithm,
            terms=copy_list(phenotypepriopresets.terms),
        )


class SeqvarsQuerySettingsPhenotypePrio(
    SeqvarsPhenotypePrioSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Presets for phenotype priorization--related settings within a ``QueryPresetsSetVersion``."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsPhenotypePrioManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="phenotypeprio"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsPhenotypePrio '{self.sodar_uuid}'"


class SeqvarsQuerySettingsVariantPrioManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        querysettings: SeqvarsQuerySettings,
        variantpriopresets: SeqvarsQueryPresetsVariantPrio,
    ) -> "SeqvarsQuerySettingsVariantPrio":
        return super().create(
            querysettings=querysettings,
            services=copy_list(variantpriopresets.services),
        )


class SeqvarsQuerySettingsVariantPrio(
    SeqvarsVariantPrioSettingsBase, SeqvarsQuerySettingsCategoryBase
):
    """Query settings in the variant priorization category."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsVariantPrioManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="variantprio"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsVariantPrio '{self.sodar_uuid}'"


class SeqvarsQuerySettingsClinvarManager(models.Manager):
    """Custom manager that allows easy creation from presets."""

    def from_presets(
        self,
        *,
        querysettings: SeqvarsQuerySettings,
        clinvarpresets: SeqvarsQueryPresetsClinvar,
    ) -> "SeqvarsQuerySettingsClinvar":
        return super().create(
            querysettings=querysettings,
            clinvar_presence_required=clinvarpresets.clinvar_presence_required,
            clinvar_germline_aggregate_description=list(
                clinvarpresets.clinvar_germline_aggregate_description
            ),
            allow_conflicting_interpretations=clinvarpresets.allow_conflicting_interpretations,
        )


class SeqvarsQuerySettingsClinvar(SeqvarsClinvarSettingsBase, SeqvarsQuerySettingsCategoryBase):
    """Query settings in the variant priorization category."""

    #: Custom manager with ``from_presets()``.
    objects = SeqvarsQuerySettingsClinvarManager()

    #: The owning ``QuerySettings``.
    querysettings = models.OneToOneField(
        SeqvarsQuerySettings, on_delete=models.CASCADE, related_name="clinvar"
    )

    def __str__(self):
        return f"SeqvarsQuerySettingsClinvar '{self.sodar_uuid}'"


class SeqvarsQueryColumnsConfigManager(models.Manager):
    """Manager for ``SeqvarsQueryColumnsConfig``."""

    def from_predefinedquery(
        self,
        *,
        predefinedquery: SeqvarsPredefinedQuery,
    ) -> "SeqvarsQueryColumnsConfig":
        if predefinedquery.columns.column_settings:
            return super().create(
                column_settings=predefinedquery.columns.column_settings,
            )
        else:
            return super().create(column_settings=[])


class SeqvarsQueryColumnsConfig(SeqvarsColumnsSettingsBase, BaseModel):
    """Per-query (not execution) configuration of columns.

    This will be copied over from the presets to the query and not the query
    settings.  Thus, it will not be persisted by query execution but is
    editable after query execution.
    """

    #: Custom manager with ``from_predefinedquery()``.
    objects = SeqvarsQueryColumnsConfigManager()

    def __str__(self):
        return f"SeqvarsQueryColumnsConfig '{self.sodar_uuid}'"


class SeqvarsQueryManager(models.Manager):
    """Custom manager for ``SeqvarsQuery``.

    Specifically, adds functionality to create a new query from a predefined
    query.
    """

    @transaction.atomic
    def from_predefinedquery(
        self,
        *,
        session: CaseAnalysisSession,
        predefinedquery: SeqvarsPredefinedQuery,
        label: typing.Optional[str] = None,
    ) -> "SeqvarsQuery":
        """Create a new query from a predefined query."""
        query = SeqvarsQuery.objects.create(
            rank=self._pick_query_rank(session),
            label=label or predefinedquery.label,
            session=session,
            settings=SeqvarsQuerySettings.objects.from_predefinedquery(
                session=session, predefinedquery=predefinedquery
            ),
            columnsconfig=SeqvarsQueryColumnsConfig.objects.from_predefinedquery(
                predefinedquery=predefinedquery
            ),
        )
        return query

    def _pick_query_rank(self, session: CaseAnalysisSession) -> int:
        """Obtain a new rank for a query in ``session``."""
        rank = 1
        for query in session.seqvarsquery_set.all():
            if query.rank >= rank:
                rank = query.rank + 1
        return rank


class SeqvarsQuery(BaseModel):
    """Allows users to prepare seqvar queries for execution and execute them."""

    #: Override the manager so we can easily create from predefined queries.
    objects = SeqvarsQueryManager()

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


class SeqvarsRecessiveModeChoice(str, Enum):
    """Enumeration for the recessive mode in pydantic models."""

    #: Recessive mode is disabled.
    DISABLED = SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_DISABLED
    #: Compound heterozygous recessive mode.
    COMPHET_RECESSIVE = SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_COMPHET_RECESSIVE
    #: Homozygous recessive mode.
    HOMOZYGOUS_RECESSIVE = SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_HOMOZYGOUS_RECESSIVE
    #: Any recessive mode.
    RECESSIVE = SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_RECESSIVE

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsQuerySettingsGenotypePydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsGenotype``."""

    #: The recessive mode.
    recessive_mode: SeqvarsRecessiveModeChoice = SeqvarsRecessiveModeChoice.DISABLED
    #: Per-sample genotype choice.
    sample_genotypes: typing.List[SeqvarsSampleGenotypePydantic] = []


class SeqvarsSampleQualitySettingsPydantic(pydantic.BaseModel):
    """Quality settings for one sample."""

    #: Name of the sample filtered for.
    sample: str
    #: Drop whole variant on failure.
    filter_active: bool = False
    #: Minimal coverage for het. sites.
    min_dp_het: typing.Optional[int] = []
    #: Minimal coverage for hom. sites.
    min_dp_hom: typing.Optional[int] = []
    #: Minimal genotype quality.
    min_gq: typing.Optional[int] = []
    #: Minimal allele balance for het. variants.
    min_ab: typing.Optional[float] = []
    #: Minimal number of alternate reads.
    min_ad: typing.Optional[int] = []
    #: Maximal number of alternate reads.
    max_ad: typing.Optional[int] = []


class SeqvarsQuerySettingsQualityPydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsQuality``."""

    #: Per-sample quality settings.
    sample_quality_settings: typing.List[SeqvarsSampleQualitySettingsPydantic] = []


class SeqvarsNuclearFrequencySettingsPydantic(pydantic.BaseModel):
    """gnomAD and in-house nuclear filter options."""

    #: Whether to enable filtration by 1000 Genomes.
    enabled: bool = False
    #: Maximal number of in-house heterozygous carriers.
    heterozygous: typing.Optional[int] = None
    #: Maximal number of in-house homozygous carriers.
    homozygous: typing.Optional[int] = None
    #: Maximal number of in-house hemizygous carriers.
    hemizygous: typing.Optional[int] = None
    #: Maximal allele frequency.
    frequency: typing.Optional[float] = None


class SeqvarsGnomadMitochondrialFrequencySettingsPydantic(pydantic.BaseModel):
    """gnomAD mitochondrial filter options."""

    #: Whether to enable filtration by 1000 Genomes.
    enabled: bool = False
    #: Maximal number of heteroplasmic carriers.
    heteroplasmic: typing.Optional[int] = None
    #: Maximal number of homoplasmic carriers.
    homoplasmic: typing.Optional[int] = None
    #: Maximal allele frequency.
    frequency: typing.Optional[float] = None


class SeqvarsHelixMtDbFrequencySettingsPydantic(pydantic.BaseModel):
    """HelixMtDb filter options."""

    #: Whether to enable filtration by mtDB
    enabled: bool = False
    #: Maximal number of heterozygous carriers in HelixMtDb
    heteroplasmic: typing.Optional[int] = None
    #: Maximal number of homozygous carriers in HelixMtDb
    homoplasmic: typing.Optional[int] = None
    #: Maximal frequency in HelixMtDb
    frequency: typing.Optional[float] = None


class SeqvarsQuerySettingsFrequencyPydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsFrequency``."""

    #: gnomAD and in-house nuclear filter options.
    nuclear: typing.Optional[SeqvarsNuclearFrequencySettingsPydantic] = None
    #: gnomAD mitochondrial filter options.
    gnomad_mtdna: typing.Optional[SeqvarsGnomadMitochondrialFrequencySettingsPydantic] = None
    #: HelixMtDb filter options.
    helixmtdb: typing.Optional[SeqvarsHelixMtDbFrequencySettingsPydantic] = None


class SeqvarsQuerySettingsConsequencePydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsConsequence``."""

    #: The variant types.
    variant_types: typing.List[SeqvarsVariantTypeChoice] = []
    #: The transcript types.
    transcript_types: typing.List[SeqvarsTranscriptTypeChoice] = []
    #: The consequences.
    consequences: typing.List[SeqvarsVariantConsequenceChoice] = []
    #: Maximal distance to next exon.
    max_dist_to_exon: typing.Optional[int] = None


class SeqvarsQuerySettingsLocusPydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsLocus``."""

    #: List of HGNC identifiers for filtration to genes.
    genes: typing.List[str] = []
    #: List of genomic regions to limit restrict the resulting variants to.
    genome_regions: typing.List[GenomeRegionPydantic] = []


class SeqvarsQuerySettingsClinvarPydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsQuerySettingsClinvar``."""

    #: Whether to require ClinVar membership.
    presence_required: bool
    #: The ClinVar germline aggregate description to include.
    germline_descriptions: typing.List[ClinvarGermlineAggregateDescriptionChoice] = []
    #: Whether to include conflicting interpretation ClinVar variants.
    allow_conflicting_interpretations: bool = False


class SeqvarsCaseQueryPydantic(pydantic.BaseModel):
    """Pydantic representation of ``SeqvarsCaseQuery``."""

    #: Genotype query settings.
    genotype: typing.Optional[SeqvarsQuerySettingsGenotypePydantic] = None
    #: Quality query settings.
    quality: typing.Optional[SeqvarsQuerySettingsQualityPydantic] = None
    #: Frequency query settings.
    frequency: typing.Optional[SeqvarsQuerySettingsFrequencyPydantic] = None
    #: Consequence query settings.
    consequence: typing.Optional[SeqvarsQuerySettingsConsequencePydantic] = None
    #: Locus query settings.
    locus: typing.Optional[SeqvarsQuerySettingsLocusPydantic] = None
    #: ClinVar query settings.
    clinvar: typing.Optional[SeqvarsQuerySettingsClinvarPydantic] = None


class DataSourceInfoPydantic(pydantic.BaseModel):
    """Describes the version version of a given datasource."""

    #: The name.
    name: str
    #: The version.
    version: str


class DataSourceInfosPydantic(pydantic.BaseModel):
    """Container for ``DataSourceInfo`` records."""

    #: Information about the used datasources.
    infos: list[DataSourceInfoPydantic] = []


class GenomeReleaseChoice(str, Enum):
    """Enumeration of the genome release."""

    #: GRCh37.
    GRCH37 = "grch37"
    #: GRCh38.
    GRCH38 = "grch38"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class ResourcesUsedPydantic(pydantic.BaseModel):
    """Store resource usage information."""

    #: Start time.
    start_time: typing.Optional[datetime.datetime] = None
    #: End time.
    end_time: typing.Optional[datetime.datetime] = None
    #: RAM usage in bytes.
    memory_used: int = 0


class SeqvarsOutputStatisticsPydantic(pydantic.BaseModel):
    """Store statistics about the output."""

    #: Total number of records.
    count_total: int = 0
    #: Number of passed records.
    count_passed: int = 0
    #: Passed records by consequence.
    passed_by_consequences: dict[SeqvarsVariantConsequenceChoice, int] = {}


class SevarsVariantScoreColumnTypeChoice(str, Enum):
    """Enumeration of the variant score type."""

    #: Number
    NUMBER = "number"
    #: String
    STRING = "string"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class SeqvarsVariantScoreColumnPydantic(pydantic.BaseModel):
    """Store information about the variant score columns in the output."""

    #: Name of the scolumn.
    name: str
    #: Label for the scolumn.
    label: str
    #: Description of the scolumn.
    description: typing.Optional[str] = None
    #: Type of the scolumn.
    type: SevarsVariantScoreColumnTypeChoice


class SeqvarsOutputHeaderPydantic(pydantic.BaseModel):
    """Store meta information about the query results."""

    #: Genome release.
    genome_release: GenomeReleaseChoice
    #: Versions for each used database or software.
    versions: dict[str, str]
    #: The used query settings.
    query: typing.Optional[SeqvarsCaseQueryPydantic]
    #: Case UUID.
    case_uuid: str
    #: Resources used.
    resources: typing.Optional[ResourcesUsedPydantic]
    #: Statistics about results.
    statistics: typing.Optional[SeqvarsOutputStatisticsPydantic]
    #: Information about the variant scores in the output.
    variant_score_columns: list[SeqvarsVariantScoreColumnPydantic] = []


class SeqvarsVcfVariantPydantic(pydantic.BaseModel):
    """Store a single VCF variant."""

    #: Genome release.
    genome_release: GenomeReleaseChoice
    #: Chromosome, normalized.
    chrom: str
    #: Chromosome number for sorting.
    chrom_no: int
    #: 1-based position.
    pos: int
    #: Reference allele.
    ref_allele: str
    #: Alternative allele.
    alt_allele: str


class GeneIdentityPydantic(pydantic.BaseModel):
    """Store gene identity information."""

    #: HGNC ID.
    hgnc_id: str
    #: HGNC symbol.
    gene_symbol: str


class GeneRelatedConsequencesPydantic(pydantic.BaseModel):
    """Store gene-related consequences."""

    #: HGVS.c or HGVS.n code of the variant.
    hgvs_t: str
    #: HGVS.p code of the variant.
    hgvs_p: typing.Optional[str]
    #: Predicted variant consequences.
    consequences: list[SeqvarsVariantConsequenceChoice]


class GeneRelatedPhenotypesPydantic(pydantic.BaseModel):
    """Phenotype-related information, if any."""

    #: ACMG supplementary finding list.
    is_acmg_sf: bool = False
    #: Whether is a known disease gene.
    is_disease_gene: bool = False


class GnomadConstraintsPydantic(pydantic.BaseModel):
    """Store gnomAD constraints."""

    #: Mis_z score.
    mis_z: float
    #: Oe_lof score.
    oe_lof: float
    #: Oe_lof_lower score.
    oe_lof_lower: float
    #: Oe_lof_upper score (LOEF).
    oe_lof_upper: float
    #: Oe_mis score.
    oe_mis: float
    #: Oe_mis_lower score.
    oe_mis_lower: float
    #: Oe_mis_upper score.
    oe_mis_upper: float
    #: PLI score.
    pli: float
    #: Syn_z score.
    syn_z: float


class DecipherConstraintsPydantic(pydantic.BaseModel):
    """Store DECIPHER constraints."""

    #: HI percentile.
    hi_percentile: float
    #: HI raw score.
    hi_index: float


class RcnvConstraintsPydantic(pydantic.BaseModel):
    """Store RCNV constraints."""

    #: Haploinsufficiency score.
    p_haplo: float
    #: Triplosensitivity score.
    p_triplo: float


class ShetConstraintsPydantic(pydantic.BaseModel):
    """Store sHET constraints."""

    #: sHET score.
    s_het: float


class ClingenDosageScoreChoice(str, Enum):
    """Enumeration of the Clingen dosage score."""

    #: Sufficient evidence for dosage pathogenicity.
    SUFFICIENT_EVIDENCE_AVAILABLE = "sufficient_evidence_available"
    #: Some evidence for dosage pathogenicity.
    SOME_EVIDENCE_AVAILABLE = "some_evidence_available"
    #: Little evidence for dosage pathogenicity.
    LITTLE_EVIDENCE = "little_evidence"
    #: No evidence available.
    NO_EVIDENCE_AVAILABLE = "no_evidence_available"
    #: Gene associated with autosomal recessive phenotype.
    RECESSIVE = "recessive"
    #: Dosage sensitivity unlikely.
    UNLIKELY = "unlikely"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class ClingenDosageAnnotationPydantic(pydantic.BaseModel):
    """Store Clingen dosage annotation."""

    #: Haploinsufficiency score.
    haplo: ClingenDosageScoreChoice
    #: Triplosensitivity score.
    triplo: ClingenDosageScoreChoice


class GeneRelatedConstraintsPydantic(pydantic.BaseModel):
    """Gene-wise constraints."""

    #: gnomAD constraints
    gnomad: typing.Optional[GnomadConstraintsPydantic] = None
    #: DECIPHER constraints
    decipher: typing.Optional[DecipherConstraintsPydantic] = None
    #: RCNV constraints
    rcnv: typing.Optional[RcnvConstraintsPydantic] = None
    #: sHET constraints
    shet: typing.Optional[ShetConstraintsPydantic] = None
    #: ClinGen dosage annotation
    clingen: typing.Optional[ClingenDosageAnnotationPydantic] = None


class GeneRelatedAnnotationPydantic(pydantic.BaseModel):
    """Store gene-related annotation (always for a single gene)."""

    #: Gene ID information.
    identity: GeneIdentityPydantic
    #: Gene-related consequences, if any (none if intergenic).
    consequences: GeneRelatedConsequencesPydantic
    #: Gene-related phenotype information, if any.
    phenotypes: GeneRelatedPhenotypesPydantic
    #: Gene-wise constraints on the gene, if any.
    constraints: GeneRelatedConstraintsPydantic


class SeqvarsNuclearFrequencyPydantic(pydantic.BaseModel):
    """Store gnomAD and in-house nuclear frequency information."""

    #: Number of covered alleles.
    an: int = 0
    #: Number of heterozygous carriers.
    het: int = 0
    #: Number of homozygous carriers.
    homalt: int = 0
    #: Number of hemizygous carriers.
    hemialt: int = 0
    #: Allele frequency.
    af: float = 0.0


class SeqvarsGnomadMitochondrialFrequencyPydantic(pydantic.BaseModel):
    """Store gnomAD mitochondrial frequency information."""

    #: Number of covered alleles.
    an: int = 0
    #: Number of heteroplasmic carriers.
    het: int = 0
    #: Number of homoplasmic carriers.
    homalt: int = 0
    #: Allele frequency.
    af: float = 0.0


class SeqvarsHelixMtDbFrequencyPydantic(pydantic.BaseModel):
    """Store HelixMtDb frequency information."""

    #: Number of covered alleles.
    an: int = 0
    #: Number of heterozygous carriers in HelixMtDb.
    het: int = 0
    #: Number of homozygous carriers in HelixMtDb.
    homalt: int = 0
    #: Frequency in HelixMtDb.
    af: float = 0.0


class SeqvarsFrequencyAnnotationPydantic(pydantic.BaseModel):
    """SPopulation frequency information"""

    #: gnomAD exomes filter.
    gnomad_exomes: typing.Optional[SeqvarsNuclearFrequencyPydantic] = None
    #: gnomAD genomes filter.
    gnomad_genomes: typing.Optional[SeqvarsNuclearFrequencyPydantic] = None
    #: gnomAD MT filter.
    gnomad_mtdna: typing.Optional[SeqvarsGnomadMitochondrialFrequencyPydantic] = None
    #: HelixMtDb filter.
    helixmtdb: typing.Optional[SeqvarsHelixMtDbFrequencyPydantic] = None
    #: In-house filter.
    inhouse: typing.Optional[SeqvarsNuclearFrequencyPydantic] = None


class SeqvarsDbIdsPydantic(pydantic.BaseModel):
    """Store database identifiers."""

    #: dbSNP ID.
    dbsnp_id: typing.Optional[str] = None


class ClinvarAggregateGermlineReviewStatusChoice(str, Enum):
    """Enumeration describing aggregate germline review status value."""

    #: No classification provided.
    NO_CLASSIFICATION_PROVIDED = "no_classification_provided"
    #: No assertion criteria provided.
    NO_ASSERTION_CRITERIA_PROVIDED = "no_assertion_criteria_provided"
    #: Criteria provided, single submitter.
    CRITERIA_PROVIDED_SINGLE_SUBMITTER = "criteria_provided_single_submitter"
    #: Criteria provided, multiple submitters, no conflicts.
    CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS = (
        "criteria_provided_multiple_submitters_no_conflicts"
    )
    #: Criteria provided, conflicting classifications.
    CRITERIA_PROVIDED_CONFLICTING_CLASSIFICATIONS = "criteria_provided_conflicting_classifications"
    #: Reviewed by expert panel.
    REVIEWED_BY_EXPERT_PANEL = "reviewed_by_expert_panel"
    #: Practice guideline.
    PRACTICE_GUIDELINE = "practice_guideline"
    #: No classifications from unflagged records.
    NO_CLASSIFICATIONS_FROM_UNFLAGGED_RECORDS = "no_classifications_from_unflagged_records"
    #: No classification for the single variant.
    NO_CLASSIFICATION_FOR_THE_SINGLE_VARIANT = "no_classification_for_the_single_variant"

    @classmethod
    def values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))


class ClinvarAnnotationPydantic(pydantic.BaseModel):
    """Store ClinVar-related annotation."""

    #: VCV accession.
    vcv_accession: str
    #: Aggregate germline significance description.
    germline_significance_description: str
    #: Aggregate germline review status.
    germline_review_status: ClinvarAggregateGermlineReviewStatusChoice
    #: Effective (aka "worst") germline significance description.
    effective_germline_significance_description: str


class SeqvarsScoreAnnotationsPydantic(pydantic.BaseModel):
    """Store the score annotations."""

    #: The score entries.
    entries: dict[str, str | int | float | None] = {}


class SeqvarsVariantRelatedAnnotationPydantic(pydantic.BaseModel):
    """Store variant-related annotation."""

    #: Database identifiers.
    dbids: typing.Optional[SeqvarsDbIdsPydantic] = None
    #: Frequency annotation.
    frequency: typing.Optional[SeqvarsFrequencyAnnotationPydantic] = None
    #: ClinVar annotation.
    clinvar: typing.Optional[ClinvarAnnotationPydantic] = None
    #: Score annotations.
    scores: typing.Optional[SeqvarsScoreAnnotationsPydantic] = None


class SeqvarsSampleCallInfoPydantic(pydantic.BaseModel):
    """Store call-related annotation."""

    #: Sample name.
    sample: str
    #: Genotype.
    genotype: typing.Optional[str] = None
    #: Depth of coverage.
    dp: typing.Optional[int] = None
    #: Alternate read depth.
    ad: typing.Optional[int] = None
    #: Genotype quality.
    gq: typing.Optional[float] = None
    #: Phase set ID.
    ps: typing.Optional[int] = None


class SeqvarsCallRelatedAnnotationPydantic(pydantic.BaseModel):
    """Store call-related annotation."""

    #: Call information for each sample.
    call_infos: dict[str, SeqvarsSampleCallInfoPydantic] = {}


class SeqvarsVariantAnnotationPydantic(pydantic.BaseModel):
    """Store the variant annotation payload (always for a single gene)."""

    #: Gene-related annotation.
    gene: typing.Optional[GeneRelatedAnnotationPydantic] = None
    #: Variant-related annotation.
    variant: typing.Optional[SeqvarsVariantRelatedAnnotationPydantic] = None
    #: Call-related annotation.
    call: typing.Optional[SeqvarsCallRelatedAnnotationPydantic] = None


class SeqvarsOutputRecordPydantic(pydantic.BaseModel):
    """Store a single output record."""

    #: UUID of the record.
    uuid: str
    #: Case UUID.
    case_uuid: str
    #: The description.
    vcf_variant: typing.Optional[SeqvarsVcfVariantPydantic]
    #: The variant annotation payload.
    variant_annotation: typing.Optional[SeqvarsVariantAnnotationPydantic]


class SeqvarsResultSet(BaseModel):
    """Store result rows and version information about the query."""

    #: The owning query execution.
    queryexecution = models.ForeignKey(SeqvarsQueryExecution, on_delete=models.CASCADE)
    #: The number of rows in the result.
    result_row_count = models.IntegerField(null=False, blank=False)
    #: Information about the data sources and versions used in the query, backed by
    #: pydantic model ``DataSourceInfos``.
    datasource_infos = SchemaField(
        schema=typing.Optional[DataSourceInfosPydantic], default=None, null=True
    )
    #: The output header record as written by `seqvars query` into first line.
    output_header = SchemaField(
        schema=typing.Optional[SeqvarsOutputHeaderPydantic], default=None, null=True
    )

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


class SeqvarsResultRow(models.Model):
    """One entry in the result set."""

    #: UUID used in URLs.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True)

    #: The owning result set.
    resultset = models.ForeignKey(SeqvarsResultSet, on_delete=models.CASCADE)

    #: Genome build
    genome_release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chrom = models.CharField(max_length=32)
    #: Chromosome as number
    chrom_no = models.IntegerField()
    #: 1-based variant position.
    pos = models.IntegerField()
    #: Variant coordinates - reference
    ref_allele = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alt_allele = models.CharField(max_length=512)

    #: The payload of the result row, backed by pydantic model
    #: ``ResultRowPayload``.
    payload = SchemaField(
        schema=typing.Optional[SeqvarsOutputRecordPydantic], default=None, null=True
    )

    def __str__(self):
        return (
            f"SeqvarsResultRow '{self.sodar_uuid}' '{self.genome_release}-{self.chrom}-"
            f"{self.pos}-{self.ref_allele}-{self.alt_allele}'"
        )
