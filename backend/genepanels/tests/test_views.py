from unittest.mock import patch

from django.urls import reverse
from parameterized import parameterized
from requests_mock import Mocker

from genepanels.models import GenePanel, GenePanelCategory, GenePanelEntry, GenePanelState
from genepanels.tests.factories import (
    GenePanelCategoryFactory,
    GenePanelEntryFactory,
    GenePanelFactory,
)
from variants.tests.helpers import TestViewsBase

ANNONARS_GENE_RESPONSE = {
    "TTN": {
        "hgnc_id": "HGNC:12403",
        "symbol": "TTN",
        "name": "titin",
        "alias_symbol": ["CMPD4", "FLJ32040", "TMD", "CMH9", "LGMD2J", "MYLK5"],
        "alias_name": [],
        "ensembl_gene_id": "ENSG00000155657",
        "ncbi_gene_id": "7273",
    },
    "GBA1": {
        "hgnc_id": "HGNC:4177",
        "symbol": "GBA1",
        "name": "glucosylceramidase beta 1",
        "alias_symbol": [],
        "alias_name": ["glucocerebrosidase"],
        "ensembl_gene_id": "ENSG00000177628",
        "ncbi_gene_id": "2629",
    },
}


class AnnonarsMockerMixin:
    def _set_annonars_mocker_NONEXISTENT(self, mock_):
        mock_.get(
            "https://annonars.com/genes/lookup?q=TTN,GBA1,NONEXISTENT",
            status_code=200,
            json={
                "genes": {**ANNONARS_GENE_RESPONSE, "NONEXISTENT": None},
            },
        )

    def _set_annonars_mocker(self, mock_):
        mock_.get(
            "https://annonars.com/genes/lookup?q=TTN,GBA1",
            status_code=200,
            json={
                "genes": {**ANNONARS_GENE_RESPONSE},
            },
        )


class IndexViewTest(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory()

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("genepanels:index"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])
        self.assertEquals(response.context["show_retired"], False)


class GenePanelCategoryListView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory()
        self.category = self.panel.category

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("genepanels:category-list"))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])
        self.assertEquals(response.context["show_retired"], False)

    def test_render_show_retired(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("genepanels:category-list"), {"show_retired": "1"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object_list"])
        self.assertEquals(response.context["show_retired"], True)


class GenePanelCategoryCreateView(TestViewsBase):
    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("genepanels:category-create"))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        self.assertEqual(GenePanelCategory.objects.count(), 0)

        post_data = {
            "title": "XXX",
            "description": "ddd",
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("genepanels:category-create"), post_data)

        self.assertEqual(GenePanelCategory.objects.count(), 1)

        self.assertEqual(response.status_code, 302)
        latest_category = GenePanelCategory.objects.all()[0]
        self.assertEqual(
            response.url,
            reverse("genepanels:category-detail", kwargs={"category": latest_category.sodar_uuid}),
        )

        self.assertEqual(GenePanelCategory.objects.count(), 1)


class GenePanelCategoryUpdateView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory()
        self.category = self.panel.category

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:category-update",
                    kwargs={"category": self.category.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"])

    def test_update(self):
        self.assertEqual(GenePanelCategory.objects.count(), 1)

        post_data = {
            "title": "XXX",
            "description": "ddd",
        }

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:category-update",
                    kwargs={"category": self.category.sodar_uuid},
                ),
                post_data,
            )

        self.assertEqual(response.status_code, 302)
        latest_category = GenePanelCategory.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse("genepanels:category-detail", kwargs={"category": latest_category.sodar_uuid}),
        )

        self.assertEqual(GenePanelCategory.objects.count(), 1)
        self.category.refresh_from_db()
        for key in ("title", "description"):
            self.assertEqual(getattr(self.category, key), post_data[key])


class GenePanelCategoryDeleteView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.category = GenePanelCategoryFactory()

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:category-delete",
                    kwargs={"category": self.category.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_delete(self):
        # Assert precondition
        self.assertEqual(GenePanelCategory.objects.all().count(), 1)

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:category-delete",
                    kwargs={"category": self.category.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse("genepanels:category-list"))

        # Assert postconditions
        self.assertEqual(GenePanelCategory.objects.all().count(), 0)


class GenePanelCreateView(AnnonarsMockerMixin, TestViewsBase):
    def setUp(self):
        super().setUp()
        self.category = GenePanelCategoryFactory()

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("genepanels:genepanel-create"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, f'<option value="{self.category.sodar_uuid}" selected>')

    def test_render_prefill_category(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse("genepanels:genepanel-create"), {"category": str(self.category.sodar_uuid)}
            )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'<option value="{self.category.sodar_uuid}" selected>')

    def test_create(self):
        self.assertEqual(GenePanel.objects.count(), 0)

        post_data = {
            "identifier": "xxx",
            "title": "XXX",
            "description": "ddd",
            "version_major": 1,
            "version_minor": 1,
            "category": str(self.category.sodar_uuid),
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("genepanels:genepanel-create"), post_data)

        self.assertEqual(GenePanel.objects.count(), 1)

        self.assertEqual(response.status_code, 302)
        latest_panel = GenePanel.objects.all()[0]
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": latest_panel.sodar_uuid}),
        )

        self.assertEqual(GenePanel.objects.count(), 1)

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_create_with_gene_list(self, mock):
        self.assertEqual(GenePanel.objects.count(), 0)
        self._set_annonars_mocker(mock)

        post_data = {
            "identifier": "xxx",
            "title": "XXX",
            "description": "ddd",
            "version_major": 1,
            "version_minor": 1,
            "category": str(self.category.sodar_uuid),
            "genes": "TTN\nGBA1",
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("genepanels:genepanel-create"), post_data)

        self.assertEqual(GenePanel.objects.count(), 1)

        self.assertEqual(response.status_code, 302)
        latest_panel = GenePanel.objects.all()[0]
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": latest_panel.sodar_uuid}),
        )

        self.assertEqual(GenePanel.objects.count(), 1)

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_create_with_gene_list_including_nonexistent_gene(self, mock):
        self.assertEqual(GenePanel.objects.count(), 0)
        self._set_annonars_mocker_NONEXISTENT(mock)

        post_data = {
            "identifier": "xxx",
            "title": "XXX",
            "description": "ddd",
            "version_major": 1,
            "version_minor": 1,
            "category": str(self.category.sodar_uuid),
            "genes": "TTN\nGBA1\nNONEXISTENT",
        }

        with self.login(self.superuser):
            response = self.client.post(reverse("genepanels:genepanel-create"), post_data)

        self.assertEqual(GenePanel.objects.count(), 0)

        self.assertEqual(response.status_code, 200)
        self.assertRegex(
            response.content.decode("utf-8"),
            r'<p id="error_1_id_genes" class="text-danger help-block">NONEXISTENT</p>',
        )


class GenePanelUpdateView(AnnonarsMockerMixin, TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.DRAFT.value)
        self.category = GenePanelCategoryFactory()

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-update",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context["object"])

    @patch("django.conf.settings.VARFISH_BACKEND_URL_ANNONARS", "https://annonars.com")
    @Mocker()
    def test_update(self, mock):
        self.assertEqual(GenePanel.objects.count(), 1)
        self._set_annonars_mocker(mock)

        post_data = {
            "identifier": "xxx",
            "title": "XXX",
            "description": "ddd",
            "version_major": 2,
            "version_minor": 2,
            "category": str(self.category.sodar_uuid),
            "genes": "TTN\nGBA1",
        }

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-update",
                    kwargs={"panel": self.panel.sodar_uuid},
                ),
                post_data,
            )

        self.assertEqual(response.status_code, 302)
        latest_panel = GenePanel.objects.order_by("-date_created")[0]
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": latest_panel.sodar_uuid}),
        )

        self.assertEqual(GenePanel.objects.count(), 1)
        self.panel.refresh_from_db()
        for key in ("identifier", "title", "description", "version_major", "version_minor"):
            self.assertEqual(getattr(self.panel, key), post_data[key])
        self.assertEqual(self.panel.category, self.category)


class GenePanelDeleteView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.DRAFT.value)
        self.category = self.panel.category

    def test_get_draft_state(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-delete",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GenePanel.objects.count(), 1)

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_get_non_draft_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-delete",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.assertEqual(GenePanel.objects.count(), 1)

    def test_post_draft_state(self):
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-delete",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:category-list"),
        )
        self.assertEqual(GenePanel.objects.count(), 0)

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_post_non_draft_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-delete",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.assertEqual(GenePanel.objects.count(), 1)


class GenePanelReleaseView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.DRAFT.value, version_minor=2)
        self.category = self.panel.category
        self.old_panel = GenePanelFactory(
            state=GenePanelState.ACTIVE.value,
            identifier=self.panel.identifier,
            category=self.panel.category,
        )

    def test_get_draft_state(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-release",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_get_non_draft_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-release",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )

    def test_post_draft_state(self):
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-release",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, GenePanelState.ACTIVE.value)
        self.old_panel.refresh_from_db()
        self.assertEqual(self.old_panel.state, GenePanelState.RETIRED.value)

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_post_non_draft_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-release",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, state)
        self.old_panel.refresh_from_db()
        self.assertEqual(self.old_panel.state, GenePanelState.ACTIVE.value)


class GenePanelRetireView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.ACTIVE.value, version_minor=2)
        self.category = self.panel.category

    def test_get_active_state(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-retire",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            [GenePanelState.DRAFT.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_get_non_active_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-retire",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )

    def test_post_active_state(self):
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-retire",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, GenePanelState.RETIRED.value)

    @parameterized.expand(
        [
            [GenePanelState.DRAFT.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_post_non_active_state(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-retire",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, state)


class GenePanelCopyAsDraftView(TestViewsBase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.ACTIVE.value, version_minor=2)
        self.category = self.panel.category
        self.entry = GenePanelEntryFactory(panel=self.panel)

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_get_non_draft(self, state):
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-copy-as-draft",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)

    def test_get_draft_state(self):
        self.panel.state = GenePanelState.DRAFT.value
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "genepanels:genepanel-copy-as-draft",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )

    @parameterized.expand(
        [
            [GenePanelState.ACTIVE.value],
            [GenePanelState.RETIRED.value],
        ]
    )
    def test_post_non_draft_state(self, state):
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(GenePanelEntry.objects.count(), 1)
        self.panel.state = state
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-copy-as-draft",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(GenePanel.objects.count(), 2)
        new_panel = GenePanel.objects.order_by("-date_created")[0]
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": new_panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, state)
        self.assertEqual(new_panel.state, GenePanelState.DRAFT.value)
        self.assertEqual(GenePanelEntry.objects.count(), 2)

    def test_post_draft_state(self):
        self.assertEqual(GenePanel.objects.count(), 1)
        self.panel.state = GenePanelState.DRAFT.value
        self.panel.save()

        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "genepanels:genepanel-copy-as-draft",
                    kwargs={"panel": self.panel.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("genepanels:genepanel-detail", kwargs={"panel": self.panel.sodar_uuid}),
        )
        self.panel.refresh_from_db()
        self.assertEqual(self.panel.state, GenePanelState.DRAFT.value)
        self.assertEqual(GenePanel.objects.count(), 1)
        self.assertEqual(GenePanelEntry.objects.count(), 1)
