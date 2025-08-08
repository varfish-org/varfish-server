from test_plus import TestCase

from seqmeta.models import EnrichmentKit, TargetBedFile
from seqmeta.tests.factories import EnrichmentKitFactory, TargetBedFileFactory


class TestEnrichmentKit(TestCase):
    def test_create(self):
        self.assertEqual(EnrichmentKit.objects.count(), 0)
        EnrichmentKitFactory()
        self.assertEqual(EnrichmentKit.objects.count(), 1)

    def test_get_absolute_url(self):
        kit = EnrichmentKitFactory()
        self.assertEqual(kit.get_absolute_url(), f"/seqmeta/enrichmentkit/{kit.sodar_uuid}/")

    def test_str(self):
        kit = EnrichmentKitFactory()
        self.assertEqual(f"EnrichmentKit '{kit.title}'", kit.__str__())


class TestTargetBedFile(TestCase):
    def test_create(self):
        self.assertEqual(TargetBedFile.objects.count(), 0)
        TargetBedFileFactory()
        self.assertEqual(TargetBedFile.objects.count(), 1)
