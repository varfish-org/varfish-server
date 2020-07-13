"""Tests for the ``forms`` module."""

from django.test import TestCase

from geneinfo.tests.factories import HpoFactory, HpoNameFactory
from variants.tests.factories import SmallVariantSetFactory, FormDataFactory
from ..forms import FilterForm


class TestFormBase(TestCase):
    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.hponame = HpoNameFactory(hpo_id="HP:0000001")
        self.hpos = [
            HpoFactory(
                database_id="OMIM:000001",
                hpo_id="HP:0000002",
                name="Disease 1;;Alternative Description",
            ),
            HpoFactory(
                database_id="OMIM:000001",
                hpo_id="HP:0000003",
                name="Disease 1;;Alternative Description",
            ),
            HpoFactory(database_id="DECIPHER:1", hpo_id="HP:0000003", name="Disease 2",),
            HpoFactory(database_id="DECIPHER:1", hpo_id="HP:0000004", name="Disease 2",),
            HpoFactory(database_id="ORPHA:1", hpo_id="HP:0000004", name="Disease 3",),
            HpoFactory(database_id="ORPHA:1", hpo_id="HP:0000005", name="Disease 3",),
        ]
        self.maxDiff = None


class TestFilterForm(TestFormBase):
    """Tests for FilterForm."""

    def test_submit_defaults(self):
        form_data = vars(FormDataFactory(names=self.variant_set.case.get_members()))
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())

    def test_genomic_region_range(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(), genomic_region="19:1,000,000-2,000,000"
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["genomic_region"], [("19", 1000000, 2000000)])

    def test_genomic_region_chr(self):
        form_data = vars(
            FormDataFactory(names=self.variant_set.case.get_members(), genomic_region="X")
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["genomic_region"], [("X", None, None)])

    def test_hpo_terms_plain(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(),
                prio_hpo_terms="; ".join([self.hponame.hpo_id]),
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms"], sorted([self.hponame.hpo_id]),
        )
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms_curated"], sorted([self.hponame.hpo_id]),
        )

    def test_hpo_terms_omim_to_hpo_conversion(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(),
                prio_hpo_terms="; ".join([self.hpos[0].database_id]),
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms"], sorted([self.hpos[0].database_id]),
        )
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms_curated"],
            sorted([self.hpos[0].hpo_id, self.hpos[1].hpo_id]),
        )

    def test_hpo_terms_decipher_to_hpo_conversion(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(),
                prio_hpo_terms="; ".join([self.hpos[2].database_id]),
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms"], sorted([self.hpos[2].database_id]),
        )
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms_curated"],
            sorted([self.hpos[2].hpo_id, self.hpos[3].hpo_id]),
        )

    def test_hpo_terms_orpha_to_hpo_conversion(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(),
                prio_hpo_terms="; ".join([self.hpos[4].database_id]),
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms"], sorted([self.hpos[4].database_id]),
        )
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms_curated"],
            sorted([self.hpos[4].hpo_id, self.hpos[5].hpo_id]),
        )

    def test_hpo_terms_mixed(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(),
                prio_hpo_terms="; ".join(
                    [
                        self.hponame.hpo_id,
                        self.hpos[0].database_id,
                        self.hpos[2].database_id,
                        self.hpos[4].database_id,
                    ]
                ),
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case, user=0)
        self.assertTrue(form.is_valid())
        self.assertListEqual(
            form.cleaned_data["prio_hpo_terms"],
            sorted(
                [
                    self.hponame.hpo_id,
                    self.hpos[0].database_id,
                    self.hpos[2].database_id,
                    self.hpos[4].database_id,
                ]
            ),
        )
        self.assertEqual(
            form.cleaned_data["prio_hpo_terms_curated"],
            sorted(
                [
                    self.hponame.hpo_id,
                    self.hpos[0].hpo_id,
                    self.hpos[1].hpo_id,
                    self.hpos[3].hpo_id,
                    self.hpos[5].hpo_id,
                ]
            ),
        )
