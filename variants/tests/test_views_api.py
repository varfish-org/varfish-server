from django.core.urlresolvers import reverse

from .factories import SmallVariantSetFactory
from .helpers import ApiViewTestBase
from ..models import Case

# TODO: add tests that include permission testing


def transmogrify_pedigree(pedigree):
    return [
        {{"patient": "name"}.get(key, key): value for key, value in m.items()} for m in pedigree
    ]


class TestCaseApiViewsBase(ApiViewTestBase):
    """Tests for Case API views."""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def _expected_case_data(self, case=None):
        case = case or self.case
        return {
            "sodar_uuid": str(case.sodar_uuid),
            "name": case.name,
            "index": case.index,
            "pedigree": transmogrify_pedigree(case.pedigree),
            "num_small_vars": case.num_small_vars,
            "num_svs": case.num_svs,
            "project": case.project.sodar_uuid,
            "notes": case.notes,
            "status": case.status,
            "tags": case.tags,
        }

    def test_list(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:api-case-list-create",
                    kwargs={"project": self.case.project.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)
            expected = [self._expected_case_data()]
            response_content = []
            for entry in response.data:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(response_content, expected)

    def test_create(self):
        case_data = {
            "name": "example",
            "index": "example",
            "pedigree": [
                {
                    "sex": 1,
                    "father": "0",
                    "mother": "0",
                    "name": "example",
                    "affected": 2,
                    "has_gt_entries": True,
                }
            ],
            "notes": "Some notes",
            "status": "initial",
            "tags": [],
        }

        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:api-case-list-create",
                    kwargs={"project": self.case.project.sodar_uuid},
                ),
                data=case_data,
                format="json",
            )

            expected = {
                **case_data,
                "project": self.case.project.sodar_uuid,
                "num_small_vars": None,
                "num_svs": None,
            }
            self.maxDiff = None
            self.assertEqual(response.status_code, 201)
            case_uuid = response.data.pop("sodar_uuid")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEquals(response.data, expected)
            self.assertIsNotNone(Case.objects.get(project=self.case.project, sodar_uuid=case_uuid))

    def test_retrieve(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:api-case-retrieve-update-destroy",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )

            expected = self._expected_case_data()
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, expected)

    def test_update(self):
        case_data = {
            "name": "UPDATED name",
            "notes": "UPDATED notes",
        }
        with self.login(self.user):
            response = self.client.patch(
                reverse(
                    "variants:api-case-retrieve-update-destroy",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                data=case_data,
                format="json",
            )

            self.assertEqual(response.status_code, 200)
            expected = {
                **self._expected_case_data(),
                **case_data,
            }
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.data, expected)

            case = Case.objects.get(project=self.case.project, sodar_uuid=self.case.sodar_uuid)
            self.assertEqual(case.name, case_data["name"])
            self.assertEqual(case.notes, case_data["notes"])

    def test_destroy(self):
        with self.login(self.user):
            response = self.client.delete(
                reverse(
                    "variants:api-case-retrieve-update-destroy",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )

            expected = None
            self.assertEqual(response.status_code, 204)
            self.assertEqual(response.data, expected)

            with self.assertRaises(Case.DoesNotExist):
                Case.objects.get(project=self.case.project, sodar_uuid=self.case.sodar_uuid)
