"""Factory Boy factory classes for ``svs``."""

import binning
import factory
import uuid

from svs.forms import (
    FILTER_FORM_TRANSLATE_REGULATORY,
    FILTER_FORM_TRANSLATE_EFFECTS,
    FILTER_FORM_TRANSLATE_SV_SUB_TYPES,
    FILTER_FORM_TRANSLATE_SV_TYPES,
)
from variants.tests.factories import CaseFactory
from ..models import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    StructuralVariantFlags,
    StructuralVariantComment,
)
import typing
import attr


def default_genotypes():
    """Build default genotype pattern (het. in first, wild-type otherwise)."""
    yield "0/1"
    while True:
        yield "0/0"


class StructuralVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StructuralVariant

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
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))

    start_ci_left = -100
    start_ci_right = 100
    end_ci_left = -100
    end_ci_right = 100

    #: Model pseudo-attribute, not stored in database.  Instead, ``case_id`` is stored.
    case = factory.SubFactory(CaseFactory)
    #: The actual reference to the case.
    case_id = factory.LazyAttribute(lambda o: o.case.id)

    caller = "DELLYv4001"
    sv_type = "DEL"
    sv_sub_type = "DEL"

    @factory.lazy_attribute
    def genotype(self):
        """Generate genotype JSON field from already set ``self.case``."""
        return {
            line["patient"]: {"gt": gt, "gq": 10, "src": 10, "srv": 5, "pec": 10, "pev": 5}
            for line, gt in zip(self.case.pedigree, self.genotypes())
        }

    @factory.lazy_attribute
    def info(self):
        """Generate info JSON field from already set ``self.case`` and genotypes from self.genotypes()."""
        num_affected = 0
        num_unaffected = 0
        for line, gt in zip(self.case.pedigree, self.genotypes()):
            if "1" in gt:
                if line.get("affected") == 2:
                    num_affected += 1
                else:
                    num_affected += 1
        return {
            "affectedCarriers": num_affected,
            "unaffectedCarriers": num_unaffected,
            "backgroundCarriers": 0,
        }

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class StructuralVariantGeneAnnotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StructuralVariantGeneAnnotation

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override to get rid of the ``sv`` keyword argument and instead define ``sv_uuid``."""
        manager = cls._get_manager(model_class)
        sv = kwargs.pop("sv")
        kwargs["sv_uuid"] = sv.sv_uuid
        return manager.create(*args, **kwargs)

    #: Model pseudo-attribute, not stored in database.  Instead, ``sv_uuid`` is stored.
    sv = factory.SubFactory(StructuralVariantFactory)
    #: The actual reference to the StructuralVariant.
    sv_uuid = factory.LazyAttribute(lambda o: o.sv.sv_uuid)

    refseq_gene_id = factory.Sequence(lambda n: "REFSEQ_%d" % n)
    refseq_transcript_id = factory.Sequence(lambda n: "NM_%d" % n)
    refseq_transcript_coding = True
    refseq_effect = ["exon_loss_variant", "3_prime_UTR_truncation", "non_coding_transcript_variant"]
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    ensembl_transcript_id = factory.Sequence(lambda n: "ENST_%d" % n)
    ensembl_transcript_coding = True
    ensembl_effect = [
        "exon_loss_variant",
        "3_prime_UTR_truncation",
        "non_coding_transcript_variant",
    ]


class _UserAnnotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    bin = factory.Sequence(lambda n: binning.assign_bin((n + 1) * 100, (n + 1) * 100 + 100))

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    sv_type = "DEL"
    sv_sub_type = "DEL"

    # user = factory.SubFactory(UserFactory)  # TODO
    case = factory.SubFactory(CaseFactory)


class StructuralVariantCommentFactory(_UserAnnotationFactory):
    class Meta:
        model = StructuralVariantComment

    text = "Some comment text."


class StructuralVariantFlagsFactory(_UserAnnotationFactory):
    class Meta:
        model = StructuralVariantFlags

    flag_bookmarked = True
    flag_candidate = False
    flag_final_causative = False
    flag_for_validation = False

    flag_visual = "empty"
    flag_validation = "empty"
    flag_phenotype_match = "empty"
    flag_summary = "empty"


@attr.s(auto_attribs=True)
class FormDataFactory:
    """Factory for default filter form data.

    The genotype filters are missing as they are added when running the test to fetch the current patient name that is
    unknown up to then. Same holds true for the case sodar_uuid.
    """

    database_select: str = "refseq"

    # database frequencies

    dgv_enabled: bool = False
    dgv_min_overlap: float = 0.75
    dgv_max_carriers: int = None
    dgv_gs_enabled: bool = False
    dgv_gs_min_overlap: float = 0.75
    dgv_gs_max_carriers: int = None
    exac_enabled: bool = False
    exac_min_overlap: float = 0.75
    exac_max_carriers: int = None
    gnomad_enabled: bool = False
    gnomad_min_overlap: float = 0.75
    gnomad_max_carriers: int = None
    dbvar_enabled: bool = False
    dbvar_min_overlap: float = 0.75
    dbvar_max_carriers: int = None
    g1k_enabled: bool = False
    g1k_min_overlap: float = 0.75
    g1k_max_carriers: int = None

    # collective frequency

    collective_enabled: bool = False
    cohort_background_carriers_min: int = None
    cohort_background_carriers_max: int = 0
    cohort_affected_carriers_min: int = 1
    cohort_affected_carriers_max: int = None
    cohort_unaffected_carriers_min: int = None
    cohort_unaffected_carriers_max: int = None

    # variant effect

    effects: typing.List[str] = list(FILTER_FORM_TRANSLATE_EFFECTS.values())

    transcripts_coding: bool = True
    transcripts_noncoding: bool = True
    require_transcript_overlap: bool = False

    sv_type: typing.List[str] = list(FILTER_FORM_TRANSLATE_SV_TYPES.values())

    sv_size_min: int = None
    sv_size_max: int = None

    sv_sub_type: typing.List[str] = list(FILTER_FORM_TRANSLATE_SV_SUB_TYPES.values())

    # gene lists / regions

    gene_blacklist: typing.List[str] = attr.Factory(list)
    region_whitelist: typing.List[str] = attr.Factory(list)
    gene_whitelist: typing.List[str] = attr.Factory(list)

    # tads

    tad_set_uuid: str = attr.Factory(uuid.uuid4)

    # regulatory features

    regulatory_ensembl: typing.List[str] = []
    regulatory_vista: typing.List[str] = []

    regulatory_vista_any_validation: bool = False
    regulatory_vista_positive: bool = False
    regulatory_vista_negative: bool = False
