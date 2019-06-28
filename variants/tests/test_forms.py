"""Tests for the ``forms`` module."""

from django.test import TestCase

from clinvar.tests.factories import ClinvarFormDataFactory
from variants.tests.factories import SmallVariantSetFactory, SmallVariantFactory
from ..forms import ClinvarForm

# TODO: test the big query form
#
# class TestFilterForm(TestCase):
#
#     def testFails(self):
#         self.fail("Write me!")


class TestClinvarForm(TestCase):
    """Tests for ClinvarForm"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.donor_names = [m["patient"] for m in self.variant_set.case.pedigree]
        self.small_var = SmallVariantFactory(in_clinvar=True, variant_set=self.variant_set)
        self.maxDiff = None

    def testSubmitDefaults(self):
        """Test submission with defaults."""
        form_data = vars(ClinvarFormDataFactory(names=self.donor_names))
        form = ClinvarForm(form_data, case=self.variant_set.case)
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data, form_data)
