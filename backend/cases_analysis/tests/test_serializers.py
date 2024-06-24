from django.forms import model_to_dict
from freezegun import freeze_time
from test_plus import TestCase

from cases_analysis.serializers import CaseAnalysisSerializer, CaseAnalysisSessionSerializer
from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory


@freeze_time("2012-01-14 12:00:01")
class TestCaseAnalysisSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.caseanalysis = CaseAnalysisFactory()

    def test_serialize_existing(self):
        serializer = CaseAnalysisSerializer(self.caseanalysis)
        expected = model_to_dict(
            self.caseanalysis,
            fields=("sodar_uuid", "case"),
        )
        # We replace the case object with its UUID.
        expected["case"] = self.caseanalysis.case.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertDictEqual(dict(serializer.data), expected)


@freeze_time("2012-01-14 12:00:01")
class TestCaseAnalysisSessionSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.caseanalysissession = CaseAnalysisSessionFactory()

    def test_serialize_existing(self):
        serializer = CaseAnalysisSessionSerializer(self.caseanalysissession)
        expected = model_to_dict(
            self.caseanalysissession,
            fields=("sodar_uuid", "caseanalysis", "user"),
        )
        # We replace the related objects with their UUID.
        expected["caseanalysis"] = str(self.caseanalysissession.caseanalysis.sodar_uuid)
        expected["case"] = self.caseanalysissession.caseanalysis.case.sodar_uuid
        expected["user"] = self.caseanalysissession.user.sodar_uuid
        # Note that "date_created", "date_modified" are ignored in model_to_dict as they
        # are not editable.
        expected["date_created"] = "2012-01-14T12:00:01Z"
        expected["date_modified"] = "2012-01-14T12:00:01Z"
        self.assertDictEqual(dict(serializer.data), expected)
