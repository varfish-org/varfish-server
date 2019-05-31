"""Factory Boy factory classes for ``geneinfo``."""

import factory

from ..models import (
    Hgnc,
    Hpo,
    Mim2geneMedgen,
    Acmg,
    RefseqToHgnc,
    HpoName,
    ExacConstraints,
    GnomadConstraints,
    EnsemblToRefseq,
    RefseqToEnsembl,
)


class RefseqToHgncFactory(factory.django.DjangoModelFactory):
    """Factory for the ``RefseqToHgnc`` model."""

    class Meta:
        model = RefseqToHgnc

    entrez_id = factory.Sequence(lambda n: str(n))
    hgnc_id = factory.Sequence(lambda n: "HGNC:%d" % n)


class HgncFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Hgnc`` model."""

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create corresponding RefseqToHgnc object to the current Hgnc object."""
        manager = cls._get_manager(model_class)
        RefseqToHgncFactory(entrez_id=kwargs["entrez_id"])
        return manager.create(*args, **kwargs)

    class Meta:
        model = Hgnc

    hgnc_id = factory.Sequence(lambda n: "HGNC:%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    name = factory.Sequence(lambda n: "Gene name %d" % n)
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    entrez_id = factory.Sequence(lambda n: str(n))


class HpoNameFactory(factory.django.DjangoModelFactory):
    """Factory for the ``HpoName`` model."""

    class Meta:
        model = HpoName

    hpo_id = factory.Sequence(lambda n: "HP:%07d" % n)
    name = factory.Sequence(lambda n: "Phenotype %d" % n)


class HpoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Hpo`` model."""

    class Meta:
        model = Hpo
        exclude = ["hpo_name", "hpo_name_entry"]

    # Dummy argument, passed to HpoName
    hpo_name = factory.Sequence(lambda n: "Phenotype %d" % n)
    # Dummy argument, creates HpoName record
    hpo_name_entry = factory.SubFactory(
        HpoNameFactory,
        hpo_id=factory.SelfAttribute("factory_parent.hpo_id"),
        name=factory.SelfAttribute("factory_parent.hpo_name"),
    )

    database_id = factory.Sequence(lambda n: "OMIM:%d" % n)
    hpo_id = factory.Sequence(lambda n: "HP:%07d" % n)
    name = factory.Sequence(lambda n: "Disease %d; Gene Symbol;;Alternative Description" % n)


class Mim2geneMedgenFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Mim2geneMedgen`` model."""

    class Meta:
        model = Mim2geneMedgen

    omim_id = factory.Sequence(lambda n: n)
    entrez_id = factory.Sequence(lambda n: str(n))
    omim_type = "phenotype"


class AcmgFactory(factory.django.DjangoModelFactory):
    """Factory for the ``Acmg`` model."""

    class Meta:
        model = Acmg

    entrez_id = factory.Sequence(lambda n: str(n))
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)


class EnsemblToRefseqFactory(factory.django.DjangoModelFactory):
    """Factory for the ``EnsemblToRefseqFactory`` model."""

    class Meta:
        model = EnsemblToRefseq

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    ensembl_transcript_id = factory.Sequence(lambda n: "ENST%d" % n)
    entrez_id = factory.Sequence(lambda n: str(n))


class RefseqToEnsemblFactory(factory.django.DjangoModelFactory):
    """Factory for the ``RefseqToEnsemblFactory`` model."""

    class Meta:
        model = RefseqToEnsembl

    entrez_id = factory.Sequence(lambda n: str(n))
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    ensembl_transcript_id = factory.Sequence(lambda n: "ENST%d" % n)


class ExacConstraintsFactory(factory.django.DjangoModelFactory):
    """Factory for the ``ExacConstraints`` model."""

    class Meta:
        model = ExacConstraints

    ensembl_transcript_id = factory.Sequence(lambda n: "ENST%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    n_exons = 2
    cds_start = factory.Sequence(lambda n: n + 1)
    cds_end = factory.Sequence(lambda n: n + 100)
    bp = factory.LazyAttribute(lambda o: o.cds_end - o.cds_start + 1)
    mu_syn = factory.Sequence(lambda n: 1 / (n + 1))
    mu_mis = factory.Sequence(lambda n: 1 / (n + 1))
    mu_lof = factory.Sequence(lambda n: 1 / (n + 1))
    exp_syn = factory.Sequence(lambda n: 1 / (n + 1))
    n_syn = factory.Sequence(lambda n: n)
    syn_z = factory.Sequence(lambda n: 1 / (n + 1))
    exp_mis = factory.Sequence(lambda n: 1 / (n + 1))
    n_mis = factory.Sequence(lambda n: n)
    mis_z = factory.Sequence(lambda n: 1 / (n + 1))
    exp_lof = factory.Sequence(lambda n: 1 / (n + 1))
    n_lof = factory.Sequence(lambda n: n)
    lof_z = factory.Sequence(lambda n: 1 / (n + 1))
    pLI = factory.Sequence(lambda n: 1 / (n + 1))
    pRec = factory.Sequence(lambda n: 1 / (n + 1))
    pNull = factory.Sequence(lambda n: 1 / (n + 1))


class GnomadConstraintsFactory(factory.django.DjangoModelFactory):
    """Factory for the ``GnomadConstraints`` model."""

    class Meta:
        model = GnomadConstraints

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    exp_syn = factory.Sequence(lambda n: 1 / (n + 1))
    obs_syn = factory.Sequence(lambda n: n)
    syn_z = factory.Sequence(lambda n: 1 / (n + 1))
    oe_syn = factory.Sequence(lambda n: 1 / (n + 1))
    exp_mis = factory.Sequence(lambda n: 1 / (n + 1))
    obs_mis = factory.Sequence(lambda n: n)
    mis_z = factory.Sequence(lambda n: 1 / (n + 1))
    oe_mis = factory.Sequence(lambda n: 1 / (n + 1))
    exp_lof = factory.Sequence(lambda n: 1 / (n + 1))
    obs_lof = factory.Sequence(lambda n: n)
    lof_z = factory.Sequence(lambda n: 1 / (n + 1))
    oe_lof = factory.Sequence(lambda n: 1 / (n + 1))
