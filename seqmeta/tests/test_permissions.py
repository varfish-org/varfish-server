from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase

from seqmeta.tests.factories import EnrichmentKitFactory


class UsersMixin:
    def setUp(self):
        super().setUp()
        self.users_edit = [
            self.superuser,
        ]
        self.users_view = [
            self.user_no_roles,
            self.owner_as_cat.user,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]
        self.users_bad = [
            self.anonymous,
        ]


class TestSeqmetaView(UsersMixin, TestProjectPermissionBase):
    def test_index(self):
        url = reverse("seqmeta:index")
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)

    def test_enrichmentkit_list(self):
        url = reverse("seqmeta:enrichmentkit-list")
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)

    def test_enrichmentkit_detail(self):
        kit = EnrichmentKitFactory()
        url = reverse("seqmeta:enrichmentkit-detail", kwargs={"enrichmentkit": str(kit.sodar_uuid)})
        self.assert_response(url, self.users_edit + self.users_view, 200)
        self.assert_response(url, self.users_bad, 302)
