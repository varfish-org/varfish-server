"""Factory Boy factory classes for ``conservation``."""

import factory

from ..models import KnowngeneAA


class KnownGeneAAFactory(factory.django.DjangoModelFactory):
    """Factory for the ``RefseqToHgnc`` model."""

    class Meta:
        model = KnowngeneAA

    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: n * 100)
    end = factory.LazyAttribute(lambda o: o.start + 2)
    transcript_id = factory.Sequence(lambda n: "uc%d.1" % n)
    alignment = "A" * 100
