from test_plus import TestCase

from varannos.plugins import VariantsDetailsPlugin, VariantsExtendQueryInfoColPlugin
from varannos.tests.factories import VarAnnoSetEntryFactory


class TestVariantsDetailsPlugin(TestCase):
    def setUp(self):
        super().setUp()
        self.plugin = VariantsDetailsPlugin()

    def test_properties(self):
        self.assertEqual(self.plugin.plugin_ordering, 100)

    def test_load_details_one(self):
        varannosetentry = VarAnnoSetEntryFactory()
        result = self.plugin.load_details(
            release=varannosetentry.release,
            chromosome=varannosetentry.chromosome,
            start=varannosetentry.start,
            end=varannosetentry.end,
            reference=varannosetentry.reference,
            alternative=varannosetentry.alternative,
        )
        expected = {
            "content": [
                {"label": "notes", "value": "Here are some notes\nwith multiple lines"},
                {"label": "pathogenicity", "value": "pathogenic"},
            ],
            "help_text": "This card displays variants from the VarAnnos app.",
            "plugin_type": "variant",
            "title": "VarAnnos",
        }
        self.assertDictEqual(result, expected)

    def test_load_details_one(self):
        varannosetentry0 = VarAnnoSetEntryFactory(varannoset__title="Foo")
        _varannosetentry1 = VarAnnoSetEntryFactory(
            varannoset__title="Bar",
            release=varannosetentry0.release,
            chromosome=varannosetentry0.chromosome,
            start=varannosetentry0.start,
            end=varannosetentry0.end,
            reference=varannosetentry0.reference,
            alternative=varannosetentry0.alternative,
        )
        result = self.plugin.load_details(
            release=varannosetentry0.release,
            chromosome=varannosetentry0.chromosome,
            start=varannosetentry0.start,
            end=varannosetentry0.end,
            reference=varannosetentry0.reference,
            alternative=varannosetentry0.alternative,
        )
        expected = {
            "content": [
                {"label": "VarAnno Set", "value": "Foo"},
                {"label": "notes", "value": "Here are some notes\nwith multiple lines"},
                {"label": "pathogenicity", "value": "pathogenic"},
                {"label": "VarAnno Set", "value": "Bar"},
                {"label": "notes", "value": "Here are some notes\nwith multiple lines"},
                {"label": "pathogenicity", "value": "pathogenic"},
            ],
            "help_text": "This card displays variants from the VarAnnos app.",
            "plugin_type": "variant",
            "title": "VarAnnos",
        }

        self.assertDictEqual(result, expected)


class TestVariantsExtendQueryInfoColPlugin(TestCase):
    def setUp(self):
        super().setUp()
        self.plugin = VariantsExtendQueryInfoColPlugin()

    def test_properties(self):
        self.assertEqual(self.plugin.plugin_ordering, 100)
        self.assertEqual(
            self.plugin.columns,
            [
                {
                    "field_name": "varannos_varannosetentry_count",
                    "label": "VarAnnos",
                }
            ],
        )
        self.assertEqual(
            self.plugin.get_extend_query_part_classes(),
            [
                "varannos.queries.ExtendQueryPartsVarAnnosJoin",
            ],
        )
