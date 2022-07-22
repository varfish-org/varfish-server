import contextlib
from itertools import chain
import typing

import attr

from sqlalchemy.dialects.postgresql.array import OVERLAP
from sqlalchemy.sql.functions import GenericFunction, ReturnTypeFromArgs
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sqlalchemy import Table, true, column, union, literal_column, delete, tuple_
from sqlalchemy.sql import select, func, and_, not_, or_, cast
from sqlalchemy.types import ARRAY, VARCHAR, Integer, Float
import sqlparse

from clinvar.models import Clinvar
from cohorts.models import Cohort
from conservation.models import KnowngeneAA
from dbsnp.models import Dbsnp
from extra_annos.models import ExtraAnno
from frequencies.models import MtDb, HelixMtDb, Mitomap
from geneinfo.models import (
    Hgnc,
    RefseqToHgnc,
    Acmg,
    GeneIdToInheritance,
    GnomadConstraints,
    ExacConstraints,
    MgiMapping,
    RefseqToGeneSymbol,
    EnsemblToGeneSymbol,
    GeneIdInHpo,
)
from hgmd.models import HgmdPublicLocus
from svs.models import StructuralVariant, StructuralVariantGeneAnnotation
from variants.models import (
    Case,
    SmallVariant,
    SmallVariantSummary,
    SmallVariantFlags,
    SmallVariantComment,
    AcmgCriteriaRating,
    SmallVariantSet,
)
from variants.forms import FILTER_FORM_TRANSLATE_INHERITANCE
from variants.helpers import get_meta


class _ArrayCatAgg(ReturnTypeFromArgs):
    name = "array_cat_agg"
    identifier = "array_cat_agg"


class _ArrayAppend(GenericFunction):
    name = "array_append"
    identifier = "array_append"
    type = ARRAY(VARCHAR())


@attr.s(frozen=True, auto_attribs=True)
class QueryParts:
    fields: typing.List[typing.Any] = attr.Factory(list)
    selectable: typing.Any = None
    conditions: typing.List[typing.Any] = attr.Factory(list)

    def to_stmt(self, order_by=None):
        result = select(self.fields).select_from(self.selectable).where(and_(*self.conditions))
        return result.order_by(*(order_by or []))

    def and_where(self, *conditions):
        return attr.evolve(self, conditions=chain(self.conditions, conditions))


def small_variant_query(_self, kwargs):
    return QueryParts(
        fields=[
            SmallVariant.sa.id,
            SmallVariant.sa.release,
            SmallVariant.sa.chromosome,
            SmallVariant.sa.chromosome_no,
            SmallVariant.sa.start,
            SmallVariant.sa.end,
            SmallVariant.sa.bin,
            SmallVariant.sa.reference,
            SmallVariant.sa.alternative,
            SmallVariant.sa.ensembl_gene_id.label("ensembl_gene_id"),
            SmallVariant.sa.refseq_gene_id.label("entrez_id"),
            SmallVariant.sa.refseq_transcript_id,
            SmallVariant.sa.refseq_hgvs_c,
            SmallVariant.sa.exac_frequency,
            SmallVariant.sa.gnomad_exomes_frequency,
            SmallVariant.sa.gnomad_genomes_frequency,
            SmallVariant.sa.thousand_genomes_frequency,
            SmallVariant.sa.exac_homozygous,
            SmallVariant.sa.gnomad_exomes_homozygous,
            SmallVariant.sa.gnomad_genomes_homozygous,
            SmallVariant.sa.thousand_genomes_homozygous,
            SmallVariant.sa.exac_heterozygous,
            SmallVariant.sa.gnomad_exomes_heterozygous,
            SmallVariant.sa.gnomad_genomes_heterozygous,
            SmallVariant.sa.thousand_genomes_heterozygous,
            SmallVariant.sa.genotype,
            SmallVariant.sa.set_id,
            SmallVariant.sa.in_clinvar,
            SmallVariant.sa.var_type,
            (SmallVariant.sa.ensembl_effect != SmallVariant.sa.refseq_effect).label(
                "effect_ambiguity"
            ),
            getattr(SmallVariant.sa, "%s_hgvs_p" % kwargs["database_select"], None).label("hgvs_p"),
            getattr(SmallVariant.sa, "%s_hgvs_c" % kwargs["database_select"], None).label("hgvs_c"),
            getattr(
                SmallVariant.sa, "%s_transcript_coding" % kwargs["database_select"], None
            ).label("transcript_coding"),
            getattr(SmallVariant.sa, "%s_effect" % kwargs["database_select"], None).label("effect"),
            getattr(SmallVariant.sa, "%s_gene_id" % kwargs["database_select"], None).label(
                "gene_id"
            ),
            getattr(SmallVariant.sa, "%s_transcript_id" % kwargs["database_select"], None).label(
                "transcript_id"
            ),
            getattr(SmallVariant.sa, "%s_exon_dist" % kwargs["database_select"], None).label(
                "exon_dist"
            ),
            # Required to retrieve ExAC constraints in variant details that just operate on the ensembl transcript id.
            SmallVariant.sa.ensembl_transcript_id,
        ],
        selectable=SmallVariant.sa.table,
        conditions=[SmallVariant.sa.alternative != "*"],
    )


class ExtendQueryPartsBase:
    def __init__(self, kwargs, case, query_id=None):
        self.kwargs = kwargs
        self.query_id = query_id
        self.case = case

    def extend(self, query_parts):
        return QueryParts(
            fields=tuple(chain(query_parts.fields, self.extend_fields(query_parts))),
            selectable=self.extend_selectable(query_parts),
            conditions=tuple(chain(query_parts.conditions, self.extend_conditions(query_parts))),
        )

    def extend_fields(self, _query_parts):
        # TODO: remove _query_parts
        return ()

    def extend_selectable(self, query_parts):
        return query_parts.selectable

    def extend_conditions(self, _query_parts):
        # TODO: remove _query_parts
        return ()


def same_variant(lhs, rhs):
    return and_(
        lhs.sa.release == rhs.sa.release,
        lhs.sa.chromosome == rhs.sa.chromosome,
        lhs.sa.start == rhs.sa.start,
        lhs.sa.end == rhs.sa.end,
        lhs.sa.reference == rhs.sa.reference,
        lhs.sa.alternative == rhs.sa.alternative,
    )


class ExtendQueryPartsDbsnpJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select([func.max(Dbsnp.sa.rsid).label("rsid")])
            .select_from(Dbsnp.sa)
            .where(same_variant(Dbsnp, SmallVariant))
            .group_by(
                Dbsnp.sa.release,
                Dbsnp.sa.chromosome,
                Dbsnp.sa.start,
                Dbsnp.sa.end,
                Dbsnp.sa.reference,
                Dbsnp.sa.alternative,
            )
            .lateral("dbsnp_subquery")
        )

    def extend_fields(self, _query_parts):
        return [func.coalesce(self.subquery.c.rsid, None).label("rsid")]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsDbsnpJoinAndFilter(ExtendQueryPartsDbsnpJoin):
    def extend_conditions(self, _query_parts):
        # Do not enable option if clinvar filter is activated as all clinvar variants have a dbsnp entry.
        if self.kwargs["remove_if_in_dbsnp"] and not self.kwargs["require_in_clinvar"]:
            return [column("rsid") == None]
        return []


class ExtendQueryPartsHgncJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kwargs["database_select"] == "refseq":
            self.subquery_refseqtohgnc = (
                select([func.max(RefseqToHgnc.sa.hgnc_id).label("hgnc_id")])
                .select_from(RefseqToHgnc.sa)
                .where(SmallVariant.sa.refseq_gene_id == RefseqToHgnc.sa.entrez_id)
                .group_by(RefseqToHgnc.sa.entrez_id)
                .lateral("refseqtohgnc_subquery")
            )
            group = Hgnc.sa.entrez_id
            link = or_(
                self.subquery_refseqtohgnc.c.hgnc_id == Hgnc.sa.hgnc_id,
                SmallVariant.sa.refseq_gene_id == Hgnc.sa.entrez_id,
            )
        else:
            group = Hgnc.sa.ensembl_gene_id
            link = SmallVariant.sa.ensembl_gene_id == group

        self.subquery_hgnc = (
            select(
                [
                    func.max(Hgnc.sa.symbol).label("symbol"),
                    func.max(Hgnc.sa.name).label("name"),
                    func.max(Hgnc.sa.gene_family).label("gene_family"),
                    func.max(Hgnc.sa.pubmed_id).label("pubmed_id"),
                    func.max(Hgnc.sa.ucsc_id_novers).label("ucsc_id_novers"),
                    func.max(Hgnc.sa.hgnc_id).label("hgnc_id"),
                    func.max(Hgnc.sa.uniprot_ids).label("uniprot_ids"),
                ]
            )
            .select_from(Hgnc.sa)
            .where(link)
            .group_by(group)
            .lateral("hgnc_subquery")
        )

    def extend_selectable(self, query_parts):
        if self.kwargs["database_select"] == "refseq":
            query_parts = query_parts.selectable.outerjoin(self.subquery_refseqtohgnc, true())
        return query_parts.selectable.outerjoin(self.subquery_hgnc, true())

    def extend_fields(self, _query_parts):
        return [
            func.coalesce(self.subquery_hgnc.c.symbol, "").label("symbol"),
            func.coalesce(self.subquery_hgnc.c.name, "").label("gene_name"),
            func.coalesce(self.subquery_hgnc.c.gene_family, "").label("gene_family"),
            func.coalesce(self.subquery_hgnc.c.pubmed_id, "").label("pubmed_id"),
            func.coalesce(self.subquery_hgnc.c.hgnc_id, "").label("hgnc_id"),
            func.coalesce(self.subquery_hgnc.c.uniprot_ids, "").label("uniprot_ids"),
        ]


class ExtendQueryPartsHgncAndConservationJoin(ExtendQueryPartsHgncJoin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select([func.max(KnowngeneAA.sa.alignment).label("least_alignment")])
            .select_from(KnowngeneAA.sa)
            .where(
                and_(
                    KnowngeneAA.sa.release == SmallVariant.sa.release,
                    KnowngeneAA.sa.chromosome == SmallVariant.sa.chromosome,
                    KnowngeneAA.sa.start
                    <= (SmallVariant.sa.start - 1 + func.length(SmallVariant.sa.reference)),
                    KnowngeneAA.sa.end > (SmallVariant.sa.start - 1),
                    KnowngeneAA.sa.transcript_id_novers == self.subquery_hgnc.c.ucsc_id_novers,
                )
            )
            .group_by(
                KnowngeneAA.sa.release,
                KnowngeneAA.sa.chromosome,
                KnowngeneAA.sa.start,
                KnowngeneAA.sa.end,
                KnowngeneAA.sa.transcript_id,
            )
            .lateral("conservation_subquery")
        )

    def extend_fields(self, _query_parts):
        fields = super().extend_fields(_query_parts)
        fields.append(func.coalesce(self.subquery.c.least_alignment, "").label("known_gene_aa"))
        return fields

    def extend_selectable(self, query_parts):
        query_parts = super().extend_selectable(query_parts)
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsGeneSymbolJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kwargs["database_select"] == "refseq":
            table = RefseqToGeneSymbol
            group = table.sa.entrez_id
            link = group == SmallVariant.sa.refseq_gene_id
        else:  # if self.kwargs["database_select"] == "ensembl"
            table = EnsemblToGeneSymbol
            group = table.sa.ensembl_gene_id
            link = group == SmallVariant.sa.ensembl_gene_id
        self.subquery = (
            select([func.max(table.sa.gene_symbol).label("gene_symbol")])
            .select_from(table.sa)
            .where(link)
            .group_by(group)
            .lateral("genesymbol_subquery")
        )

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())

    def extend_fields(self, _query_parts):
        return [func.coalesce(self.subquery.c.gene_symbol, "").label("gene_symbol")]


class ExtendQueryPartsMgiJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select([func.max(MgiMapping.sa.mgi_id).label("mgi_id")])
            .select_from(MgiMapping.sa)
            .where(MgiMapping.sa.human_entrez_id == SmallVariant.sa.refseq_gene_id)
            .group_by(MgiMapping.sa.human_entrez_id)
            .lateral("mgi_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.mgi_id]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsAcmgJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kwargs["database_select"] == "refseq":
            group = Acmg.sa.entrez_id
            link = SmallVariant.sa.refseq_gene_id == group
        else:
            group = Acmg.sa.ensembl_gene_id
            link = SmallVariant.sa.ensembl_gene_id == group

        self.subquery = (
            select([func.max(Acmg.sa.symbol).label("symbol")])
            .select_from(Acmg.sa)
            .where(link)
            .group_by(group)
            .lateral("acmg_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.symbol.label("acmg_symbol")]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsClinvarJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                (
                    Clinvar.sa.variation_type,
                    Clinvar.sa.vcv,
                    Clinvar.sa.point_rating,
                    Clinvar.sa.pathogenicity,
                    Clinvar.sa.review_status,
                    Clinvar.sa.pathogenicity_summary,
                    Clinvar.sa.details,
                )
            )
            .select_from(Clinvar.sa)
            .where(and_(same_variant(SmallVariant, Clinvar)))
            .lateral("clinvar_subquery")
        )

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())

    def extend_fields(self, _query_parts):
        return [
            self.subquery.c.variation_type,
            self.subquery.c.vcv,
            self.subquery.c.point_rating,
            self.subquery.c.pathogenicity,
            self.subquery.c.pathogenicity_summary,
            self.subquery.c.details,
        ]


class ExtendQueryPartsClinvarJoinAndFilter(ExtendQueryPartsClinvarJoin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patho_keys = (
            "pathogenic",
            "likely_pathogenic",
            "uncertain_significance",
            "likely_benign",
            "benign",
        )

    def extend_conditions(self, _query_parts):
        return [and_(self._build_membership_term(), self._build_significance_term(),)]

    def _build_membership_term(self):
        if self.kwargs["require_in_clinvar"]:
            return SmallVariant.sa.in_clinvar == True
        else:
            return True

    def _build_significance_term(self):
        terms = []
        if not self.kwargs.get("require_in_clinvar"):
            return True
        for patho_key in self.patho_keys:
            if self.kwargs.get("clinvar_include_%s" % patho_key):
                terms.append(self.subquery.c.pathogenicity == patho_key.replace("_", " "))
        return or_(*terms)


class ExtendQueryPartsHgmdJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                [
                    func.count(HgmdPublicLocus.sa.variation_name).label("hgmd_public_overlap"),
                    func.max(HgmdPublicLocus.sa.variation_name).label("hgmd_accession"),
                ]
            )
            .select_from(HgmdPublicLocus.sa)
            # This is a range query that caused an error already. So I'm writing a more elaborate comment.
            # HGMD is 0-based, and our coordinate system is 1-based, that means the end positions match, but
            # the start is one less in the HGMD compared to our system, i.e. our.start = hgmd.start + 1.
            # We need to correct for that.
            # The default interval query is:   (hgmd.start     <= our.end) and (hgmd.end >= our.start)
            # The corrected interval query is: (hgmd.start + 1 <= our.end) and (hgmd.end >= our.start)
            .where(
                and_(
                    HgmdPublicLocus.sa.release == SmallVariant.sa.release,
                    HgmdPublicLocus.sa.chromosome == SmallVariant.sa.chromosome,
                    (HgmdPublicLocus.sa.start + 1) <= SmallVariant.sa.end,
                    HgmdPublicLocus.sa.end >= SmallVariant.sa.start,
                )
            )
            .lateral("hgmd_subquery")
        )

    def extend_fields(self, _query_parts):
        return [
            func.coalesce(self.subquery.c.hgmd_public_overlap, 0).label("hgmd_public_overlap"),
            func.coalesce(self.subquery.c.hgmd_accession, "").label("hgmd_accession"),
        ]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsHgmdJoinAndFilter(ExtendQueryPartsHgmdJoin):
    def extend_conditions(self, _query_parts):
        if self.kwargs["require_in_hgmd_public"]:
            return [column("hgmd_public_overlap") > 0]
        return []


class ExtendQueryPartsCaseJoinAndFilter(ExtendQueryPartsBase):
    #: The model to retrieve the set ids from.
    model_set = SmallVariantSet

    #: The model to join with.
    model = SmallVariant

    def extend_fields(self, _query_parts):
        return [Case.sa.sodar_uuid.label("case_uuid"), Case.sa.name.label("family_name")]

    def extend_conditions(self, _query_parts):
        condition = []
        set_ = (
            self.model_set.objects.filter(case=self.case, state="active")
            .order_by("-date_created")
            .first()
        )
        if not set_:
            raise RuntimeError("No variant set to case with id %s found." % self.case.id)
        condition.append(
            and_(self.model.sa.case_id == self.case.id, self.model.sa.set_id == set_.id)
        )
        return [or_(*condition)]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(Case.sa, self.model.sa.case_id == Case.sa.id)


class ExtendQueryPartsGenotypeBase(ExtendQueryPartsBase):
    quality_term_disabled = None

    #: The model to build the term for.
    model = SmallVariant

    def _get_quality_term_disabled(self):
        if self.quality_term_disabled is None:
            raise NotImplementedError("Please set quality_term_disabled as a class variable!")

    def _get_trio_names(self):
        """Return (index, father, mother) names from trio"""
        index_lines = [
            rec
            for rec in self.case.get_filtered_pedigree_with_samples()
            if rec["patient"] == self.kwargs["compound_recessive_index"]
        ]
        if len(index_lines) != 1:  # pragma: no cover
            raise RuntimeError("Could not find index line from pedigree")
        return index_lines[0]["patient"], index_lines[0]["father"], index_lines[0]["mother"]

    def _build_quality_term(self, name):
        if self._get_quality_term_disabled():
            return True

        ad_max = self.kwargs["%s_ad_max" % name]
        rhs = and_(
            # Genotype quality is simple.
            self.model.sa.genotype[name]["gq"].astext.cast(Integer) >= self.kwargs["%s_gq" % name],
            # The depth setting depends on whether the variant is in homozygous or heterozygous state.
            or_(  # heterozygous or hemizygous state
                not_(
                    or_(
                        self.model.sa.genotype[name]["gt"].astext == "0/1",
                        self.model.sa.genotype[name]["gt"].astext == "0|1",
                        self.model.sa.genotype[name]["gt"].astext == "1/0",
                        self.model.sa.genotype[name]["gt"].astext == "1|0",
                        self.model.sa.genotype[name]["gt"].astext == "1",
                        # TODO: recognize hemizygous from 'sex="M" and chr="X" and gt="1/1"'?
                    )
                ),
                self.model.sa.genotype[name]["dp"].astext.cast(Integer)
                >= self.kwargs["%s_dp_het" % name],
            ),
            or_(  # homozygous state
                not_(
                    or_(
                        self.model.sa.genotype[name]["gt"].astext == "0/0",
                        self.model.sa.genotype[name]["gt"].astext == "0|0",
                        self.model.sa.genotype[name]["gt"].astext == "1/1",
                        self.model.sa.genotype[name]["gt"].astext == "1|1",
                        self.model.sa.genotype[name]["gt"].astext == "0",
                        self.model.sa.genotype[name]["gt"].astext == "1",
                    )
                ),
                self.model.sa.genotype[name]["dp"].astext.cast(Integer)
                >= self.kwargs["%s_dp_hom" % name],
            ),
            # Allelic depth is checked in case of het or hom.
            or_(
                self.model.sa.genotype[name]["gt"].astext == "0/0",
                self.model.sa.genotype[name]["gt"].astext == "0|0",
                self.model.sa.genotype[name]["gt"].astext == "0",
                and_(
                    self.model.sa.genotype[name]["ad"].astext.cast(Integer)
                    >= self.kwargs["%s_ad" % name]
                ),
            ),
            self.model.sa.genotype[name]["ad"].astext.cast(Integer) <= ad_max if ad_max else True,
            # Allelic balance is somewhat complicated
            and_(
                self.model.sa.genotype[name]["dp"].astext.cast(Integer) > 0,
                or_(
                    not_(
                        or_(
                            self.model.sa.genotype[name]["gt"].astext == "0/1",
                            self.model.sa.genotype[name]["gt"].astext == "0|1",
                            self.model.sa.genotype[name]["gt"].astext == "1/0",
                            self.model.sa.genotype[name]["gt"].astext == "1|0",
                        )
                    ),
                    and_(
                        (
                            self.model.sa.genotype[name]["ad"].astext.cast(Float)
                            / self.model.sa.genotype[name]["dp"].astext.cast(Float)
                        )
                        >= self.kwargs["%s_ab" % name],
                        (
                            self.model.sa.genotype[name]["ad"].astext.cast(Float)
                            / self.model.sa.genotype[name]["dp"].astext.cast(Float)
                        )
                        <= (1.0 - self.kwargs["%s_ab" % name]),
                    ),
                ),
            ),
        )
        return or_(self.model.sa.genotype[name].is_(None), rhs)

    def _build_genotype_term(self, name, gt_list):
        if gt_list:
            return or_(
                self.model.sa.genotype[name].is_(None),
                self.model.sa.genotype[name]["gt"].astext.in_(gt_list),
            )
        else:
            return True

    def _build_full_genotype_term(self, name, gt_list):
        quality_term = self._build_quality_term(name)
        genotype_term = self._build_genotype_term(name, gt_list)
        if self.kwargs.get("%s_fail" % name) == "drop-variant":
            return and_(quality_term, genotype_term)
        elif self.kwargs.get("%s_fail" % name) == "no-call":
            return or_(not_(quality_term), genotype_term)  # implication
        else:  # elif kwargs["%s_fail" % name] == "ignore"
            return genotype_term


class ExtendQueryPartsGenotypeDefaultBase(ExtendQueryPartsGenotypeBase):
    def extend_conditions(self, _query_parts):
        result = []
        for member in self.case.get_filtered_pedigree_with_samples():
            name = member["patient"]
            gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[self.kwargs["%s_gt" % name]]
            result.append(self._build_full_genotype_term(name, gt_list))
        return result


class ExtendQueryPartsGenotypeRecessiveBase(ExtendQueryPartsGenotypeBase):
    def extend_conditions(self, _query_parts):
        index, father, mother = self._get_trio_names()
        gt_patterns = {index: "hom", father: "het", mother: "het"}
        result = []
        members = [
            m for m in self.case.get_filtered_pedigree_with_samples() if m["patient"] in gt_patterns
        ]
        for member in members:
            name = member["patient"]
            gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[gt_patterns[name]]
            result.append(self._build_full_genotype_term(name, gt_list))
        return result


class ExtendQueryPartsGenotypeCompHetBase(ExtendQueryPartsGenotypeBase):
    role = None

    def extend_conditions(self, _query_parts):
        index, father, mother = self._get_trio_names()
        if self.role == "mother":
            gt_patterns = {index: "het", father: "ref", mother: "het"}
        else:  # self.gt_type == "father"
            gt_patterns = {index: "het", father: "het", mother: "ref"}
        members = [
            m for m in self.case.get_filtered_pedigree_with_samples() if m["patient"] in gt_patterns
        ]
        result = []
        for member in members:
            name = member["patient"]
            gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[gt_patterns[name]]
            result.append(self._build_full_genotype_term(name, gt_list))
        return result

    def extend_fields(self, _query_parts):
        if self.role == "mother":
            return [
                literal_column("1", Integer).label("mother_marker"),
                literal_column("0", Integer).label("father_marker"),
            ]
        else:  # self.gt_type == "father"
            return [
                literal_column("0", Integer).label("mother_marker"),
                literal_column("1", Integer).label("father_marker"),
            ]


class ExtendQueryPartsGenotypeGtDefaultFilter(ExtendQueryPartsGenotypeDefaultBase):
    quality_term_disabled = True


class ExtendQueryPartsGenotypeGtQualityDefaultFilter(ExtendQueryPartsGenotypeDefaultBase):
    quality_term_disabled = False


class ExtendQueryPartsGenotypeGtFatherFilter(ExtendQueryPartsGenotypeCompHetBase):
    quality_term_disabled = True
    role = "father"


class ExtendQueryPartsGenotypeGtMotherFilter(ExtendQueryPartsGenotypeCompHetBase):
    quality_term_disabled = True
    role = "mother"


class ExtendQueryPartsGenotypeGtQualityFatherFilter(ExtendQueryPartsGenotypeCompHetBase):
    quality_term_disabled = False
    role = "father"


class ExtendQueryPartsGenotypeGtQualityMotherFilter(ExtendQueryPartsGenotypeCompHetBase):
    quality_term_disabled = False
    role = "mother"


class ExtendQueryPartsGenotypeGtRecessiveFilter(ExtendQueryPartsGenotypeRecessiveBase):
    quality_term_disabled = True


class ExtendQueryPartsGenotypeGtQualityRecessiveFilter(ExtendQueryPartsGenotypeRecessiveBase):
    quality_term_disabled = False


class ExtendQueryPartsVarTypeFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        values = list()
        if self.kwargs["var_type_snv"]:
            values.append("snv")
        if self.kwargs["var_type_mnv"]:
            values.append("mnv")
        if self.kwargs["var_type_indel"]:
            values.append("indel")
        return [or_(SmallVariant.sa.var_type.is_(None), SmallVariant.sa.var_type.in_(values))]


class ExtendQueryPartsMitochondrialFrequenciesJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery_mtdb = (
            select(
                [
                    func.max(MtDb.sa.ac).label("mtdb_count"),
                    func.max(MtDb.sa.af).label("mtdb_frequency"),
                    func.bool_or(MtDb.sa.location == "D-loop").label("mtdb_dloop"),
                ]
            )
            .select_from(MtDb.sa)
            .where(same_variant(MtDb, SmallVariant))
            .group_by(
                MtDb.sa.release,
                MtDb.sa.chromosome,
                MtDb.sa.start,
                MtDb.sa.end,
                MtDb.sa.reference,
                MtDb.sa.alternative,
            )
            .lateral("mtdb_subquery")
        )
        self.subquery_helixmtdb = (
            select(
                [
                    func.max(HelixMtDb.sa.ac_het).label("helixmtdb_het_count"),
                    func.max(HelixMtDb.sa.ac_hom).label("helixmtdb_hom_count"),
                    func.max(HelixMtDb.sa.af).label("helixmtdb_frequency"),
                    func.bool_or(HelixMtDb.sa.is_triallelic).label("helixmtdb_is_triallelic"),
                ]
            )
            .select_from(HelixMtDb.sa)
            .where(same_variant(HelixMtDb, SmallVariant))
            .group_by(
                HelixMtDb.sa.release,
                HelixMtDb.sa.chromosome,
                HelixMtDb.sa.start,
                HelixMtDb.sa.end,
                HelixMtDb.sa.reference,
                HelixMtDb.sa.alternative,
            )
            .lateral("helixmtdb_subquery")
        )
        self.subquery_mitomap = (
            select(
                [
                    func.max(Mitomap.sa.ac).label("mitomap_count"),
                    func.max(Mitomap.sa.af).label("mitomap_frequency"),
                ]
            )
            .select_from(Mitomap.sa)
            .where(same_variant(Mitomap, SmallVariant))
            .group_by(
                Mitomap.sa.release,
                Mitomap.sa.chromosome,
                Mitomap.sa.start,
                Mitomap.sa.end,
                Mitomap.sa.reference,
                Mitomap.sa.alternative,
            )
            .lateral("mitomap_subquery")
        )

    def extend_fields(self, _query_parts):
        return [
            func.coalesce(self.subquery_mtdb.c.mtdb_count, 0).label("mtdb_count"),
            func.coalesce(self.subquery_mtdb.c.mtdb_frequency, 0.0).label("mtdb_frequency"),
            func.coalesce(self.subquery_mtdb.c.mtdb_dloop, False).label("mtdb_dloop"),
            func.coalesce(self.subquery_helixmtdb.c.helixmtdb_het_count, 0).label(
                "helixmtdb_het_count"
            ),
            func.coalesce(self.subquery_helixmtdb.c.helixmtdb_hom_count, 0).label(
                "helixmtdb_hom_count"
            ),
            func.coalesce(self.subquery_helixmtdb.c.helixmtdb_frequency, 0.0).label(
                "helixmtdb_frequency"
            ),
            func.coalesce(self.subquery_helixmtdb.c.helixmtdb_is_triallelic, False).label(
                "helixmtdb_is_triallelic"
            ),
            func.coalesce(self.subquery_mitomap.c.mitomap_count, 0).label("mitomap_count"),
            func.coalesce(self.subquery_mitomap.c.mitomap_frequency, 0.0).label(
                "mitomap_frequency"
            ),
        ]

    def extend_selectable(self, query_parts):
        query_parts = query_parts.selectable.outerjoin(self.subquery_mtdb, true())
        query_parts = query_parts.selectable.outerjoin(self.subquery_helixmtdb, true())
        return query_parts.selectable.outerjoin(self.subquery_mitomap, true())


class ExtendQueryPartsFrequenciesFilter(ExtendQueryPartsMitochondrialFrequenciesJoin):
    def extend_conditions(self, _query_parts):
        return [
            or_(
                and_(
                    SmallVariant.sa.chromosome_no < 25,
                    *self._build_population_db_term("frequency"),
                    *self._build_population_db_term("homozygous"),
                    *self._build_population_db_term("heterozygous"),
                    *self._build_population_db_term("hemizygous"),
                ),
                and_(
                    SmallVariant.sa.chromosome_no == 25,
                    *self._build_mitochondrial_db_term("mtdb", ["count", "frequency"]),
                    *self._build_mitochondrial_db_term(
                        "helixmtdb", ["het_count", "hom_count", "frequency"]
                    ),
                    *self._build_mitochondrial_db_term("mitomap", ["count", "frequency"]),
                ),
            )
        ]

    def _build_population_db_term(self, metric):
        """Build term to limit by frequency or homozygous or heterozygous count."""
        terms = []
        for db in ("exac", "thousand_genomes", "gnomad_exomes", "gnomad_genomes"):
            field_name = "%s_%s" % (db, metric)
            if self.kwargs["%s_enabled" % db] and self.kwargs.get(field_name) is not None:
                terms.append(getattr(SmallVariant.sa, field_name) <= self.kwargs[field_name])
        return terms

    def _build_mitochondrial_db_term(self, db, metrics):
        terms = []
        for metric in metrics:
            field_name = "%s_%s" % (db, metric)
            if self.kwargs["%s_enabled" % db] and self.kwargs.get(field_name) is not None:
                terms.append(
                    func.coalesce(getattr(getattr(self, "subquery_%s" % db).c, field_name), 0)
                    <= self.kwargs[field_name]
                )
        return terms


class ExtendQueryPartsInHouseJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                [
                    func.coalesce(func.sum(SmallVariantSummary.sa.count_hom_ref), 0).label(
                        "inhouse_hom_ref"
                    ),
                    func.coalesce(func.sum(SmallVariantSummary.sa.count_het), 0).label(
                        "inhouse_het"
                    ),
                    func.coalesce(func.sum(SmallVariantSummary.sa.count_hom_alt), 0).label(
                        "inhouse_hom_alt"
                    ),
                    func.coalesce(func.sum(SmallVariantSummary.sa.count_hemi_ref), 0).label(
                        "inhouse_hemi_ref"
                    ),
                    func.coalesce(func.sum(SmallVariantSummary.sa.count_hemi_alt), 0).label(
                        "inhouse_hemi_alt"
                    ),
                    func.sum(
                        func.coalesce(SmallVariantSummary.sa.count_het, 0)
                        + func.coalesce(SmallVariantSummary.sa.count_hom_alt, 0)
                        + func.coalesce(SmallVariantSummary.sa.count_hemi_alt, 0)
                    ).label("inhouse_carriers"),
                ]
            )
            .select_from(SmallVariantSummary.sa)
            .where(same_variant(SmallVariantSummary, SmallVariant))
            .group_by(
                SmallVariantSummary.sa.release,
                SmallVariantSummary.sa.chromosome,
                SmallVariantSummary.sa.start,
                SmallVariantSummary.sa.end,
                SmallVariantSummary.sa.reference,
                SmallVariantSummary.sa.alternative,
            )
            .lateral("inhouse_subquery")
        )

    def extend_fields(self, _query_parts):
        if settings.KIOSK_MODE:
            return []

        return [
            func.coalesce(self.subquery.c.inhouse_hom_ref, 0).label("inhouse_hom_ref"),
            func.coalesce(self.subquery.c.inhouse_het, 0).label("inhouse_het"),
            func.coalesce(self.subquery.c.inhouse_hom_alt, 0).label("inhouse_hom_alt"),
            func.coalesce(self.subquery.c.inhouse_hemi_ref, 0).label("inhouse_hemi_ref"),
            func.coalesce(self.subquery.c.inhouse_hemi_alt, 0).label("inhouse_hemi_alt"),
            func.coalesce(self.subquery.c.inhouse_carriers, 0).label("inhouse_carriers"),
        ]

    def extend_selectable(self, query_parts):
        if settings.KIOSK_MODE:
            return query_parts.selectable

        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsInHouseJoinAndFilter(ExtendQueryPartsInHouseJoin):
    def extend_conditions(self, _query_parts):
        """Build WHERE clause for the query based on select het/hom counts in inhouse DB."""
        if settings.KIOSK_MODE:
            return []

        terms = []
        if self.kwargs.get("inhouse_enabled"):
            if self.kwargs.get("inhouse_heterozygous") is not None:
                terms.append(
                    func.coalesce(self.subquery.c.inhouse_het, 0)
                    <= self.kwargs.get("inhouse_heterozygous")
                )
            if self.kwargs.get("inhouse_homozygous") is not None:
                terms.append(
                    func.coalesce(self.subquery.c.inhouse_hom_alt, 0)
                    + func.coalesce(self.subquery.c.inhouse_hemi_alt, 0)
                    <= self.kwargs.get("inhouse_homozygous")
                )
            if self.kwargs.get("inhouse_hemizygous") is not None:
                terms.append(
                    func.coalesce(self.subquery.c.inhouse_hemi_alt, 0)
                    <= self.kwargs.get("inhouse_hemizygous")
                )
            if self.kwargs.get("inhouse_carriers") is not None:
                terms.append(
                    func.coalesce(self.subquery.c.inhouse_carriers, 0)
                    <= self.kwargs.get("inhouse_carriers")
                )
        return terms


class ExtendQueryPartsEffectsFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        return [
            OVERLAP(
                getattr(SmallVariant.sa, "%s_effect" % self.kwargs["database_select"]),
                cast(self.kwargs["effects"], ARRAY(VARCHAR())),
            )
        ]


class ExtendQueryPartsExonDistanceFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        exon_dist = self.kwargs.get("max_exon_dist")
        if exon_dist is None:
            return []
        return [
            getattr(SmallVariant.sa, "%s_exon_dist" % self.kwargs["database_select"]) <= exon_dist
        ]


class ExtendQueryPartsTranscriptCodingFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        field = getattr(SmallVariant.sa, "%s_transcript_coding" % self.kwargs["database_select"])
        terms = []
        if not self.kwargs["transcripts_coding"]:
            terms.append(field == False)  # equality from SQL Alchemy
        if not self.kwargs["transcripts_noncoding"]:
            terms.append(field == True)  # equality from SQL Alchemy
        return [and_(*terms)]


class ExtendQueryPartsGeneListsFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        result = []
        if self.kwargs["gene_blocklist"]:
            result.append(not_(self._build_list(self.kwargs["gene_blocklist"])))
        if self.kwargs["gene_allowlist"]:
            result.append(self._build_list(self.kwargs["gene_allowlist"]))
        return result

    def _build_list(self, gene_list):
        return or_(
            SmallVariant.sa.ensembl_gene_id.in_(
                self._build_gene_sub_query("ensembl_gene_id", gene_list)
            ),
            SmallVariant.sa.refseq_gene_id.in_(self._build_gene_sub_query("entrez_id", gene_list)),
        )

    def _build_gene_sub_query(self, hgnc_field, gene_list):
        return (
            select([getattr(Hgnc.sa, hgnc_field)])
            .select_from(Hgnc.sa.table)
            .where(
                and_(
                    or_(
                        Hgnc.sa.hgnc_id.in_(gene_list),
                        Hgnc.sa.ensembl_gene_id.in_(gene_list),
                        Hgnc.sa.entrez_id.in_(gene_list),
                        Hgnc.sa.symbol.in_(gene_list),
                    ),
                    getattr(Hgnc.sa, hgnc_field) != None,  # SQL Alchemy forces us to use ``!=``
                )
            )
            .distinct()
        )


def normalize_chrom(chrom, release):
    """Normalize chromosome for the given ``release``."""
    while chrom.startswith("chr"):
        chrom = chrom[len("chr") :]
    if chrom in ("M", "MT"):
        return "MT" if release == "GRCh37" else "chrM"
    return f"chr{chrom}" if release != "GRCh37" else chrom


class ExtendQueryPartsGenomicRegionFilter(ExtendQueryPartsBase):
    def extend_conditions(self, _query_parts):
        case = self._case_for_release()
        if self.kwargs["genomic_region"]:
            return [
                or_(
                    *[
                        and_(
                            SmallVariant.sa.chromosome == normalize_chrom(chrom, case.release),
                            (SmallVariant.sa.start >= start) if start else True,
                            (SmallVariant.sa.start <= end) if end else True,
                        )
                        for chrom, start, end in self.kwargs["genomic_region"]
                    ]
                )
            ]
        return []

    def _case_for_release(self):
        if hasattr(self, "cases"):
            return self.cases[0]
        else:
            return self.case


class ExtendQueryPartsLoadPrefetchedBase(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_results = Table(
            "variants_%squery_query_results" % self._get_query_type(), get_meta()
        )

    def _get_query_type(self):
        raise NotImplementedError("Implement me!")

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(
            self.query_results, SmallVariant.sa.id == self.query_results.c.smallvariant_id
        )

    def extend_conditions(self, _query_parts):
        return [
            getattr(self.query_results.c, "%squery_id" % self._get_query_type()) == self.query_id,
            SmallVariant.sa.case_id == self.case.id,
        ]


class ExtendQueryPartsCaseLoadPrefetched(ExtendQueryPartsLoadPrefetchedBase):
    def _get_query_type(self):
        return "smallvariant"


class ExtendQueryPartsProjectLoadPrefetched(ExtendQueryPartsLoadPrefetchedBase):
    def _get_query_type(self):
        return "projectcasessmallvariant"


class ExtendQueryPartsCommentsJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select([func.count(SmallVariantComment.sa.id).label("comment_count")])
            .select_from(SmallVariantComment.sa)
            .where(
                and_(
                    same_variant(SmallVariant, SmallVariantComment),
                    SmallVariantComment.sa.case_id == SmallVariant.sa.case_id,
                )
            )
            .group_by(
                SmallVariantComment.sa.case_id,
                SmallVariantComment.sa.release,
                SmallVariantComment.sa.chromosome,
                SmallVariantComment.sa.start,
                SmallVariantComment.sa.end,
                SmallVariantComment.sa.reference,
                SmallVariantComment.sa.alternative,
            )
            .lateral("comments_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.comment_count]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsCommentsExtraAnnoJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select([func.array_agg(ExtraAnno.sa.anno_data).label("extra_annos")])
            .select_from(ExtraAnno.sa)
            .where(
                and_(
                    ExtraAnno.sa.release == SmallVariant.sa.release,
                    ExtraAnno.sa.chromosome == SmallVariant.sa.chromosome,
                    ExtraAnno.sa.start == SmallVariant.sa.start,
                    ExtraAnno.sa.end == SmallVariant.sa.end,
                    ExtraAnno.sa.reference == SmallVariant.sa.reference,
                    ExtraAnno.sa.alternative == SmallVariant.sa.alternative,
                )
            )
            .group_by(
                ExtraAnno.sa.release,
                ExtraAnno.sa.chromosome,
                ExtraAnno.sa.start,
                ExtraAnno.sa.end,
                ExtraAnno.sa.reference,
                ExtraAnno.sa.alternative,
            )
            .lateral("extra_annos_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.extra_annos]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsFlagsJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                [
                    func.count(SmallVariantFlags.sa.id).label("flag_count"),
                    func.bool_or(SmallVariantFlags.sa.flag_bookmarked).label("flag_bookmarked"),
                    func.bool_or(SmallVariantFlags.sa.flag_candidate).label("flag_candidate"),
                    func.bool_or(SmallVariantFlags.sa.flag_segregates).label("flag_segregates"),
                    func.bool_or(SmallVariantFlags.sa.flag_doesnt_segregate).label(
                        "flag_doesnt_segregate"
                    ),
                    func.bool_or(SmallVariantFlags.sa.flag_final_causative).label(
                        "flag_final_causative"
                    ),
                    func.bool_or(SmallVariantFlags.sa.flag_for_validation).label(
                        "flag_for_validation"
                    ),
                    func.bool_or(SmallVariantFlags.sa.flag_no_disease_association).label(
                        "flag_no_disease_association"
                    ),
                    func.max(SmallVariantFlags.sa.flag_visual).label("flag_visual"),
                    func.max(SmallVariantFlags.sa.flag_molecular).label("flag_molecular"),
                    func.max(SmallVariantFlags.sa.flag_validation).label("flag_validation"),
                    func.max(SmallVariantFlags.sa.flag_phenotype_match).label(
                        "flag_phenotype_match"
                    ),
                    func.max(SmallVariantFlags.sa.flag_summary).label("flag_summary"),
                ]
            )
            .select_from(SmallVariantFlags.sa)
            .where(
                and_(
                    same_variant(SmallVariant, SmallVariantFlags),
                    SmallVariantFlags.sa.case_id == SmallVariant.sa.case_id,
                )
            )
            .group_by(
                SmallVariantFlags.sa.case_id,
                SmallVariantFlags.sa.release,
                SmallVariantFlags.sa.chromosome,
                SmallVariantFlags.sa.start,
                SmallVariantFlags.sa.end,
                SmallVariantFlags.sa.reference,
                SmallVariantFlags.sa.alternative,
            )
            .lateral("flags_subquery")
        )

    def extend_fields(self, _query_parts):
        return [
            self.subquery.c.flag_count,
            self.subquery.c.flag_bookmarked,
            self.subquery.c.flag_candidate,
            self.subquery.c.flag_segregates,
            self.subquery.c.flag_doesnt_segregate,
            self.subquery.c.flag_final_causative,
            self.subquery.c.flag_for_validation,
            self.subquery.c.flag_no_disease_association,
            self.subquery.c.flag_molecular,
            self.subquery.c.flag_visual,
            self.subquery.c.flag_validation,
            self.subquery.c.flag_phenotype_match,
            self.subquery.c.flag_summary,
        ]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsFlagsJoinAndFilter(ExtendQueryPartsFlagsJoin):
    def extend_conditions(self, _query_parts):
        """Build WHERE clause for the query based on the ``SmallVariantFlags`` and ``SmallVariantComment``."""
        terms = []
        not_terms = [true()]
        none_terms = [true()]
        # Add terms for the simple, boolean-valued flags.
        flag_names = (
            "bookmarked",
            "candidate",
            "final_causative",
            "for_validation",
            "segregates",
            "doesnt_segregate",
            "no_disease_association",
        )
        for flag in flag_names:
            flag_name = "flag_%s" % flag
            if self.kwargs.get(flag_name):
                terms.append(column(flag_name))
            if self.kwargs.get("flag_simple_empty"):
                not_terms.append(not_(column(flag_name)))
                none_terms.append(column(flag_name).is_(None))
        # Add terms for the valued flags.
        flag_names = ("visual", "validation", "molecular", "phenotype_match", "summary")
        for flag in flag_names:
            flag_name = "flag_%s" % flag
            for value in ("positive", "uncertain", "negative", "empty"):
                field_name = "%s_%s" % (flag_name, value)
                if self.kwargs.get(field_name):
                    terms.append(column(flag_name) == value)
                    if value == "empty":
                        terms.append(column(flag_name).is_(None))
        return [or_(*terms, and_(*not_terms), and_(*none_terms))]


class ExtendQueryPartsAcmgCriteriaJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = (
            select(
                [
                    func.max(AcmgCriteriaRating.sa.class_auto).label("acmg_class_auto"),
                    func.max(AcmgCriteriaRating.sa.class_override).label("acmg_class_override"),
                ]
            )
            .select_from(AcmgCriteriaRating.sa)
            .where(
                and_(
                    same_variant(SmallVariant, AcmgCriteriaRating),
                    AcmgCriteriaRating.sa.case_id == SmallVariant.sa.case_id,
                )
            )
            .group_by(
                AcmgCriteriaRating.sa.case_id,
                AcmgCriteriaRating.sa.release,
                AcmgCriteriaRating.sa.chromosome,
                AcmgCriteriaRating.sa.start,
                AcmgCriteriaRating.sa.end,
                AcmgCriteriaRating.sa.reference,
                AcmgCriteriaRating.sa.alternative,
            )
            .lateral("acmg_criteria_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.acmg_class_auto, self.subquery.c.acmg_class_override]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsModesOfInheritanceJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kwargs["database_select"] == "refseq":
            gene_id = GeneIdToInheritance.sa.entrez_id
        else:  # self.kwargs["database_select"] == "ensembl"
            gene_id = GeneIdToInheritance.sa.ensembl_gene_id
        self.subquery = (
            select(
                [
                    func.array_agg(GeneIdToInheritance.sa.mode_of_inheritance).label(
                        "modes_of_inheritance"
                    )
                ]
            )
            .select_from(GeneIdToInheritance.sa)
            .where(
                getattr(SmallVariant.sa, "%s_gene_id" % self.kwargs["database_select"]) == gene_id
            )
            .group_by(gene_id)
            .lateral("modes_of_inheritance_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.modes_of_inheritance]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsDiseaseGeneJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.kwargs["database_select"] == "refseq":
            gene_id = GeneIdInHpo.sa.entrez_id
        else:  # self.kwargs["database_select"] == "ensembl"
            gene_id = GeneIdInHpo.sa.ensembl_gene_id

        self.subquery = (
            select([column("id")])
            .select_from(GeneIdInHpo.sa)
            .where(
                getattr(SmallVariant.sa, "%s_gene_id" % self.kwargs["database_select"]) == gene_id
            )
            .lateral("disease_gene_subquery")
        )

    def extend_fields(self, _query_parts):
        return [self.subquery.c.id.isnot(None).label("disease_gene")]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsGnomadConstraintsJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = [
            "pLI",
            "mis_z",
            "syn_z",
            "oe_mis",
            "oe_mis_upper",
            "oe_mis_lower",
            "oe_lof",
            "oe_lof_upper",
            "oe_lof_lower",
        ]
        self.subquery = (
            select(
                [
                    func.max(getattr(GnomadConstraints.sa, field)).label(field)
                    for field in self.fields
                ]
                + [func.max(GnomadConstraints.sa.oe_lof_upper + 0.001).label("loeuf")]
            )
            .select_from(GnomadConstraints.sa)
            .where(SmallVariant.sa.ensembl_gene_id == GnomadConstraints.sa.ensembl_gene_id)
            .group_by(GnomadConstraints.sa.ensembl_gene_id)
            .lateral("gnomad_constraints_subquery")
        )
        self.fields.append("loeuf")

    def extend_fields(self, _query_parts):
        return [getattr(self.subquery.c, field).label("gnomad_%s" % field) for field in self.fields]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsExacConstraintsJoin(ExtendQueryPartsBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = ["pLI", "mis_z", "syn_z"]
        self.subquery = (
            select(
                [func.max(getattr(ExacConstraints.sa, field)).label(field) for field in self.fields]
            )
            .select_from(ExacConstraints.sa)
            .where(
                func.split_part(SmallVariant.sa.ensembl_transcript_id, ".", 1)
                == ExacConstraints.sa.ensembl_transcript_id
            )
            .group_by(ExacConstraints.sa.ensembl_transcript_id)
            .lateral("exac_constraints_subquery")
        )

    def extend_fields(self, _query_parts):
        return [getattr(self.subquery.c, field).label("exac_%s" % field) for field in self.fields]

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


extender_classes_base = [
    ExtendQueryPartsCaseJoinAndFilter,
    ExtendQueryPartsDbsnpJoinAndFilter,
    ExtendQueryPartsVarTypeFilter,
    ExtendQueryPartsFrequenciesFilter,
    ExtendQueryPartsInHouseJoinAndFilter,
    ExtendQueryPartsEffectsFilter,
    ExtendQueryPartsExonDistanceFilter,
    ExtendQueryPartsTranscriptCodingFilter,
    ExtendQueryPartsGeneListsFilter,
    ExtendQueryPartsGenomicRegionFilter,
    ExtendQueryPartsClinvarJoinAndFilter,
    ExtendQueryPartsHgmdJoinAndFilter,
    ExtendQueryPartsGenotypeGtQualityDefaultFilter,
    ExtendQueryPartsFlagsJoinAndFilter,
    ExtendQueryPartsCommentsJoin,
    ExtendQueryPartsCommentsExtraAnnoJoin,
    ExtendQueryPartsAcmgCriteriaJoin,
]


class QueryPartsBuilder:

    core_query = small_variant_query
    qp_extender_classes = [
        *extender_classes_base,
        ExtendQueryPartsHgncJoin,
        ExtendQueryPartsGeneSymbolJoin,
        ExtendQueryPartsAcmgJoin,
        ExtendQueryPartsMgiJoin,
    ]

    def __init__(self, case, query_id):
        self.case = case
        self.query_id = query_id

    def run(self, kwargs, extender_genotype_class=None):
        query_parts = self.core_query(kwargs)
        extender_names = []
        for extender_class in self.qp_extender_classes:
            name = extender_class.__name__
            if "Genotype" in name and extender_genotype_class is not None:
                continue
            if name in extender_names:
                raise ImproperlyConfigured("Double use of extender class %s" % name)
            extender = extender_class(kwargs=kwargs, case=self.case, query_id=self.query_id)
            query_parts = extender.extend(query_parts)
        if extender_genotype_class is not None:
            extender = extender_genotype_class(
                kwargs=kwargs, case=self.case, query_id=self.query_id
            )
            query_parts = extender.extend(query_parts)

        return query_parts


class CaseLoadPrefetchedQueryPartsBuilder(QueryPartsBuilder):
    qp_extender_classes = [
        ExtendQueryPartsCaseLoadPrefetched,
        ExtendQueryPartsCaseJoinAndFilter,
        ExtendQueryPartsMitochondrialFrequenciesJoin,
        ExtendQueryPartsDbsnpJoin,
        ExtendQueryPartsHgncJoin,
        ExtendQueryPartsGeneSymbolJoin,
        ExtendQueryPartsAcmgJoin,
        ExtendQueryPartsMgiJoin,
        ExtendQueryPartsFlagsJoinAndFilter,
        ExtendQueryPartsCommentsJoin,
        ExtendQueryPartsCommentsExtraAnnoJoin,
        ExtendQueryPartsAcmgCriteriaJoin,
        ExtendQueryPartsModesOfInheritanceJoin,
        ExtendQueryPartsDiseaseGeneJoin,
        ExtendQueryPartsGnomadConstraintsJoin,
        ExtendQueryPartsExacConstraintsJoin,
        ExtendQueryPartsInHouseJoinAndFilter,
        ExtendQueryPartsClinvarJoin,
    ]


class CaseExportTableQueryPartsBuilder(QueryPartsBuilder):
    """Same as normal query, just with Conservation part added."""

    qp_extender_classes = [
        *extender_classes_base,
        ExtendQueryPartsHgncAndConservationJoin,
        ExtendQueryPartsAcmgJoin,
        ExtendQueryPartsMgiJoin,
        ExtendQueryPartsGnomadConstraintsJoin,
    ]


class CaseExportVcfQueryPartsBuilder(QueryPartsBuilder):
    """Just query tables joined, no tables that just provide information."""

    # TODO What about DbSNP and HGNC that are used for filtering???
    # TODO Should we just take the stored results and join the required data?
    # TODO But then, some extensions join AND query ... maybe split them (HGNC?, Clinvar?, dbSNP, HGMD)
    qp_extender_classes = extender_classes_base


class ProjectLoadPrefetchedQueryPartsBuilder(QueryPartsBuilder):
    qp_extender_classes = [
        ExtendQueryPartsProjectLoadPrefetched,
        ExtendQueryPartsCaseJoinAndFilter,
        ExtendQueryPartsMitochondrialFrequenciesJoin,
        ExtendQueryPartsDbsnpJoin,
        ExtendQueryPartsHgncJoin,
        ExtendQueryPartsGeneSymbolJoin,
        ExtendQueryPartsMgiJoin,
        ExtendQueryPartsAcmgJoin,
        ExtendQueryPartsFlagsJoin,
        ExtendQueryPartsCommentsJoin,
        ExtendQueryPartsAcmgCriteriaJoin,
        ExtendQueryPartsGnomadConstraintsJoin,
        ExtendQueryPartsExacConstraintsJoin,
        ExtendQueryPartsClinvarJoin,
        ExtendQueryPartsModesOfInheritanceJoin,
        ExtendQueryPartsDiseaseGeneJoin,
    ]


class ProjectExportTableQueryPartsBuilder(QueryPartsBuilder):
    qp_extender_classes = [
        *extender_classes_base,
        ExtendQueryPartsHgncAndConservationJoin,
        ExtendQueryPartsGeneSymbolJoin,
        ExtendQueryPartsAcmgJoin,
        ExtendQueryPartsMgiJoin,
        ExtendQueryPartsGnomadConstraintsJoin,
    ]


class ProjectExportVcfQueryPartsBuilder(QueryPartsBuilder):
    """Just query tables joined, no tables that just provide information."""

    # TODO What about DbSNP and HGNC that are used for filtering???
    # TODO Should we just take the stored results and join the required data?
    # TODO But then, some extensions join AND query ... maybe split them (HGNC?, Clinvar?, dbSNP, HGMD)
    qp_extender_classes = extender_classes_base


class CompHetCombiner:
    def __init__(self, case, builder):
        self.case = case
        self.builder = builder

    def to_stmt(self, kwargs, order_by=None):
        # Find out if comp het index has no parents.
        members = [
            m
            for m in self.case.get_filtered_pedigree_with_samples()
            if m["patient"] == kwargs["compound_recessive_index"]
        ]
        if len(members) != 1:
            raise RuntimeError("Could not find index from pedigree")
        # Check if parents have genotypes
        members_with_gt = self.case.get_members_with_samples()
        singleton = (
            members[0]["father"] == "0"
            and members[0]["mother"] == "0"
            or members[0]["father"] not in members_with_gt
            and members[0]["mother"] not in members_with_gt
        )
        father_stmt = DefaultCombiner(self.case, self.builder).to_stmt(
            kwargs, extender_genotype_class=ExtendQueryPartsGenotypeGtQualityFatherFilter
        )
        mother_stmt = DefaultCombiner(self.case, self.builder).to_stmt(
            kwargs, extender_genotype_class=ExtendQueryPartsGenotypeGtQualityMotherFilter
        )
        if not singleton:
            union_stmt = union(father_stmt, mother_stmt).alias("comp_het_union")
            window_stmt = (
                select(
                    [
                        *union_stmt.c,
                        func.sum(union_stmt.c.father_marker)
                        .over(partition_by=union_stmt.c.gene_id)
                        .label("father_count"),
                        func.sum(union_stmt.c.mother_marker)
                        .over(partition_by=union_stmt.c.gene_id)
                        .label("mother_count"),
                    ]
                )
                .select_from(union_stmt)
                .alias("comp_het_window")
            )
            # Remove all comp het support columns that are not required anymore to match the number of
            # columns in the default query to be able to apply the union!
            result = (
                select(
                    [
                        e
                        for e in [*window_stmt.c]
                        if not str(e).endswith(
                            (
                                ".singleton_count",
                                ".father_count",
                                ".mother_count",
                                ".mother_marker",
                                ".father_marker",
                            )
                        )
                    ]
                )
                .select_from(window_stmt)
                .where(and_(window_stmt.c.father_count > 0, window_stmt.c.mother_count > 0))
            )
        else:  # singleton
            # It doesn't matter which parent GT comp het filter we take, as there are no parents.
            # We need to distinguish the singleton case from the others, because it would match
            # the same variants twice, using the upper statement.
            # It sets the gt pattern for the index to het, this is the only thing we require.
            # Pay attention to be consistent with the marker.
            singleton_stmt = father_stmt.alias("comp_het_singleton")
            window_stmt = (
                select(
                    [
                        *singleton_stmt.c,
                        func.sum(singleton_stmt.c.father_marker)
                        .over(partition_by=singleton_stmt.c.gene_id)
                        .label("singleton_count"),
                    ]
                )
                .select_from(singleton_stmt)
                .alias("comp_het_window")
            )
            # As we require at least two variants in a gene, we need to increase the lower limit.
            # Remove also all comp het support columns that are not required anymore to match the number of
            # columns in the default query to be able to apply the union!
            result = (
                select(
                    [
                        e
                        for e in [*window_stmt.c]
                        if not str(e).endswith(
                            (
                                ".singleton_count",
                                ".father_count",
                                ".mother_count",
                                ".mother_marker",
                                ".father_marker",
                            )
                        )
                    ]
                )
                .select_from(window_stmt)
                .where(window_stmt.c.singleton_count > 1)
            )

        return result.order_by(*(order_by or []))


class DefaultCombiner:
    def __init__(self, case, builder, query_id=None):
        self.case = case
        self.builder = builder
        self.query_id = query_id

    def to_stmt(self, kwargs, order_by=None, extender_genotype_class=None):
        query_parts = self.builder(self.case, self.query_id).run(kwargs, extender_genotype_class)
        return query_parts.to_stmt(order_by=order_by)


class RecessiveCombiner:
    def __init__(self, case, builder):
        self.case = case
        self.builder = builder

    def to_stmt(self, kwargs, order_by=None):
        comphet_stmt = CompHetCombiner(self.case, self.builder).to_stmt(kwargs)
        default_stmt = DefaultCombiner(self.case, self.builder).to_stmt(
            kwargs, extender_genotype_class=ExtendQueryPartsGenotypeGtQualityRecessiveFilter
        )
        return union(comphet_stmt, default_stmt).order_by(*(order_by or []))


def _chunked(arr, max_size):
    chunks = []
    i = 0
    while i < len(arr):
        chunks.append(arr[i : i + max_size])
        i += max_size
    return chunks


class CasePrefetchQuery:
    builder = QueryPartsBuilder

    def __init__(self, case_or_cases, engine, query_id=None):
        try:
            self.cases = list(iter(case_or_cases))
        except TypeError:
            self.cases = [case_or_cases]
        self.engine = engine
        self.query_id = query_id

    def run(self, kwargs):
        order_by = [
            column("chromosome_no"),
            column("start"),
            column("end"),
            column("reference"),
            column("alternative"),
            column("family_name"),
        ]
        stmts = []
        for case in self.cases:
            comp_het_index = kwargs.get("compound_recessive_indices", {}).get(case.name)
            recessive_index = kwargs.get("recessive_indices", {}).get(case.name)
            if comp_het_index and self.query_id is None:
                # Set the current compound recessive index
                kwargs["compound_recessive_index"] = comp_het_index
                combiner = CompHetCombiner(case, self.builder)
            elif recessive_index and self.query_id is None:
                # Set the current compound recessive index
                kwargs["compound_recessive_index"] = recessive_index
                combiner = RecessiveCombiner(case, self.builder)
            else:  # compound recessive not in kwargs or disabled
                combiner = DefaultCombiner(case, self.builder, self.query_id)
            stmts.append(combiner.to_stmt(kwargs))
        stmt = union(*stmts).order_by(*order_by)
        if settings.DEBUG:
            print(
                "\n"
                + sqlparse.format(
                    stmt.compile(self.engine).string, reindent=True, keyword_case="upper"
                )
            )
        return self.engine.execute(stmt)


class CaseLoadPrefetchedQuery(CasePrefetchQuery):
    builder = CaseLoadPrefetchedQueryPartsBuilder


class CaseExportTableQuery(CasePrefetchQuery):
    builder = CaseExportTableQueryPartsBuilder


class CaseExportVcfQuery(CasePrefetchQuery):
    builder = CaseExportVcfQueryPartsBuilder


class ProjectPrefetchQuery(CasePrefetchQuery):
    def __init__(self, project_or_cohort, engine, query_id=None, user=None):
        if isinstance(project_or_cohort, Cohort) and user:
            cases = project_or_cohort.get_accessible_cases_for_user(user)
        elif isinstance(project_or_cohort, Cohort):
            cases = project_or_cohort.cases.all()
        else:
            cases = project_or_cohort.get_active_smallvariant_cases()
        super().__init__(cases, engine, query_id)


class ProjectLoadPrefetchedQuery(ProjectPrefetchQuery):
    builder = ProjectLoadPrefetchedQueryPartsBuilder


class ProjectExportTableQuery(ProjectPrefetchQuery):
    builder = ProjectExportTableQueryPartsBuilder


class ProjectExportVcfQuery(ProjectPrefetchQuery):
    builder = ProjectExportVcfQueryPartsBuilder


# Query for obtaining the knownGene alignments (used from JSON query).


class KnownGeneAAQuery:
    """Query database for the ``knownGeneAA`` information."""

    def __init__(self, engine):
        #: The Aldjemy engine to use
        self.engine = engine

    def run(self, kwargs):
        """Execute the query."""
        # TODO: Replace kwargs with actual parameters
        #
        # TODO: we should load the alignment based on UCSC transcript ID (without version) and then post-filter
        # TODO: by column...
        distinct_fields = [
            KnowngeneAA.sa.release,
            KnowngeneAA.sa.chromosome,
            KnowngeneAA.sa.start,
            KnowngeneAA.sa.end,
        ]
        query = (
            select(distinct_fields + [KnowngeneAA.sa.alignment])
            .select_from(KnowngeneAA.sa.table)
            .where(
                and_(
                    KnowngeneAA.sa.release == kwargs["release"],
                    KnowngeneAA.sa.chromosome == kwargs["chromosome"],
                    KnowngeneAA.sa.start <= int(kwargs["start"]) + (len(kwargs["reference"]) - 1),
                    KnowngeneAA.sa.end >= int(kwargs["start"]),
                )
            )
            .order_by(KnowngeneAA.sa.start)
            .distinct(*distinct_fields)
        )
        return self.engine.execute(query)


# Query for deleting the variants of a case.


class DeleteSmallVariantsQuery:
    def __init__(self, engine):
        #: The Aldjemy engine to use
        self.engine = engine

    def run(self, case_id):
        """Execute the query."""
        # Delete all small variants.
        yield self.engine.execute(
            delete(SmallVariant.sa.table).where(SmallVariant.sa.case_id == case_id)
        )


class DeleteStructuralVariantsQuery:
    def __init__(self, engine):
        #: The Aldjemy engine to use
        self.engine = engine

    def run(self, case_id):
        """Execute the query."""
        # Delete all structural variant gene annotations.
        yield self.engine.execute(
            delete(StructuralVariantGeneAnnotation.sa.table).where(
                StructuralVariantGeneAnnotation.sa.case_id == case_id
            )
        )
        # Delete all structural variants.
        yield self.engine.execute(
            delete(StructuralVariant.sa.table).where(StructuralVariant.sa.case_id == case_id)
        )


# Queries for pulling all user annotation for one or more cases from the database.


@attr.s(auto_attribs=True, frozen=True)
class _VariantInCase:
    """Identifies a variant in a case."""

    id: int
    case_id: int
    release: str
    chromosome: str
    start: int
    reference: str
    alternative: str


@attr.s(auto_attribs=True, frozen=True)
class AnnotatedSmallVariants:
    """Helper struct that contains small variants and their annotation only."""

    small_variants: typing.List[SmallVariant]
    small_variant_flags: typing.List[SmallVariantFlags]
    small_variant_comments: typing.List[SmallVariantComment]
    acmg_criteria_rating: typing.List[AcmgCriteriaRating]


class SmallVariantUserAnnotationQuery:
    """Query for all user annotated variants of one case, multiple cases, or all within a project."""

    KEYS = ["id", "case_id", "release", "chromosome", "start", "reference", "alternative"]

    def __init__(self, engine):
        #: The Aldjemy engine to use.
        self.engine = engine

    def run(self, *, case=None, cases=None, project=None):
        """Return information for single case, multiple cases, or all in a project."""
        if sum(map(int, map(bool, (case, cases, project)))) != 1:
            raise ValueError("Exactly one of case, cases, and project must be given")
        if case:
            case_ids = [case.id]
        elif cases:
            case_ids = [c.id for c in cases]
        else:
            case_ids = [c.id for c in Case.objects.filter(project=project)]
        return self._query(case_ids)

    def _query(self, case_ids: typing.List[int]):
        def chunks(lst, n=50):
            """Yield successive n-sized chunks from lst."""
            for i in range(0, len(lst), n):
                yield lst[i : i + n]

        result_flags = self._query_model(SmallVariantFlags, case_ids)
        result_comments = self._query_model(SmallVariantComment, case_ids)
        result_ratings = self._query_model(AcmgCriteriaRating, case_ids)
        variant_keys = list(
            sorted(
                set(map(self._variant_keys, result_flags))
                | set(map(self._variant_keys, result_comments))
                | set(map(self._variant_keys, result_ratings))
            )
        )

        small_var_ids = []
        for variant_keys_chunk in chunks(variant_keys):
            keys = ["case_id", "release", "chromosome", "start", "reference", "alternative"]
            stmt = (
                select([SmallVariant.sa.id])
                .select_from(SmallVariant.sa.table)
                .where(
                    tuple_(*[getattr(SmallVariant.sa, key) for key in keys]).in_(
                        [[getattr(k, key) for key in keys] for k in variant_keys_chunk]
                    )
                )
            )
            small_var_ids += [rec.id for rec in self.engine.execute(stmt)]

        flags_ids = [x["id"] for x in result_flags]
        comments_ids = [x["id"] for x in result_comments]
        ratings_ids = [x["id"] for x in result_ratings]

        return AnnotatedSmallVariants(
            small_variants=list(SmallVariant.objects.filter(id__in=small_var_ids)),
            small_variant_flags=list(SmallVariantFlags.objects.filter(id__in=flags_ids)),
            # for some reason, ordering in the model has no effect.
            small_variant_comments=list(
                SmallVariantComment.objects.filter(id__in=comments_ids).order_by("date_created")
            ),
            acmg_criteria_rating=list(AcmgCriteriaRating.objects.filter(id__in=ratings_ids)),
        )

    def _query_model(self, model: typing.Any, case_ids: typing.List[int]):
        stmt = (
            select([getattr(model.sa, key) for key in self.KEYS])
            .select_from(model.sa.table)
            .where(model.sa.case_id.in_(case_ids))
        )
        result = self.engine.execute(stmt)
        return list(map(dict, result))

    def _variant_keys(self, record: typing.Any):
        """Extract identifier of the given variant in the given case."""
        return _VariantInCase(**{key: record[key] for key in self.KEYS})
