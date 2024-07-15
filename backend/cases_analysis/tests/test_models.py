"""Test models and factories"""

from freezegun import freeze_time
from test_plus.test import TestCase

from cases_analysis.models import CaseAnalysis, CaseAnalysisSession
from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory


@freeze_time("2012-01-14 12:00:01")
class TestCaseAnalysis(TestCase):
    def test_create(self):
        self.assertEqual(CaseAnalysis.objects.count(), 0)
        CaseAnalysisFactory()
        self.assertEqual(CaseAnalysis.objects.count(), 1)

    def test_get_absolute_url(self):
        caseanalysis = CaseAnalysisFactory()
        self.assertEqual(
            (
                f"/cases-analysis/api/caseanalysis/{caseanalysis.case.sodar_uuid}/"
                f"{caseanalysis.sodar_uuid}/"
            ),
            caseanalysis.get_absolute_url(),
        )

    def test_str(self):
        caseanalysis = CaseAnalysisFactory()
        self.assertEqual(
            f"CaseAnalysis '{caseanalysis.sodar_uuid}'",
            caseanalysis.__str__(),
        )


@freeze_time("2012-01-14 12:00:01")
class TestCaseAnalysisSession(TestCase):
    def test_create(self):
        self.assertEqual(CaseAnalysisSession.objects.count(), 0)
        CaseAnalysisSessionFactory()
        self.assertEqual(CaseAnalysisSession.objects.count(), 1)

    def test_get_absolute_url(self):
        caseanalysissession = CaseAnalysisSessionFactory()
        caseanalysis = caseanalysissession.caseanalysis
        self.assertEqual(
            (
                f"/cases-analysis/api/caseanalysissession/{caseanalysis.case.sodar_uuid}/"
                f"{caseanalysissession.sodar_uuid}/"
            ),
            caseanalysissession.get_absolute_url(),
        )

    def test_property_case(self):
        caseanalysissession = CaseAnalysisSessionFactory()
        self.assertEqual(caseanalysissession.case, caseanalysissession.caseanalysis.case)

    def test_str(self):
        caseanalysissession = CaseAnalysisSessionFactory()
        self.assertEqual(
            f"CaseAnalysisSession '{caseanalysissession.sodar_uuid}'",
            caseanalysissession.__str__(),
        )
