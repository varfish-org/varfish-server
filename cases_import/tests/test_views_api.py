"""Tests for the functionality of the API views.

This module uses the "lowermost" role that allows to make the changes and focuses on the actual
functionality.
"""

from variants.tests.helpers import ApiViewTestBase


class CaseImportActionListTest(ApiViewTestBase):
    """Test listing ``CaseImportAction`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_list_empty(self):
        """GET on empty list"""

    def test_list_non_empty(self):
        """GET on non-empty list"""


class CaseImportActionCreateTest(ApiViewTestBase):
    """Tests for the **creation** of the ``CaseImportAction`` objects.

    Each tests corresponds to an individual use case.
    """

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_create_action_create_as_state_draft_succeeds(self):
        """POST action=create state=draft => succeeds"""

    def test_create_action_create_as_state_submitted_succeeds(self):
        """POST action=create state=submitted => succeeds, triggers job"""

    def test_create_action_create_as_state_other_fails(self):
        """POST action=create state=<other> => fails"""

    def test_create_action_create_as_state_submitted_fails_same_name(self):
        """POST action=create state=draft name=<collision> => fails"""

    def test_create_action_create_as_state_submitted_fails_invalid_payload(self):
        """POST action=create state=draft payload=<invalid> => fails"""

    def test_create_action_update_as_state_draft_succeeds(self):
        """POST action=update state=draft => succeeds"""

    def test_create_action_update_as_state_submitted_succeeds(self):
        """POST action=update state=submitted => succeeds, triggers job"""

    def test_create_action_update_as_state_other_fails(self):
        """POST action=update state=<other> => fail"""

    def test_create_action_create_as_state_submitted_fails_non_existing(self):
        """POST action=create state=draft name=<non-existing> => fails"""

    def test_create_action_create_as_state_submitted_fails_invalid_payload(self):
        """POST action=create state=draft payload=<invalid> => fails"""

    def test_create_action_delete_as_state_draft_succeeds(self):
        """POST action=delete state=draft => succeeds"""

    def test_create_action_delete_as_state_submitted_succeeds(self):
        """POST action=delete state=draft => succeeds, triggers job"""

    def test_create_action_create_as_state_submitted_fails_non_existing(self):
        """POST action=create state=draft name=<non-existing> => fails"""


class CaseImportActionRetrieveTest(ApiViewTestBase):
    """Tests for the **retrieval** of the ``CaseImportAction`` objects."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def test_retrieve_action(self):
        """Test retrieval of an existing action."""

    def test_retrieve_action_nonexistent(self):
        """Test retrieval of an non-existing action fails."""


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
