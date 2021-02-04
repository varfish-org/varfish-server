"""Tests for ``variants.templatetags``."""

from geneinfo.tests.factories import HpoFactory, HpoNameFactory
from test_plus.test import TestCase

from variants.templatetags import variants_tags


class TestGetTermDescription(TestCase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    def testGetHpo(self):
        hpo_name = HpoNameFactory()
        self.assertEquals(variants_tags.get_term_description(hpo_name.hpo_id), hpo_name.name)

    def testGetOrphanet(self):
        hpo = HpoFactory(database_id="ORPHA:123456", name="Some name")
        self.assertEquals(variants_tags.get_term_description(hpo.database_id), hpo.name)

    def testGetOmim(self):
        hpo = HpoFactory(database_id="MIM:123456", name="Some name")
        self.assertEquals(variants_tags.get_term_description(hpo.database_id), hpo.name)

    def testGetInvalid(self):
        self.assertIsNone(variants_tags.get_term_description("XXX"))
