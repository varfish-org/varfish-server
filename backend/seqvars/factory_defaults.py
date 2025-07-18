"""Factory defaults for seqvars query settings.

Great care is taken to keep this constant (fixing date times and UUID
generation).  We use snapshot tests to ensure that this is true and
that any changes will be tracked in source code.
"""

import logging

from dateutil.parser import parse as parse_datetime
from django.db import models
from faker import Faker

from seqvars.models.base import (
    ClinvarGermlineAggregateDescriptionChoice,
    GenomeRegionPydantic,
    LabeledSortableBaseModel,
    SeqvarsColumnConfigPydantic,
    SeqvarsGenotypePresetChoice,
    SeqvarsGenotypePresetsPydantic,
    SeqvarsInhouseFrequencySettingsPydantic,
    SeqvarsMitochondrialFrequencySettingsPydantic,
    SeqvarsNuclearFrequencySettingsPydantic,
    SeqvarsPredefinedQuery,
    SeqvarsPrioServicePydantic,
    SeqvarsQueryPresetsClinvar,
    SeqvarsQueryPresetsColumns,
    SeqvarsQueryPresetsConsequence,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsLocus,
    SeqvarsQueryPresetsPhenotypePrio,
    SeqvarsQueryPresetsQuality,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQueryPresetsVariantPrio,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantTypeChoice,
)

LOGGER = logging.getLogger(__name__)

#: DateTime for version 1.0 of the factory defaults.
TIME_VERSION_1_0 = parse_datetime("2024-07-01T00:00:00Z")
#: Base seed to use for UUID creation.
FAKER_SEED = 42


def create_seqvarsquerypresetsquality_short_read(faker: Faker) -> list[SeqvarsQueryPresetsQuality]:
    return [
        SeqvarsQueryPresetsQuality(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="super strict",
            filter_active=True,
            min_dp_het=10,
            min_dp_hom=5,
            min_ab_het=0.3,
            min_gq=30,
            min_ad=3,
        ),
        SeqvarsQueryPresetsQuality(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="strict",
            filter_active=True,
            min_dp_het=10,
            min_dp_hom=5,
            min_ab_het=0.2,
            min_gq=10,
            min_ad=3,
        ),
        SeqvarsQueryPresetsQuality(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="relaxed",
            filter_active=True,
            min_dp_het=8,
            min_dp_hom=4,
            min_ab_het=0.1,
            min_gq=10,
            min_ad=2,
        ),
        SeqvarsQueryPresetsQuality(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="any",
            filter_active=False,
        ),
    ]


def create_seqvarsquerypresetsconsequence(faker: Faker) -> list[SeqvarsQueryPresetsConsequence]:
    return [
        SeqvarsQueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="any",
            variant_types=[
                SeqvarsVariantTypeChoice.SNV,
                SeqvarsVariantTypeChoice.INDEL,
                SeqvarsVariantTypeChoice.MNV,
                SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                SeqvarsTranscriptTypeChoice.CODING,
                SeqvarsTranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION,
                SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_GAINED,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_ELONGATION,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_TRUNCATION,
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION,
                SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                SeqvarsVariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                SeqvarsVariantConsequenceChoice.PROTEIN_ALTERING_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_FIFTH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.EXONIC_SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.TFBS_ABLATION,
                # SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.GENE_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
        SeqvarsQueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="null variant",
            variant_types=[
                SeqvarsVariantTypeChoice.SNV,
                SeqvarsVariantTypeChoice.INDEL,
                SeqvarsVariantTypeChoice.MNV,
                SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                SeqvarsTranscriptTypeChoice.CODING,
            ],
            variant_consequences=[
                # high impact
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION,
                SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_GAINED,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_ELONGATION,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_TRUNCATION,
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION,
                SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION,
                # # moderate impact
                # SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                # SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                # SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                # SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                # SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # SeqvarsVariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                # SeqvarsVariantConsequenceChoice.PROTEIN_ALTERING_VARIANT,
                # # low impact
                # SeqvarsVariantConsequenceChoice.SPLICE_DONOR_FIFTH_BASE_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.EXONIC_SPLICE_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                # SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                # SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.TFBS_ABLATION,
                # SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.GENE_VARIANT
            ],
            max_distance_to_exon=None,
        ),
        SeqvarsQueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="AA change + splicing",
            variant_types=[
                SeqvarsVariantTypeChoice.SNV,
                SeqvarsVariantTypeChoice.INDEL,
                SeqvarsVariantTypeChoice.MNV,
                SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                SeqvarsTranscriptTypeChoice.CODING,
            ],
            variant_consequences=[
                # high impact
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION,
                SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_GAINED,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_ELONGATION,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_TRUNCATION,
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION,
                SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                SeqvarsVariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                SeqvarsVariantConsequenceChoice.PROTEIN_ALTERING_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_FIFTH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.EXONIC_SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                # SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                # SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.TFBS_ABLATION,
                # SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.GENE_VARIANT
            ],
            max_distance_to_exon=None,
        ),
        SeqvarsQueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="all coding + deep intronic",
            variant_types=[
                SeqvarsVariantTypeChoice.SNV,
                SeqvarsVariantTypeChoice.INDEL,
                SeqvarsVariantTypeChoice.MNV,
                SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                SeqvarsTranscriptTypeChoice.CODING,
                SeqvarsTranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION,
                SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_GAINED,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_ELONGATION,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_TRUNCATION,
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION,
                SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                SeqvarsVariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                SeqvarsVariantConsequenceChoice.PROTEIN_ALTERING_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_FIFTH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.EXONIC_SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.TFBS_ABLATION,
                # SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.GENE_VARIANT
            ],
            max_distance_to_exon=None,
        ),
        SeqvarsQueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="whole transcript",
            variant_types=[
                SeqvarsVariantTypeChoice.SNV,
                SeqvarsVariantTypeChoice.INDEL,
                SeqvarsVariantTypeChoice.MNV,
                SeqvarsVariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                SeqvarsTranscriptTypeChoice.CODING,
                SeqvarsTranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_ABLATION,
                SeqvarsVariantConsequenceChoice.EXON_LOSS_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_GAINED,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_VARIANT,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_ELONGATION,
                SeqvarsVariantConsequenceChoice.FRAMESHIFT_TRUNCATION,
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                SeqvarsVariantConsequenceChoice.FEATURE_ELONGATION,
                SeqvarsVariantConsequenceChoice.FEATURE_TRUNCATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                SeqvarsVariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                SeqvarsVariantConsequenceChoice.PROTEIN_ALTERING_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_FIFTH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.EXONIC_SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.MATURE_MIRNA_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.TFBS_ABLATION,
                # SeqvarsVariantConsequenceChoice.TFBS_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.TF_BINDING_SITE_VARIANT,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_ABLATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_AMPLIFICATION,
                # SeqvarsVariantConsequenceChoice.REGULATORY_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.GENE_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
    ]


def create_seqvarsquerypresetslocus(faker: Faker) -> list[SeqvarsQueryPresetsConsequence]:
    return [
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="whole genome",
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="nuclear chromosomes",
            genome_regions=[GenomeRegionPydantic(chromosome=str(no)) for no in range(1, 23)]
            + [
                GenomeRegionPydantic(chromosome="X"),
                GenomeRegionPydantic(chromosome="Y"),
            ],
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="autosomes",
            genome_regions=[GenomeRegionPydantic(chromosome=str(no)) for no in range(1, 23)],
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="gonosomes",
            genome_regions=[
                GenomeRegionPydantic(chromosome="X"),
                GenomeRegionPydantic(chromosome="Y"),
            ],
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="X chromosome",
            genome_regions=[
                GenomeRegionPydantic(chromosome="X"),
            ],
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="Y chromosome",
            genome_regions=[
                GenomeRegionPydantic(chromosome="Y"),
            ],
        ),
        SeqvarsQueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=7,
            label="MT genome",
            genome_regions=[
                GenomeRegionPydantic(chromosome="MT"),
            ],
        ),
    ]


def create_seqvarsquerypresetsfrequency(faker: Faker) -> list[SeqvarsQueryPresetsFrequency]:
    return [
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="dominant super strict",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.002,
                max_hom=0,
                max_het=1,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.002,
                max_hom=0,
                max_het=1,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=True,
                max_hom=None,
                max_het=None,
                max_hemi=None,
                max_carriers=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="dominant strict",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.002,
                max_hom=0,
                max_het=1,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.002,
                max_hom=0,
                max_het=1,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=True,
                max_carriers=20,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="dominant relaxed",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.01,
                max_hom=0,
                max_het=50,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.01,
                max_hom=0,
                max_het=20,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=True,
                max_carriers=20,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="recessive strict",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.001,
                max_hom=0,
                max_het=120,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.001,
                max_hom=0,
                max_het=15,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=True,
                max_carriers=20,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="recessive relaxed",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.01,
                max_hom=20,
                max_het=0,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=True,
                max_af=0.01,
                max_hom=4,
                max_het=150,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=True,
                max_carriers=20,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="any",
            gnomad_exomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
            gnomad_genomes=SeqvarsNuclearFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
            gnomad_mtdna=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_af=None,
                max_het=None,
                max_hom=None,
            ),
            helixmtdb=SeqvarsMitochondrialFrequencySettingsPydantic(
                enabled=False,
                max_het=None,
                max_hom=None,
                max_af=None,
            ),
            inhouse=SeqvarsInhouseFrequencySettingsPydantic(
                enabled=False,
                max_carriers=20,
                max_hom=None,
                max_het=None,
                max_hemi=None,
            ),
        ),
    ]


def create_seqvarsquerypresetsphenotypeprio(faker: Faker) -> list[SeqvarsQueryPresetsPhenotypePrio]:
    return [
        SeqvarsQueryPresetsPhenotypePrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            phenotype_prio_enabled=False,
            phenotype_prio_algorithm="exomiser.hiphive_human",
        ),
    ]


def create_seqvarsquerypresetsvariantprio(faker: Faker) -> list[SeqvarsQueryPresetsVariantPrio]:
    return [
        SeqvarsQueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            variant_prio_enabled=False,
        ),
        SeqvarsQueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="CADD",
            variant_prio_enabled=False,
            services=[
                SeqvarsPrioServicePydantic(name="cadd", version="1.6"),
            ],
        ),
        SeqvarsQueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="MutationTaster",
            variant_prio_enabled=False,
            services=[
                SeqvarsPrioServicePydantic(name="mutationtaster", version="2021"),
            ],
        ),
    ]


def create_seqvarsquerypresetsclinvar(faker: Faker) -> list[SeqvarsQueryPresetsClinvar]:
    return [
        SeqvarsQueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            clinvar_presence_required=False,
        ),
        SeqvarsQueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="Clinvar P/LP",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC,
                ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC,
            ],
        ),
        SeqvarsQueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="Clinvar P/LP +conflicting",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC,
                ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC,
            ],
            allow_conflicting_interpretations=True,
        ),
        SeqvarsQueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="ClinVar P/LP/VUS +conflicting",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC,
                ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC,
                ClinvarGermlineAggregateDescriptionChoice.UNCERTAIN_SIGNIFICANCE,
            ],
            allow_conflicting_interpretations=True,
        ),
    ]


#: The predefined columns.
ALL_COLUMNS: tuple[SeqvarsColumnConfigPydantic] = (
    # INFO columns
    SeqvarsColumnConfigPydantic(label="#", name="index", description="Number of row in result set"),
    SeqvarsColumnConfigPydantic(
        label="chrom/pos", name="__chrom_pos__", description="Chromosome and position"
    ),
    SeqvarsColumnConfigPydantic(
        label="ref", name="ref_allele", description="Genome reference allele"
    ),
    SeqvarsColumnConfigPydantic(
        label="alt", name="alt_allele", description="Genome alternative allele"
    ),
    SeqvarsColumnConfigPydantic(
        label="gene",
        name="payload.variant_annotation.gene.identity.gene_symbol",
        description="HGNC gene symbol",
    ),
    SeqvarsColumnConfigPydantic(
        label="HGNC ID",
        name="payload.variant_annotation.gene.identity.hgnc_id",
        description="HGNC gene ID",
    ),
    SeqvarsColumnConfigPydantic(
        label="HGVS(t)",
        name="payload.variant_annotation.gene.consequences.hgvs_t",
        description="HGVS description at CDS/transcript level",
    ),
    SeqvarsColumnConfigPydantic(
        label="HGVS(p)",
        name="payload.variant_annotation.gene.consequences.hgvs_p",
        description="HGVS description at protein level",
    ),
    SeqvarsColumnConfigPydantic(
        label="Transcript Accession",
        name="payload.variant_annotation.gene.consequences.tx_accession",
        description="Transcript accession without version",
    ),
    SeqvarsColumnConfigPydantic(
        label="Transcript Version",
        name="payload.variant_annotation.gene.consequences.tx_version",
        description="Transcript version",
    ),
    SeqvarsColumnConfigPydantic(
        label="Transcript",
        name="__tx_accession_version__",
        description="Transcript accession with version",
    ),
    SeqvarsColumnConfigPydantic(
        label="Variant Location",
        name="payload.variant_annotation.gene.consequences.location",
        description="Variant location with respect to gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="Variant Location Rank No",
        name="payload.variant_annotation.gene.consequences.rank_ord",
        description="Number of exon/intron that variant is in",
    ),
    SeqvarsColumnConfigPydantic(
        label="Variant Location Rank Total",
        name="payload.variant_annotation.gene.consequences.rank_total",
        description="Total number of exons/introns in transcript",
    ),
    SeqvarsColumnConfigPydantic(
        label="Variant Location Rank No/Total",
        name="__rank__",
        description="Rank of exon/intron and total",
    ),
    SeqvarsColumnConfigPydantic(
        label="ClinGen HI",
        name="__clingen_hi__",
        description="ClinGen Haploinsufficiency score",
    ),
    SeqvarsColumnConfigPydantic(
        label="ClinGen TS",
        name="__clingen_ts__",
        description="ClinGen Triplosensitivity score",
    ),
    SeqvarsColumnConfigPydantic(
        label="gene flags",
        name="__gene_flags__",
        description="Gene flags (ACMG SF, OMIM, HPO: AD/AR/XD/XR/YL/MT)",
    ),
    SeqvarsColumnConfigPydantic(
        label="effect",
        name="__effect__",
        description="HGVS effect description (protein/CDS/transcript)",
    ),
    SeqvarsColumnConfigPydantic(
        label="consequences",
        name="payload.variant_annotation.gene.consequences.consequences",
        description="Molecular consequence of variant as sequence ontology (SO) terms",
    ),
    SeqvarsColumnConfigPydantic(
        label="pLI gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.pli",
        description="gnomAD pLI score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="mis-z gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.mis_z",
        description="gnomAD missense z-score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="syn-z gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.syn_z",
        description="gnomAD synonymous z-score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="o/e lof gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_lof",
        description="gnomAD observed/expected loss-of-function score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="o/e mis gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_mis",
        description="gnomAD observed/expected missense score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="o/e lof lower gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_lof_lower",
        description="90% confidence interval for the lower bound of observed/expected loss-of-function for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="LOEUF gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_lof_upper",
        description="90% confidence interval for the upper bound of observed/expected loss-of-function for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="o/e mis lower gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_mis_lower",
        description="90% confidence interval for the lower bound of observed/expected missense for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="o/e mis upper gnomAD",
        name="payload.variant_annotation.gene.constraints.gnomad.oe_mis_upper",
        description="90% confidence interval for the upper bound of observed/expected missense for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="HI Percentile",
        name="payload.variant_annotation.gene.constraints.decipher.hi_percentile",
        description="Decipher Haploinsufficiency Index (HI) percentile rank for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="HI Index",
        name="payload.variant_annotation.gene.constraints.decipher.hi_index",
        description="Decipher Haploinsufficiency Index (HI) index for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="RCNV pHaplo",
        name="payload.variant_annotation.gene.constraints.rcnv.p_haplo",
        description="RCNV pHaplo haploinsufficiency score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="RCNV pTriplo",
        name="payload.variant_annotation.gene.constraints.rcnv.p_triplo",
        description="RCNV pTriplo triplosensitivity score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="sHet",
        name="payload.variant_annotation.gene.constraints.shet.s_het",
        description="sHet score for gene",
    ),
    SeqvarsColumnConfigPydantic(
        label="dbSNP ID",
        name="payload.variant_annotation.variant.dbids.dbsnp_id",
        description="dbSNP ID for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="% freq. gnomAD-exomes",
        name="payload.variant_annotation.variant.frequency.gnomad_exomes.af",
        description="gnomAD-exomes global allele frequency for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hom.alt. gnomAD-exomes",
        name="payload.variant_annotation.variant.frequency.gnomad_exomes.homalt",
        description="gnomAD-exomes total number of hom. alt. carriers",
    ),
    SeqvarsColumnConfigPydantic(
        label="# het. gnomAD-exomes",
        name="payload.variant_annotation.variant.frequency.gnomad_exomes.het",
        description="gnomAD-exomes total number of het. carriers",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hemi.alt. gnomAD-exomes",
        name="payload.variant_annotation.variant.frequency.gnomad_exomes.hemialt",
        description="gnomAD-exomes total number of hemi. alt. carriers",
    ),
    SeqvarsColumnConfigPydantic(
        label="% freq. gnomAD-genomes",
        name="payload.variant_annotation.variant.frequency.gnomad_genomes.af",
        description="gnomAD-genomes global allele frequency for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hom.alt. gnomAD-genomes",
        name="payload.variant_annotation.variant.frequency.gnomad_genomes.homalt",
        description="gnomAD-genomes total number of hom. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# het. gnomAD-genomes",
        name="payload.variant_annotation.variant.frequency.gnomad_genomes.het",
        description="gnomAD-genomes total number of het. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hemi.alt. gnomAD-genomes",
        name="payload.variant_annotation.variant.frequency.gnomad_genomes.hemialt",
        description="gnomAD-genomes total number of hemi. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="% freq. HelixMtDb",
        name="payload.variant_annotation.variant.frequency.helixmtdb.af",
        description="HelixMtDb global allele frequency for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# het. HelixMtDb",
        name="payload.variant_annotation.variant.frequency.helixmtdb.het",
        description="HelixMtDb total number of het. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hom.alt. HelixMtDb",
        name="payload.variant_annotation.variant.frequency.helixmtdb.homalt",
        description="HelixMtDb total number of hom. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="% freq. gnomAD-mtDNA",
        name="payload.variant_annotation.variant.frequency.gnomad_mtdna.af",
        description="gnomAD-mtDNA global allele frequency for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# het. gnomAD-mtDNA",
        name="payload.variant_annotation.variant.frequency.gnomad_mtdna.het",
        description="gnomAD-mtDNA number of het. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hom.alt. gnomAD-mtDNA",
        name="payload.variant_annotation.variant.frequency.gnomad_mtdna.homalt",
        description="gnomAD-mtDNA total number of hom. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# het. in-house",
        name="payload.variant_annotation.variant.frequency.inhouse.het",
        description="In-house number of het. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hom.alt. in-house",
        name="payload.variant_annotation.variant.frequency.inhouse.homalt",
        description="In-house number of hom. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="# hemi.alt. in-house",
        name="payload.variant_annotation.variant.frequency.inhouse.hemialt",
        description="In-house number of hemi. alt. carriers for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="Clinvar VCV",
        name="payload.variant_annotation.variant.clinvar.vcv_accession",
        description="ClinVar VCV accession for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="Clinvar Significance",
        name="payload.variant_annotation.variant.clinvar.germline_significance_description",
        description="ClinVar germline significance description for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="Clinvar Review Status",
        name="payload.variant_annotation.variant.clinvar.germline_review_status",
        description="ClinVar germline review status for variant / star rating",
    ),
    SeqvarsColumnConfigPydantic(
        label="Clinvar Sig. (Effective)",
        name="payload.variant_annotation.variant.clinvar.effective_germline_significance_description",
        description="ClinVar effective germline significance description for variant",
    ),
    # -- scores from CADD annotation
    SeqvarsColumnConfigPydantic(
        label="CADD Phred",
        name="payload.variant_annotation.variant.scores.entries.cadd_phred",
        description="CADD score in PHRED-scale for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="MMSplice",
        name="payload.variant_annotation.variant.scores.entries.mmsplice",
        description="MMSplice score for variant (max of all models)",
    ),
    SeqvarsColumnConfigPydantic(
        label="MMSplice model",
        name="payload.variant_annotation.variant.scores.entries.mmsplice_argmax",
        description="The model of the maximal MMSplice score",
    ),
    SeqvarsColumnConfigPydantic(
        label="Polyphen",
        name="payload.variant_annotation.variant.scores.entries.polyphen",
        description="Polyphen score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="SIFT",
        name="payload.variant_annotation.variant.scores.entries.sift",
        description="SIFT score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="SpliceAI",
        name="payload.variant_annotation.variant.scores.entries.spliceai",
        description="SpliceAI score for variant (max of all models)",
    ),
    SeqvarsColumnConfigPydantic(
        label="SpliceAI model",
        name="payload.variant_annotation.variant.scores.entries.spliceai_argmax",
        description="The model of the maximal SpliceAI score",
    ),
    # -- scores from dbNSFP
    SeqvarsColumnConfigPydantic(
        label="AlphaMissense",
        name="payload.variant_annotation.variant.scores.entries.alphamissense",
        description="AlphaMissense score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="BayesDel",
        name="payload.variant_annotation.variant.scores.entries.bayesdel_addaf",
        description="BayesDel AddAF score for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="FATHMM",
        name="payload.variant_annotation.variant.scores.entries.fathmm",
        description="FATHMM score for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="integrated fitCons",
        name="payload.variant_annotation.variant.scores.entries.fitcons_integrated",
        description="Integrated fitCons score for variant",
    ),
    SeqvarsColumnConfigPydantic(
        label="LRT",
        name="payload.variant_annotation.variant.scores.entries.lrt",
        description="LRT score",
    ),
    SeqvarsColumnConfigPydantic(
        label="MetaSVM",
        name="payload.variant_annotation.variant.scores.entries.metasvm",
        description="MetaSVM score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="Polyphen2 HDIV",
        name="payload.variant_annotation.variant.scores.entries.polyphen2_hdiv",
        description="Polyphen 2 HDIV score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="Polyphen2 HVAR",
        name="payload.variant_annotation.variant.scores.entries.polyphen2_hvar",
        description="Polyphen 2 HVAR score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="PrimateAI",
        name="payload.variant_annotation.variant.scores.entries.primateai",
        description="PrimateAI score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="PROVEAN",
        name="payload.variant_annotation.variant.scores.entries.provean",
        description="PROVEAN score for variant (missense only)",
    ),
    SeqvarsColumnConfigPydantic(
        label="REVEL",
        name="payload.variant_annotation.variant.scores.entries.revel",
        description="REVEL score for variant (missense only)",
    ),
    # Ppredefined ``FORMAT`` columns.
    SeqvarsColumnConfigPydantic(
        label="Genotype __SAMPLE__",
        name="payload.variant_annotation.call.call_infos.__SAMPLE__.genotype",
        description="Called genotype for sample",
    ),
    SeqvarsColumnConfigPydantic(
        label="Total Depth __SAMPLE__",
        name="payload.variant_annotation.call.call_infos.__SAMPLE__.dp",
        description="Total depth of coverage for sample",
    ),
    SeqvarsColumnConfigPydantic(
        label="Alternate Depth __SAMPLE__",
        name="payload.variant_annotation.call.call_infos.__SAMPLE__.ad",
        description="Alternate allele coverage for sample",
    ),
    SeqvarsColumnConfigPydantic(
        label="Genotype Quality __SAMPLE__",
        name="payload.variant_annotation.call.call_infos.__SAMPLE__.gq",
        description="Genotype quality for sample",
    ),
    SeqvarsColumnConfigPydantic(
        label="Phase Set __SAMPLE__",
        name="payload.variant_annotation.call.call_infos.__SAMPLE__.ps",
        description="Phase set of alternate allele for sample",
    ),
)


def create_seqvarsquerypresetscolumns(faker: Faker) -> list[SeqvarsQueryPresetsColumns]:
    # default column names
    COLUMNS_DEFAULT = (
        "index",
        "payload.variant_annotation.gene.identity.gene_symbol",
        "__gene_flags__",
        "__effect__",
        "payload.variant_annotation.gene.consequences.consequences",
        "payload.variant_annotation.gene.constraints.gnomad.pli",
        "payload.variant_annotation.gene.constraints.gnomad.oe_lof_upper",
        "payload.variant_annotation.variant.frequency.gnomad_exomes.af",
        "payload.variant_annotation.variant.frequency.gnomad_exomes.homalt",
        "payload.variant_annotation.variant.frequency.gnomad_genomes.af",
        "payload.variant_annotation.variant.frequency.gnomad_genomes.homalt",
        "payload.variant_annotation.variant.frequency.inhouse.het",
        "payload.variant_annotation.variant.frequency.inhouse.homalt",
        "payload.variant_annotation.variant.clinvar.germline_significance_description",
        "payload.variant_annotation.variant.clinvar.germline_review_status",
        "payload.variant_annotation.variant.scores.entries.cadd_phred",
        "payload.variant_annotation.variant.scores.entries.sift",
        "payload.variant_annotation.variant.scores.entries.spliceai",
        "payload.variant_annotation.call.call_infos.__SAMPLE__.genotype",
    )
    # clinvar filter column names
    COLUMNS_CLINVAR = (
        "index",
        "payload.variant_annotation.gene.identity.gene_symbol",
        "__gene_flags__",
        "__effect__",
        "payload.variant_annotation.gene.consequences.consequences",
        "payload.variant_annotation.gene.constraints.gnomad.pli",
        "payload.variant_annotation.gene.constraints.gnomad.oe_lof_upper",
        "payload.variant_annotation.variant.frequency.gnomad_exomes.af",
        "payload.variant_annotation.variant.frequency.gnomad_exomes.homalt",
        "payload.variant_annotation.variant.frequency.gnomad_genomes.af",
        "payload.variant_annotation.variant.frequency.gnomad_genomes.homalt",
        "payload.variant_annotation.variant.frequency.inhouse.het",
        "payload.variant_annotation.variant.frequency.inhouse.homalt",
        "payload.variant_annotation.variant.clinvar.germline_significance_description",
        "payload.variant_annotation.variant.clinvar.germline_review_status",
        "payload.variant_annotation.variant.scores.entries.cadd_phred",
        "payload.variant_annotation.variant.scores.entries.sift",
        "payload.variant_annotation.variant.scores.entries.spliceai",
        "payload.variant_annotation.call.call_infos.__SAMPLE__.genotype",
    )

    return [
        SeqvarsQueryPresetsColumns(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="defaults",
            column_settings=[
                column_config.model_copy(update={"visible": column_config.name in COLUMNS_DEFAULT})
                for column_config in ALL_COLUMNS
            ],
        ),
        SeqvarsQueryPresetsColumns(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="ClinVar",
            column_settings=[
                column_config.model_copy(update={"visible": column_config.name in COLUMNS_CLINVAR})
                for column_config in ALL_COLUMNS
            ],
        ),
        SeqvarsQueryPresetsColumns(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="all",
            column_settings=[
                column_config.model_copy(update={"visible": True}) for column_config in ALL_COLUMNS
            ],
        ),
    ]


def create_seqvarspredefined_queries(
    querypresetsversion: SeqvarsQueryPresetsSetVersion, faker: Faker
) -> list[SeqvarsPredefinedQuery]:
    def pick_by_label(label: str, queryset: models.QuerySet) -> LabeledSortableBaseModel:
        return next(filter(lambda q: q.label == label, queryset.all()))

    return [
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="defaults",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.ANY,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="de novo",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.DE_NOVO,
            ),
            quality=pick_by_label(
                "super strict", querypresetsversion.seqvarsquerypresetsquality_set
            ),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="dominant",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.DOMINANT,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="homozygous recessive",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.HOMOZYGOUS_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="compound heterozygous",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.COMPOUND_HETEROZYGOUS_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="recessive",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=7,
            label="X recessive",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.X_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("X chromosome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=8,
            label="ClinVar pathogenic",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.AFFECTED_CARRIERS,
            ),
            quality=pick_by_label("any", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "any", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label("any", querypresetsversion.seqvarsquerypresetsfrequency_set),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label(
                "Clinvar P/LP +conflicting", querypresetsversion.seqvarsquerypresetsclinvar_set
            ),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=9,
            label="mitochondrial",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.AFFECTED_CARRIERS,
            ),
            quality=pick_by_label("strict", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "any", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("MT genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.seqvarsquerypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
        SeqvarsPredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=10,
            label="whole genome",
            genotype=SeqvarsGenotypePresetsPydantic(
                choice=SeqvarsGenotypePresetChoice.ANY,
            ),
            quality=pick_by_label("any", querypresetsversion.seqvarsquerypresetsquality_set),
            consequence=pick_by_label(
                "any", querypresetsversion.seqvarsquerypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.seqvarsquerypresetslocus_set),
            frequency=pick_by_label("any", querypresetsversion.seqvarsquerypresetsfrequency_set),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label(
                "disabled", querypresetsversion.seqvarsquerypresetsvariantprio_set
            ),
            clinvar=pick_by_label("disabled", querypresetsversion.seqvarsquerypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.seqvarsquerypresetscolumns_set),
        ),
    ]


def create_seqvarspresetsset_version_short_read_genome_1_0(
    presetsset: SeqvarsQueryPresetsSet, faker: Faker
) -> SeqvarsQueryPresetsSetVersion:
    result = SeqvarsQueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        presetsset=presetsset,
        version_major=1,
        version_minor=0,
        status=SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0 = SeqvarsQueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.seqvarsquerypresetsquality_set = create_seqvarsquerypresetsquality_short_read(faker)
    version_1_0.seqvarsquerypresetsconsequence_set = create_seqvarsquerypresetsconsequence(faker)
    version_1_0.seqvarsquerypresetslocus_set = create_seqvarsquerypresetslocus(faker)
    version_1_0.seqvarsquerypresetsfrequency_set = create_seqvarsquerypresetsfrequency(faker)
    version_1_0.seqvarsquerypresetsphenotypeprio_set = create_seqvarsquerypresetsphenotypeprio(
        faker
    )
    version_1_0.seqvarsquerypresetsvariantprio_set = create_seqvarsquerypresetsvariantprio(faker)
    version_1_0.seqvarsquerypresetsclinvar_set = create_seqvarsquerypresetsclinvar(faker)
    version_1_0.seqvarsquerypresetscolumns_set = create_seqvarsquerypresetscolumns(faker)
    result.versions = [version_1_0]
    return result


def create_seqvarspresetsset_short_read_genome(rank: int = 1) -> SeqvarsQueryPresetsSet:
    """Create presets set with versions for short-read genome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = SeqvarsQueryPresetsSet(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        is_factory_default=True,
        rank=1,
        label="short-read genome sequencing",
        description=(
            "Settings for short-read genome sequencing with strict quality "
            "presets.  These settings are aimed at WGS sequencing with at "
            "least 30x coverage."
        ),
    )
    version_1_0 = SeqvarsQueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.seqvarsquerypresetsquality_set = create_seqvarsquerypresetsquality_short_read(faker)
    version_1_0.seqvarsquerypresetsconsequence_set = create_seqvarsquerypresetsconsequence(faker)
    version_1_0.seqvarsquerypresetslocus_set = create_seqvarsquerypresetslocus(faker)
    version_1_0.seqvarsquerypresetsfrequency_set = create_seqvarsquerypresetsfrequency(faker)
    version_1_0.seqvarsquerypresetsphenotypeprio_set = create_seqvarsquerypresetsphenotypeprio(
        faker
    )
    version_1_0.seqvarsquerypresetsvariantprio_set = create_seqvarsquerypresetsvariantprio(faker)
    version_1_0.seqvarsquerypresetsclinvar_set = create_seqvarsquerypresetsclinvar(faker)
    version_1_0.seqvarsquerypresetscolumns_set = create_seqvarsquerypresetscolumns(faker)
    version_1_0.seqvarspredefinedquery_set = create_seqvarspredefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result


def create_seqvarspresetsset_short_read_exome_modern(rank: int = 2) -> SeqvarsQueryPresetsSet:
    """Create presets set with versions for short-read exome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = SeqvarsQueryPresetsSet(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        is_factory_default=True,
        rank=2,
        label="short-read exome sequencing (modern)",
        description=(
            "Settings for short-read exome sequencing with strict quality "
            "presets.  These settings are aimed at 'modern' WES sequencing "
            "where a target coverage of >=20x can be achieved for >=99% of "
            "the exome."
        ),
    )
    version_1_0 = SeqvarsQueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.seqvarsquerypresetsquality_set = create_seqvarsquerypresetsquality_short_read(faker)
    version_1_0.seqvarsquerypresetsconsequence_set = create_seqvarsquerypresetsconsequence(faker)
    version_1_0.seqvarsquerypresetslocus_set = create_seqvarsquerypresetslocus(faker)
    version_1_0.seqvarsquerypresetsfrequency_set = create_seqvarsquerypresetsfrequency(faker)
    version_1_0.seqvarsquerypresetsphenotypeprio_set = create_seqvarsquerypresetsphenotypeprio(
        faker
    )
    version_1_0.seqvarsquerypresetsvariantprio_set = create_seqvarsquerypresetsvariantprio(faker)
    version_1_0.seqvarsquerypresetsclinvar_set = create_seqvarsquerypresetsclinvar(faker)
    version_1_0.seqvarsquerypresetscolumns_set = create_seqvarsquerypresetscolumns(faker)
    version_1_0.seqvarspredefinedquery_set = create_seqvarspredefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result


def create_seqvarspresetsset_short_read_exome_legacy(rank: int = 3) -> SeqvarsQueryPresetsSet:
    """Create presets set with versions for short-read exome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = SeqvarsQueryPresetsSet(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        is_factory_default=True,
        rank=3,
        label="short-read exome sequencing (legacy)",
        description=(
            "Settings for short-read exome sequencing with relaxed quality "
            "presets.  These settings are aimed at 'legacy' WES sequencing "
            "where a target coverage of >=20x cannot be achieved for a "
            "considerable portion of the exome."
        ),
    )
    version_1_0 = SeqvarsQueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.seqvarsquerypresetsquality_set = create_seqvarsquerypresetsquality_short_read(faker)
    version_1_0.seqvarsquerypresetsconsequence_set = create_seqvarsquerypresetsconsequence(faker)
    version_1_0.seqvarsquerypresetslocus_set = create_seqvarsquerypresetslocus(faker)
    version_1_0.seqvarsquerypresetsfrequency_set = create_seqvarsquerypresetsfrequency(faker)
    version_1_0.seqvarsquerypresetsphenotypeprio_set = create_seqvarsquerypresetsphenotypeprio(
        faker
    )
    version_1_0.seqvarsquerypresetsvariantprio_set = create_seqvarsquerypresetsvariantprio(faker)
    version_1_0.seqvarsquerypresetsclinvar_set = create_seqvarsquerypresetsclinvar(faker)
    version_1_0.seqvarsquerypresetscolumns_set = create_seqvarsquerypresetscolumns(faker)
    version_1_0.seqvarspredefinedquery_set = create_seqvarspredefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result


def store_factory_defaults():
    """Creates factory defaults presets sets in-memory and them to the
    database if they are not present yet.

    The main assumption is that we only have to create/add preset sets and
    versions, no modifications and no changes within versions.

    The ``sodar_uuid`` values are used to identify the records.
    """
    all_default_sets = (
        create_seqvarspresetsset_short_read_genome(),
        create_seqvarspresetsset_short_read_exome_modern(),
        create_seqvarspresetsset_short_read_exome_legacy(),
    )

    for default_set in all_default_sets:
        if not SeqvarsQueryPresetsSet.objects.filter(sodar_uuid=default_set.sodar_uuid).exists():
            print("Cloning factory default presets set %s" % default_set.label)
            presetset = default_set.save()
        else:
            presetset = SeqvarsQueryPresetsSet.objects.get(sodar_uuid=default_set.sodar_uuid)
            for version in default_set.versions.all():
                if not SeqvarsQueryPresetsSetVersion.objects.filter(
                    sodar_uuid=version.sodar_uuid
                ).exists():
                    print(
                        "Cloning factory default presets set version %d.%d for %s"
                        % (version.version_major, version.version_minor, default_set.label)
                    )
                    version.presetset = presetset
                    version.save()
