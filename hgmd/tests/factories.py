"""Factory Boy factory classes for ``hgmd``."""
import binning
import factory

from ..models import HgmdPublicLocus


class HgmdPublicLocusFactory(factory.django.DjangoModelFactory):
    """Factory for ``HgmdPublicLocus`` records."""

    class Meta:
        model = HgmdPublicLocus

    release = "GRCh37"
    chromosome = factory.Iterator((list(map(str, range(1, 23))) + ["X", "Y"]))
    start = factory.Sequence(lambda n: (n + 1) * 100 - 1)
    end = factory.LazyAttribute(lambda o: o.start + 1)
    bin = 0

    variation_name = factory.Sequence(lambda n: "CD12345%d" % n)

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
