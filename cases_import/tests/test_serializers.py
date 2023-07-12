from freezegun import freeze_time
import jsonmatch
from test_plus import TestCase

from cases_import.serializers import CaseImportActionSerializer
from cases_import.tests.factories import CaseImportActionFactory


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionSerializerTest(TestCase):
    def setUp(self):
        super().setUp()
        self.caseimportaction = CaseImportActionFactory()
        self.project = self.caseimportaction.project

    def test_serializer_run(self):
        serializer = CaseImportActionSerializer(
            self.caseimportaction, context={"project": self.project}
        )
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.caseimportaction.sodar_uuid),
                "project": self.caseimportaction.project.sodar_uuid,
                "date_created": "2012-01-14T12:00:01Z",
                "date_modified": "2012-01-14T12:00:01Z",
                "action": "create",
                "state": "draft",
                "payload": {
                    "id": "PPKT:1",
                    "subject": {
                        "id": "Zaphod",
                        "dateOfBirth": "1966-02-02T02:26:42Z",
                        "sex": "MALE",
                    },
                    "phenotypicFeatures": [
                        {"type": {"id": "HG2G:00001", "label": "Hoopy"}},
                        {"type": {"id": "HG2G:00002", "label": "Frood"}},
                    ],
                },
            }
        )
        expected.assert_matches(serializer.data)
