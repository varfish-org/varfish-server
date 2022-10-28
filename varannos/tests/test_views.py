from django.urls import reverse

from varannos.tests.factories import VarAnnoSetFactory
from variants.tests.helpers import TestViewsBase


class TestVarAnnoSetListView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.varannoset = VarAnnoSetFactory(project=self.project)

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse("varannos:varannoset-list", kwargs={"project": self.project.sodar_uuid})
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])


class TestVarAnnoSetDetailView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.varannoset = VarAnnoSetFactory(project=self.project)

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "varannos:varannoset-detail", kwargs={"varannoset": self.varannoset.sodar_uuid}
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"])
