"""Tests for the ``forms`` module."""

from django.test import TestCase

from clinvar.tests.factories import ClinvarFormDataFactory
from variants.tests.factories import SmallVariantSetFactory, FormDataFactory
from ..forms import ClinvarForm, FilterForm


class TestFormBase(TestCase):
    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.maxDiff = None


class TestClinvarForm(TestFormBase):
    """Tests for ClinvarForm"""

    def testSubmitDefaults(self):
        """Test submission with defaults."""
        form_data = vars(ClinvarFormDataFactory(names=self.variant_set.case.get_members()))
        form = ClinvarForm(form_data, case=self.variant_set.case)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data, form_data)


class TestFilterForm(TestFormBase):
    """Tests for FilterForm."""

    def test_submit_defaults(self):
        form_data = vars(FormDataFactory(names=self.variant_set.case.get_members()))
        form = FilterForm(form_data, case=self.variant_set.case)
        self.assertTrue(form.is_valid())

    def test_genomic_region_range(self):
        form_data = vars(
            FormDataFactory(
                names=self.variant_set.case.get_members(), genomic_region="19:1,000,000-2,000,000"
            )
        )
        form = FilterForm(form_data, case=self.variant_set.case)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["genomic_region"], [("19", 1000000, 2000000)])

    def test_genomic_region_chr(self):
        form_data = vars(
            FormDataFactory(names=self.variant_set.case.get_members(), genomic_region="X")
        )
        form = FilterForm(form_data, case=self.variant_set.case)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["genomic_region"], [("X", None, None)])
