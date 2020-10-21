"""Tests for the models in ``regmaps``."""

from django.test import TestCase

from ..models import RegMapCollection, RegMap, RegElementType, RegElement, RegInteraction
from .factories import (
    RegMapCollectionFactory,
    RegMapFactory,
    RegElementTypeFactory,
    RegElementFactory,
    RegInteractionFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
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
