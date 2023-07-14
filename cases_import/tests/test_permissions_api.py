"""Test permission for the API views in ``cases_import`` app.

This module contains tests that exercise the basic permissions of the API views.  That is,
the result of the actions is not tested here.  Instead, such tests are in ``test_views_api.py``.
"""

from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases_import.models import CaseImportAction
from cases_import.proto import family_payload_with_updated_case_name
from cases_import.tests.factories import CaseImportActionFactory, case_import_action_json
from variants.tests.factories import CaseFactory


class CaseImportActionApiPermissionTest(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.caseimportaction = CaseImportActionFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "cases_import:api-caseimportaction-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        def cleanup():
            CaseImportAction.objects.all().delete()

        data = case_import_action_json(project=self.project)

        url = reverse(
            "cases_import:api-caseimportaction-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.guest_as.user, self.user_no_roles]
        self.assert_response(
            url,
            good_users,
            201,
            method="POST",
            data=data,
            cleanup_method=cleanup,
            req_kwargs={"format": "json"},
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
        )
        self.assert_response(
            url,
            bad_users_403,
            403,
            method="POST",
            data=data,
            req_kwargs={"format": "json"},
        )

    def test_retrieve(self):
        url = reverse(
            "cases_import:api-caseimportaction-retrieveupdatedestroy",
            kwargs={"caseimportaction": self.caseimportaction.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        def cleanup():
            self.caseimportaction.refresh_from_db()
            self.caseimportaction.action = CaseImportAction.ACTION_UPDATE
            self.caseimportaction.save()

        case = CaseFactory(project=self.project)

        data = case_import_action_json(
            project=self.project,
            action=CaseImportAction.ACTION_UPDATE,
        )
        data["payload"] = family_payload_with_updated_case_name(data["payload"], case.name)

        url = reverse(
            "cases_import:api-caseimportaction-retrieveupdatedestroy",
            kwargs={"caseimportaction": self.caseimportaction.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.guest_as.user, self.user_no_roles]
        self.assert_response(
            url,
            good_users,
            200,
            method="PATCH",
            cleanup_method=cleanup,
            data=data,
            req_kwargs={"format": "json"},
        )
        self.assert_response(
            url,
            bad_users_401,
            401,
            method="PATCH",
            data=data,
            req_kwargs={"format": "json"},
        )
        self.assert_response(
            url,
            bad_users_403,
            403,
            method="PATCH",
            data=data,
            req_kwargs={"format": "json"},
        )

    def test_delete(self):
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        bad_users_401 = [self.anonymous]
        bad_users_403 = [self.guest_as.user, self.user_no_roles]
        for user in good_users:
            caseimportaction = CaseImportActionFactory(project=self.project)
            url = reverse(
                "cases_import:api-caseimportaction-retrieveupdatedestroy",
                kwargs={"caseimportaction": caseimportaction.sodar_uuid},
            )
            self.assert_response(
                url,
                [user],
                204,
                method="DELETE",
            )
        url = reverse(
            "cases_import:api-caseimportaction-retrieveupdatedestroy",
            kwargs={"caseimportaction": self.caseimportaction.sodar_uuid},
        )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")
