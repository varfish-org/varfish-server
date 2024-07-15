from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase

from genepanels.models import GenePanelState
from genepanels.tests.factories import GenePanelFactory


class UsersMixin:
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.DRAFT.value)
        self.category = self.panel.category
        self.users_edit = [
            self.superuser,
        ]
        self.users_view = [
            self.user_no_roles,
            self.owner_as_cat.user,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        self.users_bad = [
            self.anonymous,
        ]


class TestGenepanelsView(UsersMixin, TestProjectPermissionBase):
    def test_index(self):
        url = reverse("genepanels:index")
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)

    def test_category_list(self):
        url = reverse("genepanels:category-list")
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)

    def test_category_create(self):
        url = reverse("genepanels:category-create")
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_category_update(self):
        url = reverse(
            "genepanels:category-update", kwargs={"category": str(self.category.sodar_uuid)}
        )
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_category_detail(self):
        url = reverse(
            "genepanels:category-detail", kwargs={"category": str(self.category.sodar_uuid)}
        )
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)

    def test_category_delete(self):
        url = reverse(
            "genepanels:category-delete", kwargs={"category": str(self.category.sodar_uuid)}
        )
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_create(self):
        url = reverse("genepanels:genepanel-create")
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_update(self):
        url = reverse("genepanels:genepanel-update", kwargs={"panel": str(self.panel.sodar_uuid)})
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_delete(self):
        url = reverse("genepanels:genepanel-delete", kwargs={"panel": str(self.panel.sodar_uuid)})
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_copy_as_draft(self):
        self.panel.state = GenePanelState.ACTIVE.value
        self.panel.save()
        url = reverse(
            "genepanels:genepanel-copy-as-draft", kwargs={"panel": str(self.panel.sodar_uuid)}
        )
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_release(self):
        url = reverse("genepanels:genepanel-release", kwargs={"panel": str(self.panel.sodar_uuid)})
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)

    def test_panel_retire(self):
        self.panel.state = GenePanelState.ACTIVE.value
        self.panel.save()
        url = reverse("genepanels:genepanel-retire", kwargs={"panel": str(self.panel.sodar_uuid)})
        self.assert_response(url, self.users_edit, 200)
        self.assert_response(url, self.users_bad + self.users_view, 302)
