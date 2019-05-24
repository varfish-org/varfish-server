"""Factory Boy factory classes for ``genomicfeatures``."""

import binning
import factory

from ..models import (
    TadSet,
    TadInterval,
    TadBoundaryInterval,
    EnsemblRegulatoryFeature,
    VistaEnhancer,
    GeneInterval,
    VISTA_POSITIVE,
)


class TadSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TadSet

    release = "GRCh37"
    name = factory.Sequence(lambda n: "tad set %d" % n)
    version = "Dixon2012"
    title = "hESC TADs (Dixon et al., 2019)"


class _IntervalFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 1000)
    end = factory.Sequence(lambda n: (n + 1) * 1000 + 100)

    bin = 0
    containing_bins = []

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.containing_bins = binning.containing_bins(obj.start - 1, obj.end)
        obj.save()


class TadIntervalFactory(_IntervalFactory):
    """TADs are generated as adjacent intervals of length 100kbp."""

    class Meta:
        model = TadInterval

    tad_set = factory.SubFactory(TadSetFactory)


class TadBoundaryIntervalFactory(_IntervalFactory):
    """TAD boundaries as 10kbp intervals around the borders."""

    class Meta:
        model = TadBoundaryInterval

    tad_set = factory.SubFactory(TadSetFactory)


class EnsemblRegulatoryFeatureFactory(_IntervalFactory):
    class Meta:
        model = EnsemblRegulatoryFeature

    stable_id = factory.Sequence(lambda n: "ENSR%d" % n)
    feature_type = "Enhancer"
    feature_type_description = "Predicted enhancer region"
    so_term_accession = "SO:0000165"
    so_term_name = "enhancer"


class VistaEnhancerFactory(_IntervalFactory):
    class Meta:
        model = VistaEnhancer

    element_id = factory.Sequence(lambda n: "element_%d" % n)
    validation_result = VISTA_POSITIVE


class GeneIntervalFactory(_IntervalFactory):
    class Meta:
        model = GeneInterval

    database = "refseq"
    gene_id = factory.Sequence(lambda n: "GENE%d" % n)
