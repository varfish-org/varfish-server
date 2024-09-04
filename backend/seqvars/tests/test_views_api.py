from typing import Any

from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized
from snapshottest.unittest import TestCase as TestCaseSnapshot

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.factory_defaults import (
    create_seqvarspresetsset_short_read_exome_legacy,
    create_seqvarspresetsset_short_read_genome,
)
from seqvars.models.base import (
    SeqvarsPredefinedQuery,
    SeqvarsQuery,
    SeqvarsQueryExecution,
    SeqvarsQueryPresetsClinvar,
    SeqvarsQueryPresetsColumns,
    SeqvarsQueryPresetsConsequence,
    SeqvarsQueryPresetsFrequency,
    SeqvarsQueryPresetsLocus,
    SeqvarsQueryPresetsPhenotypePrio,
    SeqvarsQueryPresetsQuality,
    SeqvarsQueryPresetsSet,
    SeqvarsQueryPresetsSetVersion,
    SeqvarsQueryPresetsVariantPrio,
    SeqvarsQuerySettings,
    SeqvarsQuerySettingsFrequency,
)
from seqvars.serializers import (
    SeqvarsPredefinedQuerySerializer,
    SeqvarsQueryColumnsConfigSerializer,
    SeqvarsQueryDetailsSerializer,
    SeqvarsQueryExecutionDetailsSerializer,
    SeqvarsQueryExecutionSerializer,
    SeqvarsQueryPresetsClinvarSerializer,
    SeqvarsQueryPresetsColumnsSerializer,
    SeqvarsQueryPresetsConsequenceSerializer,
    SeqvarsQueryPresetsFrequencySerializer,
    SeqvarsQueryPresetsLocusSerializer,
    SeqvarsQueryPresetsPhenotypePrioSerializer,
    SeqvarsQueryPresetsQualitySerializer,
    SeqvarsQueryPresetsSetSerializer,
    SeqvarsQueryPresetsSetVersionDetailsSerializer,
    SeqvarsQueryPresetsSetVersionSerializer,
    SeqvarsQueryPresetsVariantPrioSerializer,
    SeqvarsQuerySerializer,
    SeqvarsQuerySettingsClinvarSerializer,
    SeqvarsQuerySettingsConsequenceSerializer,
    SeqvarsQuerySettingsDetailsSerializer,
    SeqvarsQuerySettingsFrequencySerializer,
    SeqvarsQuerySettingsGenotypeSerializer,
    SeqvarsQuerySettingsLocusSerializer,
    SeqvarsQuerySettingsPhenotypePrioSerializer,
    SeqvarsQuerySettingsQualitySerializer,
    SeqvarsQuerySettingsSerializer,
    SeqvarsQuerySettingsVariantPrioSerializer,
    SeqvarsResultRowSerializer,
    SeqvarsResultSetSerializer,
)
from seqvars.tests.factories import (
    SeqvarsPredefinedQueryFactory,
    SeqvarsQueryColumnsConfigFactory,
    SeqvarsQueryExecutionFactory,
    SeqvarsQueryFactory,
    SeqvarsQueryPresetsClinvarFactory,
    SeqvarsQueryPresetsColumnsFactory,
    SeqvarsQueryPresetsConsequenceFactory,
    SeqvarsQueryPresetsFrequencyFactory,
    SeqvarsQueryPresetsLocusFactory,
    SeqvarsQueryPresetsPhenotypePrioFactory,
    SeqvarsQueryPresetsQualityFactory,
    SeqvarsQueryPresetsSetFactory,
    SeqvarsQueryPresetsSetVersionFactory,
    SeqvarsQueryPresetsVariantPrioFactory,
    SeqvarsQuerySettingsClinvarFactory,
    SeqvarsQuerySettingsConsequenceFactory,
    SeqvarsQuerySettingsFactory,
    SeqvarsQuerySettingsFrequencyFactory,
    SeqvarsQuerySettingsGenotypeFactory,
    SeqvarsQuerySettingsLocusFactory,
    SeqvarsQuerySettingsPhenotypePrioFactory,
    SeqvarsQuerySettingsQualityFactory,
    SeqvarsQuerySettingsVariantPrioFactory,
    SeqvarsResultRowFactory,
    SeqvarsResultSetFactory,
)
from seqvars.tests.test_factory_defaults import canonicalize_dicts
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsSetSerializer(self.querypresetsset).data
        result_json["project"] = str(result_json["project"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
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
        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsset-list",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={**{"rank": 1, "label": "test"}, **data_override},
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 2)

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
        result_json = SeqvarsQueryPresetsSetSerializer(self.querypresetsset).data
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
        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 1)

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

        self.assertEqual(SeqvarsQueryPresetsSet.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsFactoryDefaultsViewSet(TestCaseSnapshot, ApiViewTestBase):
    def test_list(self):
        response = self.client.get(
            reverse("seqvars:api-querypresetsfactorydefaults-list"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertMatchSnapshot(canonicalize_dicts(response.json()))

    def test_retrieve(self):
        record_genome = create_seqvarspresetsset_short_read_genome()
        response = self.client.get(
            reverse(
                "seqvars:api-querypresetsfactorydefaults-detail",
                kwargs={"querypresetsset": record_genome.sodar_uuid},
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertMatchSnapshot(canonicalize_dicts(response.json()))


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsSetVersionViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetssetversion-list",
                    kwargs={"querypresetsset": self.querypresetsset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsSetVersionSerializer(self.querypresetssetversion).data
        result_json["presetsset"] = str(result_json["presetsset"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    @parameterized.expand(
        [
            [{}],
            [{"version_major": 2}],
        ]
    )
    def test_create(self, data_override: dict[str, Any]):
        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetssetversion-list",
                    kwargs={"querypresetsset": self.querypresetsset.sodar_uuid},
                ),
                data={
                    **{
                        "version_major": 1,
                        "version_minor": self.querypresetssetversion.version_minor + 1,
                        "status": SeqvarsQueryPresetsSetVersion.STATUS_ACTIVE,
                    },
                    **data_override,
                },
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetssetversion-detail",
                    kwargs={
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                        "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsSetVersionDetailsSerializer(
            self.querypresetssetversion
        ).data
        result_json["presetsset"] = dict(result_json["presetsset"])
        result_json["presetsset"]["project"] = str(result_json["presetsset"]["project"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetsset": "00000000-0000-0000-0000-000000000000"}],
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetssetversion-detail",
                    kwargs={
                        **{
                            "querypresetsset": self.querypresetsset.sodar_uuid,
                            "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"version_major": 2}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.querypresetssetversion.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.querypresetssetversion, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-querypresetssetversion-detail",
                    kwargs={
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                        "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.querypresetssetversion.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.querypresetssetversion, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetssetversion-detail",
                    kwargs={
                        "querypresetsset": self.querypresetsset.sodar_uuid,
                        "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsSetVersion.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsQualityViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsquality = SeqvarsQueryPresetsQualityFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsquality-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsQualitySerializer(self.presetsquality).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsquality-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsquality": self.presetsquality.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsQualitySerializer(self.presetsquality).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsquality-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsquality": self.presetsquality.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsQuality.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsConsequenceViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsconsequence = SeqvarsQueryPresetsConsequenceFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsconsequence-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsConsequenceSerializer(self.presetsconsequence).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsconsequence-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsConsequenceSerializer(self.presetsconsequence).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsconsequence-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsconsequence": self.presetsconsequence.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsConsequence.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsFrequencyViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsfrequency-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsFrequencySerializer(self.presetsfrequency).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsfrequency-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsFrequencySerializer(self.presetsfrequency).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsfrequency-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsfrequency": self.presetsfrequency.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsFrequency.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsLocusViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetslocus = SeqvarsQueryPresetsLocusFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetslocus-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsLocusSerializer(self.presetslocus).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetslocus-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetslocus": self.presetslocus.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsLocusSerializer(self.presetslocus).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetslocus-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetslocus": self.presetslocus.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsLocus.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsPhenotypePrioViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsphenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsPhenotypePrioSerializer(self.presetsphenotypeprio).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsPhenotypePrioSerializer(self.presetsphenotypeprio).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsphenotypeprio-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsphenotypeprio": self.presetsphenotypeprio.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsPhenotypePrio.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsVariantPrioViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsvariantprio = SeqvarsQueryPresetsVariantPrioFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsvariantprio-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsVariantPrioSerializer(self.presetsvariantprio).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsvariantprio-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsVariantPrioSerializer(self.presetsvariantprio).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsvariantprio-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsvariantprio": self.presetsvariantprio.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsVariantPrio.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsColumnsViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetscolumns = SeqvarsQueryPresetsColumnsFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetscolumns-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsColumnsSerializer(self.presetscolumns).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetscolumns-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetscolumns": self.presetscolumns.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsColumnsSerializer(self.presetscolumns).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetscolumns-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetscolumns": self.presetscolumns.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsColumns.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryPresetsClinvarViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.presetsclinvar = SeqvarsQueryPresetsClinvarFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsclinvar-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsClinvarSerializer(self.presetsclinvar).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querypresetsclinvar-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsQueryPresetsClinvarSerializer(self.presetsclinvar).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
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
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
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
        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-querypresetsclinvar-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "querypresetsclinvar": self.presetsclinvar.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsQueryPresetsClinvar.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class PredefinedQueryViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.presetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.presetsset,
            status=SeqvarsQueryPresetsSetVersion.STATUS_DRAFT,
        )
        self.predefinedquery = SeqvarsPredefinedQueryFactory(
            presetssetversion=self.presetssetversion
        )

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-predefinedquery-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsPredefinedQuerySerializer(self.predefinedquery).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-predefinedquery-list",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                    },
                ),
                data={"rank": 1, "label": "test"},
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-predefinedquery-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "predefinedquery": self.predefinedquery.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsPredefinedQuerySerializer(self.predefinedquery).data
        result_json["presetssetversion"] = str(result_json["presetssetversion"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"querypresetssetversion": "00000000-0000-0000-0000-000000000000"}],
            [{"predefinedquery": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-predefinedquery-detail",
                    kwargs={
                        **{
                            "querypresetssetversion": self.presetssetversion.sodar_uuid,
                            "predefinedquery": self.predefinedquery.sodar_uuid,
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
        self.predefinedquery.refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.predefinedquery, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-predefinedquery-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "predefinedquery": self.predefinedquery.sodar_uuid,
                    },
                ),
                data=data,
            )

        self.assertEqual(response.status_code, 200)

        self.predefinedquery.refresh_from_db()
        for key, value in data.items():
            self.assertEqual(getattr(self.predefinedquery, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-predefinedquery-detail",
                    kwargs={
                        "querypresetssetversion": self.presetssetversion.sodar_uuid,
                        "predefinedquery": self.predefinedquery.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarsPredefinedQuery.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQuerySettingsViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.querysettings = SeqvarsQuerySettingsFactory(session=self.session)

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
        result_json = SeqvarsQuerySettingsSerializer(self.querysettings).data
        result_json["session"] = str(result_json["session"])
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-querysettings-list",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                ),
                data={
                    "genotype": SeqvarsQuerySettingsGenotypeSerializer(
                        SeqvarsQuerySettingsGenotypeFactory.build(querysettings=None)
                    ).data,
                    "quality": SeqvarsQuerySettingsQualitySerializer(
                        SeqvarsQuerySettingsQualityFactory.build(querysettings=None)
                    ).data,
                    "consequence": SeqvarsQuerySettingsConsequenceSerializer(
                        SeqvarsQuerySettingsConsequenceFactory.build(querysettings=None)
                    ).data,
                    "locus": SeqvarsQuerySettingsLocusSerializer(
                        SeqvarsQuerySettingsLocusFactory.build(querysettings=None)
                    ).data,
                    "frequency": SeqvarsQuerySettingsFrequencySerializer(
                        SeqvarsQuerySettingsFrequencyFactory.build(querysettings=None)
                    ).data,
                    "phenotypeprio": SeqvarsQuerySettingsPhenotypePrioSerializer(
                        SeqvarsQuerySettingsPhenotypePrioFactory.build(querysettings=None)
                    ).data,
                    "variantprio": SeqvarsQuerySettingsVariantPrioSerializer(
                        SeqvarsQuerySettingsVariantPrioFactory.build(querysettings=None)
                    ).data,
                    "clinvar": SeqvarsQuerySettingsClinvarSerializer(
                        SeqvarsQuerySettingsClinvarFactory.build(querysettings=None)
                    ).data,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 2)

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
        result_json = SeqvarsQuerySettingsDetailsSerializer(self.querysettings).data
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
            [{"frequency": {"gnomad_genomes": {"enabled": True}}}],
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
                    value_actual = getattr(getattr(self.querysettings, key), subkey)
                    if hasattr(value_actual, "model_dump"):
                        value_actual = value_actual.model_dump(mode="json", exclude_none=True)
                    self.assertEqual(
                        value_actual,
                        subvalue,
                        f"key={key}, subkey={subkey}",
                    )
            else:
                self.assertEqual(getattr(self.querysettings, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)

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

        self.assertEqual(SeqvarsQuerySettings.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestQueryViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = SeqvarsQueryFactory(session=self.session)

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
        result_json = SeqvarsQuerySerializer(self.query).data
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarsQuery.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            settings = SeqvarsQuerySettingsSerializer(
                SeqvarsQuerySettingsFactory.build(),
            ).data
            settings["frequency"] = SeqvarsQuerySettingsFrequencySerializer(
                SeqvarsQuerySettingsFrequencyFactory.build(querysettings=None)
            ).data
            settings["genotype"] = SeqvarsQuerySettingsGenotypeSerializer(
                SeqvarsQuerySettingsGenotypeFactory.build(querysettings=None)
            ).data
            settings["quality"] = SeqvarsQuerySettingsQualitySerializer(
                SeqvarsQuerySettingsQualityFactory.build(querysettings=None)
            ).data
            settings["consequence"] = SeqvarsQuerySettingsConsequenceSerializer(
                SeqvarsQuerySettingsConsequenceFactory.build(querysettings=None)
            ).data
            settings["locus"] = SeqvarsQuerySettingsLocusSerializer(
                SeqvarsQuerySettingsLocusFactory.build(querysettings=None)
            ).data
            settings["frequency"] = SeqvarsQuerySettingsFrequencySerializer(
                SeqvarsQuerySettingsFrequencyFactory.build(querysettings=None)
            ).data
            settings["phenotypeprio"] = SeqvarsQuerySettingsPhenotypePrioSerializer(
                SeqvarsQuerySettingsPhenotypePrioFactory.build(querysettings=None)
            ).data
            settings["variantprio"] = SeqvarsQuerySettingsVariantPrioSerializer(
                SeqvarsQuerySettingsVariantPrioFactory.build(querysettings=None)
            ).data
            settings["clinvar"] = SeqvarsQuerySettingsClinvarSerializer(
                SeqvarsQuerySettingsClinvarFactory.build(querysettings=None)
            ).data

            columnsconfig = SeqvarsQueryColumnsConfigSerializer(
                SeqvarsQueryColumnsConfigFactory.build(seqvarsquery=None)
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
                    "settings": settings,
                    "columnsconfig": columnsconfig,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarsQuery.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 2)

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
        result_json = SeqvarsQueryDetailsSerializer(self.query).data
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
            [{"settings": {"frequency": {"gnomad_genomes": {"enabled": True}}}}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):  # noqa: C901
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
            if key not in data["settings"]:
                if key == "frequency":
                    data["settings"][key] = {
                        "gnomad_genomes": {},
                        "gnomad_exomes": {},
                        "gnomad_mitochondrial": {},
                        "helixmtdb": {},
                    }
                else:
                    data["settings"][key] = {}

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
                            if isinstance(value3, dict):
                                for key4, value4 in value3.items():
                                    self.assertNotEqual(
                                        getattr(
                                            getattr(getattr(getattr(self.query, key), key2), key3),
                                            key4,
                                        ),
                                        value4,
                                        f"key={key}, key2={key2}, key3={key3}, key4={key4}",
                                    )
                            else:
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
                            value_actual = getattr(getattr(getattr(self.query, key), key2), key3)
                            if hasattr(value_actual, "model_dump"):
                                value_actual = value_actual.model_dump(
                                    mode="json", exclude_none=True
                                )
                            self.assertEqual(
                                value_actual,
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
        self.assertEqual(SeqvarsQuery.objects.count(), 1)

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

        self.assertEqual(SeqvarsQuery.objects.count(), 0)

    def test_create_from(self):
        self.assertEqual(SeqvarsQuery.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            # TODO: change after https://github.com/varfish-org/varfish-server/issues/1920
            presetsset_factory = create_seqvarspresetsset_short_read_exome_legacy()
            presetsset = presetsset_factory.clone_with_latest_version(project=self.project)
            version = presetsset.versions.all()[0]
            predefinedquery = version.seqvarspredefinedquery_set.all()[0]

            response = self.client.post(
                reverse(
                    "seqvars:api-query-create-from",
                    kwargs={
                        "session": self.session.sodar_uuid,
                    },
                ),
                format="json",
                data={
                    "predefinedquery": predefinedquery.sodar_uuid,
                    "label": "test label",
                },
            )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(SeqvarsQuery.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarsQuerySettingsFrequency.objects.count(), 2)


@freeze_time("2012-01-14 12:00:01")
class TestQueryExecutionViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)

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
        result_json = SeqvarsQueryExecutionSerializer(self.queryexecution).data
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
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
        result_json = SeqvarsQueryExecutionDetailsSerializer(self.queryexecution).data
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

    def test_start(self):
        self.assertEqual(SeqvarsQueryExecution.objects.count(), 1)
        self.assertEqual(SeqvarsQuery.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-queryexecution-start",
                    kwargs={
                        "query": self.query.sodar_uuid,
                    },
                ),
            )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(SeqvarsQuery.objects.count(), 1)
        self.assertEqual(SeqvarsQueryExecution.objects.count(), 2)
        self.assertEqual(
            self.query.seqvarsqueryexecution_set.count(),
            2,
        )
        new_seqvarqueryexecution = SeqvarsQueryExecution.objects.exclude(
            pk=self.queryexecution.pk
        ).first()
        self.assertEqual(
            new_seqvarqueryexecution.state,
            SeqvarsQueryExecution.STATE_QUEUED,
        )


@freeze_time("2012-01-14 12:00:01")
class TestResultSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)
        self.resultset = SeqvarsResultSetFactory(queryexecution=self.queryexecution)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-resultset-list",
                    kwargs={
                        "queryexecution": self.queryexecution.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsResultSetSerializer(self.resultset).data
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
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
                        "queryexecution": self.queryexecution.sodar_uuid,
                        "resultset": self.resultset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarsResultSetSerializer(self.resultset).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"queryexecution": "00000000-0000-0000-0000-000000000000"}],
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
                            "queryexecution": self.queryexecution.sodar_uuid,
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
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)
        self.resultset = SeqvarsResultSetFactory(queryexecution=self.queryexecution)
        self.seqvarresultrow = SeqvarsResultRowFactory(resultset=self.resultset)

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
        result_json = SeqvarsResultRowSerializer(self.seqvarresultrow).data
        self.assertDictEqual(
            response.json(),
            {
                "count": 1,
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
        result_json = SeqvarsResultRowSerializer(self.seqvarresultrow).data
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
