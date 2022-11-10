import json

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.models import CaseComments, CasePhenotypeTerms
from variants.tests.factories import CaseCommentsFactory, CaseFactory, CasePhenotypeTermsFactory


class TestCaseAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``Case``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-case-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_retrieve(self):
        url = reverse(
            "cases:api-case-retrieveupdate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "cases:api-case-retrieveupdate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [
            self.anonymous,
        ]
        bad_users_403 = [self.guest_as.user, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="PATCH", data={})
        self.assert_response(url, bad_users_401, 401, method="PATCH", data={})
        self.assert_response(url, bad_users_403, 403, method="PATCH", data={})


class TestCasePhenotypeTermsCreateListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the create/list API views dealing with ``CasePhenotypeTerms``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        def cleanup():
            CasePhenotypeTerms.objects.all().delete()

        data = {"individual": self.case.pedigree[0]["patient"], "terms": json.dumps(["HP:123456"])}
        url = reverse(
            "cases:ajax-casephenotypeterms-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 201, method="POST", data=data, cleanup_method=cleanup)
        self.assert_response(
            url, bad_users_401, 401, method="POST", data=data, cleanup_method=cleanup
        )
        self.assert_response(
            url, bad_users_403, 403, method="POST", data=data, cleanup_method=cleanup
        )


class TestAnnotationReleaseInfoListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the list AJAX views dealing with ``AnnotationReleaseInfo``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-annotationreleaseinfo-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSvAnnotationReleaseInfoListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the list AJAX views dealing with ``SvAnnotationReleaseInfo``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-svannotationreleaseinfo-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestCasePhenotypeTermsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the retrieve/update/destroy AJAX views dealing with ``CasePhenotypeTerms``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.casephenotypeterms = CasePhenotypeTermsFactory(
            case=self.case, individual=self.case.pedigree[0]["patient"]
        )

    def test_get(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs={"casephenotypeterms": self.casephenotypeterms.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs={"casephenotypeterms": self.casephenotypeterms.sodar_uuid},
        )
        data = {"individual": self.case.pedigree[0]["patient"], "terms": json.dumps(["HP:123456"])}
        good_users = [
            self.superuser,
            self.contributor_as.user,
            self.owner_as.user,
            self.delegate_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):
        casephenotypeterms_uuid = self.casephenotypeterms.sodar_uuid

        def cleanup():
            """Re-create self.casephenotypetermss with the correct UUID if necessary."""
            if not CasePhenotypeTerms.objects.filter(sodar_uuid=casephenotypeterms_uuid):
                self.casephenotypeterms = CasePhenotypeTermsFactory(
                    sodar_uuid=casephenotypeterms_uuid,
                    case=self.case,
                    individual=self.case.pedigree[0]["patient"],
                )

        kwargs = {"casephenotypeterms": self.casephenotypeterms.sodar_uuid}
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs=kwargs,
        )
        good_users = [
            self.contributor_as.user,
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestCaseCommentCreateListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the create/list API views dealing with ``CaseComment``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-casecomment-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        data = {"comment": "This is a comment"}
        url = reverse(
            "cases:ajax-casecomment-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestCaseCommentRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the retrieve/update/destroy AJAX views dealing with ``CaseComment``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.casecomment = CaseCommentsFactory(case=self.case, user=self.contributor_as.user)

    def test_get(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_patch(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )
        data = {"comment": "comment"}
        good_users = [
            self.superuser,
            self.contributor_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.owner_as.user,
            self.delegate_as.user,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 200, method="PATCH", data=data)
        self.assert_response(url, bad_users_401, 401, method="PATCH", data=data)
        self.assert_response(url, bad_users_403, 403, method="PATCH", data=data)

    def test_delete(self):
        casecomment_uuid = self.casecomment.sodar_uuid

        def cleanup():
            """Re-create self.casecomments with the correct UUID if necessary."""
            if not CaseComments.objects.filter(sodar_uuid=casecomment_uuid):
                self.casecomment = CaseCommentsFactory(
                    sodar_uuid=casecomment_uuid, case=self.case, user=self.contributor_as.user
                )

        kwargs = {"casecomment": self.casecomment.sodar_uuid}
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs=kwargs,
        )
        good_users = [
            self.contributor_as.user,
            self.superuser,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.owner_as.user,
            self.delegate_as.user,
            self.guest_as.user,
        ]
        self.assert_response(url, good_users, 204, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_401, 401, method="DELETE", cleanup_method=cleanup)
        self.assert_response(url, bad_users_403, 403, method="DELETE", cleanup_method=cleanup)


class TestCaseGeneAnnotationListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``CaseGeneAnnotation``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-casegeneannotation-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestProjectUserPermissionsAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views returning permissions."""

    def setUp(self):
        super().setUp()

    def test_list(self):
        url = reverse(
            "cases:ajax-userpermissions",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
            self.anonymous,
            self.user_no_roles,
        ]
        self.assert_response(url, good_users, 200, method="GET")


class TestCaseAlignmentStatsListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``CaseAlignmentStats``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-casealignmentstats-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestSampleVariantStatisticsListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``SampleVariantStatistics``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-casevariantstats-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")


class TestPedigreeRelatednessListAjaxView(TestProjectAPIPermissionBase):
    """Permission tests for the API views dealing with ``PedigreeRelatedness``."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases:ajax-caserelatedness-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")
