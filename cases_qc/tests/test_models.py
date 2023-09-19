from freezegun import freeze_time
from test_plus import TestCase

from cases_qc.models import Case, CaseQc, FragmentLengthHistogram
from cases_qc.tests.factories import CaseQcFactory, FragmentLengthHistogramFactory


@freeze_time("2012-01-14 12:00:01")
class CaseQcTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        _case_qc = CaseQcFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)


@freeze_time("2012-01-14 12:00:01")
class FragmentLengthHistogramTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(Case.objects.count(), 0)
        self.assertEqual(CaseQc.objects.count(), 0)
        self.assertEqual(FragmentLengthHistogram.objects.count(), 0)
        _frag_len_histo = FragmentLengthHistogramFactory()
        self.assertEqual(CaseQc.objects.count(), 1)
        self.assertEqual(Case.objects.count(), 1)
        self.assertEqual(FragmentLengthHistogram.objects.count(), 1)
