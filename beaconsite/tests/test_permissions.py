from django.urls import reverse
from projectroles.tests.test_permissions import TestProjectPermissionBase

from beaconsite.tests.factories import ConsortiumFactory, SiteFactory


class UsersMixin:
    def setUp(self):
        super().setUp()
        self.consortium = ConsortiumFactory()
        self.site = SiteFactory()
        self.good_users = [
            self.superuser,
        ]
        self.bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.owner_as_cat.user,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
            self.guest_as.user,
        ]


class TestIndexView(UsersMixin, TestProjectPermissionBase):
    def test_index(self):
        url = reverse("beaconsite:index")
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)


class TestConsortiumViews(UsersMixin, TestProjectPermissionBase):
    def test_list(self):
        url = reverse("beaconsite:consortium-list")
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_detail(self):
        url = reverse(
            "beaconsite:consortium-detail", kwargs={"consortium": str(self.consortium.sodar_uuid)}
        )
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_update(self):
        url = reverse(
            "beaconsite:consortium-update", kwargs={"consortium": str(self.consortium.sodar_uuid)}
        )
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_delete(self):
        url = reverse(
            "beaconsite:consortium-delete", kwargs={"consortium": str(self.consortium.sodar_uuid)}
        )
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)


class TestSiteViews(UsersMixin, TestProjectPermissionBase):
    def test_list(self):
        url = reverse("beaconsite:site-list")
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_detail(self):
        url = reverse("beaconsite:site-detail", kwargs={"site": str(self.site.sodar_uuid)})
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_update(self):
        url = reverse("beaconsite:site-update", kwargs={"site": str(self.site.sodar_uuid)})
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)

    def test_delete(self):
        url = reverse("beaconsite:site-delete", kwargs={"site": str(self.site.sodar_uuid)})
        self.assert_response(url, self.good_users, 200)
        self.assert_response(url, self.bad_users, 302)
