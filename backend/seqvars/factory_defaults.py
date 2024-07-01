"""Factory defaults for seqvars query settings.

Great care is taken to keep this constant (fixing date times and UUID
generation).  We use snapshot tests to ensure that this is true and
that any changes will be tracked in source code.
"""

from dateutil.parser import parse as parse_datetime
from django.db import models
from faker import Faker

from seqvars.models import (
    ClinvarGermlineAggregateDescription,
    GenomeRegion,
    GenotypePresetChoice,
    GenotypePresets,
    LabeledSortableBaseModel,
    PredefinedQuery,
    QueryPresetsClinvar,
    QueryPresetsColumns,
    QueryPresetsConsequence,
    QueryPresetsFrequency,
    QueryPresetsLocus,
    QueryPresetsPhenotypePrio,
    QueryPresetsQuality,
    QueryPresetsSet,
    QueryPresetsSetVersion,
    QueryPresetsVariantPrio,
    TranscriptTypeChoice,
    VariantConsequenceChoice,
    VariantPrioService,
    VariantTypeChoice,
)

#: DateTime for version 1.0 of the factory defaults.
TIME_VERSION_1_0 = parse_datetime("2024-07-01T00:00:00Z")
#: Base seed to use for UUID creation.
FAKER_SEED = 42


def create_querypresetsquality_short_read(faker: Faker) -> list[QueryPresetsQuality]:
    return [
        QueryPresetsQuality(
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
        QueryPresetsQuality(
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
        QueryPresetsQuality(
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
        QueryPresetsQuality(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="any",
            filter_active=False,
        ),
    ]


def create_querypresetsconsequence(faker: Faker) -> list[QueryPresetsConsequence]:
    return [
        QueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="any",
            variant_types=[
                VariantTypeChoice.SNV,
                VariantTypeChoice.INDEL,
                VariantTypeChoice.MNV,
                VariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                TranscriptTypeChoice.CODING,
                TranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                VariantConsequenceChoice.FRAMESHIFT_VARIANT,
                VariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                VariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                VariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                VariantConsequenceChoice.START_LOST,
                VariantConsequenceChoice.STOP_GAINED,
                VariantConsequenceChoice.STOP_LOST,
                # moderate impact
                VariantConsequenceChoice.THREE_PRIME_UTR_TRUNCATION,
                VariantConsequenceChoice.FIVE_PRIME_UTR_TRUNCATION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.MISSENSE_VARIANT,
                VariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # low impact
                VariantConsequenceChoice.INITIATOR_CODON_VARIANT,
                VariantConsequenceChoice.START_RETAINED,
                VariantConsequenceChoice.STOP_RETAINED_VARIANT,
                VariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifiers
                VariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                VariantConsequenceChoice.INTRON_VARIANT,
                VariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                VariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT,
                VariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                VariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_EXON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_EXON_VARIANT,
                VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_INTRON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
        QueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="null variant",
            variant_types=[
                VariantTypeChoice.SNV,
                VariantTypeChoice.INDEL,
                VariantTypeChoice.MNV,
                VariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                TranscriptTypeChoice.CODING,
            ],
            variant_consequences=[
                # high impact
                VariantConsequenceChoice.FRAMESHIFT_VARIANT,
                VariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                VariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                VariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                VariantConsequenceChoice.START_LOST,
                VariantConsequenceChoice.STOP_GAINED,
                VariantConsequenceChoice.STOP_LOST,
                # # moderate impact
                # VariantConsequenceChoice.THREE_PRIME_UTR_TRUNCATION,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_TRUNCATION,
                # VariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                # VariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                # VariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                # VariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                # VariantConsequenceChoice.MISSENSE_VARIANT,
                # VariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # # low impact
                # VariantConsequenceChoice.INITIATOR_CODON_VARIANT,
                # VariantConsequenceChoice.START_RETAINED,
                # VariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # VariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifiers
                # VariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # VariantConsequenceChoice.INTRON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT,
                # VariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # VariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
        QueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="AA change + splicing",
            variant_types=[
                VariantTypeChoice.SNV,
                VariantTypeChoice.INDEL,
                VariantTypeChoice.MNV,
                VariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                TranscriptTypeChoice.CODING,
            ],
            variant_consequences=[
                # high impact
                VariantConsequenceChoice.FRAMESHIFT_VARIANT,
                VariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                VariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                VariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                VariantConsequenceChoice.START_LOST,
                VariantConsequenceChoice.STOP_GAINED,
                VariantConsequenceChoice.STOP_LOST,
                # moderate impact
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.MISSENSE_VARIANT,
                VariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # # low impact
                # VariantConsequenceChoice.INITIATOR_CODON_VARIANT,
                # VariantConsequenceChoice.START_RETAINED,
                # VariantConsequenceChoice.STOP_RETAINED_VARIANT,
                # VariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # # modifiers
                # VariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                # VariantConsequenceChoice.INTRON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT,
                # VariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # VariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
        QueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="all coding + deep intronic",
            variant_types=[
                VariantTypeChoice.SNV,
                VariantTypeChoice.INDEL,
                VariantTypeChoice.MNV,
                VariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                TranscriptTypeChoice.CODING,
                TranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                VariantConsequenceChoice.FRAMESHIFT_VARIANT,
                VariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                VariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                VariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                VariantConsequenceChoice.START_LOST,
                VariantConsequenceChoice.STOP_GAINED,
                VariantConsequenceChoice.STOP_LOST,
                # moderate impact
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.MISSENSE_VARIANT,
                VariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # low impact
                VariantConsequenceChoice.INITIATOR_CODON_VARIANT,
                VariantConsequenceChoice.START_RETAINED,
                VariantConsequenceChoice.STOP_RETAINED_VARIANT,
                VariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifiers
                # VariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                VariantConsequenceChoice.INTRON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                # VariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT,
                VariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # VariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_EXON_VARIANT,
                # VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_INTRON_VARIANT,
                # VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
        QueryPresetsConsequence(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="whole transcript",
            variant_types=[
                VariantTypeChoice.SNV,
                VariantTypeChoice.INDEL,
                VariantTypeChoice.MNV,
                VariantTypeChoice.COMPLEX_SUBSTITUTION,
            ],
            transcript_types=[
                TranscriptTypeChoice.CODING,
                TranscriptTypeChoice.NON_CODING,
            ],
            variant_consequences=[
                # high impact
                VariantConsequenceChoice.FRAMESHIFT_VARIANT,
                VariantConsequenceChoice.RARE_AMINO_ACID_VARIANT,
                VariantConsequenceChoice.SPLICE_ACCEPTOR_VARIANT,
                VariantConsequenceChoice.SPLICE_DONOR_VARIANT,
                VariantConsequenceChoice.START_LOST,
                VariantConsequenceChoice.STOP_GAINED,
                VariantConsequenceChoice.STOP_LOST,
                # moderate impact
                VariantConsequenceChoice.THREE_PRIME_UTR_TRUNCATION,
                VariantConsequenceChoice.FIVE_PRIME_UTR_TRUNCATION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_DELETION,
                VariantConsequenceChoice.CONSERVATIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_DELETION,
                VariantConsequenceChoice.DISRUPTIVE_INFRAME_INSERTION,
                VariantConsequenceChoice.MISSENSE_VARIANT,
                VariantConsequenceChoice.SPLICE_REGION_VARIANT,
                # low impact
                VariantConsequenceChoice.INITIATOR_CODON_VARIANT,
                VariantConsequenceChoice.START_RETAINED,
                VariantConsequenceChoice.STOP_RETAINED_VARIANT,
                VariantConsequenceChoice.SYNONYMOUS_VARIANT,
                # modifiers
                # VariantConsequenceChoice.DOWNSTREAM_GENE_VARIANT,
                VariantConsequenceChoice.INTRON_VARIANT,
                VariantConsequenceChoice.NON_CODING_TRANSCRIPT_EXON_VARIANT,
                VariantConsequenceChoice.NON_CODING_TRANSCRIPT_INTRON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT,
                VariantConsequenceChoice.CODING_SEQUENCE_VARIANT,
                # VariantConsequenceChoice.UPSTREAM_GENE_VARIANT,
                VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_EXON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_EXON_VARIANT,
                VariantConsequenceChoice.THREE_PRIME_UTR_VARIANT_INTRON_VARIANT,
                VariantConsequenceChoice.FIVE_PRIME_UTR_VARIANT_INTRON_VARIANT,
            ],
            max_distance_to_exon=None,
        ),
    ]


def create_querypresetslocus(faker: Faker) -> list[QueryPresetsConsequence]:
    return [
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="whole genome",
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="nuclear chromosomes",
            genome_regions=[GenomeRegion(chromosome=str(no)) for no in range(1, 23)]
            + [
                GenomeRegion(chromosome="X"),
                GenomeRegion(chromosome="Y"),
            ],
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="autosomes",
            genome_regions=[GenomeRegion(chromosome=str(no)) for no in range(1, 23)],
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="gonosomes",
            genome_regions=[
                GenomeRegion(chromosome="X"),
                GenomeRegion(chromosome="Y"),
            ],
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="X chromosome",
            genome_regions=[
                GenomeRegion(chromosome="X"),
            ],
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="Y chromosome",
            genome_regions=[
                GenomeRegion(chromosome="Y"),
            ],
        ),
        QueryPresetsLocus(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=7,
            label="MT genome",
            genome_regions=[
                GenomeRegion(chromosome="MT"),
            ],
        ),
    ]


def create_querypresetsfrequency(faker: Faker) -> list[QueryPresetsFrequency]:
    return [
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="dominant super strict",
            gnomad_exomes_enabled=True,
            gnomad_exomes_frequency=0.002,
            gnomad_exomes_homozygous=0,
            gnomad_exomes_heterozygous=1,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=True,
            gnomad_genomes_frequency=0.002,
            gnomad_genomes_homozygous=0,
            gnomad_genomes_heterozygous=1,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=False,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=None,
            helixmtdb_frequency=None,
            inhouse_enabled=True,
            inhouse_carriers=20,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="dominant strict",
            gnomad_exomes_enabled=True,
            gnomad_exomes_frequency=0.002,
            gnomad_exomes_homozygous=0,
            gnomad_exomes_heterozygous=20,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=True,
            gnomad_genomes_frequency=0.002,
            gnomad_genomes_homozygous=0,
            gnomad_genomes_heterozygous=4,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=False,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=None,
            helixmtdb_frequency=None,
            inhouse_enabled=True,
            inhouse_carriers=20,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="dominant relaxed",
            gnomad_exomes_enabled=True,
            gnomad_exomes_frequency=0.01,
            gnomad_exomes_homozygous=0,
            gnomad_exomes_heterozygous=50,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=True,
            gnomad_genomes_frequency=0.01,
            gnomad_genomes_homozygous=0,
            gnomad_genomes_heterozygous=20,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=True,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=400,
            helixmtdb_frequency=0.15,
            inhouse_enabled=True,
            inhouse_carriers=20,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="recessive strict",
            gnomad_exomes_enabled=True,
            gnomad_exomes_frequency=0.001,
            gnomad_exomes_homozygous=0,
            gnomad_exomes_heterozygous=120,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=True,
            gnomad_genomes_frequency=0.001,
            gnomad_genomes_homozygous=0,
            gnomad_genomes_heterozygous=15,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=True,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=None,
            helixmtdb_frequency=None,
            inhouse_enabled=True,
            inhouse_carriers=20,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="recessive relaxed",
            gnomad_exomes_enabled=True,
            gnomad_exomes_frequency=0.01,
            gnomad_exomes_homozygous=20,
            gnomad_exomes_heterozygous=1200,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=True,
            gnomad_genomes_frequency=0.01,
            gnomad_genomes_homozygous=4,
            gnomad_genomes_heterozygous=150,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=True,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=None,
            helixmtdb_frequency=None,
            inhouse_enabled=True,
            inhouse_carriers=20,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
        QueryPresetsFrequency(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="any",
            gnomad_exomes_enabled=None,
            gnomad_exomes_frequency=None,
            gnomad_exomes_homozygous=None,
            gnomad_exomes_heterozygous=None,
            gnomad_exomes_hemizygous=None,
            gnomad_genomes_enabled=None,
            gnomad_genomes_frequency=None,
            gnomad_genomes_homozygous=None,
            gnomad_genomes_heterozygous=None,
            gnomad_genomes_hemizygous=None,
            helixmtdb_enabled=None,
            helixmtdb_heteroplasmic=None,
            helixmtdb_homoplasmic=None,
            helixmtdb_frequency=None,
            inhouse_enabled=None,
            inhouse_carriers=None,
            inhouse_homozygous=None,
            inhouse_heterozygous=None,
            inhouse_hemizygous=None,
        ),
    ]


def create_querypresetsphenotypeprio(faker: Faker) -> list[QueryPresetsPhenotypePrio]:
    return [
        QueryPresetsPhenotypePrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            phenotype_prio_enabled=False,
            phenotype_prio_algorithm="exomiser.hiphive_human",
        ),
    ]


def create_querypresetsvariantprio(faker: Faker) -> list[QueryPresetsVariantPrio]:
    return [
        QueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            variant_prio_enabled=False,
        ),
        QueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="CADD",
            variant_prio_enabled=False,
            services=[
                VariantPrioService(name="cadd", version="1.6"),
            ],
        ),
        QueryPresetsVariantPrio(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="MutationTaster",
            variant_prio_enabled=False,
            services=[
                VariantPrioService(name="mutationtaster", version="2021"),
            ],
        ),
    ]


def create_querypresetsclinvar(faker: Faker) -> list[QueryPresetsClinvar]:
    return [
        QueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="disabled",
            clinvar_presence_required=False,
        ),
        QueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="Clinvar P/LP",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescription.PATHOGENIC,
                ClinvarGermlineAggregateDescription.LIKELY_PATHOGENIC,
            ],
        ),
        QueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="Clinvar P/LP +conflicting",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescription.PATHOGENIC,
                ClinvarGermlineAggregateDescription.LIKELY_PATHOGENIC,
            ],
            allow_conflicting_interpretations=True,
        ),
        QueryPresetsClinvar(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="ClinVar P/LP/VUS +conflicting",
            clinvar_presence_required=True,
            clinvar_germline_aggregate_description=[
                ClinvarGermlineAggregateDescription.PATHOGENIC,
                ClinvarGermlineAggregateDescription.LIKELY_PATHOGENIC,
                ClinvarGermlineAggregateDescription.UNCERTAIN_SIGNIFICANCE,
            ],
            allow_conflicting_interpretations=True,
        ),
    ]


def create_querypresetscolumns(faker: Faker) -> list[QueryPresetsColumns]:
    return [
        QueryPresetsColumns(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="defaults",
        ),
    ]


def create_predefined_queries(
    querypresetsversion: QueryPresetsSetVersion, faker: Faker
) -> list[PredefinedQuery]:
    def pick_by_label(label: str, queryset: models.QuerySet) -> LabeledSortableBaseModel:
        return next(filter(lambda q: q.label == label, queryset.all()))

    return [
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=1,
            label="defaults",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.ANY,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=2,
            label="de novo",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.DE_NOVO,
            ),
            quality=pick_by_label("super strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=3,
            label="dominant",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.DOMINANT,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=4,
            label="homozygous recessive",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.HOMOZYGOUS_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=5,
            label="compound heterozygous",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.COMPOUND_HETEROZYGOUS_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=6,
            label="recessive",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=7,
            label="X recessive",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.X_RECESSIVE,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label(
                "AA change + splicing", querypresetsversion.querypresetsconsequence_set
            ),
            locus=pick_by_label("X chromosome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "recessive strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=8,
            label="ClinVar pathogenic",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.AFFECTED_CARRIERS,
            ),
            quality=pick_by_label("any", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label("any", querypresetsversion.querypresetsconsequence_set),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label("any", querypresetsversion.querypresetsfrequency_set),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label(
                "Clinvar P/LP +conflicting", querypresetsversion.querypresetsclinvar_set
            ),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=9,
            label="mitochondrial",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.AFFECTED_CARRIERS,
            ),
            quality=pick_by_label("strict", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label("any", querypresetsversion.querypresetsconsequence_set),
            locus=pick_by_label("MT genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label(
                "dominant strict", querypresetsversion.querypresetsfrequency_set
            ),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
        PredefinedQuery(
            sodar_uuid=faker.uuid4(),
            date_created=TIME_VERSION_1_0,
            date_modified=TIME_VERSION_1_0,
            rank=10,
            label="whole genome",
            genotype=GenotypePresets(
                choice=GenotypePresetChoice.ANY,
            ),
            quality=pick_by_label("any", querypresetsversion.querypresetsquality_set),
            consequence=pick_by_label("any", querypresetsversion.querypresetsconsequence_set),
            locus=pick_by_label("whole genome", querypresetsversion.querypresetslocus_set),
            frequency=pick_by_label("any", querypresetsversion.querypresetsfrequency_set),
            phenotypeprio=pick_by_label(
                "disabled", querypresetsversion.querypresetsphenotypeprio_set
            ),
            variantprio=pick_by_label("disabled", querypresetsversion.querypresetsvariantprio_set),
            clinvar=pick_by_label("disabled", querypresetsversion.querypresetsclinvar_set),
            columns=pick_by_label("defaults", querypresetsversion.querypresetscolumns_set),
        ),
    ]


def create_presetsset_version_short_read_genome_1_0(
    presetsset: QueryPresetsSet, faker: Faker
) -> QueryPresetsSetVersion:
    result = QueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        presetsset=presetsset,
        version_major=1,
        version_minor=0,
        status=QueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0 = QueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=QueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.querypresetsquality_set = create_querypresetsquality_short_read(faker)
    version_1_0.querypresetsconsequence_set = create_querypresetsconsequence(faker)
    version_1_0.querypresetslocus_set = create_querypresetslocus(faker)
    version_1_0.querypresetsfrequency_set = create_querypresetsfrequency(faker)
    version_1_0.querypresetsphenotypeprio_set = create_querypresetsphenotypeprio(faker)
    version_1_0.querypresetsvariantprio_set = create_querypresetsvariantprio(faker)
    version_1_0.querypresetsclinvar_set = create_querypresetsclinvar(faker)
    version_1_0.querypresetscolumns_set = create_querypresetscolumns(faker)
    result.versions = [version_1_0]
    return result


def create_presetsset_short_read_genome(rank: int = 1) -> QueryPresetsSet:
    """Create presets set with versions for short-read genome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = QueryPresetsSet(
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
    version_1_0 = QueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=QueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.querypresetsquality_set = create_querypresetsquality_short_read(faker)
    version_1_0.querypresetsconsequence_set = create_querypresetsconsequence(faker)
    version_1_0.querypresetslocus_set = create_querypresetslocus(faker)
    version_1_0.querypresetsfrequency_set = create_querypresetsfrequency(faker)
    version_1_0.querypresetsphenotypeprio_set = create_querypresetsphenotypeprio(faker)
    version_1_0.querypresetsvariantprio_set = create_querypresetsvariantprio(faker)
    version_1_0.querypresetsclinvar_set = create_querypresetsclinvar(faker)
    version_1_0.querypresetscolumns_set = create_querypresetscolumns(faker)
    version_1_0.predefinedquery_set = create_predefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result


def create_presetsset_short_read_exome_modern(rank: int = 2) -> QueryPresetsSet:
    """Create presets set with versions for short-read exome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = QueryPresetsSet(
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
    version_1_0 = QueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=QueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.querypresetsquality_set = create_querypresetsquality_short_read(faker)
    version_1_0.querypresetsconsequence_set = create_querypresetsconsequence(faker)
    version_1_0.querypresetslocus_set = create_querypresetslocus(faker)
    version_1_0.querypresetsfrequency_set = create_querypresetsfrequency(faker)
    version_1_0.querypresetsphenotypeprio_set = create_querypresetsphenotypeprio(faker)
    version_1_0.querypresetsvariantprio_set = create_querypresetsvariantprio(faker)
    version_1_0.querypresetsclinvar_set = create_querypresetsclinvar(faker)
    version_1_0.querypresetscolumns_set = create_querypresetscolumns(faker)
    version_1_0.predefinedquery_set = create_predefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result


def create_presetsset_short_read_exome_legacy(rank: int = 3) -> QueryPresetsSet:
    """Create presets set with versions for short-read exome sequencing.

    :param rank: Rank of the presets set, also used for offsetting the seed for UUID generation.
    """
    faker = Faker()
    faker.seed_instance(FAKER_SEED + rank)
    result = QueryPresetsSet(
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
    version_1_0 = QueryPresetsSetVersion(
        sodar_uuid=faker.uuid4(),
        date_created=TIME_VERSION_1_0,
        date_modified=TIME_VERSION_1_0,
        version_major=1,
        version_minor=0,
        status=QueryPresetsSetVersion.STATUS_ACTIVE,
        signed_off_by=None,
    )
    version_1_0.querypresetsquality_set = create_querypresetsquality_short_read(faker)
    version_1_0.querypresetsconsequence_set = create_querypresetsconsequence(faker)
    version_1_0.querypresetslocus_set = create_querypresetslocus(faker)
    version_1_0.querypresetsfrequency_set = create_querypresetsfrequency(faker)
    version_1_0.querypresetsphenotypeprio_set = create_querypresetsphenotypeprio(faker)
    version_1_0.querypresetsvariantprio_set = create_querypresetsvariantprio(faker)
    version_1_0.querypresetsclinvar_set = create_querypresetsclinvar(faker)
    version_1_0.querypresetscolumns_set = create_querypresetscolumns(faker)
    version_1_0.predefinedquery_set = create_predefined_queries(version_1_0, faker)
    result.versions = [version_1_0]
    return result
