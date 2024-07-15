"""Some simple tests for the models in the ``svdbs`` package."""

from django.test import TestCase

from .factories import (
    DbVarSvFactory,
    DgvGoldStandardSvsFactory,
    DgvSvsFactory,
    ExacCnvFactory,
    GnomAdSvFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testDgvSvs(self):
        obj = DgvSvsFactory()
        obj.save(force_update=True)

    def testDgvGoldStandardSvs(self):
        obj = DgvGoldStandardSvsFactory()
        obj.save(force_update=True)

    def testDbVarSv(self):
        obj = DbVarSvFactory()
        obj.save(force_update=True)

    def testGnomadSv(self):
        obj = GnomAdSvFactory()
        obj.save(force_update=True)

    def testExacCnv(self):
        obj = ExacCnvFactory()
        obj.save(force_update=True)
