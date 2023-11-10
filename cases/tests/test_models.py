import tempfile

from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases.models import write_pedigree_as_plink
from cases.tests.factories import IndividualFactory


class TestWritePedigreeAsPlink(TestCaseSnapshot, TestCase):
    def setUp(self):
        super().setUp()
        self.individual = IndividualFactory()
        self.pedigree = self.individual.pedigree

    def testRun(self):
        with tempfile.TemporaryFile(mode="w+t") as tmpf:
            write_pedigree_as_plink(self.pedigree, tmpf)
            tmpf.flush()
            tmpf.seek(0)
            fcontents = tmpf.read()
            self.assertMatchSnapshot(fcontents, "PLINK ped file")
