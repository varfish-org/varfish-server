"""Factory Boy factory classes for ``clinvar``."""
import typing

import attr
import binning
import factory

from ..models import Clinvar


class ClinvarFactory(factory.django.DjangoModelFactory):
    """Factory for ``Clinvar`` records."""

    class Meta:
        model = Clinvar

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    variation_type = "snv"
    symbols = factory.Sequence(lambda n: ["SYMBOL%d" % n])
    hgnc_ids = factory.Sequence(lambda n: ["HGNC:%d" % n])
    variation_id = factory.Sequence(lambda n: ["Clinvar%d" % n])
    rcv = factory.Sequence(lambda n: "RCV%d" % (12345 + n))
    vcv = factory.Sequence(lambda n: "VCV%d" % (12345 + n))
    gold_stars = factory.Iterator([0, 1, 2, 3])
    pathogenicity = "uncertain significance"
    review_status = "practice guideline"
    origin = "germline"
    details = []

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
