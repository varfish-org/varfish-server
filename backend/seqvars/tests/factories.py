import django.utils.timezone
import factory

from cases_analysis.tests.factories import CaseAnalysisSessionFactory
from seqvars.models.base import (
    ClinvarGermlineAggregateDescriptionChoice,
    DataSourceInfoPydantic,
    DataSourceInfosPydantic,
    GenePanelPydantic,
    GenePanelSourceChoice,
    GenePydantic,
    GenomeReleaseChoice,
    SeqvarsColumnConfigPydantic,
    SeqvarsGenotypeChoice,
    SeqvarsGenotypePresetChoice,
    SeqvarsGenotypePresetsPydantic,
    SeqvarsInhouseFrequencySettingsPydantic,
    SeqvarsMitochondrialFrequencySettingsPydantic,
    SeqvarsNuclearFrequencySettingsPydantic,
    SeqvarsOutputRecordPydantic,
    SeqvarsPredefinedQuery,
    SeqvarsPrioServicePydantic,
    SeqvarsQuery,
    SeqvarsQueryExecution,
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
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsClinvar,
    SeqvarsQuerySettingsColumns,
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsPhenotypePrio,
    SeqvarsQuerySettingsQuality,
    SeqvarsQuerySettingsVariantPrio,
    SeqvarsResultRow,
    SeqvarsResultSet,
    SeqvarsSampleGenotypePydantic,
    SeqvarsSampleQualityFilterPydantic,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantAnnotationPydantic,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantTypeChoice,
    SeqvarsVcfVariantPydantic,
    TermPresencePydantic,
    TermPydantic,
)
from variants.tests.factories import ProjectFactory


class SampleGenotypeChoiceFactory(factory.Factory):
    sample = factory.sequence(lambda n: f"sample-{n}")
    # genotypes: see @factory.lazy_attribute_sequence below

    @factory.lazy_attribute_sequence
    def genotype(self, n: int):
        values = SeqvarsGenotypeChoice.values()
        return SeqvarsGenotypeChoice(values[n % len(values)])

    class Meta:
        model = SeqvarsSampleGenotypePydantic


class SampleGenotypeSettingsBaseFactory(factory.django.DjangoModelFactory):

    @factory.lazy_attribute
    def sample_genotypes(self):
        return [SampleGenotypeChoiceFactory() for _ in range(3)]

    class Meta:
        abstract = True


class NuclearFrequencySettingsFactory(factory.Factory):

    enabled = False
    max_hom = None
    max_het = None
    max_hemi = None
    max_af = None

    class Meta:
        model = SeqvarsNuclearFrequencySettingsPydantic


class MitochondrialFrequencySettingsFactory(factory.Factory):

    enabled = False
    max_het = None
    max_hom = None
    max_af = None

    class Meta:
        model = SeqvarsMitochondrialFrequencySettingsPydantic


class InhouseFrequencySettingsFactory(factory.Factory):

    enabled = False
    max_het = None
    max_hom = None
    max_hemi = None
    max_carriers = None

    class Meta:
        model = SeqvarsInhouseFrequencySettingsPydantic


class FrequencySettingsBaseFactory(factory.django.DjangoModelFactory):

    @factory.lazy_attribute
    def gnomad_exomes(self):
        return NuclearFrequencySettingsFactory()

    @factory.lazy_attribute
    def gnomad_genomes(self):
        return NuclearFrequencySettingsFactory()

    @factory.lazy_attribute
    def gnomad_mtdna(self):
        return MitochondrialFrequencySettingsFactory()

    @factory.lazy_attribute
    def helixmtdb(self):
        return MitochondrialFrequencySettingsFactory()

    @factory.lazy_attribute
    def inhouse(self):
        return InhouseFrequencySettingsFactory()

    class Meta:
        abstract = True


class ConsequenceSettingsBaseFactory(factory.django.DjangoModelFactory):

    variant_types = [SeqvarsVariantTypeChoice.SNV]
    transcript_types = [SeqvarsTranscriptTypeChoice.CODING]
    variant_consequences = [SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT]
    max_distance_to_exon = 50

    class Meta:
        abstract = True


class LocusSettingsBaseFactory(factory.django.DjangoModelFactory):

    genes = [
        GenePydantic(hgnc_id="HGNC:1234", symbol="GENE1"),
    ]
    gene_panels = [
        GenePanelPydantic(
            source=GenePanelSourceChoice.PANELAPP,
            panel_id="126",
            name="Monogenic hearing loss",
            version="4.39",
        )
    ]
    genome_regions = []

    class Meta:
        abstract = True


class PhenotypePrioSettingsBaseFactory(factory.django.DjangoModelFactory):

    phenotype_prio_enabled = False
    phenotype_prio_algorithm = "HiPhive"
    terms = [
        TermPresencePydantic(
            term=TermPydantic(
                term_id="HP:0000001",
                label="Phenotype 1",
            ),
            excluded=False,
        )
    ]

    class Meta:
        abstract = True


class VariantPrioSettingsBaseFactory(factory.django.DjangoModelFactory):

    variant_prio_enabled = False
    services = [SeqvarsPrioServicePydantic(name="MutationTaster", version="2021")]

    class Meta:
        abstract = True


class ClinvarSettingsBaseFactory(factory.django.DjangoModelFactory):

    clinvar_presence_required = False
    clinvar_germline_aggregate_description = [
        ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC,
        ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC,
    ]
    allow_conflicting_interpretations = False

    class Meta:
        abstract = True


class ColumnsSettingsBaseFactory(factory.django.DjangoModelFactory):

    column_settings = [
        SeqvarsColumnConfigPydantic(
            name="chromosome",
            label="Chromosome",
            width=300,
            visible=True,
        )
    ]

    class Meta:
        abstract = True


class BaseModelFactory(factory.django.DjangoModelFactory):
    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(django.utils.timezone.now)
    date_modified = factory.LazyFunction(django.utils.timezone.now)

    class Meta:
        abstract = True


class LabeledSortableBaseFactory(BaseModelFactory):
    rank = 1
    label = factory.Sequence(lambda n: f"label-{n}")
    description = None

    class Meta:
        abstract = True


class SeqvarsQueryPresetsSetFactory(LabeledSortableBaseFactory):

    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = SeqvarsQueryPresetsSet


class SeqvarsQueryPresetsSetVersionFactory(BaseModelFactory):

    presetsset = factory.SubFactory(SeqvarsQueryPresetsSetFactory)
    version_major = 1
    version_minor = 0
    status = SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE

    class Meta:
        model = SeqvarsQueryPresetsSetVersion


class SeqvarsGenotypePresetsPydanticFactory(factory.Factory):

    choice = SeqvarsGenotypePresetChoice.ANY

    class Meta:
        model = SeqvarsGenotypePresetsPydantic


class QueryPresetsBaseFactory(LabeledSortableBaseFactory):

    presetssetversion = factory.SubFactory(SeqvarsQueryPresetsSetVersionFactory)

    class Meta:
        abstract = True


class SeqvarsQueryPresetsQualityFactory(QueryPresetsBaseFactory):

    filter_active = True
    min_dp_het = 10
    min_dp_hom = 5
    min_ab_het = 0.3
    min_gq = 20
    min_ad = 3

    class Meta:
        model = SeqvarsQueryPresetsQuality


class SeqvarsQueryPresetsFrequencyFactory(FrequencySettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = SeqvarsQueryPresetsFrequency


class SeqvarsQueryPresetsConsequenceFactory(
    ConsequenceSettingsBaseFactory, QueryPresetsBaseFactory
):

    class Meta:
        model = SeqvarsQueryPresetsConsequence


class SeqvarsQueryPresetsLocusFactory(LocusSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = SeqvarsQueryPresetsLocus


class SeqvarsQueryPresetsPhenotypePrioFactory(
    PhenotypePrioSettingsBaseFactory, QueryPresetsBaseFactory
):

    class Meta:
        model = SeqvarsQueryPresetsPhenotypePrio


class SeqvarsQueryPresetsVariantPrioFactory(
    VariantPrioSettingsBaseFactory, QueryPresetsBaseFactory
):

    class Meta:
        model = SeqvarsQueryPresetsVariantPrio


class SeqvarsQueryPresetsClinvarFactory(ClinvarSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = SeqvarsQueryPresetsClinvar


class SeqvarsQueryPresetsColumnsFactory(ColumnsSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = SeqvarsQueryPresetsColumns


class SeqvarsPredefinedQueryFactory(QueryPresetsBaseFactory):

    included_in_sop = False

    genotype = SeqvarsGenotypePresetsPydanticFactory()
    quality = factory.SubFactory(SeqvarsQueryPresetsQualityFactory)
    frequency = factory.SubFactory(SeqvarsQueryPresetsFrequencyFactory)
    consequence = factory.SubFactory(SeqvarsQueryPresetsConsequenceFactory)
    locus = factory.SubFactory(SeqvarsQueryPresetsLocusFactory)
    phenotypeprio = factory.SubFactory(SeqvarsQueryPresetsPhenotypePrioFactory)
    variantprio = factory.SubFactory(SeqvarsQueryPresetsVariantPrioFactory)
    clinvar = factory.SubFactory(SeqvarsQueryPresetsClinvarFactory)
    columns = factory.SubFactory(SeqvarsQueryPresetsColumnsFactory)

    class Meta:
        model = SeqvarsPredefinedQuery


class SeqvarsQuerySettingsFactory(BaseModelFactory):

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    genotype = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsGenotypeFactory",
        factory_related_name="querysettings",
    )
    quality = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsQualityFactory",
        factory_related_name="querysettings",
    )
    consequence = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsConsequenceFactory",
        factory_related_name="querysettings",
    )
    locus = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsLocusFactory",
        factory_related_name="querysettings",
    )
    frequency = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsFrequencyFactory",
        factory_related_name="querysettings",
    )
    phenotypeprio = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsPhenotypePrioFactory",
        factory_related_name="querysettings",
    )
    variantprio = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsVariantPrioFactory",
        factory_related_name="querysettings",
    )
    clinvar = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsClinvarFactory",
        factory_related_name="querysettings",
    )
    columns = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarsQuerySettingsColumnsFactory",
        factory_related_name="querysettings",
    )

    class Meta:
        model = SeqvarsQuerySettings


class SeqvarsQuerySettingsGenotypeFactory(BaseModelFactory):

    # We pass in genotype=None to prevent creation of a second
    # ``QuerySettingsGenotype``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, genotype=None)

    recessive_mode = SeqvarsQuerySettingsGenotype.RECESSIVE_MODE_DISABLED

    sample_genotype_choices = [SampleGenotypeChoiceFactory()]

    class Meta:
        model = SeqvarsQuerySettingsGenotype


class SeqvarsQuerySettingsQualityFactory(BaseModelFactory):

    # We pass in quality=None to prevent creation of a second
    # ``QuerySettingsQuality``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, quality=None)
    sample_quality_filters = [
        SeqvarsSampleQualityFilterPydantic(
            sample="index",
        )
    ]

    class Meta:
        model = SeqvarsQuerySettingsQuality


class SeqvarsQuerySettingsFrequencyFactory(FrequencySettingsBaseFactory, BaseModelFactory):

    # We pass in frequency=None to prevent creation of a second
    # ``QuerySettingsFrequency``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, frequency=None)

    class Meta:
        model = SeqvarsQuerySettingsFrequency


class SeqvarsQuerySettingsConsequenceFactory(ConsequenceSettingsBaseFactory, BaseModelFactory):

    # We pass in consequence=None to prevent creation of a second
    # ``QuerySettingsConsequence``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, consequence=None)

    class Meta:
        model = SeqvarsQuerySettingsConsequence


class SeqvarsQuerySettingsLocusFactory(LocusSettingsBaseFactory, BaseModelFactory):

    # We pass in locus=None to prevent creation of a second
    # ``QuerySettingsLocus``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, locus=None)

    class Meta:
        model = SeqvarsQuerySettingsLocus


class SeqvarsQuerySettingsPhenotypePrioFactory(PhenotypePrioSettingsBaseFactory, BaseModelFactory):

    # We pass in phenotypeprio=None to prevent creation of a second
    # ``QuerySettingsPhenotypePrio``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, phenotypeprio=None)

    class Meta:
        model = SeqvarsQuerySettingsPhenotypePrio


class SeqvarsQuerySettingsVariantPrioFactory(VariantPrioSettingsBaseFactory, BaseModelFactory):

    # We pass in variantprio=None to prevent creation of a second
    # ``QuerySettingsVariantPrio``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, variantprio=None)

    class Meta:
        model = SeqvarsQuerySettingsVariantPrio


class SeqvarsQuerySettingsClinvarFactory(ClinvarSettingsBaseFactory, BaseModelFactory):

    # We pass in clinvar=None to prevent creation of a second
    # ``QuerySettingsClinvar``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, clinvar=None)

    class Meta:
        model = SeqvarsQuerySettingsClinvar


class SeqvarsQuerySettingsColumnsFactory(ColumnsSettingsBaseFactory, BaseModelFactory):

    # We pass in columns=None to prevent creation of a second
    # ``QuerySettingsColumns``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, columns=None)

    class Meta:
        model = SeqvarsQuerySettingsColumns


class SeqvarsQueryFactory(BaseModelFactory):

    rank = 1
    label = factory.Sequence(lambda n: f"query-{n}")

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    settings = factory.SubFactory(SeqvarsQuerySettingsFactory)

    class Meta:
        model = SeqvarsQuery


class SeqvarsQueryExecutionFactory(BaseModelFactory):

    state = SeqvarsQueryExecution.STATE_DONE
    start_time = factory.LazyFunction(django.utils.timezone.now)
    end_time = factory.LazyFunction(django.utils.timezone.now)
    # elapsed_seconds: see @factory.lazy_attribute below
    query = factory.SubFactory(SeqvarsQueryFactory)
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory)

    @factory.lazy_attribute
    def elapsed_seconds(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).seconds
        else:
            return None

    class Meta:
        model = SeqvarsQueryExecution


class SeqvarsResultSetFactory(BaseModelFactory):

    queryexecution = factory.SubFactory(SeqvarsQueryExecutionFactory)
    result_row_count = 2
    # datasource_infos: see @factory.lazy_attribute below

    @factory.lazy_attribute
    def datasource_infos(self):
        return DataSourceInfosPydantic(
            infos=[
                DataSourceInfoPydantic(
                    name="fake-name",
                    version="0.0.1",
                )
            ]
        )

    class Meta:
        model = SeqvarsResultSet


class SeqvarsVcfVariantPydanticFactory(factory.Factory):

    genome_release = GenomeReleaseChoice.GRCH37
    chrom = factory.Sequence(lambda n: f"chr{n % 22}")
    chrom_no = factory.Sequence(lambda n: n % 22)
    pos = factory.Sequence(lambda n: 10_000_000 + n)
    ref_allele = factory.Sequence(lambda n: "ACGT"[n % 4])
    alt_allele = factory.Sequence(lambda n: "TACG"[n % 4])

    class Meta:
        model = SeqvarsVcfVariantPydantic


class SeqvarsVariantAnnotationPydanticFactory(factory.Factory):

    gene = None
    variant = None
    call = None

    class Meta:
        model = SeqvarsVariantAnnotationPydantic


class SeqvarsOutputRecordPydanticFactory(factory.Factory):

    uuid = factory.Faker("uuid4")
    case_uuid = factory.Faker("uuid4")
    vcf_variant = factory.SubFactory(SeqvarsVcfVariantPydanticFactory)
    variant_annotation = factory.SubFactory(SeqvarsVariantAnnotationPydanticFactory)

    class Meta:
        model = SeqvarsOutputRecordPydantic


class SeqvarsResultRowFactory(factory.django.DjangoModelFactory):

    sodar_uuid = factory.Faker("uuid4")

    resultset = factory.SubFactory(SeqvarsResultSetFactory)

    genome_release = "GRCh38"
    chrom = factory.Sequence(lambda n: f"chr{n % 22}")
    chrom_no = factory.Sequence(lambda n: n % 22)
    pos = factory.Sequence(lambda n: 10_000_000 + n)
    ref_allele = factory.Sequence(lambda n: "ACGT"[n % 4])
    alt_allele = factory.Sequence(lambda n: "TACG"[n % 4])

    payload = factory.SubFactory(SeqvarsOutputRecordPydanticFactory)

    class Meta:
        model = SeqvarsResultRow
