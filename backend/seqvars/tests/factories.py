import datetime

import django.utils.timezone
import factory

from cases_analysis.tests.factories import CaseAnalysisSessionFactory
from seqvars.models import (
    ClinvarGermlineAggregateDescription,
    DataSourceInfo,
    DataSourceInfos,
    Gene,
    GenePanel,
    GenePanelSource,
    SeqvarsColumnConfig,
    SeqvarsGenotypeChoice,
    SeqvarsPredefinedQuery,
    SeqvarsPrioService,
    SeqvarsQuery,
    SeqvarsQueryColumnsConfig,
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
    SeqvarsQuerySettingsConsequence,
    SeqvarsQuerySettingsFrequency,
    SeqvarsQuerySettingsGenotype,
    SeqvarsQuerySettingsLocus,
    SeqvarsQuerySettingsPhenotypePrio,
    SeqvarsQuerySettingsQuality,
    SeqvarsQuerySettingsVariantPrio,
    SeqvarsResultRow,
    SeqvarsResultRowPayload,
    SeqvarsResultSet,
    SeqvarsSampleGenotypeChoice,
    SeqvarsSampleQualityFilter,
    SeqvarsTranscriptTypeChoice,
    SeqvarsVariantConsequenceChoice,
    SeqvarsVariantTypeChoice,
    Term,
    TermPresence,
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
        model = SeqvarsSampleGenotypeChoice


class SampleGenotypeSettingsBaseFactory(factory.django.DjangoModelFactory):
    sample_genotypes = factory.Faker("pydantic_field", schema=[SeqvarsSampleGenotypeChoice])

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

    variant_types = [SeqvarsVariantTypeChoice.SNV]
    transcript_types = [SeqvarsTranscriptTypeChoice.CODING]
    variant_consequences = [SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT]
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
    services = [SeqvarsPrioService(name="MutationTaster", version="2021")]

    class Meta:
        abstract = True


class ClinvarSettingsBaseFactory(factory.django.DjangoModelFactory):

    clinvar_presence_required = False
    clinvar_germline_aggregate_description = [
        ClinvarGermlineAggregateDescription.PATHOGENIC,
        ClinvarGermlineAggregateDescription.LIKELY_PATHOGENIC,
    ]
    allow_conflicting_interpretations = False

    class Meta:
        abstract = True


class ColumnsSettingsBaseFactory(factory.django.DjangoModelFactory):

    column_settings = [
        SeqvarsColumnConfig(
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

    class Meta:
        model = SeqvarsQuerySettings


class SeqvarsQuerySettingsGenotypeFactory(BaseModelFactory):

    # We pass in genotype=None to prevent creation of a second
    # ``QuerySettingsGenotype``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, genotype=None)

    sample_genotype_choices = [SampleGenotypeChoiceFactory()]

    class Meta:
        model = SeqvarsQuerySettingsGenotype


class SeqvarsQuerySettingsQualityFactory(BaseModelFactory):

    # We pass in quality=None to prevent creation of a second
    # ``QuerySettingsQuality``.
    querysettings = factory.SubFactory(SeqvarsQuerySettingsFactory, quality=None)
    sample_quality_filters = [
        SeqvarsSampleQualityFilter(
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


class SeqvarsQueryFactory(BaseModelFactory):

    rank = 1
    label = factory.Sequence(lambda n: f"query-{n}")

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    settings = factory.SubFactory(SeqvarsQuerySettingsFactory)
    columnsconfig = factory.SubFactory("seqvars.tests.factories.SeqvarsQueryColumnsConfigFactory")

    class Meta:
        model = SeqvarsQuery


class SeqvarsQueryColumnsConfigFactory(ColumnsSettingsBaseFactory, BaseModelFactory):

    class Meta:
        model = SeqvarsQueryColumnsConfig


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
        return DataSourceInfos(
            infos=[
                DataSourceInfo(
                    name="fake-name",
                    version="0.0.1",
                )
            ]
        )

    class Meta:
        model = SeqvarsResultSet


class SeqvarsResultRowFactory(factory.django.DjangoModelFactory):

    sodar_uuid = factory.Faker("uuid4")

    resultset = factory.SubFactory(SeqvarsResultSetFactory)

    release = "GRCh38"
    chromosome = factory.Sequence(lambda n: f"chr{n % 22}")
    chromosome_no = factory.Sequence(lambda n: n % 22)
    start = factory.Sequence(lambda n: 10_000_000 + n)
    stop = factory.Sequence(lambda n: 10_000_000 + n)
    reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    alternative = factory.Sequence(lambda n: "TACG"[n % 4])

    @factory.lazy_attribute
    def payload(self):
        return SeqvarsResultRowPayload(foo=42)

    class Meta:
        model = SeqvarsResultRow
