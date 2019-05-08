"""Factory Boy factory classes for ``variants``."""

import factory.django

from projectroles.models import SODAR_CONSTANTS, Project

from .factories_data import small_var_attribute, small_var_iterator
from ..models import Case, SmallVariant


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``projectroles`` ``Project`` objects."""

    class Meta:
        model = Project

    title = factory.Sequence(lambda n: "Project %03d" % n)
    type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
    parent = None
    description = factory.Sequence(lambda n: "This is project %03d" % n)


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

    @factory.lazy_attribute_sequence
    def pedigree(self, n):
        if self.structure not in ("singleton", "trio"):
            raise ValueError("Invalid structure type!")
        elif self.structure == "singleton":
            return [
                {
                    "patient": self.name,
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
                    "patient": self.name,
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


#: The gene to create the small variants for.
SYMBOL = "LAMA1"


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

    release = small_var_attribute(SYMBOL, "release")
    chromosome = small_var_attribute(SYMBOL, "chromosome")
    position = small_var_iterator(SYMBOL, "position")
    reference = small_var_iterator(SYMBOL, "reference")
    alternative = small_var_iterator(SYMBOL, "alternative")
    var_type = small_var_iterator(SYMBOL, "var_type")
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
    in_clinvar = small_var_iterator(SYMBOL, "in_clinvar")
    exac_frequency = small_var_iterator(SYMBOL, "exac_frequency")
    exac_homozygous = small_var_iterator(SYMBOL, "exac_homozygous")
    exac_heterozygous = small_var_iterator(SYMBOL, "exac_heterozygous")
    exac_hemizygous = small_var_iterator(SYMBOL, "exac_hemizygous")
    thousand_genomes_frequency = small_var_iterator(SYMBOL, "thousand_genomes_frequency")
    thousand_genomes_homozygous = small_var_iterator(SYMBOL, "thousand_genomes_homozygous")
    thousand_genomes_heterozygous = small_var_iterator(SYMBOL, "thousand_genomes_heterozygous")
    thousand_genomes_hemizygous = small_var_iterator(SYMBOL, "thousand_genomes_hemizygous")
    gnomad_exomes_frequency = small_var_iterator(SYMBOL, "gnomad_exomes_frequency")
    gnomad_exomes_homozygous = small_var_iterator(SYMBOL, "gnomad_exomes_homozygous")
    gnomad_exomes_heterozygous = small_var_iterator(SYMBOL, "gnomad_exomes_heterozygous")
    gnomad_exomes_hemizygous = small_var_iterator(SYMBOL, "gnomad_exomes_hemizygous")
    gnomad_genomes_frequency = small_var_iterator(SYMBOL, "gnomad_genomes_frequency")
    gnomad_genomes_homozygous = small_var_iterator(SYMBOL, "gnomad_genomes_homozygous")
    gnomad_genomes_heterozygous = small_var_iterator(SYMBOL, "gnomad_genomes_heterozygous")
    gnomad_genomes_hemizygous = small_var_iterator(SYMBOL, "gnomad_genomes_hemizygous")
    refseq_gene_id = small_var_iterator(SYMBOL, "refseq_gene_id")
    refseq_transcript_id = small_var_iterator(SYMBOL, "refseq_transcript_id")
    refseq_transcript_coding = small_var_iterator(SYMBOL, "refseq_transcript_coding")
    refseq_hgvs_c = small_var_iterator(SYMBOL, "refseq_hgvs_c")
    refseq_hgvs_p = small_var_iterator(SYMBOL, "refseq_hgvs_p")
    refseq_effect = small_var_iterator(SYMBOL, "refseq_effect")
    ensembl_gene_id = small_var_iterator(SYMBOL, "ensembl_gene_id")
    ensembl_transcript_id = small_var_iterator(SYMBOL, "ensembl_transcript_id")
    ensembl_transcript_coding = small_var_iterator(SYMBOL, "ensembl_transcript_coding")
    ensembl_hgvs_c = small_var_iterator(SYMBOL, "ensembl_hgvs_c")
    ensembl_hgvs_p = small_var_iterator(SYMBOL, "ensembl_hgvs_p")
    ensembl_effect = small_var_iterator(SYMBOL, "ensembl_effect")
