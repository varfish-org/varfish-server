from django.forms import model_to_dict
from django.urls import reverse

from varannos.models import VarAnnoSet, VarAnnoSetEntry
from varannos.tests.factories import VarAnnoSetEntryFactory, VarAnnoSetFactory
from variants.tests.helpers import ApiViewTestBase


class TestVarAnnoSetApiViews(ApiViewTestBase):
    """Tests for ``VarAnnoSet`` API views."""

    def setUp(self):
        super().setUp()
        self.varannoset = VarAnnoSetFactory(project=self.project)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "varannos:api-varannoset-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )

        self.assertEqual(response.status_code, 200)
        expected = [
            {
                **model_to_dict(self.varannoset, exclude=("id")),
                "project": str(self.varannoset.project.sodar_uuid),
                "sodar_uuid": str(self.varannoset.sodar_uuid),
            }
        ]
        response_content = []
        for entry in response.data:  # remove some warts
            entry = dict(entry)
            entry["sodar_uuid"] = str(entry["sodar_uuid"])
            entry["project"] = str(entry["project"])
            entry.pop("date_created")  # complex; not worth testing
            entry.pop("date_modified")  # the same
            response_content.append(entry)
        self.assertEquals(response_content, expected)

    def test_create(self):
        post_data = {
            "release": "GRCh37",
            "title": "This is a title",
            "fields": ["pathogenicity", "notes",],
        }

        self.assertEqual(VarAnnoSet.objects.count(), 1)
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannoset-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                method="POST",
                data=post_data,
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        expected = {
            **post_data,
            "description": None,
            "project": self.varannoset.project.sodar_uuid,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
        }
        self.assertDictEqual(response.data, expected)
        self.assertIsNotNone(VarAnnoSet.objects.get(sodar_uuid=response.data["sodar_uuid"]))
        self.assertEqual(VarAnnoSet.objects.count(), 2)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannoset-retrieveupdatedestroy",
                    kwargs={"varannoset": self.varannoset.sodar_uuid,},
                )
            )

        expected = {
            **model_to_dict(self.varannoset, exclude=("id")),
            "project": self.varannoset.project.sodar_uuid,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
        }
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, expected)

    def test_update(self):
        patch_data = {
            "title": "This is a new title",
        }

        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannoset-retrieveupdatedestroy",
                    kwargs={"varannoset": self.varannoset.sodar_uuid,},
                ),
                method="PATCH",
                data=patch_data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.varannoset.refresh_from_db()
        self.assertEqual(self.varannoset.title, patch_data["title"])

    def test_destroy(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannoset-retrieveupdatedestroy",
                    kwargs={"varannoset": self.varannoset.sodar_uuid,},
                ),
                method="DELETE",
            )

        expected = None
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, expected)

        with self.assertRaises(VarAnnoSet.DoesNotExist):
            VarAnnoSet.objects.get(sodar_uuid=self.varannoset.sodar_uuid)


class TestVarAnnoSetEntryApiViews(ApiViewTestBase):
    """Tests for ``VarAnnoSetEntry`` API views."""

    def setUp(self):
        super().setUp()
        self.varannosetentry = VarAnnoSetEntryFactory(varannoset__project=self.project)
        self.varannoset = self.varannosetentry.varannoset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "varannos:api-varannosetentry-listcreate",
                    kwargs={"varannoset": self.varannoset.sodar_uuid},
                )
            )

        self.assertEqual(response.status_code, 200)
        expected = [
            {
                **model_to_dict(self.varannosetentry, exclude=("id")),
                "sodar_uuid": str(self.varannosetentry.sodar_uuid),
                "varannoset": str(self.varannosetentry.varannoset.sodar_uuid),
                "date_created": response.data[0]["date_created"],
                "date_modified": response.data[0]["date_modified"],
            }
        ]
        response_content = []
        for entry in response.data:  # remove some warts
            entry = dict(entry)
            entry["sodar_uuid"] = str(entry["sodar_uuid"])
            entry["varannoset"] = str(entry["varannoset"])
            response_content.append(entry)

        self.assertDictEqual(response_content[0], expected[0])
        self.assertEquals(response_content, expected)

    def test_create(self):
        post_data = {
            "release": "GRCh37",
            "chromosome": "1",
            "reference": "C",
            "alternative": "T",
            "start": 424242,
            "end": 424242,
            "payload": {"pathogenicity": "benign", "notes": "Here are some notes",},
        }

        self.assertEqual(VarAnnoSetEntry.objects.count(), 1)
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannosetentry-listcreate",
                    kwargs={"varannoset": self.varannoset.sodar_uuid},
                ),
                method="POST",
                data=post_data,
                format="json",
            )

        self.assertEqual(response.status_code, 201)
        expected = {
            **post_data,
            "varannoset": self.varannosetentry.varannoset.sodar_uuid,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
        }
        self.assertDictEqual(response.data, expected)
        self.assertIsNotNone(VarAnnoSetEntry.objects.get(sodar_uuid=response.data["sodar_uuid"]))
        self.assertEqual(VarAnnoSetEntry.objects.count(), 2)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannosetentry-retrieveupdatedestroy",
                    kwargs={"varannosetentry": self.varannosetentry.sodar_uuid,},
                )
            )

        self.assertEqual(response.status_code, 200)
        expected = {
            **model_to_dict(self.varannosetentry, exclude=("id")),
            "varannoset": self.varannosetentry.varannoset.sodar_uuid,
            "sodar_uuid": response.data["sodar_uuid"],
            "date_created": response.data["date_created"],
            "date_modified": response.data["date_modified"],
        }
        self.assertDictEqual(response.data, expected)

    def test_update(self):
        patch_data = {"payload": {"pathogenicity": "benign", "notes": "Here are some notes",}}

        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannosetentry-retrieveupdatedestroy",
                    kwargs={"varannosetentry": self.varannosetentry.sodar_uuid,},
                ),
                method="PATCH",
                data=patch_data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.varannosetentry.refresh_from_db()
        self.assertEqual(self.varannosetentry.payload, patch_data["payload"])

    def test_destroy(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "varannos:api-varannosetentry-retrieveupdatedestroy",
                    kwargs={"varannosetentry": self.varannosetentry.sodar_uuid,},
                ),
                method="DELETE",
            )

        expected = None
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, expected)

        with self.assertRaises(VarAnnoSetEntry.DoesNotExist):
            VarAnnoSetEntry.objects.get(sodar_uuid=self.varannosetentry.sodar_uuid)
