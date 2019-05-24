"""Some simple tests for the models in the ``genomicfeatures`` package."""

from django.test import TestCase

from .factories import (
    TadSetFactory,
    TadIntervalFactory,
    TadBoundaryIntervalFactory,
    EnsemblRegulatoryFeatureFactory,
    VistaEnhancerFactory,
    GeneIntervalFactory,
)


class ModelsSmokeTest(TestCase):
    """Simple smoke tests for the model classes"""

    def setUp(self):
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
