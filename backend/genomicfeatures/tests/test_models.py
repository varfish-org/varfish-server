"""Some simple tests for the models in the ``genomicfeatures`` package."""

from django.test import TestCase

from .factories import (
    EnsemblRegulatoryFeatureFactory,
    GeneIntervalFactory,
    TadBoundaryIntervalFactory,
    TadIntervalFactory,
    TadSetFactory,
    VistaEnhancerFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # show full diff

    def testTadSetFactory(self):
        obj = TadSetFactory()
        obj.save(force_update=True)

    def testTadIntervalFactory(self):
        obj = TadIntervalFactory()
        obj.save(force_update=True)

    def testTadBoundaryIntervalFactory(self):
        obj = TadBoundaryIntervalFactory()
        obj.save(force_update=True)

    def testEnsemblRegulatoryFeatureFactory(self):
        obj = EnsemblRegulatoryFeatureFactory()
        obj.save(force_update=True)

    def testVistaEnhancerFactory(self):
        obj = VistaEnhancerFactory()
        obj.save(force_update=True)

    def testGeneIntervalFactory(self):
        obj = GeneIntervalFactory()
        obj.save(force_update=True)
