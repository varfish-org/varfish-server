import datetime

import factory

from cases.tests.factories import CaseAnalysisSessionFactory
from seqvars.models import (
    DataSourceInfo,
    DataSourceInfos,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQuerySettings,
    SeqvarResultRow,
    SeqvarResultRowPayload,
    SeqvarResultSet,
)


class _BaseFactory(factory.django.DjangoModelFactory):
    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    class Meta:
        abstract = True


class SeqvarQuerySettingsFactory(_BaseFactory):

    class Meta:
        model = SeqvarQuerySettings


class SeqvarQueryFactory(_BaseFactory):

    rank = 1
    title = factory.Sequence(lambda n: f"query-{n}")

    session = factory.SubFactory(CaseAnalysisSessionFactory)
    settings_buffer = factory.SubFactory(SeqvarQuerySettingsFactory)

    class Meta:
        model = SeqvarQuery


class SeqvarQueryExecutionFactory(_BaseFactory):

    state = SeqvarQueryExecution.STATE_DONE
    start_time = factory.LazyFunction(datetime.datetime.now)
    end_time = factory.LazyFunction(datetime.datetime.now)
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


class SeqvarResultSetFactory(_BaseFactory):

    queryexecution = factory.SubFactory(SeqvarQuerySettingsFactory)
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
