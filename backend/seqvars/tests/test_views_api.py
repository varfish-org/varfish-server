from typing import Any

from django.urls import reverse
from freezegun import freeze_time
from parameterized import parameterized

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.models import (
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
    SeqvarQuerySettingsFrequency,
)
from seqvars.serializers import (
    SeqvarPresetsFrequencySerializer,
    SeqvarQueryDetailsSerializer,
    SeqvarQueryExecutionDetailsSerializer,
    SeqvarQueryExecutionSerializer,
    SeqvarQueryPresetsSetDetailsSerializer,
    SeqvarQueryPresetsSetSerializer,
    SeqvarQuerySerializer,
    SeqvarQuerySettingsDetailsSerializer,
    SeqvarQuerySettingsFrequencySerializer,
    SeqvarQuerySettingsSerializer,
    SeqvarResultRowSerializer,
    SeqvarResultSetSerializer,
)
from seqvars.tests.factories import (
    SeqvarPresetsFrequencyFactory,
    SeqvarQueryExecutionFactory,
    SeqvarQueryFactory,
    SeqvarQueryPresetsSetFactory,
    SeqvarQuerySettingsFactory,
    SeqvarQuerySettingsFrequencyFactory,
    SeqvarResultRowFactory,
    SeqvarResultSetFactory,
)
from variants.tests.factories import CaseFactory
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
        result_json = SeqvarQueryPresetsSetDetailsSerializer(self.seqvarquerypresetsset).data
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


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQuerySettingsViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquerysettings = SeqvarQuerySettingsFactory(session=self.caseanalysissession)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerysettings-list",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQuerySettingsSerializer(self.seqvarquerysettings).data
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
        self.assertEqual(SeqvarQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "seqvars:api-seqvarquerysettings-list",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                    },
                ),
                data={
                    "seqvarquerysettingsfrequency": SeqvarQuerySettingsFrequencySerializer(
                        SeqvarQuerySettingsFrequencyFactory.build(querysettings=None)
                    ).data
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerysettings-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQuerySettingsDetailsSerializer(self.seqvarquerysettings).data
        result_json["session"] = str(result_json["session"])
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"caseanalysissession": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarquerysettings": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquerysettings-detail",
                    kwargs={
                        **{
                            "caseanalysissession": self.caseanalysissession.sodar_uuid,
                            "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [{"seqvarquerysettingsfrequency": {"gnomad_genomes_enabled": True}}],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.seqvarquerysettings.refresh_from_db()
        for key in data.keys():
            getattr(self.seqvarquerysettings, key).refresh_from_db()
        for key, value in data.items():
            self.assertNotEqual(getattr(self.seqvarquerysettings, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-seqvarquerysettings-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
                    },
                ),
                data=data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.seqvarquerysettings.refresh_from_db()
        for key in data.keys():
            getattr(self.seqvarquerysettings, key).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    self.assertEqual(
                        getattr(getattr(self.seqvarquerysettings, key), subkey),
                        subvalue,
                        f"key={key}, subkey={subkey}",
                    )
            else:
                self.assertEqual(getattr(self.seqvarquerysettings, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarQuerySettings.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-seqvarquerysettings-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarQuerySettings.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquery-list",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQuerySerializer(self.seqvarquery).data
        self.assertDictEqual(
            response.json(),
            {
                "next": None,
                "previous": None,
                "results": [result_json],
            },
        )

    def test_create(self):
        self.assertEqual(SeqvarQuery.objects.count(), 1)
        self.assertEqual(SeqvarQuerySettings.objects.count(), 1)
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 1)
        with self.login(self.superuser):
            settings_buffer = SeqvarQuerySettingsSerializer(
                SeqvarQuerySettingsFactory.build(),
            ).data
            settings_buffer["seqvarquerysettingsfrequency"] = (
                SeqvarQuerySettingsFrequencySerializer(
                    SeqvarQuerySettingsFrequencyFactory.build(querysettings=None)
                ).data
            )
            response = self.client.post(
                reverse(
                    "seqvars:api-seqvarquery-list",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                    },
                ),
                data={
                    "label": "test label",
                    "settings_buffer": settings_buffer,
                },
                format="json",
            )
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(SeqvarQuery.objects.count(), 2)
        self.assertEqual(SeqvarQuerySettings.objects.count(), 2)
        self.assertEqual(SeqvarQuerySettingsFrequency.objects.count(), 2)

    def test_retrieve_existing(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquery-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQueryDetailsSerializer(self.seqvarquery).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"caseanalysissession": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarquery": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarquery-detail",
                    kwargs={
                        **{
                            "caseanalysissession": self.caseanalysissession.sodar_uuid,
                            "seqvarquery": self.seqvarquery.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)

    @parameterized.expand(
        [
            [
                {
                    "settings_buffer": {
                        "seqvarquerysettingsfrequency": {"gnomad_genomes_enabled": True}
                    }
                }
            ],
        ]
    )
    def test_patch(self, data: dict[str, Any]):
        self.seqvarquery.refresh_from_db()
        for key, value in data.items():
            getattr(self.seqvarquery, key).refresh_from_db()
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    getattr(getattr(self.seqvarquery, key), key2).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    if isinstance(value2, dict):
                        for key3, value3 in value2.items():
                            self.assertNotEqual(
                                getattr(getattr(getattr(self.seqvarquery, key), key2), key3),
                                value3,
                                f"key={key}, key2={key2}, key3={key3}",
                            )
                    else:
                        self.assertNotEqual(
                            getattr(getattr(self.seqvarquery, key), key2),
                            value2,
                            f"key={key}, key2={key2}",
                        )
            else:
                self.assertNotEqual(getattr(self.seqvarquery, key), value, f"key={key}")

        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "seqvars:api-seqvarquery-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                    },
                ),
                data=data,
                format="json",
            )

        self.assertEqual(response.status_code, 200)

        self.seqvarquery.refresh_from_db()
        for key in data.keys():
            getattr(self.seqvarquery, key).refresh_from_db()
        for key, value in data.items():
            if isinstance(value, dict):
                for key2, value2 in value.items():
                    if isinstance(value2, dict):
                        for key3, value3 in value2.items():
                            self.assertEqual(
                                getattr(getattr(getattr(self.seqvarquery, key), key2), key3),
                                value3,
                                f"key={key}, key2={key2}, key3={key3}",
                            )
                    else:
                        self.assertEqual(
                            getattr(getattr(self.seqvarquery, key), key2),
                            value2,
                            f"key={key}, key2={key2}",
                        )
            else:
                self.assertEqual(getattr(self.seqvarquery, key), value, f"key={key}")

    def test_delete(self):
        self.assertEqual(SeqvarQuery.objects.count(), 1)

        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "seqvars:api-seqvarquery-detail",
                    kwargs={
                        "caseanalysissession": self.caseanalysissession.sodar_uuid,
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                    },
                ),
            )

        self.assertEqual(response.status_code, 204)

        self.assertEqual(SeqvarQuery.objects.count(), 0)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarQueryExecutionViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarqueryexecution-list",
                    kwargs={
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQueryExecutionSerializer(self.seqvarqueryexecution).data
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
                    "seqvars:api-seqvarqueryexecution-detail",
                    kwargs={
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                        "seqvarqueryexecution": self.seqvarqueryexecution.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarQueryExecutionDetailsSerializer(self.seqvarqueryexecution).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"seqvarquery": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarqueryexecution": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarqueryexecution-detail",
                    kwargs={
                        **{
                            "seqvarquery": self.seqvarquery.sodar_uuid,
                            "seqvarqueryexecution": self.seqvarqueryexecution.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarResultSetViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)
        self.seqvarresultset = SeqvarResultSetFactory(queryexecution=self.seqvarqueryexecution)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarresultset-list",
                    kwargs={
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarResultSetSerializer(self.seqvarresultset).data
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
                    "seqvars:api-seqvarresultset-detail",
                    kwargs={
                        "seqvarquery": self.seqvarquery.sodar_uuid,
                        "seqvarresultset": self.seqvarresultset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarResultSetSerializer(self.seqvarresultset).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"seqvarquery": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarresultset": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarresultset-detail",
                    kwargs={
                        **{
                            "seqvarquery": self.seqvarquery.sodar_uuid,
                            "seqvarresultset": self.seqvarresultset.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)


@freeze_time("2012-01-14 12:00:01")
class TestSeqvarResultRowViewSet(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(
            caseanalysis=self.caseanalysis, user=self.superuser
        )
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)
        self.seqvarresultset = SeqvarResultSetFactory(queryexecution=self.seqvarqueryexecution)
        self.seqvarresultrow = SeqvarResultRowFactory(resultset=self.seqvarresultset)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarresultrow-list",
                    kwargs={
                        "seqvarresultset": self.seqvarresultset.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarResultRowSerializer(self.seqvarresultrow).data
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
                    "seqvars:api-seqvarresultrow-detail",
                    kwargs={
                        "seqvarresultset": self.seqvarresultset.sodar_uuid,
                        "seqvarresultrow": self.seqvarresultrow.sodar_uuid,
                    },
                )
            )
        self.assertEqual(response.status_code, 200)
        result_json = SeqvarResultRowSerializer(self.seqvarresultrow).data
        self.assertDictEqual(response.json(), result_json)

    @parameterized.expand(
        [
            [{"seqvarresultset": "00000000-0000-0000-0000-000000000000"}],
            [{"seqvarresultrow": "00000000-0000-0000-0000-000000000000"}],
        ]
    )
    def test_retrieve_nonexisting(self, kwargs_override: dict[str, Any]):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqvars:api-seqvarresultrow-detail",
                    kwargs={
                        **{
                            "seqvarresultset": self.seqvarresultset.sodar_uuid,
                            "seqvarresultrow": self.seqvarresultrow.sodar_uuid,
                        },
                        **kwargs_override,
                    },
                )
            )
        self.assertEqual(response.status_code, 404)
