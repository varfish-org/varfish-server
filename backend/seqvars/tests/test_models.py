"""Test models and factories"""

from freezegun import freeze_time
from test_plus.test import TestCase

from seqvars.models import (
    GenotypeChoice,
    Query,
    QueryExecution,
    QueryPresetsFrequency,
    QueryPresetsSet,
    QuerySettings,
    QuerySettingsFrequency,
    ResultRow,
    ResultSet,
)
from seqvars.tests.factories import (
    QueryExecutionFactory,
    QueryFactory,
    QueryPresetsFrequencyFactory,
    QueryPresetsSetFactory,
    QuerySettingsFactory,
    QuerySettingsFrequencyFactory,
    ResultRowFactory,
    ResultSetFactory,
    SampleGenotypeChoiceFactory,
)


class TestCaseGenotypeChoice(TestCase):

    def test_values(self):
        self.assertEqual(
            ["ref", "het", "hom"],
            GenotypeChoice.values(),
        )


class TestSampleGenotypeChoice(TestCase):

    def test_values(self):
        SampleGenotypeChoiceFactory()


class TestQueryPresetsSet(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsSet.objects.count(), 0)
        QueryPresetsSetFactory()
        self.assertEqual(QueryPresetsSet.objects.count(), 1)

    def test_str(self):
        querypresetsset = QueryPresetsSetFactory()
        self.assertEqual(
            f"QueryPresetsSet '{querypresetsset.sodar_uuid}'",
            querypresetsset.__str__(),
        )


class TestQueryPresetsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(QueryPresetsFrequency.objects.count(), 0)
        QueryPresetsFrequencyFactory()
        self.assertEqual(QueryPresetsFrequency.objects.count(), 1)

    def test_str(self):
        querypresetsfrequency = QueryPresetsFrequencyFactory()
        self.assertEqual(
            f"QueryPresetsFrequency '{querypresetsfrequency.sodar_uuid}'",
            querypresetsfrequency.__str__(),
        )


class TestQuerySettings(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettings.objects.count(), 0)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 0)
        QuerySettingsFactory()
        self.assertEqual(QuerySettings.objects.count(), 1)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        querysettings = QuerySettingsFactory()
        self.assertEqual(
            f"QuerySettings '{querysettings.sodar_uuid}'",
            querysettings.__str__(),
        )


class TestQuerySettingsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(QuerySettingsFrequency.objects.count(), 0)
        QuerySettingsFrequencyFactory()
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        querysettingsfrequency = QuerySettingsFrequencyFactory()
        self.assertEqual(
            f"QuerySettingsFrequency '{querysettingsfrequency.sodar_uuid}'",
            querysettingsfrequency.__str__(),
        )


class TestQuery(TestCase):

    def test_create(self):
        self.assertEqual(Query.objects.count(), 0)
        QueryFactory()
        self.assertEqual(Query.objects.count(), 1)

    def test_property_case(self):
        query = QueryFactory()
        self.assertEqual(
            query.session.caseanalysis.case.pk,
            query.case.pk,
        )

    def test_str(self):
        query = QueryFactory()
        self.assertEqual(
            f"Query '{query.sodar_uuid}'",
            query.__str__(),
        )


class TestQueryExecution(TestCase):

    def test_create(self):
        self.assertEqual(QueryExecution.objects.count(), 0)
        QueryExecutionFactory()
        self.assertEqual(QueryExecution.objects.count(), 1)

    def test_property_case(self):
        queryexecution = QueryExecutionFactory()
        self.assertEqual(
            queryexecution.query.session.caseanalysis.case.pk,
            queryexecution.case.pk,
        )

    def test_str(self):
        queryexecution = QueryExecutionFactory()
        self.assertEqual(
            f"QueryExecution '{queryexecution.sodar_uuid}'",
            queryexecution.__str__(),
        )


class TestResultSet(TestCase):

    def test_create(self):
        self.assertEqual(ResultSet.objects.count(), 0)
        ResultSetFactory()
        self.assertEqual(ResultSet.objects.count(), 1)

    def test_property_case(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            resultset.queryexecution.query.session.caseanalysis.case.pk,
            resultset.case.pk,
        )

    def test_get_absolute_url(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            (f"/seqvars/api/resultset/{resultset.case.sodar_uuid}/" f"{resultset.sodar_uuid}/"),
            resultset.get_absolute_url(),
        )

    def test_str(self):
        resultset = ResultSetFactory()
        self.assertEqual(
            f"ResultSet '{resultset.sodar_uuid}'",
            resultset.__str__(),
        )


class TestResultRow(TestCase):

    def test_create(self):
        self.assertEqual(ResultRow.objects.count(), 0)
        ResultRowFactory()
        self.assertEqual(ResultRow.objects.count(), 1)

    def test_str(self):
        seqvarresultrow = ResultRowFactory()
        self.assertEqual(
            (
                f"ResultRow '{seqvarresultrow.sodar_uuid}' '{seqvarresultrow.release}-"
                f"{seqvarresultrow.chromosome}-{seqvarresultrow.start}-"
                f"{seqvarresultrow.reference}-{seqvarresultrow.alternative}'"
            ),
            seqvarresultrow.__str__(),
        )
