"""Test models and factories"""

from test_plus.test import TestCase

from genepanels.models import (
    GenePanel,
    GenePanelCategory,
    GenePanelEntry,
    GenePanelState,
    expand_panels_in_gene_list,
)
from genepanels.tests.factories import (
    GenePanelCategoryFactory,
    GenePanelEntryFactory,
    GenePanelFactory,
)


class TestGenePanelCategory(TestCase):
    def test_create(self):
        self.assertEqual(GenePanelCategory.objects.count(), 0)
        GenePanelCategoryFactory()
        self.assertEqual(GenePanelCategory.objects.count(), 1)

    def test_get_absolute_url(self):
        category = GenePanelCategoryFactory()
        self.assertEqual(
            category.get_absolute_url(), f"/genepanels/category/{category.sodar_uuid}/"
        )

    def test_str(self):
        category = GenePanelCategoryFactory()
        self.assertEqual(f"Category '{category.title}'", category.__str__())


class TestGenePanel(TestCase):
    def test_create(self):
        self.assertEqual(GenePanel.objects.count(), 0)
        GenePanelFactory()
        self.assertEqual(GenePanel.objects.count(), 1)


class TestGenePanelEntry(TestCase):
    def test_create(self):
        self.assertEqual(GenePanelEntry.objects.count(), 0)
        GenePanelEntryFactory()
        self.assertEqual(GenePanelEntry.objects.count(), 1)

    def test_get_absolute_url(self):
        panel = GenePanelFactory()
        self.assertEqual(panel.get_absolute_url(), f"/genepanels/panel/{panel.sodar_uuid}/")

    def test_get_hgnc_list(self):
        panel = GenePanelFactory()
        entry1 = GenePanelEntryFactory(panel=panel)
        entry2 = GenePanelEntryFactory(panel=panel)
        self.assertEqual(panel.get_hgnc_list(), [entry1.hgnc_id, entry2.hgnc_id])


class TestExpandPanelsInGeneList(TestCase):
    def setUp(self):
        super().setUp()
        self.panel = GenePanelFactory(state=GenePanelState.ACTIVE.value)
        self.entry = GenePanelEntryFactory(panel=self.panel)

    def test_call_empty(self):
        actual = expand_panels_in_gene_list([])
        expected = []
        self.assertEqual(expected, actual)

    def test_call_gene_only(self):
        actual = expand_panels_in_gene_list(["dummy"])
        expected = ["dummy"]
        self.assertEqual(expected, actual)

    def test_call_panel_only(self):
        actual = expand_panels_in_gene_list(["GENEPANEL:" + self.panel.identifier])
        expected = [self.entry.hgnc_id]
        self.assertEqual(expected, actual)

    def test_call_mixed(self):
        actual = expand_panels_in_gene_list(
            ["dummy", "GENEPANEL:" + self.panel.identifier, "dummy2"]
        )
        expected = ["dummy", self.entry.hgnc_id, "dummy2"]
        self.assertEqual(expected, actual)

    def test_call_invalid_panel(self):
        self.panel.state = GenePanelState.RETIRED.value
        self.panel.save()
        with self.assertRaises(ValueError):
            expand_panels_in_gene_list(["GENEPANEL:" + self.panel.identifier])
