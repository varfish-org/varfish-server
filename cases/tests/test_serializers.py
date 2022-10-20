from django.forms import model_to_dict
from test_plus import TestCase

from cases.serializers import CaseCommentSerializer, CaseGeneAnnotationSerializer
from variants.tests.factories import CaseCommentsFactory, CaseGeneAnnotationEntryFactory

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestCaseCommentSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.case_comment = CaseCommentsFactory()

    def testSerializeExisting(self):
        serializer = CaseCommentSerializer(self.case_comment)
        expected = model_to_dict(self.case_comment)
        expected.pop("id")
        expected["case"] = self.case_comment.case.sodar_uuid
        expected["date_created"] = self.case_comment.date_created.strftime(TIMEF)
        expected["date_modified"] = self.case_comment.date_modified.strftime(TIMEF)
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        self.assertDictEqual(serializer.data, expected)


class TestCaseGeneAnnotationSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.entry = CaseGeneAnnotationEntryFactory()

    def testSerializeExisting(self):
        serializer = CaseGeneAnnotationSerializer(self.entry)
        expected = model_to_dict(self.entry)
        expected.pop("id")
        expected["case"] = self.entry.case.sodar_uuid
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        self.assertDictEqual(serializer.data, expected)
