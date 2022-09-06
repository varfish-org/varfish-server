"""Tests for the models in ``svs``."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from svs.models import (
    BackgroundSv,
    BackgroundSvSet,
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    StructuralVariantGeneAnnotation,
    StructuralVariantSet,
    cleanup_variant_sets,
)

from .factories import (
    BackgroundSvFactory,
    BackgroundSvSetFactory,
    StructuralVariantCommentFactory,
    StructuralVariantFactory,
    StructuralVariantFlagsFactory,
    StructuralVariantGeneAnnotationFactory,
    StructuralVariantSetFactory,
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


class TestCleanupVariantSets(TestCase):
    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(state="deleting")
        self.variant_set.date_created = timezone.now() - timedelta(hours=13)
        self.variant_set.save()
        self.sv_anno = StructuralVariantGeneAnnotationFactory(
            variant_set=self.variant_set, sv__variant_set=self.variant_set
        )

    def test(self):
        self.assertEqual(StructuralVariantSet.objects.count(), 1)
        self.assertEqual(StructuralVariant.objects.count(), 1)
        self.assertEqual(StructuralVariantGeneAnnotation.objects.count(), 1)
        cleanup_variant_sets(12)
        self.assertEqual(StructuralVariantSet.objects.count(), 0)
        self.assertEqual(StructuralVariant.objects.count(), 0)
        self.assertEqual(StructuralVariantGeneAnnotation.objects.count(), 0)


class TestBackgroundSv(TestCase):
    def testConstruction(self):
        _variant = BackgroundSvFactory()
        self.assertEqual(BackgroundSvSet.objects.count(), 1)
        self.assertEqual(BackgroundSv.objects.count(), 1)


class TestBackgroundSvSet(TestCase):
    def testConstruction(self):
        _variant_set = BackgroundSvSetFactory()
        self.assertEqual(BackgroundSv.objects.count(), 0)
        self.assertEqual(BackgroundSvSet.objects.count(), 1)
