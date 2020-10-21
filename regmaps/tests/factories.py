"""Factory Boy factory classes for ``regmaps``."""

import binning
import factory

from ..models import RegMapCollection, RegMap, RegElementType, RegElement, RegInteraction


class RegMapCollectionFactory(factory.django.DjangoModelFactory):
    """Factory for ``RegMapCollection`` records."""

    class Meta:
        model = RegMapCollection

    release = "GRCh37"
    version = "v0.0.20201022"
    title = factory.Sequence(lambda n: "reg map collection %d" % n)
    short_title = factory.Sequence(lambda n: "collection %d" % n)
    slug = factory.Sequence(lambda n: "coll_%d" % n)
    description = factory.Sequence(lambda n: "Regulatory map collection #%d" % n)


class RegMapFactory(factory.django.DjangoModelFactory):
    """Factory for ``RegMap`` records."""

    class Meta:
        model = RegMap

    collection = factory.SubFactory(RegMapCollectionFactory)
    title = factory.Sequence(lambda n: "reg map %d" % n)
    short_title = factory.Sequence(lambda n: "map %d" % n)
    slug = factory.Sequence(lambda n: "map_%d" % n)
    description = factory.Sequence(lambda n: "Regulatory map %d" % n)


class RegElementTypeFactory(factory.django.DjangoModelFactory):
    """Factory for ``RegElementType`` records."""

    class Meta:
        model = RegElementType

    collection = factory.SubFactory(RegMapCollectionFactory)
    title = factory.Sequence(lambda n: "element type %d" % n)
    short_title = factory.Sequence(lambda n: "type %d" % n)
    slug = factory.Sequence(lambda n: "eltype_%d" % n)
    description = factory.Sequence(lambda n: "Regulatory element type %d" % n)


class RegElementFactory(factory.django.DjangoModelFactory):
    """Factory for ``RegElement`` records."""

    class Meta:
        model = RegElement

    reg_map = factory.SubFactory(RegMapFactory)
    elem_type = factory.LazyAttribute(
        lambda o: RegElementTypeFactory(collection=o.reg_map.collection)
    )

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)
    bin = factory.LazyAttribute(lambda obj: binning.assign_bin(obj.start, obj.end))
    score = 1.0
    extra_data = None

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class RegInteractionFactory(factory.django.DjangoModelFactory):
    """Factory for ``RegInteraction`` records."""

    class Meta:
        model = RegInteraction

    reg_map = factory.SubFactory(RegMapFactory)
    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 1000)
    end = factory.Sequence(lambda n: (n + 1) * 1500 + 100)
    bin = factory.LazyAttribute(lambda obj: binning.assign_bin(obj.start, obj.end))
    score = 1.0

    chromosome1 = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start1 = factory.Sequence(lambda n: (n + 1) * 1000)
    end1 = factory.Sequence(lambda n: (n + 1) * 1000 + 100)
    chromosome2 = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start2 = factory.Sequence(lambda n: (n + 1) * 1500)
    end2 = factory.Sequence(lambda n: (n + 1) * 1500 + 100)

    extra_data = None

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
