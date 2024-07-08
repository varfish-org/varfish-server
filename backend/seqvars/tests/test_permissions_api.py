from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.models import (
    SeqvarsPredefinedQuery,
    SeqvarsQuery,
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
)
from seqvars.serializers import (
    SeqvarsQueryColumnsConfigSerializer,
    SeqvarsQuerySettingsClinvarSerializer,
    SeqvarsQuerySettingsConsequenceSerializer,
    SeqvarsQuerySettingsFrequencySerializer,
    SeqvarsQuerySettingsGenotypeSerializer,
    SeqvarsQuerySettingsLocusSerializer,
    SeqvarsQuerySettingsPhenotypePrioSerializer,
    SeqvarsQuerySettingsQualitySerializer,
    SeqvarsQuerySettingsVariantPrioSerializer,
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
from variants.tests.factories import CaseFactory


class TestQueryPresetsSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsset-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsset-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsset_uuid = self.querypresetsset.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsSet.objects.exclude(sodar_uuid=querypresetsset_uuid):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "querypresetsset": self.querypresetsset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "querypresetsset": self.querypresetsset.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "querypresetsset": self.querypresetsset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsset_uuid = self.querypresetsset.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsSet.objects.filter(sodar_uuid=querypresetsset_uuid):
                self.querypresetsset = SeqvarsQueryPresetsSetFactory(
                    sodar_uuid=querypresetsset_uuid,
                    project=self.project,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsVersionSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetssetversion-list",
            kwargs={"querypresetsset": self.querypresetsset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetssetversion-list",
            kwargs={"querypresetsset": self.querypresetsset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "version_minor": 2,
        }

        querypresetssetversion_uuid = self.querypresetssetversion.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsSetVersion.objects.exclude(
                sodar_uuid=querypresetssetversion_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetssetversion-detail",
            kwargs={
                "querypresetsset": self.querypresetsset.sodar_uuid,
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetssetversion-detail",
            kwargs={
                "querypresetsset": self.querypresetsset.sodar_uuid,
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetssetversion-detail",
            kwargs={
                "querypresetsset": self.querypresetsset.sodar_uuid,
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetssetversion_uuid = self.querypresetssetversion.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsSetVersion.objects.filter(
                sodar_uuid=querypresetssetversion_uuid
            ):
                self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
                    sodar_uuid=querypresetssetversion_uuid, presetsset=self.querypresetsset
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsFrequencyViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsfrequency-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsfrequency-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsfrequency_uuid = self.querypresetsfrequency.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsFrequency.objects.exclude(
                sodar_uuid=querypresetsfrequency_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsfrequency-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsfrequency": self.querypresetsfrequency.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsfrequency-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsfrequency": self.querypresetsfrequency.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsfrequency-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsfrequency": self.querypresetsfrequency.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsfrequency_uuid = self.querypresetsfrequency.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsFrequency.objects.filter(
                sodar_uuid=querypresetsfrequency_uuid
            ):
                self.querypresetsfrequency = SeqvarsQueryPresetsFrequencyFactory(
                    sodar_uuid=querypresetsfrequency_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsQualityViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsquality = SeqvarsQueryPresetsQualityFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsquality-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsquality-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsquality_uuid = self.querypresetsquality.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsQuality.objects.exclude(
                sodar_uuid=querypresetsquality_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsquality-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsquality": self.querypresetsquality.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsquality-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsquality": self.querypresetsquality.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsquality-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsquality": self.querypresetsquality.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsquality_uuid = self.querypresetsquality.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsQuality.objects.filter(sodar_uuid=querypresetsquality_uuid):
                self.querypresetsquality = SeqvarsQueryPresetsQualityFactory(
                    sodar_uuid=querypresetsquality_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsConsequenceViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsconsequence = SeqvarsQueryPresetsConsequenceFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsconsequence-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsconsequence-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsconsequence_uuid = self.querypresetsconsequence.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsConsequence.objects.exclude(
                sodar_uuid=querypresetsconsequence_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsconsequence-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsconsequence": self.querypresetsconsequence.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsconsequence-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsconsequence": self.querypresetsconsequence.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsconsequence-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsconsequence": self.querypresetsconsequence.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsconsequence_uuid = self.querypresetsconsequence.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsConsequence.objects.filter(
                sodar_uuid=querypresetsconsequence_uuid
            ):
                self.querypresetsconsequence = SeqvarsQueryPresetsConsequenceFactory(
                    sodar_uuid=querypresetsconsequence_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsLocusViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetslocus = SeqvarsQueryPresetsLocusFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetslocus-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetslocus-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetslocus_uuid = self.querypresetslocus.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsLocus.objects.exclude(sodar_uuid=querypresetslocus_uuid):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetslocus-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetslocus": self.querypresetslocus.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetslocus-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetslocus": self.querypresetslocus.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetslocus-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetslocus": self.querypresetslocus.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetslocus_uuid = self.querypresetslocus.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsLocus.objects.filter(sodar_uuid=querypresetslocus_uuid):
                self.querypresetslocus = SeqvarsQueryPresetsLocusFactory(
                    sodar_uuid=querypresetslocus_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsPhenotypePrioViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsphenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsphenotypeprio-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsphenotypeprio-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsphenotypeprio_uuid = self.querypresetsphenotypeprio.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsPhenotypePrio.objects.exclude(
                sodar_uuid=querypresetsphenotypeprio_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsphenotypeprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsphenotypeprio": self.querypresetsphenotypeprio.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsphenotypeprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsphenotypeprio": self.querypresetsphenotypeprio.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsphenotypeprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsphenotypeprio": self.querypresetsphenotypeprio.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsphenotypeprio_uuid = self.querypresetsphenotypeprio.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsPhenotypePrio.objects.filter(
                sodar_uuid=querypresetsphenotypeprio_uuid
            ):
                self.querypresetsphenotypeprio = SeqvarsQueryPresetsPhenotypePrioFactory(
                    sodar_uuid=querypresetsphenotypeprio_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsVariantPrioViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsvariantprio = SeqvarsQueryPresetsVariantPrioFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsvariantprio-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsvariantprio-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsvariantprio_uuid = self.querypresetsvariantprio.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsVariantPrio.objects.exclude(
                sodar_uuid=querypresetsvariantprio_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsvariantprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsvariantprio": self.querypresetsvariantprio.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsvariantprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsvariantprio": self.querypresetsvariantprio.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsvariantprio-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsvariantprio": self.querypresetsvariantprio.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsvariantprio_uuid = self.querypresetsvariantprio.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsVariantPrio.objects.filter(
                sodar_uuid=querypresetsvariantprio_uuid
            ):
                self.querypresetsvariantprio = SeqvarsQueryPresetsVariantPrioFactory(
                    sodar_uuid=querypresetsvariantprio_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsColumnsViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetscolumns = SeqvarsQueryPresetsColumnsFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetscolumns-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetscolumns-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetscolumns_uuid = self.querypresetscolumns.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsColumns.objects.exclude(
                sodar_uuid=querypresetscolumns_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetscolumns-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetscolumns": self.querypresetscolumns.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetscolumns-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetscolumns": self.querypresetscolumns.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetscolumns-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetscolumns": self.querypresetscolumns.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetscolumns_uuid = self.querypresetscolumns.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsColumns.objects.filter(sodar_uuid=querypresetscolumns_uuid):
                self.querypresetscolumns = SeqvarsQueryPresetsColumnsFactory(
                    sodar_uuid=querypresetscolumns_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsClinvarViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.querypresetsclinvar = SeqvarsQueryPresetsClinvarFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsclinvar-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querypresetsclinvar-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        querypresetsclinvar_uuid = self.querypresetsclinvar.sodar_uuid

        def cleanup():
            for obj in SeqvarsQueryPresetsClinvar.objects.exclude(
                sodar_uuid=querypresetsclinvar_uuid
            ):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querypresetsclinvar-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsclinvar": self.querypresetsclinvar.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querypresetsclinvar-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsclinvar": self.querypresetsclinvar.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-querypresetsclinvar-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "querypresetsclinvar": self.querypresetsclinvar.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querypresetsclinvar_uuid = self.querypresetsclinvar.sodar_uuid

        def cleanup():
            if not SeqvarsQueryPresetsClinvar.objects.filter(sodar_uuid=querypresetsclinvar_uuid):
                self.querypresetsclinvar = SeqvarsQueryPresetsClinvarFactory(
                    sodar_uuid=querypresetsclinvar_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestPredefinedQueryViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = SeqvarsQueryPresetsSetFactory(project=self.project)
        self.querypresetssetversion = SeqvarsQueryPresetsSetVersionFactory(
            presetsset=self.querypresetsset
        )
        self.predefinedquery = SeqvarsPredefinedQueryFactory(
            presetssetversion=self.querypresetssetversion
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-predefinedquery-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-predefinedquery-list",
            kwargs={"querypresetssetversion": self.querypresetssetversion.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "rank": 1,
            "label": "test",
        }

        predefinedquery_uuid = self.predefinedquery.sodar_uuid

        def cleanup():
            for obj in SeqvarsPredefinedQuery.objects.exclude(sodar_uuid=predefinedquery_uuid):
                obj.delete()

        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-predefinedquery-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "predefinedquery": self.predefinedquery.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-predefinedquery-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "predefinedquery": self.predefinedquery.sodar_uuid,
            },
        )
        data = {"rank": 42}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):

        url = reverse(
            "seqvars:api-predefinedquery-detail",
            kwargs={
                "querypresetssetversion": self.querypresetssetversion.sodar_uuid,
                "predefinedquery": self.predefinedquery.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        predefinedquery_uuid = self.predefinedquery.sodar_uuid

        def cleanup():
            if not SeqvarsPredefinedQuery.objects.filter(sodar_uuid=predefinedquery_uuid):
                self.predefinedquery = SeqvarsPredefinedQueryFactory(
                    sodar_uuid=predefinedquery_uuid,
                    presetssetversion=self.querypresetssetversion,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQuerySettingsViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.querysettings = SeqvarsQuerySettingsFactory(session=self.session)

    def test_list(self):
        url = reverse(
            "seqvars:api-querysettings-list",
            kwargs={
                "session": self.session.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-querysettings-list",
            kwargs={
                "session": self.session.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
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
        }

        querysettings_uuid = self.querysettings.sodar_uuid

        def cleanup():
            for obj in SeqvarsQuerySettings.objects.exclude(sodar_uuid=querysettings_uuid):
                obj.delete()

        self.assert_response(
            url,
            good_users,
            201,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )
        self.assert_response(
            url,
            bad_users_403,
            403,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-querysettings-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "querysettings": self.querysettings.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-querysettings-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "querysettings": self.querysettings.sodar_uuid,
            },
        )
        data = {"frequency": {"gnomad_genomes": {"enabled": True}}}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(
            url, good_users, 200, method="PATCH", data=data, req_kwargs={"format": "json"}
        )
        self.assert_response(
            url, bad_users_401, 401, method="PATCH", data=data, req_kwargs={"format": "json"}
        )
        self.assert_response(
            url, bad_users_403, 403, method="PATCH", data=data, req_kwargs={"format": "json"}
        )

    def test_delete(self):

        url = reverse(
            "seqvars:api-querysettings-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "querysettings": self.querysettings.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        querysettings_uuid = self.querysettings.sodar_uuid

        def cleanup():
            if not SeqvarsQuerySettings.objects.filter(sodar_uuid=querysettings_uuid):
                self.querysettings = SeqvarsQuerySettingsFactory(
                    sodar_uuid=querysettings_uuid,
                    session=self.session,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.query = SeqvarsQueryFactory(session=self.session)

    def test_list(self):
        url = reverse(
            "seqvars:api-query-list",
            kwargs={
                "session": self.session.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "seqvars:api-query-list",
            kwargs={
                "session": self.session.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_guest, self.user_finder_cat]

        data = {
            "label": "test label",
            "settings": {
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
            "columnsconfig": SeqvarsQueryColumnsConfigSerializer(
                SeqvarsQueryColumnsConfigFactory.build(seqvarsquery=None)
            ).data,
        }

        query_uuid = self.query.sodar_uuid

        def cleanup():
            for obj in SeqvarsQuery.objects.exclude(settings__sodar_uuid=query_uuid):
                obj.delete()
            for obj in SeqvarsQuerySettings.objects.exclude(sodar_uuid=query_uuid):
                obj.delete()

        self.assert_response(
            url,
            good_users,
            201,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )
        self.assert_response(
            url,
            bad_users_403,
            403,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
            cleanup_method=cleanup,
        )

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-query-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "query": self.query.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "seqvars:api-query-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "query": self.query.sodar_uuid,
            },
        )
        data = {"query_buffer": {"frequency": {"gnomad_genomes_enabled": True}}}
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(
            url, good_users, 200, method="PATCH", data=data, req_kwargs={"format": "json"}
        )
        self.assert_response(
            url, bad_users_401, 401, method="PATCH", data=data, req_kwargs={"format": "json"}
        )
        self.assert_response(
            url, bad_users_403, 403, method="PATCH", data=data, req_kwargs={"format": "json"}
        )

    def test_delete(self):

        url = reverse(
            "seqvars:api-query-detail",
            kwargs={
                "session": self.session.sodar_uuid,
                "query": self.query.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_contributor,
            self.user_owner,
            self.user_delegate,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [
            self.user_no_roles,
            self.user_guest,
        ]

        query_uuid = self.query.sodar_uuid

        def cleanup():
            if not SeqvarsQuery.objects.filter(sodar_uuid=query_uuid):
                self.query = SeqvarsQueryFactory(
                    sodar_uuid=query_uuid,
                    session=self.session,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryExecutionViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)

    def test_list(self):
        url = reverse(
            "seqvars:api-queryexecution-list",
            kwargs={
                "query": self.query.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-queryexecution-detail",
            kwargs={
                "query": self.query.sodar_uuid,
                "queryexecution": self.queryexecution.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestResultSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)
        self.resultset = SeqvarsResultSetFactory(queryexecution=self.queryexecution)

    def test_list(self):
        url = reverse(
            "seqvars:api-resultset-list",
            kwargs={
                "query": self.query.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-resultset-detail",
            kwargs={
                "query": self.query.sodar_uuid,
                "resultset": self.resultset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestResultRowViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.session = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.query = SeqvarsQueryFactory(session=self.session)
        self.queryexecution = SeqvarsQueryExecutionFactory(query=self.query)
        self.resultset = SeqvarsResultSetFactory(queryexecution=self.queryexecution)
        self.seqvarresultrow = SeqvarsResultRowFactory(resultset=self.resultset)

    def test_list(self):
        url = reverse(
            "seqvars:api-resultrow-list",
            kwargs={
                "resultset": self.resultset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        url = reverse(
            "seqvars:api-resultrow-detail",
            kwargs={
                "resultset": self.resultset.sodar_uuid,
                "seqvarresultrow": self.seqvarresultrow.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles, self.user_finder_cat]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")
