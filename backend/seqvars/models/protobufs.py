"""Helpers for conversion from query models to protobufs."""

from seqvars.models.base import (
    ClinvarGermlineAggregateDescriptionChoice,
    SeqvarsGenotypeChoice,
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsClinvar,
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsQuality,
    SeqvarsRecessiveModeChoice,
    SeqvarsSampleGenotypePydantic,
    SeqvarsSampleQualityFilterPydantic,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantTypeChoice,
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

SEQVARS_GENOTYPE_CHOICE_MAPPING: dict[SeqvarsGenotypeChoice, GenotypeChoice.ValueType] = {
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
        genotype=SEQVARS_GENOTYPE_CHOICE_MAPPING[sample_genotype.genotype],
        include_no_call=sample_genotype.include_no_call,
        enabled=sample_genotype.enabled,
    )


SEQVARS_RECESSIVE_MODE_MAPPING: dict[SeqvarsRecessiveModeChoice, RecessiveMode.ValueType] = {
    SeqvarsRecessiveModeChoice.DISABLED: RecessiveMode.RECESSIVE_MODE_DISABLED,
    SeqvarsRecessiveModeChoice.COMPHET_RECESSIVE: RecessiveMode.RECESSIVE_MODE_COMPOUND_HETEROZYGOUS,
    SeqvarsRecessiveModeChoice.HOMOZYGOUS_RECESSIVE: RecessiveMode.RECESSIVE_MODE_HOMOZYGOUS,
    SeqvarsRecessiveModeChoice.RECESSIVE: RecessiveMode.RECESSIVE_MODE_ANY,
}


def _genotype_to_protobuf(genotype: SeqvarsQuerySettingsGenotype) -> QuerySettingsGenotype:
    return QuerySettingsGenotype(
        recessive_mode=SEQVARS_RECESSIVE_MODE_MAPPING[genotype.recessive_mode],
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


SEQVARS_VARIANT_TYPE_MAPPING: dict[SeqvarsVariantTypeChoice, VariantType.ValueType] = {
    SeqvarsVariantTypeChoice.SNV: VariantType.VARIANT_TYPE_SNV,
    SeqvarsVariantTypeChoice.INDEL: VariantType.VARIANT_TYPE_INDEL,
    SeqvarsVariantTypeChoice.MNV: VariantType.VARIANT_TYPE_MNV,
    SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION: VariantType.VARIANT_TYPE_COMPLEX_SUBSTITUTION,
}

SEQVARS_TRANSCRIPT_TYPE_MAPPING: dict[SeqvarsTranscriptTypeChoice : TranscriptType.ValueType] = {
    SeqvarsTranscriptTypeChoice.CODING: TranscriptType.TRANSCRIPT_TYPE_CODING,
    SeqvarsTranscriptTypeChoice.NON_CODING: TranscriptType.TRANSCRIPT_TYPE_NON_CODING,
}


SEQVARS_VARIANT_CONSEQUENCE_MAPPING: dict[
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
    SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT: Consequence.CONSEQUENCE_FIVE_PRIME_UTR_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT: Consequence.CONSEQUENCE_FIVE_PRIME_UTR_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT: Consequence.CONSEQUENCE_THREE_PRIME_UTR_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT: Consequence.CONSEQUENCE_THREE_PRIME_UTR_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT: Consequence.CONSEQUENCE_NON_CODING_TRANSCRIPT_EXON_VARIANT,
    SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT: Consequence.CONSEQUENCE_NON_CODING_TRANSCRIPT_INTRON_VARIANT,
    SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT: Consequence.CONSEQUENCE_UPSTREAM_GENE_VARIANT,
    SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT: Consequence.CONSEQUENCE_DOWNSTREAM_GENE_VARIANT,
    SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT: Consequence.CONSEQUENCE_INTERGENIC_VARIANT,
    SeqvarsVariantConsequenceChoice.INTRON_VARIANT: Consequence.CONSEQUENCE_INTRON_VARIANT,
}


def _consequence_to_protobuf(
    consequence: SeqvarsQuerySettingsConsequence,
) -> QuerySettingsConsequence:
    return QuerySettingsConsequence(
        variant_types=[SEQVARS_VARIANT_TYPE_MAPPING[vt] for vt in consequence.variant_types],
        transcript_types=[
            SEQVARS_TRANSCRIPT_TYPE_MAPPING[tt] for tt in consequence.transcript_types
        ],
        consequences=[
            SEQVARS_VARIANT_CONSEQUENCE_MAPPING[csq] for csq in consequence.variant_consequences
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


CLINVAR_AGG_DESC_MAPPING: dict[
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
            CLINVAR_AGG_DESC_MAPPING[desc]
            for desc in clinvar.clinvar_germline_aggregate_description
        ],
        allow_conflicting_interpretations=clinvar.allow_conflicting_interpretations,
    )


def querysettings_to_protobuf(settings: SeqvarsQuerySettings) -> CaseQuery:
    """Convert a query model to a protobuf."""
    return CaseQuery(
        genotype=_genotype_to_protobuf(settings.genotype),
        quality=_quality_to_protobuf(settings.quality),
        frequency=_frequency_to_protobuf(settings.frequency),
        consequence=_consequence_to_protobuf(settings.consequence),
        locus=_locus_to_protobuf(settings.locus),
        clinvar=_clinvar_to_protobuf(settings.clinvar),
    )
