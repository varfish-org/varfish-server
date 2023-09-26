"""Tests for the models in ``regmaps``."""

from django.test import TestCase

from ..models import RegElement, RegElementType, RegInteraction, RegMap, RegMapCollection
from .factories import (
    RegElementFactory,
    RegElementTypeFactory,
    RegInteractionFactory,
    RegMapCollectionFactory,
    RegMapFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testRegMapCollection(self):
        obj = RegMapCollectionFactory()
        obj.save(force_update=True)
        self.assertEqual(1, RegMapCollection.objects.count())

    def testRegMap(self):
        obj = RegMapFactory()
        obj.save(force_update=True)
        self.assertEqual(1, RegMap.objects.count())

    def testRegElementType(self):
        obj = RegElementTypeFactory()
        obj.save(force_update=True)
        self.assertEqual(1, RegElementType.objects.count())

    def testRegElement(self):
        obj = RegElementFactory()
        obj.save(force_update=True)
        self.assertEqual(1, RegElement.objects.count())

    def testRegInteraction(self):
        obj = RegInteractionFactory()
        obj.save(force_update=True)
        self.assertEqual(1, RegInteraction.objects.count())
