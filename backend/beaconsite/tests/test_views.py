"""Tests for UI views in the beaconsite app"""

from Crypto.PublicKey import RSA
from django.urls import reverse

from beaconsite.models import Consortium, Site
from variants.tests.helpers import TestViewsBase


class TestIndexView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("beaconsite:index"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["consortium_list"])
        self.assertIsNotNone(response.context["site_list"])
        self.assertEqual(response.context["consortium_list"][0].pk, self.consortium.pk)
        self.assertEqual(response.context["site_list"][0].pk, self.site.pk)


class TestConsortiumListView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("beaconsite:consortium-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])
        self.assertEqual(response.context["object_list"][0].pk, self.consortium.pk)


class TestConsortiumCreateView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("beaconsite:consortium-create"))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.assertEqual(Consortium.objects.count(), 1)

        post_data = {
            "title": "XXX",
            "identifier": "xxx",
            "description": "ddd",
            "state": Consortium.ENABLED,
            "sites": [self.site.pk],
            "projects": [self.project.pk],
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("beaconsite:consortium-create"), post_data)

        self.assertEqual(response.status_code, 302)
        latest_consortium = Consortium.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse(
                "beaconsite:consortium-detail", kwargs={"consortium": latest_consortium.sodar_uuid}
            ),
        )

        self.assertEqual(Consortium.objects.count(), 2)


class TestConsortiumUpdateView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "beaconsite:consortium-update",
                    kwargs={"consortium": self.consortium.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"])

    def test_update(self):
        self.assertEqual(Consortium.objects.count(), 1)

        post_data = {
            "title": "XXX",
            "identifier": "xxx",
            "description": "ddd",
            "state": Consortium.ENABLED,
            "sites": [self.site.pk],
            "projects": [self.project.pk],
        }

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "beaconsite:consortium-update",
                    kwargs={"consortium": self.consortium.sodar_uuid},
                ),
                post_data,
            )

        self.assertEqual(response.status_code, 302)
        latest_consortium = Consortium.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse(
                "beaconsite:consortium-detail", kwargs={"consortium": latest_consortium.sodar_uuid}
            ),
        )

        self.assertEqual(Consortium.objects.count(), 1)
        self.consortium.refresh_from_db()
        for key in ("title", "identifier", "description", "state"):
            self.assertEqual(getattr(self.consortium, key), post_data[key])
        self.assertEqual([self.site.pk], [s.pk for s in self.consortium.sites.all()])
        self.assertEqual([self.project.pk], [p.pk for p in self.consortium.projects.all()])


class TestConsortiumDeleteView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "beaconsite:consortium-delete",
                    kwargs={"consortium": self.consortium.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_delete(self):
        # Assert precondition
        self.assertEqual(Consortium.objects.all().count(), 1)

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "beaconsite:consortium-delete",
                    kwargs={"consortium": self.consortium.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("beaconsite:consortium-list"))

        # Assert postconditions
        self.assertEqual(Consortium.objects.all().count(), 0)


class TestSiteListView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("beaconsite:site-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])
        self.assertEqual(response.context["object_list"][0].pk, self.site.pk)


class TestSiteCreateView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("beaconsite:site-create"))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.assertEqual(Site.objects.count(), 1)

        rsa_key = RSA.generate(2048)
        public_key = rsa_key.public_key().export_key("PEM").decode("ascii")
        post_data = {
            "title": "XXX",
            "identifier": "xxx",
            "description": "ddd",
            "state": Site.ENABLED,
            "role": Site.REMOTE,
            "entrypoint_url": "http://site.example.com",
            "key_algo": Site.RSA_SHA256,
            "public_key": public_key,
            "consortia": [self.consortium.pk],
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("beaconsite:site-create"), post_data)

        self.assertEqual(response.status_code, 302)
        latest_site = Site.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse("beaconsite:site-detail", kwargs={"site": latest_site.sodar_uuid}),
        )

        self.assertEqual(Site.objects.count(), 2)


class TestSiteUpdateView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "beaconsite:site-update",
                    kwargs={"site": self.site.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"])

    def test_update(self):
        self.assertEqual(Site.objects.count(), 1)

        rsa_key = RSA.generate(2048)
        public_key = rsa_key.public_key().export_key("PEM").decode("ascii")
        post_data = {
            "title": "XXX",
            "identifier": "xxx",
            "description": "ddd",
            "state": Site.ENABLED,
            "role": Site.REMOTE,
            "entrypoint_url": "http://site.example.com",
            "key_algo": Site.RSA_SHA256,
            "public_key": public_key,
            "consortia": [self.consortium.pk],
        }

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "beaconsite:site-update",
                    kwargs={"site": self.site.sodar_uuid},
                ),
                post_data,
            )

        self.assertEqual(response.status_code, 302)
        latest_site = Site.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse("beaconsite:site-detail", kwargs={"site": latest_site.sodar_uuid}),
        )

        self.assertEqual(Site.objects.count(), 1)
        self.site.refresh_from_db()
        keys = (
            "title",
            "identifier",
            "description",
            "state",
            "role",
            "entrypoint_url",
            "key_algo",
            "public_key",
        )
        for key in keys:
            self.assertEqual(getattr(self.site, key), post_data[key])
        self.assertEqual([self.consortium.pk], [s.pk for s in self.site.consortia.all()])


class TestSiteDeleteView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "beaconsite:site-delete",
                    kwargs={"site": self.site.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_delete(self):
        # Assert precondition
        self.assertEqual(Site.objects.all().count(), 1)

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "beaconsite:site-delete",
                    kwargs={"site": self.site.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("beaconsite:site-list"))

        # Assert postconditions
        self.assertEqual(Site.objects.all().count(), 0)
