"""Factory defaults for seqvars query settings.

Great care is taken to keep this constant (fixing date times and UUID
generation).  We use snapshot tests to ensure that this is true and
that any changes will be tracked in source code.
"""

from dateutil.parser import parse as parse_datetime
from django.db import models
from faker import Faker

from seqvars.models.base import (
    ClinvarGermlineAggregateDescriptionChoice,
    GenomeRegionPydantic,
    GnomadMitochondrialFrequencySettingsPydantic,
    GnomadNuclearFrequencySettingsPydantic,
    HelixmtDbFrequencySettingsPydantic,
    InhouseFrequencySettingsPydantic,
    LabeledSortableBaseModel,
    SeqvarsGenotypePresetChoice,
    SeqvarsGenotypePresetsPydantic,
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
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
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
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                # # moderate impact
                # SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                # SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                # SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                # SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                # SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # # low impact
                # SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                # SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                # SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                # SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
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
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                # SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                # SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
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
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
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
                SeqvarsVariantConsequenceChoice.STOP_LOST,
                SeqvarsVariantConsequenceChoice.START_LOST,
                SeqvarsVariantConsequenceChoice.TRANSCRIPT_AMPLIFICATION,
                # moderate impact
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                SeqvarsVariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT,
                # low impact
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_5TH_BASE_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_DONOR_REGION_VARIANT,
                SeqvarsVariantConsequenceChoice.SPLICE_POLYPYRIMIDINE_TRACT_VARIANT,
                SeqvarsVariantConsequenceChoice.START_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.STOP_RETAINED_VARIANT,
                SeqvarsVariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifier
                SeqvarsVariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.FIVE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.THREE_PRIME_UTR_INTRON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                SeqvarsVariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # SeqvarsVariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # SeqvarsVariantConsequenceChoice.INTERGENIC_VARIANT,
                SeqvarsVariantConsequenceChoice.INTRON_VARIANT,
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
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.002,
                homozygous=0,
                heterozygous=1,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.002,
                homozygous=0,
                heterozygous=1,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=True,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
                frequency=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="dominant strict",
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.002,
                homozygous=0,
                heterozygous=1,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.002,
                homozygous=0,
                heterozygous=1,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="dominant relaxed",
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=0,
                heterozygous=50,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=0,
                heterozygous=20,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="recessive strict",
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.001,
                homozygous=0,
                heterozygous=120,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.001,
                homozygous=0,
                heterozygous=15,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="recessive relaxed",
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=20,
                heterozygous=0,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=4,
                heterozygous=150,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=True,
                frequency=0.01,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
        ),
        SeqvarsQueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="any",
            gnomad_exomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
            gnomad_genomes=GnomadNuclearFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
            ),
            gnomad_mitochondrial=GnomadMitochondrialFrequencySettingsPydantic(
                enabled=False,
                frequency=None,
                heteroplasmic=None,
                homoplasmic=None,
            ),
            helixmtdb=HelixmtDbFrequencySettingsPydantic(
                enabled=False,
                heteroplasmic=None,
                homoplasmic=None,
                frequency=None,
            ),
            inhouse=InhouseFrequencySettingsPydantic(
                enabled=False,
                frequency=0.01,
                homozygous=None,
                heterozygous=None,
                hemizygous=None,
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


def create_seqvarsquerypresetscolumns(faker: Faker) -> list[SeqvarsQueryPresetsColumns]:
    return [
        SeqvarsQueryPresetsColumns(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="defaults",
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
