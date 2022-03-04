"""Tests for ``variants.models``."""
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

from django.conf import settings
from projectroles.models import Project, SODAR_CONSTANTS

from variants.tests.factories import (
    SmallVariantFlagsFactory,
    ProjectFactory,
    SmallVariantFactory,
    CaseWithVariantSetFactory,
)
from test_plus.test import TestCase

from ..models import (
    SmallVariantFlags,
    SmallVariantSet,
    cleanup_variant_sets,
    SmallVariant,
    Case,
    clear_old_kiosk_cases,
)


class TestSmallVariantFlags(TestCase):
    """Basic tests for the ``SmallVariantFlags`` class."""

    def testCreate(self):
        self.assertEquals(SmallVariantFlags.objects.count(), 0)
        SmallVariantFlagsFactory()
        self.assertEquals(SmallVariantFlags.objects.count(), 1)


class TestCleanupVariantSets(TestCase):
    def setUp(self):
        self.superuser = self.make_user("superuser")
        _, self.variant_set_active_above_thres, _ = CaseWithVariantSetFactory.get(
            "small", state="active"
        )
        self.variant_set_active_above_thres.date_created = datetime.now() - timedelta(hours=1)
        self.variant_set_active_above_thres.save()
        _, self.variant_set_inactive_above_thres, _ = CaseWithVariantSetFactory.get(
            "small", state="importing"
        )
        self.variant_set_inactive_above_thres.date_created = datetime.now() - timedelta(hours=2)
        self.variant_set_inactive_above_thres.save()
        _, self.variant_set_active_below_thres, _ = CaseWithVariantSetFactory.get(
            "small", state="active"
        )
        self.variant_set_active_below_thres.date_created = datetime.now() - timedelta(hours=13)
        self.variant_set_active_below_thres.save()
        _, self.variant_set_inactive_below_thres, _ = CaseWithVariantSetFactory.get(
            "small", state="importing"
        )
        self.variant_set_inactive_below_thres.date_created = datetime.now() - timedelta(hours=14)
        self.variant_set_inactive_below_thres.save()

    def test_cleanup_variant_sets(self):
        self.assertEqual(SmallVariantSet.objects.all().count(), 4)
        cleanup_variant_sets()
        variant_sets = SmallVariantSet.objects.all().order_by("-date_created")
        self.assertEqual(variant_sets.count(), 3)
        self.assertEqual(variant_sets[0].id, self.variant_set_active_above_thres.id)
        self.assertEqual(variant_sets[1].id, self.variant_set_inactive_above_thres.id)
        self.assertEqual(variant_sets[2].id, self.variant_set_active_below_thres.id)


class TestClearOldKioskCases(TestCase):
    def setUp(self):
        self.superuser = self.make_user("kiosk_user")
        self.category = ProjectFactory(
            title=settings.KIOSK_CAT, type=SODAR_CONSTANTS["PROJECT_TYPE_CATEGORY"]
        )
        self.project_above_thres = ProjectFactory(
            title=settings.KIOSK_PROJ_PREFIX + str(uuid.uuid4()), parent=self.category
        )
        self.project_below_thres = ProjectFactory(
            title=settings.KIOSK_PROJ_PREFIX + str(uuid.uuid4()), parent=self.category
        )
        self.case_above_thres, self.variant_set_above_thres, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project_above_thres
        )
        self.case_below_thres, self.variant_set_below_thres, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project_below_thres
        )
        self.case_below_thres.date_created = datetime.now() - timedelta(weeks=9)
        self.case_below_thres.save()
        self.small_vars_above_thres = SmallVariantFactory.create_batch(
            3, variant_set=self.variant_set_above_thres
        )
        self.small_vars_below_thres = SmallVariantFactory.create_batch(
            3, variant_set=self.variant_set_below_thres
        )

    @patch("django.conf.settings.KIOSK_MODE", True)
    def test_clear_old_kiosk_cases(self):
        self.assertEqual(Project.objects.filter(parent=self.category).count(), 2)
        self.assertEqual(Case.objects.all().count(), 2)
        self.assertEqual(SmallVariant.objects.all().count(), 6)
        clear_old_kiosk_cases()
        projects = Project.objects.filter(parent=self.category)
        cases = Case.objects.all().order_by("-date_created")
        self.assertEqual(projects.count(), 1)
        self.assertEqual(cases.count(), 1)
        self.assertEqual(SmallVariant.objects.all().count(), 3)
        self.assertEqual(projects[0].id, self.project_above_thres.id)
        self.assertEqual(cases[0].id, self.case_above_thres.id)
