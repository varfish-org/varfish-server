from unittest.mock import patch

from django.urls import reverse
from freezegun import freeze_time
from snapshottest.unittest import TestCase as TestCaseSnapshot

from cases_qc.tests import helpers
from cases_qc.tests.factories import CaseQcFactory, DragenWgsOverallMeanCovFactory
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class CaseQcRetrieveApiViewTest(ApiViewTestBase, TestCaseSnapshot):
    """Test retrieval of ``CaseQc`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    @patch("faker.providers.misc.Provider.uuid4", new_callable=helpers.determined_uuids)
    @patch("faker.providers.lorem.Provider.word", new_callable=helpers.determined_words)
    def test_retrieve_existing(self, _mock_uuid, _mock_word):
        """GET on existing case"""
        caseqc = CaseQcFactory(case__project=self.project)
        _entry = DragenWgsOverallMeanCovFactory(caseqc=caseqc)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_qc:api-caseqc-retrieve",
                    kwargs={"case": caseqc.case.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 200)
        self.assertMatchSnapshot(response.json())

    @patch("faker.providers.misc.Provider.uuid4", new_callable=helpers.determined_uuids)
    @patch("faker.providers.lorem.Provider.word", new_callable=helpers.determined_words)
    def test_retrieve_nonexisting(self, _mock_uuid, _mock_word):
        """GET on non-existing case"""
        case = CaseFactory(project=self.project)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_qc:api-caseqc-retrieve",
                    kwargs={"case": case.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 404)
