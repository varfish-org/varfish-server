from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from seqvars.models import SeqvarPresetsFrequency, SeqvarQueryPresetsSet, SeqvarQuerySettings
from seqvars.serializers import SeqvarQuerySettingsFrequencySerializer
from seqvars.tests.factories import (
    SeqvarPresetsFrequencyFactory,
    SeqvarQueryPresetsSetFactory,
    SeqvarQuerySettingsFactory,
    SeqvarQuerySettingsFrequencyFactory,
)
from variants.tests.factories import CaseFactory


class TestSeqvarQueryPresetsSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarquerypresetsset-list",
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
            "seqvars:api-seqvarquerypresetsset-list",
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

        seqvarquerypresetsset_uuid = self.seqvarquerypresetsset.sodar_uuid

        def cleanup():
            for obj in SeqvarQueryPresetsSet.objects.exclude(sodar_uuid=seqvarquerypresetsset_uuid):
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
            "seqvars:api-seqvarquerypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
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
            "seqvars:api-seqvarquerypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
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
            "seqvars:api-seqvarquerypresetsset-detail",
            kwargs={
                "project": self.project.sodar_uuid,
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
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

        seqvarquerypresetsset_uuid = self.seqvarquerypresetsset.sodar_uuid

        def cleanup():
            if not SeqvarQueryPresetsSet.objects.filter(sodar_uuid=seqvarquerypresetsset_uuid):
                self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory(
                    sodar_uuid=seqvarquerypresetsset_uuid,
                    project=self.project,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSeqvarPresetsFrequencyViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.seqvarquerypresetsset = SeqvarQueryPresetsSetFactory(project=self.project)
        self.seqvarpresetsfrequency = SeqvarPresetsFrequencyFactory(
            presetsset=self.seqvarquerypresetsset
        )

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarpresetsfrequency-list",
            kwargs={"seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid},
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
            "seqvars:api-seqvarpresetsfrequency-list",
            kwargs={"seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid},
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

        seqvarpresetsfrequency_uuid = self.seqvarpresetsfrequency.sodar_uuid

        def cleanup():
            for obj in SeqvarPresetsFrequency.objects.exclude(
                sodar_uuid=seqvarpresetsfrequency_uuid
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
            "seqvars:api-seqvarpresetsfrequency-detail",
            kwargs={
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                "seqvarpresetsfrequency": self.seqvarpresetsfrequency.sodar_uuid,
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
            "seqvars:api-seqvarpresetsfrequency-detail",
            kwargs={
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                "seqvarpresetsfrequency": self.seqvarpresetsfrequency.sodar_uuid,
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
            "seqvars:api-seqvarpresetsfrequency-detail",
            kwargs={
                "seqvarquerypresetsset": self.seqvarquerypresetsset.sodar_uuid,
                "seqvarpresetsfrequency": self.seqvarpresetsfrequency.sodar_uuid,
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

        seqvarquerypresetsset_uuid = self.seqvarpresetsfrequency.sodar_uuid

        def cleanup():
            if not SeqvarPresetsFrequency.objects.filter(sodar_uuid=seqvarquerypresetsset_uuid):
                self.seqvarpresetsfrequency = SeqvarPresetsFrequencyFactory(
                    sodar_uuid=seqvarquerypresetsset_uuid, presetsset=self.seqvarquerypresetsset
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSeqvarQuerySettingsViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.seqvarquerysettings = SeqvarQuerySettingsFactory(case=self.case)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarquerysettings-list",
            kwargs={
                "case": self.case.sodar_uuid,
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
            "seqvars:api-seqvarquerysettings-list",
            kwargs={
                "case": self.case.sodar_uuid,
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
            "seqvarquerysettingsfrequency": SeqvarQuerySettingsFrequencySerializer(
                SeqvarQuerySettingsFrequencyFactory.build(querysettings=None)
            ).data,
        }

        seqvarquerysettings_uuid = self.seqvarquerysettings.sodar_uuid

        def cleanup():
            for obj in SeqvarQuerySettings.objects.exclude(sodar_uuid=seqvarquerysettings_uuid):
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
            "seqvars:api-seqvarquerysettings-detail",
            kwargs={
                "case": self.case.sodar_uuid,
                "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
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
            "seqvars:api-seqvarquerysettings-detail",
            kwargs={
                "case": self.case.sodar_uuid,
                "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
            },
        )
        data = {"seqvarquerysettingsfrequency": {"gnomad_genomes_enabled": True}}
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
            "seqvars:api-seqvarquerysettings-detail",
            kwargs={
                "case": self.case.sodar_uuid,
                "seqvarquerysettings": self.seqvarquerysettings.sodar_uuid,
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

        seqvarquerysettings_uuid = self.seqvarquerysettings.sodar_uuid

        def cleanup():
            if not SeqvarQuerySettings.objects.filter(sodar_uuid=seqvarquerysettings_uuid):
                self.seqvarpresetsfrequency = SeqvarQuerySettingsFactory(
                    sodar_uuid=seqvarquerysettings_uuid, case=self.case
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)
