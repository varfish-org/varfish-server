"""Tests for the models in ``svs``."""

from datetime import timedelta

from django.utils import timezone
from test_plus import TestCase

from svs.models import (
    BackgroundSv,
    BackgroundSvSet,
    FilterSvBgJob,
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    StructuralVariantGeneAnnotation,
    StructuralVariantSet,
    SvQuery,
    SvQueryResultRow,
    SvQueryResultSet,
    cleanup_variant_sets,
)
from svs.tests.factories import (
    BackgroundSvFactory,
    BackgroundSvSetFactory,
    FilterSvBgJobFactory,
    StructuralVariantCommentFactory,
    StructuralVariantFactory,
    StructuralVariantFlagsFactory,
    StructuralVariantGeneAnnotationFactory,
    StructuralVariantSetFactory,
    SvQueryResultRowFactory,
    SvQueryResultSetFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
        super().setUp()
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


class TestFilterSvBgJob(TestCase):
    def testConstruction(self):
        user = self.make_user("superuser")
        _filtersvbgjob = FilterSvBgJobFactory(user=user)
        self.assertEqual(FilterSvBgJob.objects.count(), 1)
        self.assertEqual(SvQuery.objects.count(), 1)


class TestSvQueryResultSet(TestCase):
    def testConstruction(self):
        user = self.make_user("superuser")
        filtersvbgjob = FilterSvBgJobFactory(user=user)
        _svqueryresultset = SvQueryResultSetFactory(svquery=filtersvbgjob.svquery)
        self.assertEqual(SvQueryResultSet.objects.count(), 1)


class TestSvQueryResultRow(TestCase):
    def testConstruction(self):
        user = self.make_user("superuser")
        filtersvbgjob = FilterSvBgJobFactory(user=user)
        svqueryresultset = SvQueryResultSetFactory(svquery=filtersvbgjob.svquery)
        _svqueryresultrow = SvQueryResultRowFactory(svqueryresultset=svqueryresultset)
        self.assertEqual(SvQueryResultRow.objects.count(), 1)
