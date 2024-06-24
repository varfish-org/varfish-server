import datetime

import django.utils.timezone
import factory

from cases_analysis.tests.factories import CaseAnalysisSessionFactory
from seqvars.models import (
    DataSourceInfo,
    DataSourceInfos,
    GenotypeChoice,
    SampleGenotypeChoice,
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarQuerySettingsFrequency,
    SeqvarResultRow,
    SeqvarResultRowPayload,
    SeqvarResultSet,
)
from variants.tests.factories import ProjectFactory


class SampleGenotypeChoiceFactory(factory.Factory):
    sample = factory.sequence(lambda n: f"sample-{n}")
    # genotypes: see @factory.lazy_attribute_sequence below

    @factory.lazy_attribute_sequence
    def genotypes(self, n: int):
        values = GenotypeChoice.values()
        return [GenotypeChoice(values[n % len(values)])]

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


class SeqvarQueryPresetsSetFactory(LabeledSortableBaseFactory):

    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = SeqvarQueryPresetsSet


class SeqvarPresetsBaseFactory(LabeledSortableBaseFactory):

    presetsset = factory.SubFactory(SeqvarQueryPresetsSetFactory)

    class Meta:
        abstract = True


class SeqvarPresetsFrequencyFactory(FrequencySettingsBaseFactory, SeqvarPresetsBaseFactory):

    class Meta:
        model = SeqvarPresetsFrequency


class SeqvarQuerySettingsFactory(BaseModelFactory):

    seqvarquerysettingsfrequency = factory.RelatedFactory(
        "seqvars.tests.factories.SeqvarQuerySettingsFrequencyFactory",
        factory_related_name="querysettings",
    )

    class Meta:
        model = SeqvarQuerySettings


class SeqvarQuerySettingsFrequencyFactory(BaseModelFactory):

    # We pass in seqvarquerysettingsfrequency=None to prevent creation of a second
    # ``SeqvarQuerySettingsFrequency``.
    querysettings = factory.SubFactory(
        SeqvarQuerySettingsFactory, seqvarquerysettingsfrequency=None
    )

    class Meta:
        model = SeqvarQuerySettingsFrequency


class SeqvarQueryFactory(BaseModelFactory):

    rank = 1
    label = factory.Sequence(lambda n: f"query-{n}")

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    settings_buffer = factory.SubFactory(SeqvarQuerySettingsFactory)

    class Meta:
        model = SeqvarQuery


class SeqvarQueryExecutionFactory(BaseModelFactory):

    state = SeqvarQueryExecution.STATE_DONE
    start_time = factory.LazyFunction(django.utils.timezone.now)
    end_time = factory.LazyFunction(django.utils.timezone.now)
    # elapsed_seconds: see @factory.lazy_attribute below
    query = factory.SubFactory(SeqvarQueryFactory)
    querysettings = factory.SubFactory(SeqvarQuerySettingsFactory)

    @factory.lazy_attribute
    def elapsed_seconds(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).seconds
        else:
            return None

    class Meta:
        model = SeqvarQueryExecution


class SeqvarResultSetFactory(BaseModelFactory):

    queryexecution = factory.SubFactory(SeqvarQueryExecutionFactory)
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
        model = SeqvarResultSet


class SeqvarResultRowFactory(factory.django.DjangoModelFactory):

    sodar_uuid = factory.Faker("uuid4")

    resultset = factory.SubFactory(SeqvarResultSetFactory)

    release = "GRCh38"
    chromosome = factory.Sequence(lambda n: f"chr{n % 22}")
    chromosome_no = factory.Sequence(lambda n: n % 22)
    start = factory.Sequence(lambda n: 10_000_000 + n)
    stop = factory.Sequence(lambda n: 10_000_000 + n)
    reference = factory.Sequence(lambda n: "ACGT"[n % 4])
    alternative = factory.Sequence(lambda n: "TACG"[n % 4])

    @factory.lazy_attribute
    def payload(self):
        return SeqvarResultRowPayload(foo=42)

    class Meta:
        model = SeqvarResultRow
