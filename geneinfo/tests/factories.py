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
    GeneIdToInheritance,
    MgiMapping,
    RefseqToGeneSymbol,
    EnsemblToGeneSymbol,
    GeneIdInHpo,
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
    mu_syn = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    mu_mis = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    mu_lof = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    exp_syn = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    n_syn = factory.Sequence(lambda n: n)
    syn_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    exp_mis = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    n_mis = factory.Sequence(lambda n: n)
    mis_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    exp_lof = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    n_lof = factory.Sequence(lambda n: n)
    lof_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    pLI = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    pRec = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    pNull = factory.Sequence(lambda n: 1 / 2 ** (n % 12))


class GnomadConstraintsFactory(factory.django.DjangoModelFactory):
    """Factory for the ``GnomadConstraints`` model."""

    class Meta:
        model = GnomadConstraints

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
    exp_syn = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    obs_syn = factory.Sequence(lambda n: n)
    syn_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    oe_syn = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    exp_mis = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    obs_mis = factory.Sequence(lambda n: n)
    mis_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    oe_mis = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    exp_lof = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    obs_lof = factory.Sequence(lambda n: n)
    lof_z = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    oe_lof = factory.Sequence(lambda n: 1 / 2 ** (n % 12))
    pLI = factory.Sequence(lambda n: 1 / 2 ** (n % 12) + 1.234)
    oe_lof_upper = factory.Sequence(lambda n: 1 / 3 ** (n % 12))
    oe_lof_lower = factory.Sequence(lambda n: 1 / 0.75 ** (n % 12))


class GeneIdToInheritanceFactory(factory.django.DjangoModelFactory):
    """Factory for the ``GeneIdToInheritance`` model/materialized view."""

    class Meta:
        model = GeneIdToInheritance

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    entrez_id = factory.Sequence(lambda n: str(n))
    mode_of_inheritance = factory.Iterator([m for m, v in GeneIdToInheritance.MODES_OF_INHERITANCE])


class GeneIdInHpoFactory(factory.django.DjangoModelFactory):
    """Factory for the ``GeneIdInHpo`` model/materialized view."""

    class Meta:
        model = GeneIdInHpo

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    entrez_id = factory.Sequence(lambda n: str(n))


class MgiMappingFactory(factory.django.DjangoModelFactory):
    """Factory for the ``MgiMapping`` model/materialized view."""

    class Meta:
        model = MgiMapping

    hgnc_id = factory.Sequence(lambda n: "HGNC:%d" % n)
    omim_id = factory.Sequence(lambda n: "OMIM:%d" % n)
    human_coordinates = "chr1:1-100(+)"
    human_entrez_id = factory.Sequence(lambda n: str(n))
    human_nucleotide_refseq_ids = []
    human_protein_refseq_ids = []
    human_swissprot_ids = []
    mgi_id = factory.Sequence(lambda n: "MGI:%d" % n)
    mouse_coordinates = "chr1:1-100(+)"
    mouse_entrez_id = factory.Sequence(lambda n: str(n + 100))
    mouse_nucleotide_refseq_ids = []
    mouse_protein_refseq_ids = []
    mouse_swissprot_ids = []


class RefseqToGeneSymbolFactory(factory.django.DjangoModelFactory):
    """Factory for the ``RefseqToGeneSymbol`` model."""

    class Meta:
        model = RefseqToGeneSymbol

    entrez_id = factory.Sequence(lambda n: str(n))
    gene_symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)


class EnsemblToGeneSymbolFactory(factory.django.DjangoModelFactory):
    """Factory for the ``EnsemblToGeneSymbol`` model."""

    class Meta:
        model = EnsemblToGeneSymbol

    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    gene_symbol = factory.Sequence(lambda n: "SYMBOL%d" % n)
