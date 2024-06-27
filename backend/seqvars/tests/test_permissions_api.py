from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.models import (
    SeqvarPresetsFrequency,
    SeqvarQuery,
    SeqvarQueryPresetsSet,
    SeqvarQuerySettings,
)
from seqvars.serializers import (
    SeqvarQuerySettingsFrequencySerializer,
    SeqvarQuerySettingsSerializer,
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
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquerysettings = SeqvarQuerySettingsFactory(session=self.caseanalysissession)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarquerysettings-list",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
                self.seqvarquerysettings = SeqvarQuerySettingsFactory(
                    sodar_uuid=seqvarquerysettings_uuid,
                    session=self.caseanalysissession,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSeqvarQueryViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarquery-list",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
            "seqvars:api-seqvarquery-list",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
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
            "settings_buffer": {
                "seqvarquerysettingsfrequency": (
                    SeqvarQuerySettingsFrequencySerializer(
                        SeqvarQuerySettingsFrequencyFactory.build(querysettings=None)
                    ).data
                ),
            },
        }

        seqvarquery_uuid = self.seqvarquery.sodar_uuid

        def cleanup():
            for obj in SeqvarQuerySettings.objects.exclude(sodar_uuid=seqvarquery_uuid):
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
            "seqvars:api-seqvarquery-detail",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
                "seqvarquery": self.seqvarquery.sodar_uuid,
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
            "seqvars:api-seqvarquery-detail",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
                "seqvarquery": self.seqvarquery.sodar_uuid,
            },
        )
        data = {"query_buffer": {"seqvarquerysettingsfrequency": {"gnomad_genomes_enabled": True}}}
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
            "seqvars:api-seqvarquery-detail",
            kwargs={
                "caseanalysissession": self.caseanalysissession.sodar_uuid,
                "seqvarquery": self.seqvarquery.sodar_uuid,
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

        seqvarquery_uuid = self.seqvarquery.sodar_uuid

        def cleanup():
            if not SeqvarQuery.objects.filter(sodar_uuid=seqvarquery_uuid):
                self.seqvarquery = SeqvarQueryFactory(
                    sodar_uuid=seqvarquery_uuid,
                    session=self.caseanalysissession,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestSeqvarQueryExecutionViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarqueryexecution-list",
            kwargs={
                "seqvarquery": self.seqvarquery.sodar_uuid,
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
            "seqvars:api-seqvarqueryexecution-detail",
            kwargs={
                "seqvarquery": self.seqvarquery.sodar_uuid,
                "seqvarqueryexecution": self.seqvarqueryexecution.sodar_uuid,
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


class TestSeqvarResultSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)
        self.seqvarresultset = SeqvarResultSetFactory(queryexecution=self.seqvarqueryexecution)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarresultset-list",
            kwargs={
                "seqvarquery": self.seqvarquery.sodar_uuid,
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
            "seqvars:api-seqvarresultset-detail",
            kwargs={
                "seqvarquery": self.seqvarquery.sodar_uuid,
                "seqvarresultset": self.seqvarresultset.sodar_uuid,
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


class TestSeqvarResultRowViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.caseanalysis = CaseAnalysisFactory(case=self.case)
        self.caseanalysissession = CaseAnalysisSessionFactory(caseanalysis=self.caseanalysis)
        self.seqvarquery = SeqvarQueryFactory(session=self.caseanalysissession)
        self.seqvarqueryexecution = SeqvarQueryExecutionFactory(query=self.seqvarquery)
        self.seqvarresultset = SeqvarResultSetFactory(queryexecution=self.seqvarqueryexecution)
        self.seqvarresultrow = SeqvarResultRowFactory(resultset=self.seqvarresultset)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarresultrow-list",
            kwargs={
                "seqvarresultset": self.seqvarresultset.sodar_uuid,
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
            "seqvars:api-seqvarresultrow-detail",
            kwargs={
                "seqvarresultset": self.seqvarresultset.sodar_uuid,
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
