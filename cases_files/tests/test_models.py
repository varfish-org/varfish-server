from freezegun import freeze_time
from test_plus import TestCase

from cases_files.models import ExternalFile, InternalFile
from cases_files.tests.factories import ExternalFileFactory, InternalFileFactory


@freeze_time("2012-01-14 12:00:01")
class ExternalFileTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(ExternalFile.objects.count(), 0)
        _external_file = ExternalFileFactory()
        self.assertEqual(ExternalFile.objects.count(), 1)

    def test_update(self):
        external_file = ExternalFileFactory()
        self.assertEqual(ExternalFile.objects.get().available, True)
        external_file.available = False
        external_file.save()
        external_file.refresh_from_db()
        self.assertEqual(ExternalFile.objects.get().available, False)


@freeze_time("2012-01-14 12:00:01")
class InternalFileTest(TestCase):
    def setUp(self):
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(InternalFile.objects.count(), 0)
        _external_file = InternalFileFactory()
        self.assertEqual(InternalFile.objects.count(), 1)

    def test_update(self):
        external_file = InternalFileFactory()
        self.assertEqual(
            InternalFile.objects.get().checksum,
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        checksum = "d41d8cd98f00b204e9800998ecf8427e"
        external_file.checksum = checksum
        external_file.save()
        external_file.refresh_from_db()
        self.assertEqual(InternalFile.objects.get().checksum, checksum)
