"""Tests for the functionality of the API views.

This module uses the "lowermost" role that allows to make the changes and focuses on the actual
functionality.
"""

import copy
import functools
from unittest.mock import patch

from bgjobs.models import BackgroundJob
from django.urls import reverse
from freezegun import freeze_time
import jsonmatch
from parameterized import parameterized
import yaml

from cases_import.models import CaseImportAction, CaseImportBackgroundJob
from cases_import.proto import family_payload_with_updated_case_name
from cases_import.tests.factories import CaseImportActionFactory
from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


@functools.cache
def load_family_payload():
    with open("cases_import/tests/data/family.yaml", "rt") as inputf:
        return yaml.safe_load(inputf)["family"]


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionListTest(ApiViewTestBase):
    """Test listing ``CaseImportAction`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_list_empty(self):
        """GET on empty list"""
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(), {"count": 0, "next": None, "previous": None, "results": []}
        )

    def test_list_non_empty(self):
        """GET on non-empty list"""
        self.caseimportaction = CaseImportActionFactory(project=self.project)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                **extra,
            )
        self.assertEqual(response.status_code, 200)
        expected_json = jsonmatch.compile(
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "action": "create",
                        "date_created": "2012-01-14T12:00:01Z",
                        "date_modified": "2012-01-14T12:00:01Z",
                        "payload": dict,
                        "project": str(self.project.sodar_uuid),
                        "sodar_uuid": str(self.caseimportaction.sodar_uuid),
                        "state": "draft",
                    }
                ],
            }
        )
        expected_json.assert_matches(response.json())


@freeze_time("2012-01-14 12:00:01")
class CaseImportActionCreateTest(ApiViewTestBase):
    """Tests for the **creation** of the ``CaseImportAction`` objects.

    Each tests corresponds to an individual use case.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def _test_create_action_create_with_state_succeeds(self, state: str):
        self.assertEqual(CaseImportAction.objects.count(), 0)

        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_CREATE,
                    "state": state,
                    "payload": load_family_payload(),
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 201, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 1)
        caseimportaction = CaseImportAction.objects.all()[0]

        expected_json = jsonmatch.compile(
            {
                "action": CaseImportAction.ACTION_CREATE,
                "state": state,
                "date_created": "2012-01-14T12:00:01Z",
                "date_modified": "2012-01-14T12:00:01Z",
                "payload": dict,
                "project": str(self.project.sodar_uuid),
                "sodar_uuid": str(caseimportaction.sodar_uuid),
            }
        )

        expected_json.assert_matches(response.json())

    def test_create_action_create_as_state_draft_succeeds(self):
        """POST action=create state=draft => succeeds"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_create_with_state_succeeds(CaseImportAction.STATE_DRAFT)

        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

    @patch("cases_import.models.run_caseimportactionbackgroundjob")
    def test_create_action_create_as_state_submitted_succeeds(self, mock_run):
        """POST action=create state=submitted => succeeds, triggers job"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_create_with_state_succeeds(CaseImportAction.STATE_SUBMITTED)

        self.assertEquals(BackgroundJob.objects.count(), 1)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 1)

        caseimportaction = CaseImportAction.objects.all()[0]
        backgroundjob = BackgroundJob.objects.all()[0]
        caseimportbackgroundjob = CaseImportBackgroundJob.objects.all()[0]
        self.assertEquals(caseimportbackgroundjob.bg_job.pk, backgroundjob.pk)
        self.assertEquals(caseimportbackgroundjob.caseimportaction.pk, caseimportaction.pk)

        mock_run.assert_called_once_with(pk=caseimportbackgroundjob.pk)

    @parameterized.expand(
        [
            [CaseImportAction.STATE_RUNNING],
            [CaseImportAction.STATE_FAILED],
            [CaseImportAction.STATE_SUCCESS],
        ]
    )
    def test_create_action_create_as_state_other_fails(self, state):
        """POST action=create state=<other> => fails"""
        self.assertEqual(CaseImportAction.objects.count(), 0)

        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_CREATE,
                    "state": state,
                    "payload": load_family_payload(),
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def test_create_action_create_as_state_draft_fails_same_name(self):
        """POST action=create state=draft name=<collision> => fails"""
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), case.name)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_CREATE,
                    "state": CaseImportAction.STATE_DRAFT,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def test_create_action_create_as_state_draft_fails_invalid_payload(self):
        """POST action=create state=draft payload=<invalid> => fails"""
        payload = copy.deepcopy(load_family_payload())
        payload["pedigree"]["persons"][0]["familyId"] = "InCoNsiStEnT"
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_CREATE,
                    "state": CaseImportAction.STATE_DRAFT,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def _test_create_action_update_with_state_succeeds(self, state: str):
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), case.name)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_UPDATE,
                    "state": state,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 201, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 1)

    def test_create_action_update_as_state_draft_succeeds(self):
        """POST action=update state=draft => succeeds"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_update_with_state_succeeds(CaseImportAction.STATE_DRAFT)

        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

    @patch("cases_import.models.run_caseimportactionbackgroundjob")
    def test_create_action_update_as_state_submitted_succeeds(self, mock_run):
        """POST action=update state=submitted => succeeds, triggers job"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_update_with_state_succeeds(CaseImportAction.STATE_SUBMITTED)

        self.assertEquals(BackgroundJob.objects.count(), 1)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 1)

        caseimportaction = CaseImportAction.objects.all()[0]
        backgroundjob = BackgroundJob.objects.all()[0]
        caseimportbackgroundjob = CaseImportBackgroundJob.objects.all()[0]
        self.assertEquals(caseimportbackgroundjob.bg_job.pk, backgroundjob.pk)
        self.assertEquals(caseimportbackgroundjob.caseimportaction.pk, caseimportaction.pk)

        mock_run.assert_called_once_with(pk=caseimportbackgroundjob.pk)

    @parameterized.expand(
        [
            [CaseImportAction.STATE_RUNNING],
            [CaseImportAction.STATE_FAILED],
            [CaseImportAction.STATE_SUCCESS],
        ]
    )
    def test_create_action_update_as_state_other_fails(self, state):
        """POST action=update state=<other> => fail"""
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), case.name)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_UPDATE,
                    "state": state,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def test_create_action_create_as_state_submitted_fails_non_existing(self):
        """POST action=create state=draft name=<non-existing> => fails"""
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), f"xX{case.name}Xx")
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_UPDATE,
                    "state": CaseImportAction.STATE_DRAFT,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def test_create_action_create_as_state_submitted_fails_invalid_payload(self):
        """POST action=create state=draft payload=<invalid> => fails"""
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = copy.deepcopy(load_family_payload())
        payload["pedigree"]["persons"][0]["familyId"] = "InCoNsiStEnT"
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_UPDATE,
                    "state": CaseImportAction.STATE_DRAFT,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)

    def _test_create_action_delete_with_state_succeeds(self, state: str):
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), case.name)
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_DELETE,
                    "state": state,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 201, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 1)

    def test_create_action_delete_as_state_draft_succeeds(self):
        """POST action=delete state=draft => succeeds"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_delete_with_state_succeeds(CaseImportAction.STATE_DRAFT)

        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

    @patch("cases_import.models.run_caseimportactionbackgroundjob")
    def test_create_action_delete_as_state_submitted_succeeds(self, mock_run):
        """POST action=delete state=draft => succeeds, triggers job"""
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEquals(CaseImportBackgroundJob.objects.count(), 0)

        self._test_create_action_delete_with_state_succeeds(CaseImportAction.STATE_SUBMITTED)

        caseimportaction = CaseImportAction.objects.all()[0]
        backgroundjob = BackgroundJob.objects.all()[0]
        caseimportbackgroundjob = CaseImportBackgroundJob.objects.all()[0]
        self.assertEquals(caseimportbackgroundjob.bg_job.pk, backgroundjob.pk)
        self.assertEquals(caseimportbackgroundjob.caseimportaction.pk, caseimportaction.pk)

        mock_run.assert_called_once_with(pk=caseimportbackgroundjob.pk)

    def test_create_action_delete_as_state_draft_fails_non_existing(self):
        """POST action=create state=draft name=<non-existing> => fails"""
        case = CaseFactory(project=self.project)
        self.assertEqual(CaseImportAction.objects.count(), 0)

        payload = family_payload_with_updated_case_name(load_family_payload(), f"xX{case.name}Xx")
        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "cases_import:api-caseimportaction-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data={
                    "action": CaseImportAction.ACTION_DELETE,
                    "state": CaseImportAction.STATE_DRAFT,
                    "payload": payload,
                },
                format="json",
                **extra,
            )
        self.assertEqual(response.status_code, 400, response.content)

        self.assertEqual(CaseImportAction.objects.count(), 0)


class CaseImportActionRetrieveTest(ApiViewTestBase):
    """Tests for the **retrieval** of the ``CaseImportAction`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_retrieve_action(self):
        """Test retrieval of an existing action."""
        caseimportaction = CaseImportActionFactory(project=self.project)

        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_import:api-caseimportaction-retrieveupdatedestroy",
                    kwargs={"caseimportaction": caseimportaction.sodar_uuid},
                ),
                format="json",
                **extra,
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json().get("sodar_uuid"), str(caseimportaction.sodar_uuid), response.json()
        )

    def test_retrieve_action_nonexistent(self):
        """Test retrieval of an non-existing action fails."""
        caseimportaction = CaseImportActionFactory(project=self.project)
        caseimportaction.delete()

        extra = self.get_accept_header(None, None)
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "cases_import:api-caseimportaction-retrieveupdatedestroy",
                    kwargs={"caseimportaction": caseimportaction.sodar_uuid},
                ),
                format="json",
                **extra,
            )

        self.assertEqual(response.status_code, 404)


class CaseImportActionUpdateTest(ApiViewTestBase):
    """Tests for the **update** of the ``CaseImportAction`` objects.

    Each tests corresponds to an individual use case.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_update_action_create_as_state_draft_succeeds(self):
        """PATCH action=create state=draft => succeeds"""

    def test_update_action_create_as_state_submitted_succeeds(self):
        """PATCH action=create state=submitted => succeeds, triggers job"""

    def test_update_action_create_as_state_other_fails(self):
        """PATCH action=create state=<other> => fails"""

    def test_update_action_update_as_state_draft_succeeds(self):
        """PATCH action=update state=update => succeeds"""

    def test_update_action_update_as_state_submitted_succeeds(self):
        """PATCH action=update state=submitted => succeeds, triggers job"""

    def test_update_action_create_as_state_other_fails(self):
        """PATCH action=update state=<other> => fail"""

    def test_update_action_as_state_submitted_fails_same_name(self):
        """PATCH action=create state=draft name=<collision> => fails"""

    def test_update_action_as_state_submitted_fails_invalid_payload(self):
        """PATCH action=create state=draft payload=<invalid> => fails"""


class CaseImportActionUpdateTest(ApiViewTestBase):
    """Tests for the **deletion** of the ``CaseImportAction`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_delete_action_create_state_draft(self):
        """DELETE action=create state=draft => succeeds"""

    def test_delete_action_create_state_other(self):
        """DELETE action=create state=<other> => fails"""

    def test_delete_action_update_state_draft(self):
        """DELETE action=update state=draft => succeeds"""

    def test_delete_action_create_state_other(self):
        """DELETE action=update state=<other> => fails"""

    def test_delete_action_delete_state_draft(self):
        """DELETE action=delete state=draft => succeeds"""

    def test_delete_action_delete_state_other(self):
        """DELETE action=delete state=<other> => fails"""
