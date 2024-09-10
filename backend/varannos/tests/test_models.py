"""Test models and factories"""

from datetime import datetime, timedelta

from freezegun import freeze_time
from test_plus.test import TestCase

from varannos.models import VarAnnoSet, VarAnnoSetEntry
from varannos.tests.factories import VarAnnoSetEntryFactory, VarAnnoSetFactory


class TestVarAnnoSet(TestCase):
    def test_create(self):
        self.assertEqual(VarAnnoSet.objects.count(), 0)
        VarAnnoSetFactory()
        self.assertEqual(VarAnnoSet.objects.count(), 1)

    def test_get_absolute_url(self):
        obj = VarAnnoSetFactory()
        self.assertEqual(obj.get_absolute_url(), f"/varannos/varannoset/details/{obj.sodar_uuid}/")

    def test_days_since_modification(self):
        with freeze_time((datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")):
            old_one = VarAnnoSetFactory()
        self.assertEqual(old_one.days_since_modification(), 10)
        new_one = VarAnnoSetFactory(date_modified=datetime.now())
        self.assertEqual(new_one.days_since_modification(), 0)


class TestVarAnnoSetEntry(TestCase):
    def test_create(self):
        self.assertEqual(VarAnnoSetEntry.objects.count(), 0)
        VarAnnoSetEntryFactory()
        self.assertEqual(VarAnnoSetEntry.objects.count(), 1)
