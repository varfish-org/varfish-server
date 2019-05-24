"""Tests for the models in ``svs``."""

from django.test import TestCase

from svs.models import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    StructuralVariantComment,
    StructuralVariantFlags,
)
from .factories import (
    StructuralVariantFactory,
    StructuralVariantGeneAnnotationFactory,
    StructuralVariantFlagsFactory,
    StructuralVariantCommentFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
        self.maxDiff = None  # show full diff

    def testStructuralVariant(self):
        obj = StructuralVariantFactory()
        obj.save(force_update=True)
        self.assertEqual(1, StructuralVariant.objects.count())

    def testStructuralVariantGeneAnnotation(self):
        obj = StructuralVariantGeneAnnotationFactory()
        obj.save(force_update=True)
        self.assertEqual(1, StructuralVariantGeneAnnotation.objects.count())

    def testStructuralVariantComment(self):
        obj = StructuralVariantCommentFactory()
        obj.save(force_update=True)
        self.assertEqual(1, StructuralVariantComment.objects.count())

    def testStructuralVariantFlags(self):
        obj = StructuralVariantFlagsFactory()
        obj.save(force_update=True)
        self.assertEqual(1, StructuralVariantFlags.objects.count())
