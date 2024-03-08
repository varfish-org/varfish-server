"""Factory Boy factory classes for ``conservation``."""

import binning
import factory

from ..models import KnowngeneAA


class KnownGeneAAFactory(factory.django.DjangoModelFactory):
    """Factory for the ``RefseqToHgnc`` model."""

    class Meta:
        model = KnowngeneAA

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: n * 100)
    end = factory.LazyAttribute(lambda o: o.start + 2)
    bin = 0
    transcript_id = factory.Sequence(lambda n: "uc%d.1" % n)
    alignment = "A" * 100

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
