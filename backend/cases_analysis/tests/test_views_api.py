from django.urls import reverse

from cases_analysis.models import CaseAnalysis, CaseAnalysisSession
from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


class TestCaseAnalysisViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()

    def test_list(self):
        self.assertEqual(CaseAnalysis.objects.count(), 0)
        self.assertEqual(CaseAnalysisSession.objects.count(), 0)

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_analysis:api-caseanalysis-list",
                    kwargs={"case": self.case.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(CaseAnalysis.objects.count(), 1)
        self.assertEqual(CaseAnalysisSession.objects.count(), 0)

    def test_retrieve_existing(self):
        caseanalysis = CaseAnalysisFactory(case=self.case)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_analysis:api-caseanalysis-detail",
                    kwargs={"case": self.case.sodar_uuid, "caseanalysis": caseanalysis.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)


class TestCaseAnalysisSessionViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory()

    def test_list(self):
        self.assertEqual(CaseAnalysis.objects.count(), 0)
        self.assertEqual(CaseAnalysisSession.objects.count(), 0)

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_analysis:api-caseanalysissession-list",
                    kwargs={"case": self.case.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(CaseAnalysis.objects.count(), 1)
        self.assertEqual(CaseAnalysisSession.objects.count(), 1)

    def test_retrieve(self):
        caseanalysis = CaseAnalysisFactory(case=self.case)
        caseanalysissession = CaseAnalysisSessionFactory(
            caseanalysis=caseanalysis, user=self.superuser
        )
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_analysis:api-caseanalysissession-detail",
                    kwargs={
                        "case": self.case.sodar_uuid,
                        "caseanalysissession": caseanalysissession.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
