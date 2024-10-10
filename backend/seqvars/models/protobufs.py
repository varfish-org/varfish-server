"""Helpers for conversion from query models to protobufs."""

import datetime
from typing import Optional

from google.protobuf.struct_pb2 import Value

from seqvars.models.base import (
    ClingenDosageAnnotationPydantic,
    ClingenDosageScoreChoice,
    ClinvarAggregateGermlineReviewStatusChoice,
    ClinvarAnnotationPydantic,
    ClinvarGermlineAggregateDescriptionChoice,
    DecipherConstraintsPydantic,
    GeneIdentityPydantic,
    GeneRelatedAnnotationPydantic,
    GeneRelatedConsequencesPydantic,
    GeneRelatedConstraintsPydantic,
    GeneRelatedPhenotypesPydantic,
    GenomeRegionPydantic,
    GenomeReleaseChoice,
    GnomadConstraintsPydantic,
    OneBasedRangePydantic,
    RcnvConstraintsPydantic,
    ResourcesUsedPydantic,
    SeqvarsCallRelatedAnnotationPydantic,
    SeqvarsCaseQueryPydantic,
    SeqvarsDbIdsPydantic,
    SeqvarsFrequencyAnnotationPydantic,
    SeqvarsGenotypeChoice,
    SeqvarsGnomadMitochondrialFrequencyPydantic,
    SeqvarsGnomadMitochondrialFrequencySettingsPydantic,
    SeqvarsHelixMtDbFrequencyPydantic,
    SeqvarsHelixMtDbFrequencySettingsPydantic,
    SeqvarsModeOfInheritance,
    SeqvarsNuclearFrequencyPydantic,
    SeqvarsNuclearFrequencySettingsPydantic,
    SeqvarsOutputHeaderPydantic,
    SeqvarsOutputRecordPydantic,
    SeqvarsOutputStatisticsPydantic,
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsClinvar,
    SeqvarsQuerySettingsClinvarPydantic,
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsConsequencePydantic,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsFrequencyPydantic,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsGenotypePydantic,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsLocusPydantic,
    SeqvarsQuerySettingsQuality,
    SeqvarsQuerySettingsQualityPydantic,
    SeqvarsRecessiveModeChoice,
    SeqvarsSampleCallInfoPydantic,
    SeqvarsSampleGenotypePydantic,
    SeqvarsSampleQualityFilterPydantic,
    SeqvarsSampleQualitySettingsPydantic,
    SeqvarsScoreAnnotationsPydantic,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantAnnotationPydantic,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantRelatedAnnotationPydantic,
    SeqvarsVariantScoreColumnPydantic,
    SeqvarsVariantScoreColumnTypeChoice,
    SeqvarsVariantTypeChoice,
    SeqvarsVcfVariantPydantic,
    ShetConstraintsPydantic,
)
from seqvars.protos.output_pb2 import (
    AggregateGermlineReviewStatus,
    CallRelatedAnnotation,
    ClingenDosageAnnotation,
    ClingenDosageScore,
    ClinvarAnnotation,
    DbIds,
    DecipherConstraints,
    FrequencyAnnotation,
    GeneIdentity,
    GeneRelatedAnnotation,
    GeneRelatedConsequences,
    GeneRelatedConstraints,
    GeneRelatedPhenotypes,
    GenomeRelease,
    GnomadConstraints,
    GnomadMitochondrialFrequency,
    HelixMtDbFrequency,
    ModeOfInheritance,
    NuclearFrequency,
    OutputHeader,
    OutputRecord,
    OutputStatistics,
    ResourcesUsed,
    SampleCallInfo,
    ScoreAnnotations,
    ShetConstraints,
    VariantAnnotation,
    VariantRelatedAnnotation,
    VariantScoreColumn,
    VariantScoreColumnType,
    VcfVariant,
    VersionEntry,
)
from seqvars.protos.query_pb2 import (
    CaseQuery,
    ClinvarGermlineAggregateDescription,
    Consequence,
    GenomicRegion,
    GenotypeChoice,
    GnomadMitochondrialFrequencySettings,
    HelixMtDbFrequencySettings,
    NuclearFrequencySettings,
    QuerySettingsClinVar,
    QuerySettingsConsequence,
    QuerySettingsFrequency,
    QuerySettingsGenotype,
    QuerySettingsLocus,
    QuerySettingsQuality,
    Range,
    RecessiveMode,
    SampleGenotypeChoice,
    SampleQualitySettings,
    TranscriptType,
    VariantType,
)

SEQVARS_GENOTYPE_CHOICE_MAPPING_TO_PB: dict[SeqvarsGenotypeChoice, GenotypeChoice.ValueType] = {
    SeqvarsGenotypeChoice.ANY: GenotypeChoice.GENOTYPE_CHOICE_ANY,
    SeqvarsGenotypeChoice.REF: GenotypeChoice.GENOTYPE_CHOICE_REF,
    SeqvarsGenotypeChoice.HET: GenotypeChoice.GENOTYPE_CHOICE_HET,
    SeqvarsGenotypeChoice.HOM: GenotypeChoice.GENOTYPE_CHOICE_HOM,
    SeqvarsGenotypeChoice.NON_HET: GenotypeChoice.GENOTYPE_CHOICE_NON_HET,
    SeqvarsGenotypeChoice.NON_HOM: GenotypeChoice.GENOTYPE_CHOICE_NON_HOM,
    SeqvarsGenotypeChoice.VARIANT: GenotypeChoice.GENOTYPE_CHOICE_VARIANT,
    SeqvarsGenotypeChoice.RECESSIVE_INDEX: GenotypeChoice.GENOTYPE_CHOICE_RECESSIVE_INDEX,
    SeqvarsGenotypeChoice.RECESSIVE_FATHER: GenotypeChoice.GENOTYPE_CHOICE_RECESSIVE_FATHER,
    SeqvarsGenotypeChoice.RECESSIVE_MOTHER: GenotypeChoice.GENOTYPE_CHOICE_RECESSIVE_MOTHER,
}


def _genotype_choice_to_protobuf(
    sample_genotype: SeqvarsSampleGenotypePydantic,
) -> SampleGenotypeChoice:
    return SampleGenotypeChoice(
        sample=sample_genotype.sample,
        genotype=SEQVARS_GENOTYPE_CHOICE_MAPPING_TO_PB[sample_genotype.genotype],
        include_no_call=sample_genotype.include_no_call,
        enabled=sample_genotype.enabled,
    )


SEQVARS_RECESSIVE_MODE_MAPPING_TO_PB: dict[SeqvarsRecessiveModeChoice, RecessiveMode.ValueType] = {
    SeqvarsRecessiveModeChoice.DISABLED: RecessiveMode.RECESSIVE_MODE_DISABLED,
    SeqvarsRecessiveModeChoice.COMPHET_RECESSIVE: RecessiveMode.RECESSIVE_MODE_COMPOUND_HETEROZYGOUS,
    SeqvarsRecessiveModeChoice.HOMOZYGOUS_RECESSIVE: RecessiveMode.RECESSIVE_MODE_HOMOZYGOUS,
    SeqvarsRecessiveModeChoice.RECESSIVE: RecessiveMode.RECESSIVE_MODE_ANY,
}


def _genotype_to_protobuf(genotype: SeqvarsQuerySettingsGenotype) -> QuerySettingsGenotype:
    return QuerySettingsGenotype(
        recessive_mode=SEQVARS_RECESSIVE_MODE_MAPPING_TO_PB[genotype.recessive_mode],
        sample_genotypes=[
            _genotype_choice_to_protobuf(sample_genotype)
            for sample_genotype in genotype.sample_genotype_choices
        ],
    )


def _sample_quality_to_protobuf(
    sample_quality: SeqvarsSampleQualityFilterPydantic,
) -> SampleQualitySettings:
    return SampleQualitySettings(
        sample=sample_quality.sample,
        filter_active=sample_quality.filter_active,
        min_dp_het=sample_quality.min_dp_het,
        min_dp_hom=sample_quality.min_dp_hom,
        min_ab=sample_quality.min_ab_het,
        min_gq=sample_quality.min_gq,
        min_ad=sample_quality.min_ad,
        max_ad=sample_quality.max_ad,
    )


def _quality_to_protobuf(quality: SeqvarsQuerySettingsQuality) -> QuerySettingsQuality:
    return QuerySettingsQuality(
        sample_qualities=list(map(_sample_quality_to_protobuf, quality.sample_quality_filters)),
    )


def _frequency_to_protobuf(frequency: SeqvarsQuerySettingsFrequency) -> QuerySettingsFrequency:
    return QuerySettingsFrequency(
        gnomad_exomes=NuclearFrequencySettings(
            enabled=frequency.gnomad_exomes.enabled,
            heterozygous=frequency.gnomad_exomes.heterozygous,
            homozygous=frequency.gnomad_exomes.homozygous,
            hemizygous=frequency.gnomad_exomes.hemizygous,
            frequency=frequency.gnomad_exomes.frequency,
        ),
        gnomad_genomes=NuclearFrequencySettings(
            enabled=frequency.gnomad_genomes.enabled,
            heterozygous=frequency.gnomad_genomes.heterozygous,
            homozygous=frequency.gnomad_genomes.homozygous,
            hemizygous=frequency.gnomad_genomes.hemizygous,
            frequency=frequency.gnomad_genomes.frequency,
        ),
        gnomad_mtdna=GnomadMitochondrialFrequencySettings(
            enabled=frequency.gnomad_mitochondrial.enabled,
            heteroplasmic=frequency.gnomad_mitochondrial.heteroplasmic,
            homoplasmic=frequency.gnomad_mitochondrial.homoplasmic,
            frequency=frequency.gnomad_mitochondrial.frequency,
        ),
        helixmtdb=HelixMtDbFrequencySettings(
            enabled=frequency.helixmtdb.enabled,
            heteroplasmic=frequency.helixmtdb.heteroplasmic,
            homoplasmic=frequency.helixmtdb.homoplasmic,
            frequency=frequency.helixmtdb.frequency,
        ),
        inhouse=NuclearFrequencySettings(
            enabled=frequency.inhouse.enabled,
            heterozygous=frequency.inhouse.heterozygous,
            homozygous=frequency.inhouse.homozygous,
            hemizygous=frequency.inhouse.hemizygous,
            frequency=frequency.inhouse.frequency,
        ),
    )


SEQVARS_VARIANT_TYPE_MAPPING_TO_PB: dict[SeqvarsVariantTypeChoice, VariantType.ValueType] = {
    SeqvarsVariantTypeChoice.SNV: VariantType.VARIANT_TYPE_SNV,
    SeqvarsVariantTypeChoice.INDEL: VariantType.VARIANT_TYPE_INDEL,
    SeqvarsVariantTypeChoice.MNV: VariantType.VARIANT_TYPE_MNV,
    SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION: VariantType.VARIANT_TYPE_COMPLEX_SUBSTITUTION,
}

SEQVARS_TRANSCRIPT_TYPE_MAPPING_TO_PB: dict[
    SeqvarsTranscriptTypeChoice : TranscriptType.ValueType
] = {
    SeqvarsTranscriptTypeChoice.CODING: TranscriptType.TRANSCRIPT_TYPE_CODING,
    SeqvarsTranscriptTypeChoice.NON_CODING: TranscriptType.TRANSCRIPT_TYPE_NON_CODING,
}


SEQVARS_VARIANT_CONSEQUENCE_MAPPING_TO_PB: dict[
    SeqvarsVariantConsequenceChoice : Consequence.ValueType
] = {
    SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION: Consequence.CONSEQUENCE_TRANSCRIPT_ABLATION,
    SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT: Consequence.CONSEQUENCE_EXON_LOSS_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT: Consequence.CONSEQUENCE_SPLICE_ACCEPTOR_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT: Consequence.CONSEQUENCE_SPLICE_DONOR_VARIANT,
    SeqvarsVariantConsequenceChoice.STOP_GAINED: Consequence.CONSEQUENCE_STOP_GAINED,
    SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT: Consequence.CONSEQUENCE_FRAMESHIFT_VARIANT,
    SeqvarsVariantConsequenceChoice.STOP_LOST: Consequence.CONSEQUENCE_STOP_LOST,
    SeqvarsVariantConsequenceChoice.START_LOST: Consequence.CONSEQUENCE_START_LOST,
    SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION: Consequence.CONSEQUENCE_TRANSCRIPT_AMPLIFICATION,
    SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION: Consequence.CONSEQUENCE_FEATURE_ELONGATION,
    SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION: Consequence.CONSEQUENCE_FEATURE_TRUNCATION,
    SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION: Consequence.CONSEQUENCE_DISRUPTIVE_INFRAME_INSERTION,
    SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION: Consequence.CONSEQUENCE_DISRUPTIVE_INFRAME_DELETION,
    SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION: Consequence.CONSEQUENCE_CONSERVATIVE_INFRAME_INSERTION,
    SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION: Consequence.CONSEQUENCE_CONSERVATIVE_INFRAME_DELETION,
    SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT: Consequence.CONSEQUENCE_MISSENSE_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT: Consequence.CONSEQUENCE_SPLICE_DONOR_FIFTH_BASE_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT: Consequence.CONSEQUENCE_SPLICE_REGION_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT: Consequence.CONSEQUENCE_SPLICE_DONOR_REGION_VARIANT,
    SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT: Consequence.CONSEQUENCE_SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
    SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT: Consequence.CONSEQUENCE_START_RETAINED_VARIANT,
    SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT: Consequence.CONSEQUENCE_STOP_RETAINED_VARIANT,
    SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT: Consequence.CONSEQUENCE_SYNONYMOUS_VARIANT,
    SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT: Consequence.CONSEQUENCE_CODING_SEQUENCE_VARIANT,
    SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT: Consequence.CONSEQUENCE_MATURE_MIRNA_VARIANT,
    SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT: Consequence.CONSEQUENCE_FIVE_PRIME_UTR_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT: Consequence.CONSEQUENCE_FIVE_PRIME_UTR_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT: Consequence.CONSEQUENCE_THREE_PRIME_UTR_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT: Consequence.CONSEQUENCE_THREE_PRIME_UTR_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT: Consequence.CONSEQUENCE_NON_CODING_TRANSCRIPT_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT: Consequence.CONSEQUENCE_NON_CODING_TRANSCRIPT_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT: Consequence.CONSEQUENCE_UPSTREAM_GENE_VARIANT,
    SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT: Consequence.CONSEQUENCE_DOWNSTREAM_GENE_VARIANT,
    SeqvarsVariantConsequenceChoice.TFBS_ABLATION: Consequence.CONSEQUENCE_TFBS_ABLATION,
    SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION: Consequence.CONSEQUENCE_TFBS_AMPLIFICATION,
    SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT: Consequence.CONSEQUENCE_TF_BINDING_SITE_VARIANT,
    SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION: Consequence.CONSEQUENCE_REGULATORY_REGION_ABLATION,
    SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION: Consequence.CONSEQUENCE_REGULATORY_REGION_AMPLIFICATION,
    SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT: Consequence.CONSEQUENCE_REGULATORY_REGION_VARIANT,
    SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT: Consequence.CONSEQUENCE_INTERGENIC_VARIANT,
    SeqvarsVariantConsequenceChoice.INTRON_VARIANT: Consequence.CONSEQUENCE_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.GENE_VARIANT: Consequence.CONSEQUENCE_GENE_VARIANT,
}


def _consequence_to_protobuf(
    consequence: SeqvarsQuerySettingsConsequence,
) -> QuerySettingsConsequence:
    return QuerySettingsConsequence(
        variant_types=[SEQVARS_VARIANT_TYPE_MAPPING_TO_PB[vt] for vt in consequence.variant_types],
        transcript_types=[
            SEQVARS_TRANSCRIPT_TYPE_MAPPING_TO_PB[tt] for tt in consequence.transcript_types
        ],
        consequences=[
            SEQVARS_VARIANT_CONSEQUENCE_MAPPING_TO_PB[csq]
            for csq in consequence.variant_consequences
        ],
        max_dist_to_exon=consequence.max_distance_to_exon,
    )


def _locus_to_protobuf(locus: SeqvarsQuerySettingsLocus) -> QuerySettingsLocus:
    # TODO: map genes in ``locus.gene_panels``!
    QuerySettingsLocus(
        genes=[gene.hgnc_id for gene in locus.genes],
        genome_regions=[
            GenomicRegion(
                chromosome=region.chromosome,
                range=(
                    None
                    if region.range is None
                    else Range(start=region.range.start, end=region.range.end)
                ),
            )
            for region in locus.genome_regions
        ],
    )


CLINVAR_AGG_DESC_MAPPING_TO_PB: dict[
    ClinvarGermlineAggregateDescriptionChoice, ClinvarGermlineAggregateDescription.ValueType
] = {
    ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC: ClinvarGermlineAggregateDescription.CLINVAR_GERMLINE_AGGREGATE_DESCRIPTION_PATHOGENIC,
    ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC: ClinvarGermlineAggregateDescription.CLINVAR_GERMLINE_AGGREGATE_DESCRIPTION_LIKELY_PATHOGENIC,
    ClinvarGermlineAggregateDescriptionChoice.UNCERTAIN_SIGNIFICANCE: ClinvarGermlineAggregateDescription.CLINVAR_GERMLINE_AGGREGATE_DESCRIPTION_UNCERTAIN_SIGNIFICANCE,
    ClinvarGermlineAggregateDescriptionChoice.LIKELY_BENIGN: ClinvarGermlineAggregateDescription.CLINVAR_GERMLINE_AGGREGATE_DESCRIPTION_LIKELY_BENIGN,
    ClinvarGermlineAggregateDescriptionChoice.BENIGN: ClinvarGermlineAggregateDescription.CLINVAR_GERMLINE_AGGREGATE_DESCRIPTION_BENIGN,
}


def _clinvar_to_protobuf(clinvar: SeqvarsQuerySettingsClinvar) -> QuerySettingsClinVar:
    return QuerySettingsClinVar(
        presence_required=clinvar.clinvar_presence_required,
        germline_descriptions=[
            CLINVAR_AGG_DESC_MAPPING_TO_PB[desc]
            for desc in clinvar.clinvar_germline_aggregate_description
        ],
        allow_conflicting_interpretations=clinvar.allow_conflicting_interpretations,
    )


def querysettings_to_protobuf(settings: SeqvarsQuerySettings) -> CaseQuery:
    """Convert a ``SeqvarsQuerySettings`` model to a ``CaseQuery`` protobuf."""
    return CaseQuery(
        genotype=_genotype_to_protobuf(settings.genotype),
        quality=_quality_to_protobuf(settings.quality),
        frequency=_frequency_to_protobuf(settings.frequency),
        consequence=_consequence_to_protobuf(settings.consequence),
        locus=_locus_to_protobuf(settings.locus),
        clinvar=_clinvar_to_protobuf(settings.clinvar),
    )


GENOME_RELEASE_MAPPING: dict[GenomeRelease.ValueType, GenomeReleaseChoice] = {
    GenomeRelease.GENOME_RELEASE_GRCH37: GenomeReleaseChoice.GRCH37,
    GenomeRelease.GENOME_RELEASE_GRCH38: GenomeReleaseChoice.GRCH38,
}


def _genome_release_choice_from_protobuf(
    genome_release: GenomeRelease.ValueType,
) -> GenomeReleaseChoice:
    return GENOME_RELEASE_MAPPING[genome_release]


def _versions_from_protobuf(versions: list[VersionEntry]) -> dict[str, str]:
    return {version.name: version.version for version in versions}


SEQVARS_GENOTYPE_CHOICE_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in SEQVARS_GENOTYPE_CHOICE_MAPPING_TO_PB.items()
}


def _seqvars_genotype_choice_from_protobuf(
    genotype: GenotypeChoice.ValueType,
) -> SeqvarsGenotypeChoice:
    return SEQVARS_GENOTYPE_CHOICE_MAPPING_FROM_PB[genotype]


def _seqvars_sample_genotype_from_protobuf(
    sample_genotype: SampleGenotypeChoice,
) -> SeqvarsSampleGenotypePydantic:
    return SeqvarsSampleGenotypePydantic(
        sample=sample_genotype.sample,
        genotype=(_seqvars_genotype_choice_from_protobuf(sample_genotype.genotype)),
        include_no_call=sample_genotype.include_no_call,
        enabled=sample_genotype.enabled,
    )


SEQVARS_RECESSIVE_MODE_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in SEQVARS_RECESSIVE_MODE_MAPPING_TO_PB.items()
}


def _seqvars_recessive_mode_choice_from_protobuf(
    genotype: GenotypeChoice.ValueType,
) -> SeqvarsGenotypeChoice:
    return SEQVARS_RECESSIVE_MODE_MAPPING_FROM_PB[genotype]


def _seqvars_query_settings_genotype_from_protobuf(
    genotype: QuerySettingsGenotype,
) -> SeqvarsQuerySettingsGenotypePydantic:
    return SeqvarsQuerySettingsGenotypePydantic(
        recessive_mode=(_seqvars_recessive_mode_choice_from_protobuf(genotype.recessive_mode)),
        sample_genotype=[
            _seqvars_sample_genotype_from_protobuf(sample_genotype)
            for sample_genotype in genotype.sample_genotypes
        ],
    )


def _seqvars_sample_quality_settings_from_protobuf(
    sample_quality: SampleQualitySettings,
) -> SeqvarsSampleQualitySettingsPydantic:
    return SeqvarsSampleQualitySettingsPydantic(
        sample=sample_quality.sample,
        filter_active=sample_quality.filter_active,
        min_dp_het=sample_quality.min_dp_het,
        min_dp_hom=sample_quality.min_dp_hom,
        min_gq=sample_quality.min_gq,
        min_ab=sample_quality.min_ab,
        min_ad=sample_quality.min_ad,
        max_ad=sample_quality.max_ad,
    )


def _seqvars_query_settings_quality_from_protobuf(
    quality: QuerySettingsQuality,
) -> SeqvarsQuerySettingsQualityPydantic:
    return SeqvarsQuerySettingsQualityPydantic(
        sample_quality_settings=[
            _seqvars_sample_quality_settings_from_protobuf(sample_quality)
            for sample_quality in quality.sample_qualities
        ]
    )


def _seqvars_nuclear_frequency_settings_from_protobuf(
    frequency: NuclearFrequencySettings,
) -> SeqvarsNuclearFrequencySettingsPydantic:
    return SeqvarsNuclearFrequencySettingsPydantic(
        enabled=frequency.enabled,
        heterozygous=frequency.heterozygous,
        homozygous=frequency.homozygous,
        hemizygous=frequency.hemizygous,
        frequency=frequency.frequency,
    )


def _seqvars_gnomad_mitochondrial_frequency_settings_from_protobuf(
    frequency: GnomadMitochondrialFrequencySettings,
) -> SeqvarsGnomadMitochondrialFrequencySettingsPydantic:
    return SeqvarsGnomadMitochondrialFrequencySettingsPydantic(
        enabled=frequency.enabled,
        heteroplasmic=frequency.heteroplasmic,
        homoplasmic=frequency.homoplasmic,
        frequency=frequency.frequency,
    )


def _seqvars_helixmtdb_frequency_settings_from_protobuf(
    frequency: HelixMtDbFrequencySettings,
) -> SeqvarsHelixMtDbFrequencySettingsPydantic:
    return SeqvarsHelixMtDbFrequencySettingsPydantic(
        enabled=frequency.enabled,
        heteroplasmic=frequency.heteroplasmic,
        homoplasmic=frequency.homoplasmic,
        frequency=frequency.frequency,
    )


def _seqvars_query_settings_frequency_from_protobuf(
    frequency: QuerySettingsFrequency,
) -> SeqvarsQuerySettingsFrequencyPydantic:
    return SeqvarsQuerySettingsFrequencyPydantic(
        gnomad_exomes=(
            _seqvars_nuclear_frequency_settings_from_protobuf(frequency.gnomad_exomes)
            if frequency.HasField("gnomad_exomes")
            else None
        ),
        gnomad_genomes=(
            _seqvars_nuclear_frequency_settings_from_protobuf(frequency.gnomad_genomes)
            if frequency.HasField("gnomad_genomes")
            else None
        ),
        gnomad_mitochondrial=(
            _seqvars_gnomad_mitochondrial_frequency_settings_from_protobuf(frequency.gnomad_mtdna)
            if frequency.HasField("gnomad_mtdna")
            else None
        ),
        helixmtdb=(
            _seqvars_helixmtdb_frequency_settings_from_protobuf(frequency.helixmtdb)
            if frequency.HasField("helixmtdb")
            else None
        ),
        inhouse=(
            _seqvars_nuclear_frequency_settings_from_protobuf(frequency.inhouse)
            if frequency.HasField("inhouse")
            else None
        ),
    )


SEQVARS_VARIANT_TYPE_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in SEQVARS_VARIANT_TYPE_MAPPING_TO_PB.items()
}


def _seqvars_variant_type_choice_from_protobuf(
    variant_type: VariantType.ValueType,
) -> SeqvarsVariantTypeChoice:
    return SEQVARS_VARIANT_TYPE_MAPPING_FROM_PB[variant_type]


SEQVARS_TRANSCRIPT_TYPE_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in SEQVARS_TRANSCRIPT_TYPE_MAPPING_TO_PB.items()
}


def _seqvars_transcript_type_choice_from_protobuf(
    variant_type: TranscriptType.ValueType,
) -> SeqvarsTranscriptTypeChoice:
    return SEQVARS_TRANSCRIPT_TYPE_MAPPING_FROM_PB[variant_type]


SEQVARS_VARIANT_CONSEQUENCE_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in SEQVARS_VARIANT_CONSEQUENCE_MAPPING_TO_PB.items()
}


def _seqvars_variant_consequence_choice_from_protobuf(
    consequence: Consequence.ValueType,
) -> SeqvarsVariantConsequenceChoice:
    return SEQVARS_VARIANT_CONSEQUENCE_MAPPING_FROM_PB[consequence]


def _seqvars_query_settings_consequence_from_protobuf(
    consequence: QuerySettingsConsequence,
) -> SeqvarsQuerySettingsConsequencePydantic:
    return SeqvarsQuerySettingsConsequencePydantic(
        variant_types=[
            _seqvars_variant_type_choice_from_protobuf(vt) for vt in consequence.variant_types
        ],
        transcript_types=[
            _seqvars_transcript_type_choice_from_protobuf(tt) for tt in consequence.transcript_types
        ],
        consequences=[
            _seqvars_variant_consequence_choice_from_protobuf(csq)
            for csq in consequence.consequences
        ],
        max_dist_to_exon=(
            None if consequence.max_dist_to_exon == 0 else consequence.max_dist_to_exon
        ),
    )


def _genome_region_from_protobuf(region: GenomicRegion) -> GenomeRegionPydantic:
    return GenomeRegionPydantic(
        chromosome=region.chromosome,
        range=(
            None
            if region.range is None
            else OneBasedRangePydantic(
                start=region.range.start,
                end=region.range.end,
            )
        ),
    )


def _seqvars_query_settings_locus_from_protobuf(
    locus: QuerySettingsLocus,
) -> SeqvarsQuerySettingsLocusPydantic:
    return SeqvarsQuerySettingsLocusPydantic(
        genes=locus.genes,
        genome_regions=[_genome_region_from_protobuf(region) for region in locus.genome_regions],
    )


CLINVAR_AGG_DESC_MAPPING_FROM_PB = {
    pb_value: pydantic_value
    for (pydantic_value, pb_value) in CLINVAR_AGG_DESC_MAPPING_TO_PB.items()
}


def _clinvar_germline_aggregate_description_choice_from_protobuf(
    desc: ClinvarGermlineAggregateDescription.ValueType,
) -> ClinvarGermlineAggregateDescriptionChoice:
    return CLINVAR_AGG_DESC_MAPPING_FROM_PB[desc]


def _seqvars_query_settings_clinvar_from_protobuf(
    clinvar: QuerySettingsClinVar,
) -> SeqvarsQuerySettingsClinvarPydantic:
    return SeqvarsQuerySettingsClinvarPydantic(
        presence_required=clinvar.presence_required,
        clinvar_germline_aggregate_description=[
            _clinvar_germline_aggregate_description_choice_from_protobuf(desc)
            for desc in clinvar.germline_descriptions
        ],
        allow_conflicting_interpretations=clinvar.allow_conflicting_interpretations,
    )


def _seqvars_case_query_from_protobuf(query: CaseQuery) -> SeqvarsCaseQueryPydantic:
    return SeqvarsCaseQueryPydantic(
        genotype=(
            _seqvars_query_settings_genotype_from_protobuf(query.genotype)
            if query.HasField("genotype")
            else None
        ),
        quality=(
            _seqvars_query_settings_quality_from_protobuf(query.quality)
            if query.HasField("quality")
            else None
        ),
        frequency=(
            _seqvars_query_settings_frequency_from_protobuf(query.frequency)
            if query.HasField("frequency")
            else None
        ),
        consequence=(
            _seqvars_query_settings_consequence_from_protobuf(query.consequence)
            if query.HasField("consequence")
            else None
        ),
        locus=(
            _seqvars_query_settings_locus_from_protobuf(query.locus)
            if query.HasField("locus")
            else None
        ),
        clinvar=(
            _seqvars_query_settings_clinvar_from_protobuf(query.clinvar)
            if query.HasField("clinvar")
            else None
        ),
    )


def _seqvars_output_statistics_from_protobuf(
    statistics: OutputStatistics,
) -> SeqvarsOutputStatisticsPydantic:
    return SeqvarsOutputStatisticsPydantic(
        count_total=statistics.count_total,
        count_passed=statistics.count_passed,
        passed_by_consequences=dict(
            (
                _seqvars_variant_consequence_choice_from_protobuf(item.consequence),
                item.count,
            )
            for item in statistics.passed_by_consequences
        ),
    )


VARIANT_SCORE_COLUMN_TYPE_MAPPING: dict[
    VariantScoreColumnType.ValueType : SeqvarsVariantScoreColumnTypeChoice
] = {
    VariantScoreColumnType.VARIANT_SCORE_COLUMN_TYPE_NUMBER: SeqvarsVariantScoreColumnTypeChoice.NUMBER,
    VariantScoreColumnType.VARIANT_SCORE_COLUMN_TYPE_STRING: SeqvarsVariantScoreColumnTypeChoice.STRING,
}


def _variant_score_column_type_choice_from_protobuf(
    variant_score_column_type: VariantScoreColumnType.ValueType,
) -> SeqvarsVariantScoreColumnTypeChoice:
    return VARIANT_SCORE_COLUMN_TYPE_MAPPING[variant_score_column_type]


def _seqvars_variant_score_column_from_protobuf(
    variant_score_column: VariantScoreColumn,
) -> SeqvarsVariantScoreColumnPydantic:
    return SeqvarsVariantScoreColumnPydantic(
        name=variant_score_column.name,
        label=variant_score_column.label,
        description=variant_score_column.description,
        type=_variant_score_column_type_choice_from_protobuf(variant_score_column.type),
    )


def _seqvars_variant_score_columns_from_protobuf(
    variant_score_columns: list[VariantScoreColumn],
) -> list[SeqvarsVariantScoreColumnPydantic]:
    return list(map(_seqvars_variant_score_column_from_protobuf, variant_score_columns))


def _resources_used_from_protobuf(resources: ResourcesUsed) -> ResourcesUsedPydantic:
    return ResourcesUsedPydantic(
        start_time=(
            resources.start_time.ToDatetime(tzinfo=datetime.timezone.utc)
            if resources.HasField("start_time") and resources.start_time
            else None
        ),
        end_time=(
            resources.end_time.ToDatetime(tzinfo=datetime.timezone.utc)
            if resources.HasField("end_time") and resources.end_time
            else None
        ),
        memory_used=resources.memory_used,
    )


def outputheader_from_protobuf(output_header: OutputHeader) -> SeqvarsOutputHeaderPydantic:
    """Convert ``OutputHeader`` protobuf to a ``SeqvarsOutputHeaderPydantic`` model."""
    return SeqvarsOutputHeaderPydantic(
        genome_release=(_genome_release_choice_from_protobuf(output_header.genome_release)),
        versions=(_versions_from_protobuf(output_header.versions)),
        query=(
            _seqvars_case_query_from_protobuf(output_header.query)
            if output_header.HasField("query")
            else None
        ),
        case_uuid=output_header.case_uuid,
        statistics=(
            _seqvars_output_statistics_from_protobuf(output_header.statistics)
            if output_header.HasField("statistics")
            else None
        ),
        variant_score_columns=(
            _seqvars_variant_score_columns_from_protobuf(output_header.variant_score_columns)
            if output_header.variant_score_columns
            else None
        ),
        resources=(
            _resources_used_from_protobuf(output_header.resources)
            if output_header.HasField("resources")
            else None
        ),
    )


def _seqvars_vcf_variant_from_protobuf(vcf_variant: VcfVariant) -> SeqvarsVcfVariantPydantic:
    return SeqvarsVcfVariantPydantic(
        genome_release=_genome_release_choice_from_protobuf(vcf_variant.genome_release),
        chrom=vcf_variant.chrom,
        chrom_no=vcf_variant.chrom_no,
        pos=vcf_variant.pos,
        ref_allele=vcf_variant.ref_allele,
        alt_allele=vcf_variant.alt_allele,
    )


def _gene_identity_from_protobuf(identity: GeneIdentity) -> GeneIdentityPydantic:
    return GeneIdentityPydantic(
        hgnc_id=identity.hgnc_id,
        gene_symbol=identity.gene_symbol,
    )


def _consequences_from_protobuf(
    consequences: GeneRelatedConsequences,
) -> GeneRelatedConsequencesPydantic:
    return GeneRelatedConsequencesPydantic(
        hgvs_t=consequences.hgvs_t,
        hgvs_p=consequences.hgvs_p,
        consequences=[
            _seqvars_variant_consequence_choice_from_protobuf(csq)
            for csq in consequences.consequences
        ],
    )


MODE_OF_INHERITANCE_MAPPING: dict[
    ModeOfInheritance.ValueType : SeqvarsVariantScoreColumnTypeChoice
] = {
    ModeOfInheritance.MODE_OF_INHERITANCE_AUTOSOMAL_DOMINANT: SeqvarsModeOfInheritance.AUTOSOMAL_DOMINANT,
    ModeOfInheritance.MODE_OF_INHERITANCE_AUTOSOMAL_RECESSIVE: SeqvarsModeOfInheritance.AUTOSOMAL_RECESSIVE,
    ModeOfInheritance.MODE_OF_INHERITANCE_X_LINKED_DOMINANT: SeqvarsModeOfInheritance.X_LINKED_DOMINANT,
    ModeOfInheritance.MODE_OF_INHERITANCE_X_LINKED_RECESSIVE: SeqvarsModeOfInheritance.X_LINKED_RECESSIVE,
    ModeOfInheritance.MODE_OF_INHERITANCE_Y_LINKED: SeqvarsModeOfInheritance.Y_LINKED,
    ModeOfInheritance.MODE_OF_INHERITANCE_MITOCHONDRIAL: SeqvarsModeOfInheritance.MITOCHONDRIAL,
}


def _mode_of_inheritance_from_protobuf(
    mode_of_inheritance: ModeOfInheritance.ValueType,
) -> SeqvarsModeOfInheritance:
    return MODE_OF_INHERITANCE_MAPPING[mode_of_inheritance]


def _phenotypes_from_protobuf(phenotypes: GeneRelatedPhenotypes) -> GeneRelatedPhenotypesPydantic:
    return GeneRelatedPhenotypesPydantic(
        is_acmg_sf=phenotypes.is_acmg_sf,
        is_disease_gene=phenotypes.is_disease_gene,
        mode_of_inheritances=list(
            map(_mode_of_inheritance_from_protobuf, phenotypes.mode_of_inheritances)
        ),
    )


def _gnomad_constraints_from_protobuf(gnomad: GnomadConstraints) -> GnomadConstraintsPydantic:
    return GnomadConstraintsPydantic(
        mis_z=gnomad.mis_z,
        oe_lof=gnomad.oe_lof,
        oe_lof_lower=gnomad.oe_lof_lower,
        oe_lof_upper=gnomad.oe_lof_upper,
        oe_mis=gnomad.oe_mis,
        oe_mis_lower=gnomad.oe_mis_lower,
        oe_mis_upper=gnomad.oe_mis_upper,
        pli=gnomad.pli,
        syn_z=gnomad.syn_z,
    )


def _decipher_constraints_from_protobuf(
    decipher: DecipherConstraints,
) -> DecipherConstraintsPydantic:
    return DecipherConstraintsPydantic(
        hi_percentile=decipher.p_hi,
        hi_index=decipher.hi_index,
    )


def _rcnv_constraints_from_protobuf(rcnv: DecipherConstraints) -> RcnvConstraintsPydantic:
    return RcnvConstraintsPydantic(
        p_haplo=rcnv.p_haplo,
        p_triplo=rcnv.p_triplo,
    )


def _shet_constraints_from_protobuf(shet: ShetConstraints) -> ShetConstraintsPydantic:
    return ShetConstraintsPydantic(
        s_het=shet.s_het,
    )


CLINGEN_DOSAGE_MAPPING_FROM_PB: dict[ClingenDosageScore.ValueType, ClingenDosageScoreChoice] = {
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_SUFFICIENT_EVIDENCE_AVAILABLE: ClingenDosageScoreChoice.SUFFICIENT_EVIDENCE_AVAILABLE,
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_SOME_EVIDENCE_AVAILABLE: ClingenDosageScoreChoice.SOME_EVIDENCE_AVAILABLE,
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_LITTLE_EVIDENCE: ClingenDosageScoreChoice.LITTLE_EVIDENCE,
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_NO_EVIDENCE_AVAILABLE: ClingenDosageScoreChoice.NO_EVIDENCE_AVAILABLE,
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_RECESSIVE: ClingenDosageScoreChoice.RECESSIVE,
    ClingenDosageScore.CLINGEN_DOSAGE_SCORE_UNLIKELY: ClingenDosageScoreChoice.UNLIKELY,
}


def _clingen_dosage_score_from_protobuf(
    score: ClingenDosageScore.ValueType,
) -> Optional[ClingenDosageScoreChoice]:
    if score == ClingenDosageScore.CLINGEN_DOSAGE_SCORE_UNSPECIFIED:
        return None
    else:
        return CLINGEN_DOSAGE_MAPPING_FROM_PB[score]


def _clingen_dosage_annotation_from_protobuf(
    clingen: ClingenDosageAnnotation,
) -> Optional[ClingenDosageAnnotationPydantic]:
    result = ClingenDosageAnnotationPydantic(
        haplo=_clingen_dosage_score_from_protobuf(clingen.haplo),
        triplo=_clingen_dosage_score_from_protobuf(clingen.triplo),
    )
    if result.haplo is None and result.triplo is None:
        return None
    else:
        return result


def _constraints_from_protobuf(
    constraints: GeneRelatedConstraints,
) -> GeneRelatedConstraintsPydantic:
    return GeneRelatedConstraintsPydantic(
        gnomad=(
            _gnomad_constraints_from_protobuf(constraints.gnomad)
            if constraints.HasField("gnomad")
            else None
        ),
        decipher=(
            _decipher_constraints_from_protobuf(constraints.decipher)
            if constraints.HasField("decipher")
            else None
        ),
        rcnv=(
            _rcnv_constraints_from_protobuf(constraints.rcnv)
            if constraints.HasField("rcnv")
            else None
        ),
        shet=(
            _shet_constraints_from_protobuf(constraints.shet)
            if constraints.HasField("shet")
            else None
        ),
        clingen=(
            _clingen_dosage_annotation_from_protobuf(constraints.clingen)
            if constraints.HasField("clingen")
            else None
        ),
    )


def _gene_related_annotation_from_protobuf(
    gene: GeneRelatedAnnotation,
) -> GeneRelatedAnnotationPydantic:
    return GeneRelatedAnnotationPydantic(
        identity=_gene_identity_from_protobuf(gene.identity) if gene.HasField("identity") else None,
        consequences=(
            _consequences_from_protobuf(gene.consequences)
            if gene.HasField("consequences")
            else None
        ),
        phenotypes=(
            _phenotypes_from_protobuf(gene.phenotypes) if gene.HasField("phenotypes") else None
        ),
        constraints=(
            _constraints_from_protobuf(gene.constraints) if gene.HasField("constraints") else None
        ),
    )


def _seqvars_db_ids_from_protobuf(dbids: DbIds) -> SeqvarsDbIdsPydantic:
    return SeqvarsDbIdsPydantic(
        dbsnp_id=dbids.dbsnp_id,
    )


def _seqvars_nuclear_frequency_from_protobuf(
    frequency: NuclearFrequency,
) -> SeqvarsNuclearFrequencyPydantic:
    return SeqvarsNuclearFrequencyPydantic(
        an=frequency.an,
        het=frequency.het,
        homalt=frequency.homalt,
        hemialt=frequency.hemialt,
        af=frequency.af,
    )


def _seqvars_gnomad_mitochondrial_frequency_from_protobuf(
    frequency: GnomadMitochondrialFrequency,
) -> SeqvarsGnomadMitochondrialFrequencyPydantic:
    return SeqvarsGnomadMitochondrialFrequencyPydantic(
        an=frequency.an,
        het=frequency.het,
        homalt=frequency.homalt,
        af=frequency.af,
    )


def _seqvars_helixmtdb_frequency_from_protobuf(
    frequency: HelixMtDbFrequency,
) -> SeqvarsHelixMtDbFrequencyPydantic:
    return SeqvarsHelixMtDbFrequencyPydantic(
        an=frequency.an,
        het=frequency.het,
        homalt=frequency.homalt,
        af=frequency.af,
    )


def _frequency_annotation_from_protobuf(
    frequency: FrequencyAnnotation,
) -> SeqvarsFrequencyAnnotationPydantic:
    return SeqvarsFrequencyAnnotationPydantic(
        gnomad_exomes=(
            _seqvars_nuclear_frequency_from_protobuf(frequency.gnomad_exomes)
            if frequency.HasField("gnomad_exomes")
            else None
        ),
        gnomad_genomes=(
            _seqvars_nuclear_frequency_from_protobuf(frequency.gnomad_genomes)
            if frequency.HasField("gnomad_genomes")
            else None
        ),
        gnomad_mitochondrial=(
            _seqvars_gnomad_mitochondrial_frequency_from_protobuf(frequency.gnomad_mtdna)
            if frequency.HasField("gnomad_mtdna")
            else None
        ),
        helixmtdb=(
            _seqvars_helixmtdb_frequency_from_protobuf(frequency.helixmtdb)
            if frequency.HasField("helixmtdb")
            else None
        ),
        inhouse=(
            _seqvars_nuclear_frequency_from_protobuf(frequency.inhouse)
            if frequency.HasField("inhouse")
            else None
        ),
    )


AGGREGATE_CLINVAR_MAPPING_FROM_PB: dict[
    AggregateGermlineReviewStatus.ValueType, ClinvarAggregateGermlineReviewStatusChoice
] = {
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATION_PROVIDED: ClinvarAggregateGermlineReviewStatusChoice.NO_CLASSIFICATION_PROVIDED,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED: ClinvarAggregateGermlineReviewStatusChoice.NO_ASSERTION_CRITERIA_PROVIDED,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_SINGLE_SUBMITTER: ClinvarAggregateGermlineReviewStatusChoice.CRITERIA_PROVIDED_SINGLE_SUBMITTER,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS: ClinvarAggregateGermlineReviewStatusChoice.CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_CONFLICTING_CLASSIFICATIONS: ClinvarAggregateGermlineReviewStatusChoice.CRITERIA_PROVIDED_CONFLICTING_CLASSIFICATIONS,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_REVIEWED_BY_EXPERT_PANEL: ClinvarAggregateGermlineReviewStatusChoice.REVIEWED_BY_EXPERT_PANEL,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_PRACTICE_GUIDELINE: ClinvarAggregateGermlineReviewStatusChoice.PRACTICE_GUIDELINE,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATIONS_FROM_UNFLAGGED_RECORDS: ClinvarAggregateGermlineReviewStatusChoice.NO_CLASSIFICATIONS_FROM_UNFLAGGED_RECORDS,
    AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATION_FOR_THE_SINGLE_VARIANT: ClinvarAggregateGermlineReviewStatusChoice.NO_CLASSIFICATION_FOR_THE_SINGLE_VARIANT,
}


def _clinvar_aggregate_germline_review_status_from_protobuf(
    status: AggregateGermlineReviewStatus.ValueType,
) -> Optional[ClinvarAggregateGermlineReviewStatusChoice]:
    if status == AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_UNSPECIFIED:
        return None
    else:
        return AGGREGATE_CLINVAR_MAPPING_FROM_PB[status]


def _clinvar_annotation_from_protobuf(clinvar: ClinvarAnnotation) -> ClinvarAnnotationPydantic:
    return ClinvarAnnotationPydantic(
        vcv_accession=clinvar.vcv_accession,
        germline_significance_description=clinvar.germline_significance_description,
        germline_review_status=_clinvar_aggregate_germline_review_status_from_protobuf(
            clinvar.germline_review_status
        ),
        effective_germline_significance_description=clinvar.effective_germline_significance_description,
    )


def convert_protobuf_value_to_python(value: Value) -> None | int | float | str | bool:
    """Convert a Protobuf value to a Python value."""
    # Determine which kind of value is set
    kind = value.WhichOneof("kind")
    # Convert the Protobuf value to a corresponding Python value
    if kind == "null_value":
        return None
    elif kind == "number_value":
        return value.number_value
    elif kind == "string_value":
        return value.string_value
    elif kind == "bool_value":
        return value.bool_value
    else:
        raise ValueError(f"Cannot convert value of kind {kind} to Python")


def _score_annotation_from_protobuf(scores: ScoreAnnotations) -> SeqvarsScoreAnnotationsPydantic:
    return SeqvarsScoreAnnotationsPydantic(
        entries={
            entry.key: convert_protobuf_value_to_python(entry.value) for entry in scores.entries
        }
    )


def _variant_related_annotation_from_protobuf(
    variant: VariantRelatedAnnotation,
) -> GeneRelatedAnnotationPydantic:
    return SeqvarsVariantRelatedAnnotationPydantic(
        dbids=_seqvars_db_ids_from_protobuf(variant.dbids) if variant.HasField("dbids") else None,
        frequency=(
            _frequency_annotation_from_protobuf(variant.frequency)
            if variant.HasField("frequency")
            else None
        ),
        clinvar=(
            _clinvar_annotation_from_protobuf(variant.clinvar)
            if variant.HasField("clinvar")
            else None
        ),
        scores=(
            _score_annotation_from_protobuf(variant.scores) if variant.HasField("scores") else None
        ),
    )


def _seqvars_sample_call_info_from_protobuf(
    call_info: SampleCallInfo,
) -> SeqvarsSampleCallInfoPydantic:
    return SeqvarsSampleCallInfoPydantic(
        sample=call_info.sample,
        genotype=call_info.genotype,
        dp=call_info.dp,
        ad=call_info.ad,
        gq=call_info.gq,
        ps=call_info.ps,
    )


def _sevars_call_related_annotation_from_protobuf(
    call: CallRelatedAnnotation,
) -> GeneRelatedAnnotationPydantic:
    return SeqvarsCallRelatedAnnotationPydantic(
        call_infos={
            call_info.sample: _seqvars_sample_call_info_from_protobuf(call_info)
            for call_info in call.call_infos
        }
    )


def _seqvars_variant_annotation_from_protobuf(
    variant_annotation: VariantAnnotation,
) -> SeqvarsVariantAnnotationPydantic:
    return SeqvarsVariantAnnotationPydantic(
        gene=(
            _gene_related_annotation_from_protobuf(variant_annotation.gene)
            if variant_annotation.HasField("gene")
            else None
        ),
        variant=(
            _variant_related_annotation_from_protobuf(variant_annotation.variant)
            if variant_annotation.HasField("variant")
            else None
        ),
        call=(
            _sevars_call_related_annotation_from_protobuf(variant_annotation.call)
            if variant_annotation.HasField("call")
            else None
        ),
    )


def seqvars_output_record_from_protobuf(output_record: OutputRecord) -> SeqvarsOutputRecordPydantic:
    return SeqvarsOutputRecordPydantic(
        uuid=output_record.uuid,
        case_uuid=output_record.case_uuid,
        vcf_variant=(
            _seqvars_vcf_variant_from_protobuf(output_record.vcf_variant)
            if output_record.HasField("vcf_variant")
            else None
        ),
        variant_annotation=(
            _seqvars_variant_annotation_from_protobuf(output_record.variant_annotation)
            if output_record.HasField("variant_annotation")
            else None
        ),
    )
