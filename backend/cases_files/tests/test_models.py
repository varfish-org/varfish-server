from freezegun import freeze_time
from test_plus import TestCase

from cases_files.models import (
    IndividualExternalFile,
    IndividualInternalFile,
    PedigreeExternalFile,
    PedigreeInternalFile,
)
from cases_files.tests.factories import (
    IndividualExternalFileFactory,
    IndividualInternalFileFactory,
    PedigreeExternalFileFactory,
    PedigreeInternalFileFactory,
)


@freeze_time("2012-01-14 12:00:01")
class IndividualExternalFileTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(IndividualExternalFile.objects.count(), 0)
        _individual_external_file = IndividualExternalFileFactory()  # noqa: F841
        self.assertEqual(IndividualExternalFile.objects.count(), 1)

    def test_update(self):
        IndividualExternal_file = IndividualExternalFileFactory()
        self.assertEqual(IndividualExternalFile.objects.get().available, True)
        IndividualExternal_file.available = False
        IndividualExternal_file.save()
        IndividualExternal_file.refresh_from_db()
        self.assertEqual(IndividualExternalFile.objects.get().available, False)


@freeze_time("2012-01-14 12:00:01")
class PedigreeExternalFileTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(PedigreeExternalFile.objects.count(), 0)
        _pedigree_external_file = PedigreeExternalFileFactory()  # noqa: F841
        self.assertEqual(PedigreeExternalFile.objects.count(), 1)

    def test_update(self):
        PedigreeExternal_file = PedigreeExternalFileFactory()
        self.assertEqual(PedigreeExternalFile.objects.get().available, True)
        PedigreeExternal_file.available = False
        PedigreeExternal_file.save()
        PedigreeExternal_file.refresh_from_db()
        self.assertEqual(PedigreeExternalFile.objects.get().available, False)


@freeze_time("2012-01-14 12:00:01")
class IndividualInternalFileTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(IndividualInternalFile.objects.count(), 0)
        _individual_internal_file = IndividualInternalFileFactory()  # noqa: F841
        self.assertEqual(IndividualInternalFile.objects.count(), 1)

    def test_update(self):
        external_file = IndividualInternalFileFactory()
        self.assertEqual(
            IndividualInternalFile.objects.get().checksum,
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        checksum = "d41d8cd98f00b204e9800998ecf8427e"
        external_file.checksum = checksum
        external_file.save()
        external_file.refresh_from_db()
        self.assertEqual(IndividualInternalFile.objects.get().checksum, checksum)


@freeze_time("2012-01-14 12:00:01")
class PedigreeInternalFileTest(TestCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def test_create(self):
        self.assertEqual(PedigreeInternalFile.objects.count(), 0)
        _pedigree_external_file = PedigreeInternalFileFactory()  # noqa: F841
        self.assertEqual(PedigreeInternalFile.objects.count(), 1)

    def test_update(self):
        external_file = PedigreeInternalFileFactory()
        self.assertEqual(
            PedigreeInternalFile.objects.get().checksum,
            "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        )
        checksum = "d41d8cd98f00b204e9800998ecf8427e"
        external_file.checksum = checksum
        external_file.save()
        external_file.refresh_from_db()
        self.assertEqual(PedigreeInternalFile.objects.get().checksum, checksum)
