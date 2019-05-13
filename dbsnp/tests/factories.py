import factory

from ..models import Dbsnp


class DbsnpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Dbsnp

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    position = factory.Sequence(lambda n: n * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    rsid = factory.Sequence(lambda n: "rs%d" % n)
