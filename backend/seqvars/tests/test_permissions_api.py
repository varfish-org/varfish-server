from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_analysis.tests.factories import CaseAnalysisFactory, CaseAnalysisSessionFactory
from seqvars.models import Query, QueryPresetsFrequency, QueryPresetsSet, QuerySettings
from seqvars.serializers import QuerySettingsFrequencySerializer, QuerySettingsSerializer
from seqvars.tests.factories import (
    QueryExecutionFactory,
    QueryFactory,
    QueryPresetsFrequencyFactory,
    QueryPresetsSetFactory,
    QuerySettingsFactory,
    QuerySettingsFrequencyFactory,
    ResultRowFactory,
    ResultSetFactory,
)
from variants.tests.factories import CaseFactory


class TestQueryPresetsSetViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory(project=self.project)

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
            for obj in QueryPresetsSet.objects.exclude(sodar_uuid=querypresetsset_uuid):
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
            if not QueryPresetsSet.objects.filter(sodar_uuid=querypresetsset_uuid):
                self.querypresetsset = QueryPresetsSetFactory(
                    sodar_uuid=querypresetsset_uuid,
                    project=self.project,
                )

        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestQueryPresetsFrequencyViewSet(TestProjectAPIPermissionBase):

    def setUp(self):
        super().setUp()
        self.querypresetsset = QueryPresetsSetFactory(project=self.project)
        self.querypresetsfrequency = QueryPresetsFrequencyFactory(presetsset=self.querypresetsset)

    def test_list(self):
        url = reverse(
            "seqvars:api-querypresetsfrequency-list",
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
            "seqvars:api-querypresetsfrequency-list",
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
            "rank": 1,
            "label": "test",
        }

        querypresetsfrequency_uuid = self.querypresetsfrequency.sodar_uuid

        def cleanup():
            for obj in QueryPresetsFrequency.objects.exclude(sodar_uuid=querypresetsfrequency_uuid):
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
                "querypresetsset": self.querypresetsset.sodar_uuid,
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
                "querypresetsset": self.querypresetsset.sodar_uuid,
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
                "querypresetsset": self.querypresetsset.sodar_uuid,
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

        querypresetsset_uuid = self.querypresetsfrequency.sodar_uuid

        def cleanup():
            if not QueryPresetsFrequency.objects.filter(sodar_uuid=querypresetsset_uuid):
                self.querypresetsfrequency = QueryPresetsFrequencyFactory(
                    sodar_uuid=querypresetsset_uuid, presetsset=self.querypresetsset
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
        self.querysettings = QuerySettingsFactory(session=self.session)

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
            "querysettingsfrequency": QuerySettingsFrequencySerializer(
                QuerySettingsFrequencyFactory.build(querysettings=None)
            ).data,
        }

        querysettings_uuid = self.querysettings.sodar_uuid

        def cleanup():
            for obj in QuerySettings.objects.exclude(sodar_uuid=querysettings_uuid):
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
        data = {"querysettingsfrequency": {"gnomad_genomes_enabled": True}}
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
            if not QuerySettings.objects.filter(sodar_uuid=querysettings_uuid):
                self.querysettings = QuerySettingsFactory(
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
        self.query = QueryFactory(session=self.session)

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
            "settings_buffer": {
                "querysettingsfrequency": (
                    QuerySettingsFrequencySerializer(
                        QuerySettingsFrequencyFactory.build(querysettings=None)
                    ).data
                ),
            },
        }

        query_uuid = self.query.sodar_uuid

        def cleanup():
            for obj in QuerySettings.objects.exclude(sodar_uuid=query_uuid):
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
        data = {"query_buffer": {"querysettingsfrequency": {"gnomad_genomes_enabled": True}}}
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
            if not Query.objects.filter(sodar_uuid=query_uuid):
                self.query = QueryFactory(
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
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)

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
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)
        self.resultset = ResultSetFactory(queryexecution=self.queryexecution)

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
        self.query = QueryFactory(session=self.session)
        self.queryexecution = QueryExecutionFactory(query=self.query)
        self.resultset = ResultSetFactory(queryexecution=self.queryexecution)
        self.seqvarresultrow = ResultRowFactory(resultset=self.resultset)

    def test_list(self):
        url = reverse(
            "seqvars:api-seqvarresultrow-list",
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
            "seqvars:api-seqvarresultrow-detail",
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
