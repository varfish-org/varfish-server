"""Factory Boy factory classes for ``variants``."""

import datetime
import typing
import uuid

import attr
from bgjobs.tests.factories import BackgroundJobFactory
import binning
from django.utils import timezone
import factory
from factory.fuzzy import FuzzyDateTime
from projectroles.models import SODAR_CONSTANTS, RemoteSite

from config.settings.base import VARFISH_CADD_SUBMISSION_VERSION

from ..models import (
    AcmgCriteriaRating,
    CaddSubmissionBgJob,
    Case,
    CaseAwareProject,
    CaseComments,
    CaseGeneAnnotationEntry,
    CasePhenotypeTerms,
    CaseVariantStats,
    ChromosomePresets,
    DeleteCaseBgJob,
    DistillerSubmissionBgJob,
    ExportFileBgJob,
    ExportFileJobResult,
    ExportProjectCasesFileBgJob,
    ExportProjectCasesFileBgJobResult,
    FilterBgJob,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    ProjectCasesFilterBgJob,
    ProjectCasesSmallVariantQuery,
    QualityPresets,
    QuickPresets,
    SampleVariantStatistics,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantQuery,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
    SmallVariantSet,
    SmallVariantSummary,
    SyncCaseListBgJob,
)


@attr.s(auto_attribs=True)
class FormDataFactoryBase:
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
    mtdb_enabled: bool = False
    mtdb_count: int = 0
    mtdb_frequency: int = 0.0
    helixmtdb_enabled: bool = False
    helixmtdb_hom_count: int = 0
    helixmtdb_het_count: int = 0
    helixmtdb_frequency: int = 0.0
    mitomap_enabled: bool = False
    mitomap_count: int = 0
    mitomap_frequency: int = 0.0
    transcripts_coding: bool = True
    transcripts_noncoding: bool = True
    require_in_clinvar: bool = False
    clinvar_include_benign: bool = False
    clinvar_include_likely_benign: bool = False
    clinvar_include_uncertain_significance: bool = False
    clinvar_include_likely_pathogenic: bool = False
    clinvar_include_pathogenic: bool = False
    compound_recessive_indices: typing.Dict[str, str] = {}
    recessive_indices: typing.Dict[str, str] = {}
    cohort: uuid.UUID = ""

    # This is a dummy attribute to generate the name-dependent fields.
    # It is removed after initialization.
    names: typing.List[str] = []

    def __attrs_post_init__(self):
        for name in self.names:
            self.__dict__.update(
                {
                    "%s_fail" % name: "ignore",
                    "%s_gt" % name: "any",
                    "%s_dp_het" % name: 0,
                    "%s_dp_hom" % name: 0,
                    "%s_ab" % name: 0,
                    "%s_gq" % name: 0,
                    "%s_ad" % name: 0,
                    "%s_ad_max" % name: "",
                }
            )
        delattr(self, "names")


@attr.s(auto_attribs=True)
class ProcessedFormDataFactory(FormDataFactoryBase):
    """Factory for the filter form data after cleaning.

    The genotype filters are missing as they are added when running the test to fetch the current patient name that is
    unknown up to then. Same holds true for the case sodar_uuid.
    """

    effects: typing.List[str] = attr.Factory(lambda: list(["synonymous_variant"]))
    gene_blocklist: typing.List[str] = attr.Factory(list)
    genomic_region: typing.List[str] = attr.Factory(list)
    gene_allowlist: typing.List[str] = attr.Factory(list)


@attr.s(auto_attribs=True)
class ResubmitFormDataFactory(ProcessedFormDataFactory):
    result_rows_limit: int = 80
    submit: str = "display"
    file_type: str = "tsv"
    export_flags: bool = True
    export_comments: bool = True

    def __attrs_post_init__(self):
        for name in self.names:
            self.__dict__.update({"%s_export" % name: True})
        super().__attrs_post_init__()


@attr.s(auto_attribs=True)
class FormDataFactory(FormDataFactoryBase):
    """Factory for the data transferred from the filter form."""

    effect_coding_transcript_intron_variant: bool = True
    effect_complex_substitution: bool = True
    effect_direct_tandem_duplication: bool = True
    effect_disruptive_inframe_deletion: bool = True
    effect_disruptive_inframe_insertion: bool = True
    effect_downstream_gene_variant: bool = True
    effect_exon_loss_variant: bool = True
    effect_feature_truncation: bool = True
    effect_5_prime_UTR_exon_variant: bool = True
    effect_5_prime_UTR_intron_variant: bool = True
    effect_frameshift_elongation: bool = True
    effect_frameshift_truncation: bool = True
    effect_frameshift_variant: bool = True
    effect_inframe_deletion: bool = True
    effect_inframe_insertion: bool = True
    effect_intergenic_variant: bool = True
    effect_internal_feature_elongation: bool = True
    effect_missense_variant: bool = True
    effect_mnv: bool = True
    effect_non_coding_transcript_exon_variant: bool = True
    effect_non_coding_transcript_intron_variant: bool = True
    effect_splice_acceptor_variant: bool = True
    effect_splice_donor_variant: bool = True
    effect_splice_region_variant: bool = True
    effect_start_lost: bool = True
    effect_stop_gained: bool = True
    effect_stop_lost: bool = True
    effect_stop_retained_variant: bool = True
    effect_structural_variant: bool = True
    effect_synonymous_variant: bool = True
    effect_3_prime_UTR_exon_variant: bool = True
    effect_3_prime_UTR_intron_variant: bool = True
    effect_transcript_ablation: bool = True
    effect_upstream_gene_variant: bool = True
    gene_blocklist: str = ""
    genomic_region: str = ""
    gene_allowlist: str = ""
    flag_bookmarked: bool = True
    flag_incidental: bool = True
    flag_candidate: bool = True
    flag_final_causative: bool = True
    flag_for_validation: bool = True
    flag_no_disease_association: bool = True
    flag_segregates: bool = True
    flag_doesnt_segregate: bool = True
    flag_phenotype_match_empty: bool = True
    flag_phenotype_match_negative: bool = True
    flag_phenotype_match_positive: bool = True
    flag_phenotype_match_uncertain: bool = True
    flag_simple_empty: bool = True
    flag_summary_empty: bool = True
    flag_summary_negative: bool = True
    flag_summary_positive: bool = True
    flag_summary_uncertain: bool = True
    flag_validation_empty: bool = True
    flag_validation_negative: bool = True
    flag_validation_positive: bool = True
    flag_validation_uncertain: bool = True
    flag_visual_empty: bool = True
    flag_visual_negative: bool = True
    flag_visual_positive: bool = True
    flag_visual_uncertain: bool = True
    flag_molecular_empty: bool = True
    flag_molecular_negative: bool = True
    flag_molecular_positive: bool = True
    flag_molecular_uncertain: bool = True
    prio_enabled: bool = False
    prio_algorithm: str = ""
    prio_hpo_terms: str = ""
    prio_gm: str = ""
    photo_file: str = ""
    patho_enabled: bool = False
    gm_enabled: bool = False
    pedia_enabled: bool = False
    patho_score: str = ""
    file_type: str = "tsv"
    export_flags: bool = True
    export_comments: bool = True
    result_rows_limit: int = 80
    training_mode: bool = False
    submit: str = "display"
    filter_job_uuid: uuid.UUID = ""

    def __attrs_post_init__(self):
        for name in self.names:
            self.__dict__.update({"%s_export" % name: True})
        super().__attrs_post_init__()


@attr.s(auto_attribs=True)
class ChromosomalPositionFormDataFactoryBase:
    release: str = "GRCh37"
    chromosome: str = None
    start: int = None
    end: int = None
    bin: int = None
    reference: str = None
    alternative: str = None


@attr.s(auto_attribs=True)
class FlagsFormDataFactoryBase:
    flag_bookmarked: bool = True
    flag_incidental: bool = True
    flag_candidate: bool = False
    flag_final_causative: bool = False
    flag_for_validation: bool = False
    flag_no_disease_association: bool = False
    flag_segregates: bool = False
    flag_doesnt_segregate: bool = False
    flag_visual: str = "empty"
    flag_molecular: str = "empty"
    flag_validation: str = "empty"
    flag_phenotype_match: str = "empty"
    flag_summary: str = "empty"


@attr.s(auto_attribs=True)
class MultiSmallVariantFlagsAndCommentFormDataFactory(FlagsFormDataFactoryBase):
    text: str = "Comment X"


class RemoteSiteFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``projectroles`` ``RemoteSite`` objects."""

    class Meta:
        model = RemoteSite

    name = factory.Sequence(lambda n: "Remote Site %d" % n)
    url = factory.Sequence(lambda n: "https://sodar-%d.example.com" % n)
    mode = SODAR_CONSTANTS["SITE_MODE_TARGET"]
    description = factory.Sequence(lambda n: "This is remote site #%d" % n)
    secret = factory.Sequence(lambda n: "secret-%d" % n)
    user_display = True


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``projectroles`` ``Project`` objects."""

    class Meta:
        model = CaseAwareProject

    title = factory.Sequence(lambda n: "Project %03d" % n)
    type = SODAR_CONSTANTS["PROJECT_TYPE_PROJECT"]
    parent = None
    description = factory.Sequence(lambda n: "This is project %03d" % n)


class CoreCaseFactory(factory.django.DjangoModelFactory):
    """Base class for CoreCase factories."""

    class Params:
        #: The sex of the index
        sex = 1  # 1: unaffected, 2: affected
        #: The structure can be "singleton", "trio" or "quartet" at the moment.
        structure = "singleton"
        #: The supported inheritance patterns are "denovo", "dominant", and "recessive" at the
        #: moment.  This is only used for non-singletons.  When dominant, the father will be
        #: affected.
        inheritance = "denovo"

    sodar_uuid = factory.Faker("uuid4")
    date_created = factory.LazyFunction(datetime.datetime.now)
    date_modified = factory.LazyFunction(datetime.datetime.now)

    release = factory.Sequence(lambda n: "GRCh%d" % (37 + n % 2))
    name = factory.LazyAttributeSequence(lambda o, n: "case %03d: %s" % (n, o.structure))
    index = factory.Sequence(lambda n: "index_%03d-N1-DNA1-WES1" % n)
    project = factory.SubFactory(ProjectFactory)

    @factory.lazy_attribute_sequence
    def pedigree(self, n):
        if self.structure not in (
            "singleton",
            "duo",
            "trio",
            "trio-noparents",
            "quartet",
            "quintet",
        ):
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
        elif self.structure == "duo":
            father = "father_%03d-N1-DNA1-WES1" % n
            return [
                {
                    "patient": self.index,
                    "father": father,
                    "mother": "0",
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
            ]
        elif self.structure == "trio":
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
        elif self.structure == "trio-noparents":
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
                    "has_gt_entries": False,
                },
                {
                    "patient": mother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": False,
                },
            ]
        elif self.structure == "quartet":
            # Father - Mother - Siblings
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            sibling = "sibling_%03d-N1-DNA1-WES1" % n
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
                    "patient": sibling,
                    "father": father,
                    "mother": mother,
                    "sex": (self.sex % 2) + 1,  # make sibling the opposite sex
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
        else:  # self.structure == "quintet":
            # Index - Father - Mother - Grandfather - Grandmother
            father = "father_%03d-N1-DNA1-WES1" % n
            mother = "mother_%03d-N1-DNA1-WES1" % n
            grandfather = "grandfather_%03d-N1-DNA1-WES1" % n
            grandmother = "grandmother_%03d-N1-DNA1-WES1" % n
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
                    "father": grandfather,
                    "mother": grandmother,
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
                {
                    "patient": grandfather,
                    "father": "0",
                    "mother": "0",
                    "sex": 1,  # always male
                    "affected": 2 if self.inheritance == "dominant" else 1,
                    "has_gt_entries": True,
                },
                {
                    "patient": grandmother,
                    "father": "0",
                    "mother": "0",
                    "sex": 2,  # always female
                    "affected": 1,  # never affected
                    "has_gt_entries": True,
                },
            ]


class CaseFactory(CoreCaseFactory):
    """Factory for creating ``Case`` objects."""

    latest_variant_set = None
    latest_structural_variant_set = None
    pedigree_obj = factory.RelatedFactory(
        "cases.tests.factories.PedigreeFactory", factory_related_name="case"
    )

    class Meta:
        model = Case


class CasePhenotypeTermsFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``CasePhenotypeTerms`` objects."""

    class Meta:
        model = CasePhenotypeTerms

    case = factory.SubFactory(CaseFactory)
    individual = factory.LazyAttribute(lambda o: o.case.get_members()[0])
    terms = factory.Sequence(lambda n: ["HP:%07d" % n, "MIM:%7d" % n, "ORPHA:%7d" % n])


class CaseCommentsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseComments

    case = factory.SubFactory(CaseFactory)
    user = None  # TODO Wait for SODAR core to offer a user factory
    comment = "This is a comment."


class SmallVariantQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SmallVariantQuery

    case = factory.SubFactory(CaseFactory)
    query_settings = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.case.get_members()))
    )
    query_settings_version_major = 0
    query_settings_version_minor = 0
    name = factory.Sequence(lambda n: "SmallVariantQuery%d" % n)
    public = False


class ProjectCasesSmallVariantQueryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProjectCasesSmallVariantQuery

    project = factory.SubFactory(ProjectFactory)
    query_settings = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.project.get_members()))
    )
    name = factory.Sequence(lambda n: "ProjectCasesSmallVariantQuery%d" % n)
    public = False


class CaseWithVariantSetFactory:
    """Factory for a ``Case`` with a variant set for both small and structural variants"""

    @staticmethod
    def get(variant_set_type=None, **kwargs):
        from svs.tests.factories import StructuralVariantSetFactory

        state = kwargs.pop("state") if kwargs.get("state") else None
        case = CaseFactory(**kwargs)
        variant_set_kwargs = {"case": case}
        if state:
            variant_set_kwargs["state"] = state

        if variant_set_type == "small" or variant_set_type is None:
            case.latest_variant_set = SmallVariantSetFactory(**variant_set_kwargs)
        if variant_set_type == "structural" or variant_set_type is None:
            case.latest_structural_variant_set = StructuralVariantSetFactory(**variant_set_kwargs)
        case.save()
        return case, case.latest_variant_set, case.latest_structural_variant_set


def default_genotypes():
    """Build default genotype pattern (het. in first, wild-type otherwise)."""
    yield {"gt": "0/1", "ad": 15, "dp": 30, "gq": 99}
    while True:
        yield {"gt": "0/0", "ad": 0, "dp": 30, "gq": 99}


def count_gt(*gts):
    """Return counter for the given genotypes."""

    def result(o):
        return len([x["gt"] for x in o.genotype.values() if x["gt"] in gts])

    return result


class SmallVariantSetFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SmallVariantSet`` objects."""

    class Meta:
        model = SmallVariantSet

    case = factory.SubFactory(CaseFactory)
    # Fix the state of all created SmallVariantSet objects to ``"active"``.
    state = "active"


CHROMOSOME_LIST_TESTING = [str(chrom) for chrom in list(range(1, 23)) + ["X", "Y"]]
CHROMOSOME_MAPPING = {str(chrom): i + 1 for i, chrom in enumerate(list(range(1, 23)) + ["X", "Y"])}
CHROMOSOME_MAPPING.update({f"chr{chrom}": i for chrom, i in CHROMOSOME_MAPPING.items()})


class SmallVariantFactory(factory.django.DjangoModelFactory):
    """Factory for creating ``SmallVariant`` objects."""

    class Meta:
        model = SmallVariant
        exclude = ["case", "variant_set"]

    class Params:
        #: The genotypes to create, by default only first is het. the rest is wild-type.
        genotypes = default_genotypes

    release = "GRCh37"
    chromosome = factory.Iterator(CHROMOSOME_LIST_TESTING)
    chromosome_no = factory.LazyAttribute(lambda o: CHROMOSOME_MAPPING[o.chromosome])
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    var_type = "snv"
    #: Model pseudo-attribute, not stored in database.  Instead, ``case_id`` is stored.  Also, the case is taken
    #: from the ``SmallVariantSet`` that is auto-created via a ``SubFactory``.
    case = factory.PostGeneration(
        lambda obj, create, extracted, **kwargs: Case.objects.get(id=obj.case_id)
    )
    #: The actual foreign key to the ``Case``.
    case_id = factory.SelfAttribute("variant_set.case.id")
    #: Model pseudo-attribute, not stored in database.  Instead, ``set_id`` is stored.
    variant_set = factory.SubFactory(SmallVariantSetFactory)
    #: The actual reference to the ``SmallVariantSet``.
    set_id = factory.LazyAttribute(lambda o: o.variant_set.id)

    @factory.lazy_attribute
    def genotype(self):
        """Generate genotype JSON field from already set ``self.case``."""
        return {
            line["patient"]: gt
            for line, gt in zip(self.variant_set.case.pedigree, self.genotypes())
        }

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()

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
    refseq_exon_dist = 0
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    ensembl_transcript_id = factory.Sequence(lambda n: "ENST%d" % n)
    ensembl_transcript_coding = True
    ensembl_hgvs_c = "c.123C>T"
    ensembl_hgvs_p = "p.I2T"
    ensembl_effect = factory.List(["synonymous_variant"])
    ensembl_exon_dist = 0


class SmallVariantSummaryFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantSummary`` model."""

    class Meta:
        model = SmallVariantSummary

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    count_het = 0
    count_hom_ref = 0
    count_hom_alt = 0
    count_hemi_ref = 0
    count_hemi_alt = 0

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class SmallVariantQueryResultSetFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantQueryResult`` model."""

    class Meta:
        model = SmallVariantQueryResultSet

    smallvariantquery = factory.SubFactory(SmallVariantQueryFactory)
    case = None

    start_time = FuzzyDateTime(timezone.now())
    end_time = factory.LazyAttribute(lambda o: o.start_time + datetime.timedelta(hours=1))
    elapsed_seconds = factory.LazyAttribute(lambda o: (o.end_time - o.start_time).total_seconds())
    result_row_count = 0


class SmallVariantQueryResultRowFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantQueryResultRow`` model."""

    class Meta:
        model = SmallVariantQueryResultRow

    smallvariantqueryresultset = factory.SubFactory(SmallVariantQueryResultSetFactory)

    release = "GRCh37"
    chromosome = factory.Iterator(list(map(str, range(1, 23))) + ["X", "Y"])
    chromosome_no = factory.Iterator(list(range(1, 25)))

    @factory.lazy_attribute
    def bin(self):
        return binning.assign_bin(self.start - 1, self.end)

    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.Sequence(lambda n: (n + 1) * 100 + 100)

    payload = {}


class FilterBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``FilterBgJob`` model."""

    class Meta:
        model = FilterBgJob
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
    smallvariantquery = factory.SubFactory(
        SmallVariantQueryFactory,
        case=factory.SelfAttribute("factory_parent.case"),
        user=factory.SelfAttribute("factory_parent.user"),
    )


class ProjectCasesFilterBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``ProjectCasesFilterBgJob`` model."""

    class Meta:
        model = ProjectCasesFilterBgJob
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    project = factory.SubFactory(ProjectFactory)
    cohort = None
    bg_job = factory.SubFactory(
        BackgroundJobFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )
    projectcasessmallvariantquery = factory.SubFactory(
        ProjectCasesSmallVariantQueryFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )


class DistillerSubmissionBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``DistillerSubmissionBgJob`` model."""

    class Meta:
        model = DistillerSubmissionBgJob
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
    query_args = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.case.get_members()))
    )


class CaddSubmissionBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``CaddSubmissionBgJob`` model."""

    class Meta:
        model = CaddSubmissionBgJob
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
    query_args = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.case.get_members()))
    )
    cadd_version = VARFISH_CADD_SUBMISSION_VERSION


class ExportFileBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``ExportFileBgJob`` model."""

    class Meta:
        model = ExportFileBgJob
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
    query_args = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.case.get_members()))
    )
    file_type = "tsv"


class ExportFileJobResultFactory(factory.django.DjangoModelFactory):
    """Factory for ``ExportFileJobResult`` model."""

    class Meta:
        model = ExportFileJobResult
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    job = factory.SubFactory(
        ExportFileBgJobFactory, user=factory.SelfAttribute("factory_parent.user")
    )
    payload = b"Testcontent"
    expiry_time = timezone.now()


class ExportProjectCasesFileBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``ExportProjectCasesFileBgJobFactory`` model."""

    class Meta:
        model = ExportProjectCasesFileBgJob
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    project = factory.SubFactory(ProjectFactory)
    bg_job = factory.SubFactory(
        BackgroundJobFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )
    query_args = factory.LazyAttribute(
        lambda o: vars(ResubmitFormDataFactory(names=o.project.get_members()))
    )
    file_type = "tsv"


class ExportProjectCasesFileBgJobResultFactory(factory.django.DjangoModelFactory):
    """Factory for ``ExportProjectCasesFileJobResult`` model."""

    class Meta:
        model = ExportProjectCasesFileBgJobResult
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    job = factory.SubFactory(
        ExportProjectCasesFileBgJobFactory, user=factory.SelfAttribute("factory_parent.user")
    )
    payload = b"Testcontent"
    expiry_time = timezone.now()


class SmallVariantFlagsFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantFlagsFactory`` model."""

    class Meta:
        model = SmallVariantFlags

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    case = factory.SubFactory(CaseFactory)
    flag_bookmarked = True
    flag_candidate = False
    flag_incidental = False
    flag_final_causative = False
    flag_for_validation = False
    flag_no_disease_association = False
    flag_segregates = False
    flag_doesnt_segregate = False
    flag_molecular = ""
    flag_visual = ""
    flag_validation = ""
    flag_phenotype_match = ""
    flag_summary = ""

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class AcmgCriteriaRatingFactory(factory.django.DjangoModelFactory):
    """Factory for ``AcmgCriteriaRating`` model."""

    class Meta:
        model = AcmgCriteriaRating

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    case = factory.SubFactory(CaseFactory)

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class SmallVariantCommentFactory(factory.django.DjangoModelFactory):
    """Factory for ``SmallVariantComment`` model."""

    class Meta:
        model = SmallVariantComment

    release = "GRCh37"
    chromosome = factory.Iterator(list(CHROMOSOME_MAPPING.keys()))
    start = factory.Sequence(lambda n: (n + 1) * 100)
    end = factory.LazyAttribute(lambda o: o.start + len(o.reference) - len(o.alternative))
    bin = 0
    reference = factory.Iterator("ACGT")
    alternative = factory.Iterator("CGTA")
    user = None
    text = factory.Sequence(lambda n: "Comment %d" % n)
    case = factory.SubFactory(CaseFactory)

    @factory.post_generation
    def fix_bins(obj, *args, **kwargs):
        obj.bin = binning.assign_bin(obj.start - 1, obj.end)
        obj.save()


class CaseVariantStatsFactory(factory.django.DjangoModelFactory):
    """Factory for ``CaseVariantStatsFactory`` model."""

    class Meta:
        model = CaseVariantStats

    variant_set = factory.SubFactory(SmallVariantSetFactory)


class SampleVariantStatisticsFactory(factory.django.DjangoModelFactory):
    """Factory for ``SampleVariantStatisticsFactory`` model."""

    class Meta:
        model = SampleVariantStatistics
        exclude = ["variant_set"]

    stats = factory.SubFactory(
        CaseVariantStatsFactory, variant_set=factory.SelfAttribute("factory_parent.variant_set")
    )
    sample_name = factory.Sequence(lambda n: "Donor%d" % n)
    ontarget_transitions = 1
    ontarget_transversions = 1
    ontarget_snvs = 1
    ontarget_indels = 1
    ontarget_mnvs = 1
    ontarget_effect_counts = {}
    ontarget_indel_sizes = {}
    ontarget_dps = {}
    ontarget_dp_quantiles = [0.1, 0.2, 0.3, 0.4, 0.5]
    het_ratio = 1.0
    chrx_het_hom = 1.0
    # Dummy argument to pass to CaseVariantStatsFactory
    variant_set = None


class DeleteCaseBgJobFactory(factory.django.DjangoModelFactory):
    """Factory for ``DeleteCaseBgJob`` model."""

    class Meta:
        model = DeleteCaseBgJob
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


class SyncCaseListBgJobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SyncCaseListBgJob
        exclude = ["user"]

    # Dummy argument ``user`` to pass to subfactory BackgroundJobFactory
    user = None
    project = factory.LazyAttribute(lambda o: o.case.project)
    bg_job = factory.SubFactory(
        BackgroundJobFactory,
        project=factory.SelfAttribute("factory_parent.project"),
        user=factory.SelfAttribute("factory_parent.user"),
    )


class CaseGeneAnnotationEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CaseGeneAnnotationEntry

    case = factory.SubFactory(CaseFactory)
    gene_symbol = factory.Sequence(lambda n: "GENE%d" % n)
    entrez_id = factory.Sequence(lambda n: "%d" % n)
    ensembl_gene_id = factory.Sequence(lambda n: "ENSG%d" % n)
    annotation = factory.Sequence(
        lambda n: {
            "percentage_at_20x": 90 + n % 10,
            "level": "info",
            "message": f"This is a test message {n}",
        }
    )


class PresetSetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PresetSet

    project = factory.SubFactory(ProjectFactory)
    label = factory.Sequence(lambda n: f"Preset Set #{n}")
    version_major = 1
    version_minor = 1
    state = "draft"
    database = factory.Sequence(lambda n: ["refseq", "ensembl"][n % 2])


class FrequencyPresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FrequencyPresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Frequency Presets #{n}")


class ImpactPresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImpactPresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Impact Presets #{n}")
    max_exon_dist = None
    effects = ["synonymous_variant"]


class QualityPresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QualityPresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Quality Presets #{n}")
    fail = "drop-variant"


class ChromosomePresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ChromosomePresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Chromosome Presets #{n}")


class FlagsEtcPresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FlagsEtcPresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Flags etc. Presets #{n}")


class QuickPresetsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuickPresets

    presetset = factory.SubFactory(PresetSetFactory)
    label = factory.Sequence(lambda n: f"Quick Presets #{n}")

    inheritance = factory.Sequence(lambda n: ["de_novo", "dominant", "recessive"][n % 3])
    frequency = factory.SubFactory(
        FrequencyPresetsFactory, presetset=factory.SelfAttribute("..presetset")
    )
    impact = factory.SubFactory(
        ImpactPresetsFactory, presetset=factory.SelfAttribute("..presetset")
    )
    quality = factory.SubFactory(
        QualityPresetsFactory, presetset=factory.SelfAttribute("..presetset")
    )
    chromosome = factory.SubFactory(
        ChromosomePresetsFactory, presetset=factory.SelfAttribute("..presetset")
    )
    flagsetc = factory.SubFactory(
        FlagsEtcPresetsFactory, presetset=factory.SelfAttribute("..presetset")
    )
