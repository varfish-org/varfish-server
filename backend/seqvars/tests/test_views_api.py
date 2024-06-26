from typing import Any

from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized

from seqvars.models import SeqvarPresetsFrequency, SeqvarQueryPresetsSet
from seqvars.serializers import SeqvarPresetsFrequencySerializer, SeqvarQueryPresetsSetSerializer
from seqvars.tests.factories import SeqvarPresetsFrequencyFactory, SeqvarQueryPresetsSetFactory
from variants.tests.helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryPresetsSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory(project=self.project)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQueryPresetsSetSerializer(self.seqvarquerypresetsset).data
        result_json["project"] = str(result_json["project"])
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    @parameterized.expand(
        [
            [{}],
            [{"description": "description"}],
        ]
    )
    def test_create(self, data_override: dict[str, Any]):
        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={**{"rank": 1, "label": "test"}, **data_override},
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQueryPresetsSetSerializer(self.seqvarquerypresetsset).data
        result_json["project"] = str(result_json["project"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"project": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarquerypresetsset": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-detail",
                    kwargs={
                        **{
                            "project": self.project.sodar_uuid,
                            "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"rank": 2}],
            [{"description": "description"}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.seqvarquerypresetsset.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.seqvarquerypresetsset, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.seqvarquerypresetsset.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.seqvarquerypresetsset, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-seqvarquerypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarQueryPresetsSet.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarPresetsFrequencyViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarQueryPresetsSetFactory(project=self.project)
        self.presetsfrequency = SeqvarPresetsFrequencyFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-list",
                    kwargs={
                        "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarPresetsFrequencySerializer(self.presetsfrequency).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-list",
                    kwargs={
                        "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-detail",
                    kwargs={
                        "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                        "seqvarpresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarPresetsFrequencySerializer(self.presetsfrequency).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"seqvarquerypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarpresetsfrequency": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-detail",
                    kwargs={
                        **{
                            "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                            "seqvarpresetsfrequency": self.presetsfrequency.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"rank": 2}],
            [{"description": "description"}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.presetsfrequency.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsfrequency, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-detail",
                    kwargs={
                        "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                        "seqvarpresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsfrequency.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsfrequency, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-seqvarpresetsfrequency-detail",
                    kwargs={
                        "seqvarquerypresetsset": self.presetsset.sodar_uuid,
                        "seqvarpresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarPresetsFrequency.objects.count(), 0)
