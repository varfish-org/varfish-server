from django.urls import reverse

from seqmeta.tests.factories import TargetBedFileFactory
from variants.tests.helpers import TestViewsBase


class IndexViewTest(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.targetbedfile = TargetBedFileFactory()
        self.enrichmentkit = self.targetbedfile.enrichmentkit

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("seqmeta:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object_list"].count(), 1)


class EnrichmentKitListViewTest(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.targetbedfile = TargetBedFileFactory()
        self.enrichmentkit = self.targetbedfile.enrichmentkit

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("seqmeta:enrichmentkit-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object_list"].count(), 1)


class EnrichmentKitDetailView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.targetbedfile = TargetBedFileFactory()
        self.enrichmentkit = self.targetbedfile.enrichmentkit

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "seqmeta:enrichmentkit-detail",
                    kwargs={"enrichmentkit": self.enrichmentkit.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.enrichmentkit)
