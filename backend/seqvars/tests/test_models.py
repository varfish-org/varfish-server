"""Test models and factories"""

from freezegun import freeze_time
from test_plus.test import TestCase

from seqvars.models import (
    GenotypeChoice,
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryExecution,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarQuerySettingsFrequency,
    SeqvarResultRow,
    SeqvarResultSet,
)
from seqvars.tests.factories import (
    SampleGenotypeChoiceFactory,
    SeqvarPresetsFrequencyFactory,
    SeqvarQueryExecutionFactory,
    SeqvarQueryFactory,
    SeqvarQueryPresetsSetFactory,
    SeqvarQuerySettingsFactory,
    SeqvarQuerySettingsFrequencyFactory,
    SeqvarResultRowFactory,
    SeqvarResultSetFactory,
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


class TestSeqvarQueryPresetsSet(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 0)
        SeqvarQueryPresetsSetFactory()
        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 1)

    def test_str(self):
        seqvarquerypresetsset = SeqvarQueryPresetsSetFactory()
        self.assertEqual(
            f"SeqvarQueryPresetsSet '{seqvarquerypresetsset.sodar_uuid}'",
            seqvarquerypresetsset.__str__(),
        )


class TestSeqvarPresetsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 0)
        SeqvarPresetsFrequencyFactory()
        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 1)

    def test_str(self):
        seqvarpresetsfrequency = SeqvarPresetsFrequencyFactory()
        self.assertEqual(
            f"SeqvarPresetsFrequency '{seqvarpresetsfrequency.sodar_uuid}'",
            seqvarpresetsfrequency.__str__(),
        )


class TestSeqvarQuerySettings(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarQuerySettings.objects.count(), 0)
        SeqvarQuerySettingsFactory()
        self.assertEqual(SeqvarQuerySettings.objects.count(), 1)

    def test_str(self):
        seqvarquerysettings = SeqvarQuerySettingsFactory()
        self.assertEqual(
            f"SeqvarQuerySettings '{seqvarquerysettings.sodar_uuid}'",
            seqvarquerysettings.__str__(),
        )


class TestSeqvarQuerySettingsFrequency(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 0)
        SeqvarQuerySettingsFrequencyFactory()
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 1)

    def test_str(self):
        seqvarquerysettingsfrequency = SeqvarQuerySettingsFrequencyFactory()
        self.assertEqual(
            f"SeqvarQuerySettingsFrequency '{seqvarquerysettingsfrequency.sodar_uuid}'",
            seqvarquerysettingsfrequency.__str__(),
        )


class TestSeqvarQuery(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarQuery.objects.count(), 0)
        SeqvarQueryFactory()
        self.assertEqual(SeqvarQuery.objects.count(), 1)

    def test_property_case(self):
        seqvarquery = SeqvarQueryFactory()
        self.assertEqual(
            seqvarquery.session.caseanalysis.case.pk,
            seqvarquery.case.pk,
        )

    def test_str(self):
        seqvarquery = SeqvarQueryFactory()
        self.assertEqual(
            f"SeqvarQuery '{seqvarquery.sodar_uuid}'",
            seqvarquery.__str__(),
        )


class TestSeqvarQueryExecution(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarQueryExecution.objects.count(), 0)
        SeqvarQueryExecutionFactory()
        self.assertEqual(SeqvarQueryExecution.objects.count(), 1)

    def test_property_case(self):
        seqvarqueryexecution = SeqvarQueryExecutionFactory()
        self.assertEqual(
            seqvarqueryexecution.query.session.caseanalysis.case.pk,
            seqvarqueryexecution.case.pk,
        )

    def test_str(self):
        seqvarqueryexecution = SeqvarQueryExecutionFactory()
        self.assertEqual(
            f"SeqvarQueryExecution '{seqvarqueryexecution.sodar_uuid}'",
            seqvarqueryexecution.__str__(),
        )


class TestSeqvarResultSet(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarResultSet.objects.count(), 0)
        SeqvarResultSetFactory()
        self.assertEqual(SeqvarResultSet.objects.count(), 1)

    def test_property_case(self):
        seqvarresultset = SeqvarResultSetFactory()
        self.assertEqual(
            seqvarresultset.queryexecution.query.session.caseanalysis.case.pk,
            seqvarresultset.case.pk,
        )

    def test_get_absolute_url(self):
        seqvarresultset = SeqvarResultSetFactory()
        self.assertEqual(
            (
                f"/seqvars/api/seqvarresultset/{seqvarresultset.case.sodar_uuid}/"
                f"{seqvarresultset.sodar_uuid}/"
            ),
            seqvarresultset.get_absolute_url(),
        )

    def test_str(self):
        seqvarresultset = SeqvarResultSetFactory()
        self.assertEqual(
            f"SeqvarResultSet '{seqvarresultset.sodar_uuid}'",
            seqvarresultset.__str__(),
        )


class TestSeqvarResultRow(TestCase):

    def test_create(self):
        self.assertEqual(SeqvarResultRow.objects.count(), 0)
        SeqvarResultRowFactory()
        self.assertEqual(SeqvarResultRow.objects.count(), 1)

    def test_str(self):
        seqvarresultrow = SeqvarResultRowFactory()
        self.assertEqual(
            (
                f"SeqvarResultRow '{seqvarresultrow.sodar_uuid}' '{seqvarresultrow.release}-"
                f"{seqvarresultrow.chromosome}-{seqvarresultrow.start}-"
                f"{seqvarresultrow.reference}-{seqvarresultrow.alternative}'"
            ),
            seqvarresultrow.__str__(),
        )
