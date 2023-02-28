"""Factory Boy factory classes for ``svs``."""

import datetime
import typing
import uuid

import attr
import attrs
from bgjobs.models import BackgroundJob
from bgjobs.tests.factories import BackgroundJobFactory
import binning
from django.utils import timezone
import factory
from factory.fuzzy import FuzzyDateTime

from variants.models import Case
from variants.tests.factories import CaseFactory, ProjectFactory

from ..models import (
    BackgroundSv,
    BackgroundSvSet,
    FilterSvBgJob,
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    StructuralVariantGeneAnnotation,
    StructuralVariantSet,
    SvQuery,
    SvQueryResultRow,
    SvQueryResultSet,
)


def default_genotypes():
    """Build default genotype pattern (het. in first, wild-type otherwise)."""
    yield "0/1"
    while True:
        yield "0/0"


class StructuralVariantSetFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SmallVariantSet`` objects."""

    class Meta:
        model = StructuralVariantSet

    case = factory.SubFactory(CaseFactory)
    # Fix the state of all created SmallVariantSet objects to ``"active"``.
    state = "active"


class StructuralVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StructuralVariant
        exclude = ["case", "variant_set"]

    class Params:
        #: The genotypes to create, by default only first is het. the rest is wild-type.
        genotypes = default_genotypes

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    chromosome_no = factory.Iterator(list(range(1, 25)))
    chromosome2 = factory.LazyAttribute(lambda obj: obj.chromosome)
    chromosome_no2 = factory.LazyAttribute(lambda obj: obj.chromosome_no)
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)
    pe_orientation = "3to5"

    start_ci_left = -100
    start_ci_right = 100
    end_ci_left = -100
    end_ci_right = 100

    #: Model pseudo-attribute, not stored in database.  Instead, ``set_id`` is stored.
    variant_set = factory.SubFactory(StructuralVariantSetFactory)
    #: The actual reference to the ``StructuralVariantSet``.
    set_id = factory.LazyAttribute(lambda o: o.variant_set.id)
    #: Model pseudo-attribute, not stored in database.  Instead ``case_id`` is stored.
    case = factory.LazyAttribute(lambda obj: Case.objects.get(id=obj.case_id))
    #: The actual foreign key to the ``Case``.
    case_id = factory.SelfAttribute("variant_set.case.id")

    caller = "DELLYv4001"
    sv_type = "DEL"
    sv_sub_type = "DEL"

    @factory.lazy_attribute
    def genotype(self):
        # Properties of GT field for deletions.
        gt_properties = {
            "0/0": {
                "gq": 50,  # genotype quality
                "pec": 20,  # paired-end coverage
                "pev": 00,  # paired-end variant count
                "src": 20,  # split read coverage
                "srv": 00,  # split read variant count
                "cn": 2,  # copy number
                "anc": 1.0,  # average normalized coverage
                "amq": 50,  # average mapping quality
            },
            "0/1": {
                "gq": 50,  # genotype quality
                "pec": 20,  # paired-end coverage
                "pev": 10,  # paired-end variant count
                "src": 20,  # split read coverage
                "srv": 10,  # split read variant count
                "cn": 1,  # copy number
                "anc": 0.5,  # average normalized coverage
                "amq": 50,  # average mapping quality
            },
            "1/1": {
                "gq": 50,  # genotype quality
                "pec": 20,  # paired-end coverage
                "pev": 20,  # paired-end variant count
                "src": 20,  # split read coverage
                "srv": 20,  # split read variant count
                "cn": 0,  # copy number
                "anc": 0.0,  # average normalized coverage
                "amq": 50,  # average mapping quality
            },
        }
        result = {}
        for line, gt in zip(self.case.pedigree, self.genotypes()):
            result[line["patient"]] = {"gt": gt, **gt_properties[gt]}
        return result

    @factory.lazy_attribute
    def num_hom_alt(self):
        return len([k for k, v in self.genotype.items() if v["gt"] in ("1/1", "1|1")])

    @factory.lazy_attribute
    def num_hom_ref(self):
        return len([k for k, v in self.genotype.items() if v["gt"] in ("0/0", "0|0")])

    @factory.lazy_attribute
    def num_het(self):
        return len([k for k, v in self.genotype.items() if v["gt"] in ("0/1", "0|1", "1/0", "1|0")])

    @factory.lazy_attribute
    def num_hemi_ref(self):
        return len([k for k, v in self.genotype.items() if v["gt"] == "0"])

    @factory.lazy_attribute
    def num_hemi_alt(self):
        return len([k for k, v in self.genotype.items() if v["gt"] == "1"])

    @factory.lazy_attribute
    def bin(self):
        if self.chromosome == self.chromosome2:
            return binning.assign_bin(self.start, self.end)
        else:
            return binning.assign_bin(self.start, self.start + 1)

    @factory.lazy_attribute
    def bin2(self):
        if self.chromosome == self.chromosome2:
            return binning.assign_bin(self.start, self.end)
        else:
            return binning.assign_bin(self.end, self.end + 1)

    @factory.lazy_attribute
    def info(self):
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


class StructuralVariantGeneAnnotationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StructuralVariantGeneAnnotation
        exclude = ["sv", "case", "variant_set"]

    #: Model pseudo-attribute, not stored in database.  Instead, ``sv_uuid`` is stored.
    sv = factory.SubFactory(StructuralVariantFactory)
    #: The actual reference to the StructuralVariant.
    sv_uuid = factory.LazyAttribute(lambda o: o.sv.sv_uuid)

    #: Model pseudo-attribute, not stored in database.  Instead, ``set_id`` is stored.
    variant_set = factory.LazyAttribute(lambda o: StructuralVariantSet.objects.get(pk=o.sv.set_id))
    #: The actual reference to the ``StructuralVariantSet``.
    set_id = factory.SelfAttribute("sv.set_id")
    #: Model pseudo-attribute, not stored in database.  Instead ``case_id`` is stored.
    case = factory.SelfAttribute("variant_set.case")
    #: The actual foreign key to the ``Case``.
    case_id = factory.SelfAttribute("variant_set.case.id")

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

    @factory.lazy_attribute
    def bin(self):
        return binning.assign_bin(self.end, self.end + 1)

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
    flag_no_disease_association = False
    flag_segregates = False
    flag_doesnt_segregate = False

    flag_molecular = "empty"
    flag_visual = "empty"
    flag_validation = "empty"
    flag_phenotype_match = "empty"
    flag_summary = "empty"


class BackgroundSvSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BackgroundSvSet

    genomebuild = "GRCh37"
    varfish_version = "1.2.0"
    state = "active"


class BackgroundSvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BackgroundSv

    bg_sv_set = factory.SubFactory(BackgroundSvSetFactory)

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    chromosome_no = factory.Iterator(list(range(1, 25)))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    chromosome2 = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    chromosome_no2 = factory.Iterator(list(range(1, 25)))
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)
    pe_orientation = "3to5"
    sv_type = "DEL"
    bin = factory.LazyAttribute(lambda obj: binning.assign_bin(obj.start, obj.end))

    src_count = 1
    carriers = 1
    carriers_het = 1
    carriers_hom = 0
    carriers_hemi = 0


@attrs.define(auto_attribs=True)
class SvQuerySettingsFactory:
    """Factory for generating SV query settings JSON-compatible dicts based on python-attrs."""

    names: typing.List[str] = attrs.field(factory=list, repr=False)


def as_dict_no_names(attrs_obj_with_names):
    """Helper function that returns an ``attrs`` object as a dict without the ``names`` attribute."""
    return attrs.asdict(attrs_obj_with_names, filter=lambda a, _v: a.name not in ["names"])


class SvQueryFactory(factory.django.DjangoModelFactory):
    """Factory for ``SvQuery`` model."""

    class Meta:
        model = SvQuery

    case = factory.SubFactory(CaseFactory)
    query_settings = factory.LazyAttribute(
        lambda o: as_dict_no_names(SvQuerySettingsFactory(names=o.case.get_members()))
    )


@attrs.define
class SvQueryResultsPayloadFactory:
    """Factory for generating SV query results JSON-compatible dicts based on python-attrs."""

    names: typing.List[str] = attrs.field(factory=list, repr=False)

    rows: typing.List[typing.Any] = attrs.field(factory=list)


class SvQueryResultSetFactory(factory.django.DjangoModelFactory):
    """Factory for ``SvQueryResult`` model."""

    class Meta:
        model = SvQueryResultSet

    svquery = factory.SubFactory(SvQueryFactory)

    start_time = FuzzyDateTime(timezone.now())
    end_time = factory.LazyAttribute(lambda o: o.start_time + datetime.timedelta(hours=1))
    elapsed_seconds = factory.LazyAttribute(lambda o: (o.end_time - o.start_time).total_seconds())
    result_row_count = 0


class SvQueryResultRowFactory(factory.django.DjangoModelFactory):
    """Factory for ``SvQueryResultRow`` model."""

    class Meta:
        model = SvQueryResultRow

    svqueryresultset = factory.SubFactory(SvQueryResultSetFactory)

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    chromosome_no = factory.Iterator(list(range(1, 25)))
    chromosome2 = factory.LazyAttribute(lambda obj: obj.chromosome)
    chromosome_no2 = factory.LazyAttribute(lambda obj: obj.chromosome_no)

    @factory.lazy_attribute
    def bin(self):
        if self.chromosome == self.chromosome2:
            return binning.assign_bin(self.start, self.end)
        else:
            return binning.assign_bin(self.start, self.start + 1)

    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)
    pe_orientation = "3to5"

    sv_type = "DEL"
    sv_sub_type = "DEL"

    payload = {}


class FilterSvBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``FilterSvBgJob`` model."""

    class Meta:
        model = FilterSvBgJob
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    case = factory.SubFactory(CaseFactory)
    project = factory.LazyAttribute(lambda o: o.case.project)
    bg_job = factory.SubFactory(
        BackgroundJobFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )
    svquery = factory.SubFactory(
        SvQueryFactory,
        case=factory.SelfAttribute("factory_parent.case"),
        user=factory.SelfAttribute("factory_parent.user"),
    )


class BackgroundJobFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``bgjobs.BackgroundJob`` objects."""

    class Meta:
        model = BackgroundJob

    user = None
    project = factory.SubFactory(ProjectFactory)
