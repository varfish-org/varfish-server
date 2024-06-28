from typing import Any

from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.models import (
    Query,
    QueryPresetsClinvar,
    QueryPresetsColumns,
    QueryPresetsConsequence,
    QueryPresetsFrequency,
    QueryPresetsLocus,
    QueryPresetsPhenotypePrio,
    QueryPresetsQuality,
    QueryPresetsSet,
    QueryPresetsVariantPrio,
    QuerySettings,
    QuerySettingsFrequency,
)
from seqvars.serializers import (
    QueryColumnsConfigSerializer,
    QueryDetailsSerializer,
    QueryExecutionDetailsSerializer,
    QueryExecutionSerializer,
    QueryPresetsClinvarSerializer,
    QueryPresetsColumnsSerializer,
    QueryPresetsConsequenceSerializer,
    QueryPresetsFrequencySerializer,
    QueryPresetsLocusSerializer,
    QueryPresetsPhenotypePrioSerializer,
    QueryPresetsQualitySerializer,
    QueryPresetsSetDetailsSerializer,
    QueryPresetsSetSerializer,
    QueryPresetsVariantPrioSerializer,
    QuerySerializer,
    QuerySettingsClinvarSerializer,
    QuerySettingsConsequenceSerializer,
    QuerySettingsDetailsSerializer,
    QuerySettingsFrequencySerializer,
    QuerySettingsGenotypeSerializer,
    QuerySettingsLocusSerializer,
    QuerySettingsPhenotypePrioSerializer,
    QuerySettingsQualitySerializer,
    QuerySettingsSerializer,
    QuerySettingsVariantPrioSerializer,
    ResultRowSerializer,
    ResultSetSerializer,
)
from seqvars.tests.factories import (
    QueryColumnsConfigFactory,
    QueryExecutionFactory,
    QueryFactory,
    QueryPresetsClinvarFactory,
    QueryPresetsColumnsFactory,
    QueryPresetsConsequenceFactory,
    QueryPresetsFrequencyFactory,
    QueryPresetsLocusFactory,
    QueryPresetsPhenotypePrioFactory,
    QueryPresetsQualityFactory,
    QueryPresetsSetFactory,
    QueryPresetsVariantPrioFactory,
    QuerySettingsClinvarFactory,
    QuerySettingsConsequenceFactory,
    QuerySettingsFactory,
    QuerySettingsFrequencyFactory,
    QuerySettingsGenotypeFactory,
    QuerySettingsLocusFactory,
    QuerySettingsPhenotypePrioFactory,
    QuerySettingsQualityFactory,
    QuerySettingsVariantPrioFactory,
    ResultRowFactory,
    ResultSetFactory,
)
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory(project=self.project)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsSetSerializer(self.querypresetsset).data
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
        self.assertEqual(QueryPresetsSet.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={**{"rank": 1, "label": "test"}, **data_override},
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(QueryPresetsSet.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsSetDetailsSerializer(self.querypresetsset).data
        result_json["project"] = str(result_json["project"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"project": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsset-detail",
                    kwargs={
                        **{
                            "project": self.project.sodar_uuid,
                            "querypresetsset": self.querypresetsset.sodar_uuid,
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
        self.querypresetsset.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.querypresetsset, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.querypresetsset.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.querypresetsset, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsSet.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsset-detail",
                    kwargs={
                        "project": self.project.sodar_uuid,
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsSet.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsQualityViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsquality = QueryPresetsQualityFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsquality-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsQualitySerializer(self.presetsquality).data
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
        self.assertEqual(QueryPresetsQuality.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsquality-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsQuality.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsquality": self.presetsquality.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsQualitySerializer(self.presetsquality).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsquality": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsquality": self.presetsquality.sodar_uuid,
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
        self.presetsquality.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsquality, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsquality": self.presetsquality.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsquality.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsquality, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsQuality.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsquality": self.presetsquality.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsQuality.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsConsequenceViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsconsequence = QueryPresetsConsequenceFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsconsequence-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsConsequenceSerializer(self.presetsconsequence).data
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
        self.assertEqual(QueryPresetsConsequence.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsconsequence-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsConsequence.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsConsequenceSerializer(self.presetsconsequence).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsconsequence": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
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
        self.presetsconsequence.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsconsequence, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsconsequence.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsconsequence, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsConsequence.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsConsequence.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsFrequencyViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsfrequency = QueryPresetsFrequencyFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsfrequency-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsFrequencySerializer(self.presetsfrequency).data
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
        self.assertEqual(QueryPresetsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsfrequency-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsFrequencySerializer(self.presetsfrequency).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsfrequency": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
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
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsfrequency.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsfrequency, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsFrequency.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsFrequency.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsLocusViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetslocus = QueryPresetsLocusFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetslocus-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsLocusSerializer(self.presetslocus).data
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
        self.assertEqual(QueryPresetsLocus.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetslocus-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsLocus.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetslocus": self.presetslocus.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsLocusSerializer(self.presetslocus).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetslocus": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetslocus": self.presetslocus.sodar_uuid,
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
        self.presetslocus.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetslocus, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetslocus": self.presetslocus.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetslocus.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetslocus, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsLocus.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetslocus": self.presetslocus.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsLocus.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsPhenotypePrioViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsphenotypeprio = QueryPresetsPhenotypePrioFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsPhenotypePrioSerializer(self.presetsphenotypeprio).data
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
        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsPhenotypePrioSerializer(self.presetsphenotypeprio).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsphenotypeprio": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
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
        self.presetsphenotypeprio.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsphenotypeprio, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsphenotypeprio.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsphenotypeprio, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsPhenotypePrio.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsVariantPrioViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsvariantprio = QueryPresetsVariantPrioFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsvariantprio-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsVariantPrioSerializer(self.presetsvariantprio).data
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
        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsvariantprio-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsVariantPrioSerializer(self.presetsvariantprio).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsvariantprio": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
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
        self.presetsvariantprio.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsvariantprio, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsvariantprio.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsvariantprio, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsVariantPrio.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsColumnsViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetscolumns = QueryPresetsColumnsFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetscolumns-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsColumnsSerializer(self.presetscolumns).data
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
        self.assertEqual(QueryPresetsColumns.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetscolumns-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsColumns.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetscolumns": self.presetscolumns.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsColumnsSerializer(self.presetscolumns).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetscolumns": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetscolumns": self.presetscolumns.sodar_uuid,
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
        self.presetscolumns.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetscolumns, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetscolumns": self.presetscolumns.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetscolumns.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetscolumns, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsColumns.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetscolumns": self.presetscolumns.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsColumns.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsClinvarViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = QueryPresetsSetFactory(project=self.project)
        self.presetsclinvar = QueryPresetsClinvarFactory(presetsset=self.presetsset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsclinvar-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsClinvarSerializer(self.presetsclinvar).data
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
        self.assertEqual(QueryPresetsClinvar.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsclinvar-list",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QueryPresetsClinvar.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryPresetsClinvarSerializer(self.presetsclinvar).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetsclinvar": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.presetsset.sodar_uuid,
                            "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
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
        self.presetsclinvar.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.presetsclinvar, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.presetsclinvar.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.presetsclinvar, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QueryPresetsClinvar.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        "querypresetsset": self.presetsset.sodar_uuid,
                        "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QueryPresetsClinvar.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.querysettings = QuerySettingsFactory(session=self.session)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querysettings-list",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QuerySettingsSerializer(self.querysettings).data
        result_json["session"] = str(result_json["session"])
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(QuerySettings.objects.count(), 1)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querysettings-list",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                ),
                data={
                    "genotype": QuerySettingsGenotypeSerializer(
                        QuerySettingsGenotypeFactory.build(querysettings=None)
                    ).data,
                    "quality": QuerySettingsQualitySerializer(
                        QuerySettingsQualityFactory.build(querysettings=None)
                    ).data,
                    "consequence": QuerySettingsConsequenceSerializer(
                        QuerySettingsConsequenceFactory.build(querysettings=None)
                    ).data,
                    "locus": QuerySettingsLocusSerializer(
                        QuerySettingsLocusFactory.build(querysettings=None)
                    ).data,
                    "frequency": QuerySettingsFrequencySerializer(
                        QuerySettingsFrequencyFactory.build(querysettings=None)
                    ).data,
                    "phenotypeprio": QuerySettingsPhenotypePrioSerializer(
                        QuerySettingsPhenotypePrioFactory.build(querysettings=None)
                    ).data,
                    "variantprio": QuerySettingsVariantPrioSerializer(
                        QuerySettingsVariantPrioFactory.build(querysettings=None)
                    ).data,
                    "clinvar": QuerySettingsClinvarSerializer(
                        QuerySettingsClinvarFactory.build(querysettings=None)
                    ).data,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(QuerySettings.objects.count(), 2)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querysettings-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "querysettings": self.querysettings.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QuerySettingsDetailsSerializer(self.querysettings).data
        result_json["session"] = str(result_json["session"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"session": "00000000-0000-0000-0000-000000000000"}],
            [{"querysettings": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querysettings-detail",
                    kwargs={
                        **{
                            "session": self.session.sodar_uuid,
                            "querysettings": self.querysettings.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"frequency": {"gnomad_genomes_enabled": True}}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.querysettings.refresh_from_db()
        for key in data.keys():
            getattr(self.querysettings, key).refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.querysettings, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querysettings-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "querysettings": self.querysettings.sodar_uuid,
                    },
                ),
                data=data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.querysettings.refresh_from_db()
        for key in data.keys():
            getattr(self.querysettings, key).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    self.assertEqual(
                        getattr(getattr(self.querysettings, key), subkey),
                        subvalue,
                        f"key={key}, subkey={subkey}",
                    )
            else:
                self.assertEqual(getattr(self.querysettings, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(QuerySettings.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querysettings-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "querysettings": self.querysettings.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(QuerySettings.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = QueryFactory(session=self.session)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-query-list",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QuerySerializer(self.query).data
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(Query.objects.count(), 1)
        self.assertEqual(QuerySettings.objects.count(), 1)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            settings_buffer = QuerySettingsSerializer(
                QuerySettingsFactory.build(),
            ).data
            settings_buffer["frequency"] = QuerySettingsFrequencySerializer(
                QuerySettingsFrequencyFactory.build(querysettings=None)
            ).data
            settings_buffer["genotype"] = QuerySettingsGenotypeSerializer(
                QuerySettingsGenotypeFactory.build(querysettings=None)
            ).data
            settings_buffer["quality"] = QuerySettingsQualitySerializer(
                QuerySettingsQualityFactory.build(querysettings=None)
            ).data
            settings_buffer["consequence"] = QuerySettingsConsequenceSerializer(
                QuerySettingsConsequenceFactory.build(querysettings=None)
            ).data
            settings_buffer["locus"] = QuerySettingsLocusSerializer(
                QuerySettingsLocusFactory.build(querysettings=None)
            ).data
            settings_buffer["frequency"] = QuerySettingsFrequencySerializer(
                QuerySettingsFrequencyFactory.build(querysettings=None)
            ).data
            settings_buffer["phenotypeprio"] = QuerySettingsPhenotypePrioSerializer(
                QuerySettingsPhenotypePrioFactory.build(querysettings=None)
            ).data
            settings_buffer["variantprio"] = QuerySettingsVariantPrioSerializer(
                QuerySettingsVariantPrioFactory.build(querysettings=None)
            ).data
            settings_buffer["clinvar"] = QuerySettingsClinvarSerializer(
                QuerySettingsClinvarFactory.build(querysettings=None)
            ).data

            columnsconfig = QueryColumnsConfigSerializer(
                QueryColumnsConfigFactory.build(query=None)
            ).data

            response = self.client.post(
                reverse(
                    "seqvars:api-query-list",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                ),
                data={
                    "label": "test label",
                    "settings_buffer": settings_buffer,
                    "columnsconfig": columnsconfig,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(Query.objects.count(), 2)
        self.assertEqual(QuerySettings.objects.count(), 2)
        self.assertEqual(QuerySettingsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-query-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "query": self.query.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryDetailsSerializer(self.query).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"session": "00000000-0000-0000-0000-000000000000"}],
            [{"query": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-query-detail",
                    kwargs={
                        **{
                            "session": self.session.sodar_uuid,
                            "query": self.query.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"settings_buffer": {"frequency": {"gnomad_genomes_enabled": True}}}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        keys = [
            "genotype",
            "quality",
            "consequence",
            "locus",
            "frequency",
            "phenotypeprio",
            "variantprio",
            "clinvar",
        ]
        for key in keys:
            if not key in data["settings_buffer"]:
                data["settings_buffer"][key] = {}

        self.query.refresh_from_db()
        for key, value in data.items():
            getattr(self.query, key).refresh_from_db()
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    getattr(getattr(self.query, key), key2).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    if isinstance(value2, dict):
                        for key3, value3 in value2.items():
                            self.assertNotEqual(
                                getattr(getattr(getattr(self.query, key), key2), key3),
                                value3,
                                f"key={key}, key2={key2}, key3={key3}",
                            )
                    else:
                        self.assertNotEqual(
                            getattr(getattr(self.query, key), key2),
                            value2,
                            f"key={key}, key2={key2}",
                        )
            else:
                self.assertNotEqual(getattr(self.query, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-query-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "query": self.query.sodar_uuid,
                    },
                ),
                data=data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.query.refresh_from_db()
        for key in data.keys():
            getattr(self.query, key).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    if isinstance(value2, dict):
                        for key3, value3 in value2.items():
                            self.assertEqual(
                                getattr(getattr(getattr(self.query, key), key2), key3),
                                value3,
                                f"key={key}, key2={key2}, key3={key3}",
                            )
                    else:
                        self.assertEqual(
                            getattr(getattr(self.query, key), key2),
                            value2,
                            f"key={key}, key2={key2}",
                        )
            else:
                self.assertEqual(getattr(self.query, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(Query.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-query-detail",
                    kwargs={
                        "session": self.session.sodar_uuid,
                        "query": self.query.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(Query.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryExecutionViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-queryexecution-list",
                    kwargs={
                        "query": self.query.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryExecutionSerializer(self.queryexecution).data
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-queryexecution-detail",
                    kwargs={
                        "query": self.query.sodar_uuid,
                        "queryexecution": self.queryexecution.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = QueryExecutionDetailsSerializer(self.queryexecution).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"query": "00000000-0000-0000-0000-000000000000"}],
            [{"queryexecution": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-queryexecution-detail",
                    kwargs={
                        **{
                            "query": self.query.sodar_uuid,
                            "queryexecution": self.queryexecution.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)


@freeze_time("2012-01-14 12:00:01")
class TestResultSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)
        self.resultset = ResultSetFactory(queryexecution=self.queryexecution)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultset-list",
                    kwargs={
                        "query": self.query.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = ResultSetSerializer(self.resultset).data
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultset-detail",
                    kwargs={
                        "query": self.query.sodar_uuid,
                        "resultset": self.resultset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = ResultSetSerializer(self.resultset).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"query": "00000000-0000-0000-0000-000000000000"}],
            [{"resultset": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultset-detail",
                    kwargs={
                        **{
                            "query": self.query.sodar_uuid,
                            "resultset": self.resultset.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)


@freeze_time("2012-01-14 12:00:01")
class TestResultRowViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)
        self.resultset = ResultSetFactory(queryexecution=self.queryexecution)
        self.seqvarresultrow = ResultRowFactory(resultset=self.resultset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultrow-list",
                    kwargs={
                        "resultset": self.resultset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = ResultRowSerializer(self.seqvarresultrow).data
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultrow-detail",
                    kwargs={
                        "resultset": self.resultset.sodar_uuid,
                        "seqvarresultrow": self.seqvarresultrow.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = ResultRowSerializer(self.seqvarresultrow).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"resultset": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarresultrow": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultrow-detail",
                    kwargs={
                        **{
                            "resultset": self.resultset.sodar_uuid,
                            "seqvarresultrow": self.seqvarresultrow.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)
