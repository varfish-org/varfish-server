import binning
import factory

from ..models import Dbsnp


class DbsnpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dbsnp

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - 1)
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    rsid = factory.Sequence(lambda n: "rs%d" % n)

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()
