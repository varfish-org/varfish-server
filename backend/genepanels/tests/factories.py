import factory

from genepanels.models import GenePanel, GenePanelCategory, GenePanelEntry, GenePanelState
from varfish.users.tests.factories import UserFactory


class GenePanelCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenePanelCategory

    title = factory.Sequence(lambda n: f"Gene Panel Category {n}")


class GenePanelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenePanel

    identifier = factory.Sequence(lambda n: f"some.panel-{n}")
    state = GenePanelState.ACTIVE.value
    version_major = 1
    version_minor = 1

    signed_off_by = factory.SubFactory(UserFactory)
    category = factory.SubFactory(GenePanelCategoryFactory)
    title = factory.Sequence(lambda n: f"Gene Panel Category {n}")


class GenePanelEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GenePanelEntry

    panel = factory.SubFactory(GenePanelFactory)

    symbol = factory.Sequence(lambda n: f"SYMBOL-{n}")
    hgnc_id = factory.Sequence(lambda n: f"HGNC:{n}")
    ensembl_id = factory.Sequence(lambda n: f"ENSG{n}")
    ncbi_id = factory.Sequence(lambda n: f"NCBI{n}")
