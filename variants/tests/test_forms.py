"""Tests for the ``forms`` module."""

from django.test import TestCase

from ._fixtures import fixture_setup_case1_simple, CLINVAR_FORM_DEFAULTS
from ..models import Case
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
        fixture_setup_case1_simple()
        self.maxDiff = None

    def testSubmitDefaults(self):
        """Test submission with defaults."""
        form_data = CLINVAR_FORM_DEFAULTS
        form = ClinvarForm(form_data, case=Case.objects.first())
        self.assertTrue(form.is_valid())
        self.assertEquals(form.cleaned_data, form_data)
