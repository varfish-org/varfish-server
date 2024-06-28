import datetime

import django.utils.timezone
import factory

from cases_analysis.tests.factories import CaseAnalysisSessionFactory
from seqvars.models import (
    ClinvarGermlineAggregateDescription,
    ColumnConfig,
    DataSourceInfo,
    DataSourceInfos,
    Gene,
    GenePanel,
    GenePanelSource,
    GenotypeChoice,
    Query,
    QueryColumnsConfig,
    QueryExecution,
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
    QuerySettings,
    QuerySettingsClinvar,
    QuerySettingsConsequence,
    QuerySettingsFrequency,
    QuerySettingsGenotype,
    QuerySettingsLocus,
    QuerySettingsPhenotypePrio,
    QuerySettingsQuality,
    QuerySettingsVariantPrio,
    ResultRow,
    ResultRowPayload,
    ResultSet,
    SampleGenotypeChoice,
    SampleQualityFilter,
    Term,
    TermPresence,
    TranscriptTypeChoice,
    VariantConsequenceChoice,
    VariantPrioService,
    VariantTypeChoice,
)
from variants.tests.factories import ProjectFactory


class SampleGenotypeChoiceFactory(factory.Factory):
    sample = factory.sequence(lambda n: f"sample-{n}")
    # genotypes: see @factory.lazy_attribute_sequence below

    @factory.lazy_attribute_sequence
    def genotype(self, n: int):
        values = GenotypeChoice.values()
        return GenotypeChoice(values[n % len(values)])

    class Meta:
        model = SampleGenotypeChoice


class SampleGenotypeSettingsBaseFactory(factory.django.DjangoModelFactory):
    sample_genotypes = factory.Faker("pydantic_field", schema=[SampleGenotypeChoice])

    @factory.lazy_attribute
    def sample_genotypes(self):
        return [SampleGenotypeChoiceFactory() for _ in range(3)]

    class Meta:
        abstract = True


class FrequencySettingsBaseFactory(factory.django.DjangoModelFactory):

    gnomad_exomes_enabled = False
    gnomad_exomes_frequency = None
    gnomad_exomes_homozygous = None
    gnomad_exomes_heterozygous = None
    gnomad_exomes_hemizygous = None

    gnomad_genomes_enabled = False
    gnomad_genomes_frequency = None
    gnomad_genomes_homozygous = None
    gnomad_genomes_heterozygous = None
    gnomad_genomes_hemizygous = None

    helixmtdb_enabled = False
    helixmtdb_heteroplasmic = None
    helixmtdb_homoplasmic = None
    helixmtdb_frequency = None

    inhouse_enabled = False
    inhouse_carriers = None
    inhouse_homozygous = None
    inhouse_heterozygous = None
    inhouse_hemizygous = None

    class Meta:
        abstract = True


class ConsequenceSettingsBaseFactory(factory.django.DjangoModelFactory):

    variant_types = [VariantTypeChoice.SNV]
    transcript_types = [TranscriptTypeChoice.CODING]
    variant_consequences = [VariantConsequenceChoice.MISSENSE_VARIANT]
    max_distance_to_exon = 50

    class Meta:
        abstract = True


class LocusSettingsBaseFactory(factory.django.DjangoModelFactory):

    genes = [
        Gene(hgnc_id="HGNC:1234", symbol="GENE1"),
    ]
    gene_panels = [
        GenePanel(
            source=GenePanelSource.PANELAPP,
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
        TermPresence(
            term=Term(
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
    services = [VariantPrioService(name="MutationTaster", version="2021")]

    class Meta:
        abstract = True


class ClinvarSettingsBaseFactory(factory.django.DjangoModelFactory):

    clinvar_presence_required = False
    clinvar_germline_aggregate_description = [
        ClinvarGermlineAggregateDescription.PATHOGENIC,
        ClinvarGermlineAggregateDescription.LIKELY_PATHOGENIC,
    ]
    allow_conflicting_interpretations = False
    include_legacy_descriptions = False

    class Meta:
        abstract = True


class ColumnsSettingsBaseFactory(factory.django.DjangoModelFactory):

    column_settings = [
        ColumnConfig(
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


class QueryPresetsSetFactory(LabeledSortableBaseFactory):

    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = QueryPresetsSet


class QueryPresetsSetVersionFactory(BaseModelFactory):

    presetsset = factory.SubFactory(QueryPresetsSetFactory)
    version_major = 1
    version_minor = 0
    status = QueryPresetsSetVersion.STATUS_ACTIVE

    class Meta:
        model = QueryPresetsSetVersion


class QueryPresetsBaseFactory(LabeledSortableBaseFactory):

    presetssetversion = factory.SubFactory(QueryPresetsSetVersionFactory)

    class Meta:
        abstract = True


class QueryPresetsQualityFactory(QueryPresetsBaseFactory):

    filter_active = True
    min_dp_het = 10
    min_dp_hom = 5
    min_ab_het = 0.3
    min_gq = 20
    min_ad = 3

    class Meta:
        model = QueryPresetsQuality


class QueryPresetsFrequencyFactory(FrequencySettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsFrequency


class QueryPresetsConsequenceFactory(ConsequenceSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsConsequence


class QueryPresetsLocusFactory(LocusSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsLocus


class QueryPresetsPhenotypePrioFactory(PhenotypePrioSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsPhenotypePrio


class QueryPresetsVariantPrioFactory(VariantPrioSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsVariantPrio


class QueryPresetsClinvarFactory(ClinvarSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsClinvar


class QueryPresetsColumnsFactory(ColumnsSettingsBaseFactory, QueryPresetsBaseFactory):

    class Meta:
        model = QueryPresetsColumns


class QuerySettingsFactory(BaseModelFactory):

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    genotype = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsGenotypeFactory",
        factory_related_name="querysettings",
    )
    quality = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsQualityFactory",
        factory_related_name="querysettings",
    )
    consequence = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsConsequenceFactory",
        factory_related_name="querysettings",
    )
    locus = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsLocusFactory",
        factory_related_name="querysettings",
    )
    frequency = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsFrequencyFactory",
        factory_related_name="querysettings",
    )
    phenotypeprio = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsPhenotypePrioFactory",
        factory_related_name="querysettings",
    )
    variantprio = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsVariantPrioFactory",
        factory_related_name="querysettings",
    )
    clinvar = factory.RelatedFactory(
        "seqvars.tests.factories.QuerySettingsClinvarFactory",
        factory_related_name="querysettings",
    )

    class Meta:
        model = QuerySettings


class QuerySettingsGenotypeFactory(BaseModelFactory):

    # We pass in genotype=None to prevent creation of a second
    # ``QuerySettingsGenotype``.
    querysettings = factory.SubFactory(QuerySettingsFactory, genotype=None)

    sample_genotype_choices = [SampleGenotypeChoiceFactory()]

    class Meta:
        model = QuerySettingsGenotype


class QuerySettingsQualityFactory(BaseModelFactory):

    # We pass in quality=None to prevent creation of a second
    # ``QuerySettingsQuality``.
    querysettings = factory.SubFactory(QuerySettingsFactory, quality=None)
    sample_quality_filters = [
        SampleQualityFilter(
            sample="index",
        )
    ]

    class Meta:
        model = QuerySettingsQuality


class QuerySettingsFrequencyFactory(FrequencySettingsBaseFactory, BaseModelFactory):

    # We pass in frequency=None to prevent creation of a second
    # ``QuerySettingsFrequency``.
    querysettings = factory.SubFactory(QuerySettingsFactory, frequency=None)

    class Meta:
        model = QuerySettingsFrequency


class QuerySettingsConsequenceFactory(ConsequenceSettingsBaseFactory, BaseModelFactory):

    # We pass in consequence=None to prevent creation of a second
    # ``QuerySettingsConsequence``.
    querysettings = factory.SubFactory(QuerySettingsFactory, consequence=None)

    class Meta:
        model = QuerySettingsConsequence


class QuerySettingsLocusFactory(LocusSettingsBaseFactory, BaseModelFactory):

    # We pass in locus=None to prevent creation of a second
    # ``QuerySettingsLocus``.
    querysettings = factory.SubFactory(QuerySettingsFactory, locus=None)

    class Meta:
        model = QuerySettingsLocus


class QuerySettingsPhenotypePrioFactory(PhenotypePrioSettingsBaseFactory, BaseModelFactory):

    # We pass in phenotypeprio=None to prevent creation of a second
    # ``QuerySettingsPhenotypePrio``.
    querysettings = factory.SubFactory(QuerySettingsFactory, phenotypeprio=None)

    class Meta:
        model = QuerySettingsPhenotypePrio


class QuerySettingsVariantPrioFactory(VariantPrioSettingsBaseFactory, BaseModelFactory):

    # We pass in variantprio=None to prevent creation of a second
    # ``QuerySettingsVariantPrio``.
    querysettings = factory.SubFactory(QuerySettingsFactory, variantprio=None)

    class Meta:
        model = QuerySettingsVariantPrio


class QuerySettingsClinvarFactory(ClinvarSettingsBaseFactory, BaseModelFactory):

    # We pass in clinvar=None to prevent creation of a second
    # ``QuerySettingsClinvar``.
    querysettings = factory.SubFactory(QuerySettingsFactory, clinvar=None)

    class Meta:
        model = QuerySettingsClinvar


class QueryFactory(BaseModelFactory):

    rank = 1
    label = factory.Sequence(lambda n: f"query-{n}")

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    settings = factory.SubFactory(QuerySettingsFactory)
    columnsconfig = factory.SubFactory("seqvars.tests.factories.QueryColumnsConfigFactory")

    class Meta:
        model = Query


class QueryColumnsConfigFactory(ColumnsSettingsBaseFactory, BaseModelFactory):

    class Meta:
        model = QueryColumnsConfig


class QueryExecutionFactory(BaseModelFactory):

    state = QueryExecution.STATE_DONE
    start_time = factory.LazyFunction(django.utils.timezone.now)
    end_time = factory.LazyFunction(django.utils.timezone.now)
    # elapsed_seconds: see @factory.lazy_attribute below
    query = factory.SubFactory(QueryFactory)
    querysettings = factory.SubFactory(QuerySettingsFactory)

    @factory.lazy_attribute
    def elapsed_seconds(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).seconds
        else:
            return None

    class Meta:
        model = QueryExecution


class ResultSetFactory(BaseModelFactory):

    queryexecution = factory.SubFactory(QueryExecutionFactory)
    result_row_count = 2
    # datasource_infos: see @factory.lazy_attribute below

    @factory.lazy_attribute
    def datasource_infos(self):
        return DataSourceInfos(
            infos=[
                DataSourceInfo(
                    name="fake-name",
                    version="0.0.1",
                )
            ]
        )

    class Meta:
        model = ResultSet


class ResultRowFactory(factory.django.DjangoModelFactory):

    sodar_uuid = factory.Faker("uuid4")

    resultset = factory.SubFactory(ResultSetFactory)

    release = "GRCh38"
    chromosome = factory.Sequence(lambda n: f"chr{n % 22}")
    chromosome_no = factory.Sequence(lambda n: n % 22)
    start = factory.Sequence(lambda n: 10_000_000 + n)
    stop = factory.Sequence(lambda n: 10_000_000 + n)
    reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    alternative = factory.Sequence(lambda n: "TACG"[n % 4])

    @factory.lazy_attribute
    def payload(self):
        return ResultRowPayload(foo=42)

    class Meta:
        model = ResultRow
