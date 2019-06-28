"""Tests for ``variants.models``."""

from variants.tests.factories import SmallVariantFlagsFactory
from test_plus.test import TestCase

from ..models import SmallVariantFlags


class TestSmallVariantFlags(TestCase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    def testCreate(self):
        self.assertEquals(SmallVariantFlags.objects.count(), 0)
        SmallVariantFlagsFactory()
        self.assertEquals(SmallVariantFlags.objects.count(), 1)
