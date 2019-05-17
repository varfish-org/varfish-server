"""Factory Boy factory classes for ``variants``."""

import factory

from projectroles.models import SODAR_CONSTANTS, Project

from ..models import (
    Case,
    SmallVariant,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    SmallVariantSummary,
    ClinvarQuery,
)
import typing
import attr


class SmallVariantQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SmallVariantQuery

    case = None
    form_id = factory.Sequence(lambda n: str(n))
    form_version = factory.Sequence(lambda n: n)
    query_settings = factory.List([])
    name = factory.Sequence(lambda n: "SmallVariantQuery%d" % n)
    public = False


class ClinvarQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ClinvarQuery

    case = None
    form_id = factory.Sequence(lambda n: str(n))
    form_version = factory.Sequence(lambda n: n)
    query_settings = factory.List([])
    name = factory.Sequence(lambda n: "ClinvarQuery%d" % n)
    public = False


class ProjectCasesSmallVariantQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectCasesSmallVariantQuery

    project = None
    form_id = factory.Sequence(lambda n: str(n))
    form_version = factory.Sequence(lambda n: n)
    query_settings = factory.List([])
    name = factory.Sequence(lambda n: "ProjectCasesSmallVariantQuery%d" % n)
    public = False


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``projectroles`` ``Project`` objects."""

    class Meta:
        model = Project

    title = factory.Sequence(lambda n: "Project %03d" % n)
    type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
    parent = None
    description = factory.Sequence(lambda n: "This is project %03d" % n)
    projectcasessmallvariantquery = factory.RelatedFactory(
        ProjectCasesSmallVariantQueryFactory, "project"
    )


class CaseFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``Case`` objects."""

    class Meta:
        model = Case

    class Params:
        #: The sex of the index
        sex = 1  # 1: unaffected, 2: affected
        #: The structure can be "singleton" or "trio" at the moment.
        structure = "singleton"
        #: The supported inheritance patterns are "denovo", "dominant", and "recessive" at the
        #: moment.  This is only used for non-singletons.  When dominant, the father will be
        #: affected.
        inheritance = "denovo"

    name = factory.LazyAttributeSequence(lambda o, n: "case %03d: %s" % (n, o.structure))
    index = factory.Sequence(lambda n: "index_%03d-N1-DNA1-WES1" % n)
    pedigree = []
    project = factory.SubFactory(ProjectFactory)
    smallvariantquery = factory.RelatedFactory(SmallVariantQueryFactory, "case")
    clinvarquery = factory.RelatedFactory(ClinvarQueryFactory, "case")

    @factory.lazy_attribute_sequence
    def pedigree(self, n):
        if self.structure not in ("singleton", "trio"):
            raise ValueError("Invalid structure type!")
        elif self.structure == "singleton":
            return [
                {
                    "patient": self.index,
                    "father": "0",
                    "mother": "0",
                    "sex": self.sex,
                    "affected": 2,
                    "has_gt_entries": True,
                }
            ]
        else:  # self.structure == "trio"
            # Father and mother name
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": mother,
                    "sex": self.sex,
                    "affected": 2,  # always affected
                    "has_gt_entries": True,
                },
                {
                    "patient": father,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
            ]


def default_genotypes():
    """Build default genotype pattern (het. in first, wild-type otherwise)."""
    yield "0/1"
    while True:
        yield "0/0"


def count_gt(*gts):
    """Return counter for the given genotypes."""

    def result(o):
        return len([x["gt"] for x in o.genotype.values() if x["gt"] in gts])

    return result


class SmallVariantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SmallVariant`` objects.

    Allows creation of a finite set of actual variants from ``LAMA1`` gene.
    """

    class Meta:
        model = SmallVariant

    class Params:
        #: The genotypes to create, by default only first is het. the rest is wild-type.
        genotypes = default_genotypes

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to get rid of the ``case`` keyword argument and instead define ``case_id``."""
        manager = cls._get_manager(model_class)
        case = kwargs.pop("case")
        kwargs["case_id"] = case.id
        return manager.create(*args, **kwargs)

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    position = factory.Sequence(lambda n: (n + 1) * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    var_type = "snv"
    #: Model pseudo-attribute, not stored in database.  Instead, ``case_id`` is stored.
    case = factory.SubFactory(CaseFactory)
    #: The actual reference to the case.
    case_id = factory.LazyAttribute(lambda o: o.case.id)

    @factory.lazy_attribute
    def genotype(self):
        """Generate genotype JSON field from already set ``self.case``."""
        return {
            line["patient"]: {"gt": gt} for line, gt in zip(self.case.pedigree, self.genotypes())
        }

    num_hom_alt = factory.LazyAttribute(count_gt("0/0"))
    num_hom_ref = factory.LazyAttribute(count_gt("1/1"))
    num_het = factory.LazyAttribute(count_gt("0/1", "1/0", "0|1", "1|0"))
    num_hemi_alt = 0
    num_hemi_ref = 0
    in_clinvar = False
    exac_frequency = 0.0001
    exac_homozygous = 0
    exac_heterozygous = 0
    exac_hemizygous = 0
    thousand_genomes_frequency = 0.0001
    thousand_genomes_homozygous = 0
    thousand_genomes_heterozygous = 0
    thousand_genomes_hemizygous = 0
    gnomad_exomes_frequency = 0.0001
    gnomad_exomes_homozygous = 0
    gnomad_exomes_heterozygous = 0
    gnomad_exomes_hemizygous = 0
    gnomad_genomes_frequency = 0.0001
    gnomad_genomes_homozygous = 0
    gnomad_genomes_heterozygous = 0
    gnomad_genomes_hemizygous = 0
    refseq_gene_id = factory.Sequence(lambda n: str(n))
    refseq_transcript_id = factory.Sequence(lambda n: "NM_%d" % n)
    refseq_transcript_coding = True
    refseq_hgvs_c = "c.123C>T"
    refseq_hgvs_p = "p.I2T"
    refseq_effect = factory.List(["synonymous_variant"])
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    ensembl_transcript_id = factory.Sequence(lambda n: "ENST%d" % n)
    ensembl_transcript_coding = True
    ensembl_hgvs_c = "c.123C>T"
    ensembl_hgvs_p = "p.I2T"
    ensembl_effect = factory.List(["synonymous_variant"])


class SmallVariantSummaryFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantSummary`` model."""

    class Meta:
        model = SmallVariantSummary

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    position = factory.Sequence(lambda n: (n + 1) * 100)
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    count_hom_ref = 0
    count_het = 0
    count_hom_alt = 0
    count_hemi_ref = 0
    count_hemi_alt = 0


@attr.s(auto_attribs=True)
class FormDataFactory:
    """Factory for default filter form data.

    The genotype filters are missing as they are added when running the test to fetch the current patient name that is
    unknown up to then. Same holds true for the case sodar_uuid.
    """

    effects: typing.List[str] = attr.Factory(lambda: list(["synonymous_variant"]))
    database_select: str = "refseq"
    var_type_snv: bool = True
    var_type_mnv: bool = True
    var_type_indel: bool = True
    exac_enabled: bool = False
    exac_frequency: float = 0.0
    exac_heterozygous: int = 0
    exac_homozygous: int = 0
    thousand_genomes_enabled: bool = False
    thousand_genomes_frequency: float = 0.0
    thousand_genomes_heterozygous: int = 0
    thousand_genomes_homozygous: int = 0
    gnomad_exomes_enabled: bool = False
    gnomad_exomes_frequency: float = 0.0
    gnomad_exomes_heterozygous: int = 0
    gnomad_exomes_homozygous: int = 0
    gnomad_genomes_enabled: bool = False
    gnomad_genomes_frequency: float = 0.0
    gnomad_genomes_heterozygous: int = 0
    gnomad_genomes_homozygous: int = 0
    inhouse_enabled: bool = False
    inhouse_carriers: int = 0
    inhouse_heterozygous: int = 0
    inhouse_homozygous: int = 0
    transcripts_coding: bool = True
    transcripts_noncoding: bool = True
    require_in_clinvar: bool = False
    remove_if_in_dbsnp: bool = False
    require_in_hgmd_public: bool = False
    display_hgmd_public_membership: bool = False
    clinvar_include_benign: bool = False
    clinvar_include_likely_benign: bool = False
    clinvar_include_uncertain_significance: bool = False
    clinvar_include_likely_pathogenic: bool = True
    clinvar_include_pathogenic: bool = True
    gene_blacklist: typing.List[str] = attr.Factory(list)
    genomic_region: typing.List[str] = attr.Factory(list)
    gene_whitelist: typing.List[str] = attr.Factory(list)
