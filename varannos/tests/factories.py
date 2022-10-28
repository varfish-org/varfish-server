import factory.django

from varannos.models import VarAnnoSet, VarAnnoSetEntry
from variants.tests.factories import CHROMOSOME_LIST_TESTING, ProjectFactory


class VarAnnoSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VarAnnoSet

    project = factory.SubFactory(ProjectFactory)
    release = "GRCh37"
    title = factory.Sequence(lambda n: f"Variant Annotation Set {n}")
    fields = [
        "pathogenicity",
        "notes",
    ]


class VarAnnoSetEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VarAnnoSetEntry

    varannoset = factory.SubFactory(VarAnnoSetFactory)

    release = "GRCh37"
    chromosome = factory.Iterator(CHROMOSOME_LIST_TESTING)
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")

    payload = {
        "pathogenicity": "pathogenic",
        "notes": "Here are some notes\nwith multiple lines",
    }
