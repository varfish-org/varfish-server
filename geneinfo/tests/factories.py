"""Factory Boy factory classes for ``geneinfo``."""

import factory

from ..models import Hgnc, Hpo, Mim2geneMedgen


class HgncFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Hgnc`` model."""

    class Meta:
        model = Hgnc

    hgnc_id = factory.Sequence(lambda n: "HGNC:%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    name = factory.Sequence(lambda n: "Gene name %d" % n)
    entrez_id = factory.Sequence(lambda n: str(n))
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)


class HpoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Hpo`` model."""

    class Meta:
        model = Hpo

    database_id = factory.Sequence(lambda n: "OMIM:%d" % n)
    hpo_id = factory.Sequence(lambda n: "HP:%07d" % n)


class Mim2geneMedgenFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Mim2geneMedgen`` model."""

    class Meta:
        model = Mim2geneMedgen

    omim_id = factory.Sequence(lambda n: n)
    entrez_id = factory.Sequence(lambda n: str(n))
