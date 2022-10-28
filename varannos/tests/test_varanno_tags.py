from test_plus import TestCase

from varannos.templatetags.varannos_tags import add_chr_prefix, get_details_varannosets
from varannos.tests.factories import VarAnnoSetFactory
from variants.tests.factories import ProjectFactory


class TestTemplateTags(TestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()

    def test_details_varannosets(self):
        for i in range(10):
            VarAnnoSetFactory(project=self.project)
        result = get_details_varannosets(self.project)
        self.assertEqual(len(result), 5)

    def test_add_chr_prefix_5(self):
        self.assertEqual(add_chr_prefix("5"), "chr5")

    def test_add_chr_prefix_chr5(self):
        self.assertEqual(add_chr_prefix("chr5"), "chr5")
