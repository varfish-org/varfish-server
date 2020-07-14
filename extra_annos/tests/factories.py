"""Factory Boy factory classes for ``extra_annos``."""
import binning
import factory

from ..models import ExtraAnno, ExtraAnnoField


class ExtraAnnoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``ExtraAnno`` model."""

    class Meta:
        model = ExtraAnno

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: n * 100)
    end = factory.LazyAttribute(lambda o: o.start + 2)
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    anno_data = [9.71]

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class ExtraAnnoFieldFactory(factory.django.DjangoModelFactory):
    """Factory for the ``ExtraAnnoField`` model."""

    class Meta:
        model = ExtraAnnoField

    field = factory.Sequence(lambda n: n)
    label = factory.Sequence(lambda n: "label-%d" % n)
