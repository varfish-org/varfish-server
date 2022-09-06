"""Building queries for structural variants based on the ``QueryParts`` infrastructure from ``variants``."""

import enum
from itertools import chain
import logging
import operator
import sys

from django.conf import settings
from django.db.models import Q
from sqlalchemy import ARRAY, VARCHAR, any_, column, text
from sqlalchemy.sql import and_, case, cast, desc, func, not_, or_, select, true
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.types import Float, Integer
import sqlparse

from geneinfo.models import Hgnc
from genomicfeatures.models import (
    EnsemblRegulatoryFeature,
    GeneInterval,
    TadBoundaryInterval,
    TadInterval,
    TadSet,
    VistaEnhancer,
)
from regmaps.models import RegElement, RegInteraction, RegMapCollection
from svdbs.models import DbVarSv, DgvGoldStandardSvs, DgvSvs, ExacCnv, GnomAdSv, ThousandGenomesSv
from variants.queries import ExtendQueryPartsBase
from variants.queries import ExtendQueryPartsCaseJoinAndFilter as _ExtendQueryPartsCaseJoinAndFilter
from variants.queries import ExtendQueryPartsDiseaseGeneJoin as _ExtendQueryPartsDiseaseGeneJoin
from variants.queries import ExtendQueryPartsGenotypeDefaultBase, QueryParts, QueryPartsBuilder

from .models import (
    BackgroundSv,
    BackgroundSvSet,
    StructuralVariant,
    StructuralVariantComment,
    StructuralVariantFlags,
    StructuralVariantGeneAnnotation,
    StructuralVariantSet,
)

#: Logger to use in this module.
LOGGER = logging.getLogger(__name__)


def overlaps(lhs, rhs, min_overlap=None, rhs_start=None, rhs_end=None, padding=None):
    """Returns term of ``lhs`` overlapping with ``rhs`` based on the start/end fields.

    Padding is only interpreted if ``min_overlap`` is ``None``.
    """
    if padding is None:
        padding = 0
    if rhs_start is None:
        rhs_start = rhs.sa.start
    if rhs_end is None:
        rhs_end = rhs.sa.end
    if min_overlap is None:
        return and_(
            lhs.sa.release == rhs.sa.release,
            lhs.sa.chromosome == rhs.sa.chromosome,
            lhs.sa.bin.in_(
                select([column("bin")]).select_from(func.overlapping_bins(rhs_start - 1, rhs_end))
            ),
            lhs.sa.end >= rhs_start - padding,
            lhs.sa.start <= rhs_end + padding,
        )
    else:
        term_overlap = func.least(lhs.sa.end, rhs_end) - func.greatest(lhs.sa.start, rhs_start) + 1
        return and_(
            lhs.sa.release == rhs.sa.release,
            lhs.sa.chromosome == rhs.sa.chromosome,
            rhs.sa.bin.in_(
                select([column("bin")]).select_from(
                    func.overlapping_bins(lhs.sa.start - 1, lhs.sa.end)
                )
            ),
            lhs.sa.end >= rhs_start,
            lhs.sa.start <= rhs_end,
            cast(term_overlap, Float) / func.greatest((rhs_end - rhs_start + 1), 1) > min_overlap,
            cast(term_overlap, Float) / func.greatest((lhs.sa.end - lhs.sa.start + 1), 1)
            > min_overlap,
        )


def structural_variant_query(_self, kwargs):
    """Return the core ``QueryParts`` for the structural variant query.

    This will result in selecting the fields from ``StructuralVariant`` with a left outer join to
    ``StructuralVariantGeneAnnotation`` on the ``sv_uuid`` field.  Everything else will come from the query parts
    extenders.
    """
    if kwargs["database_select"] == "refseq":
        gene_id = StructuralVariantGeneAnnotation.sa.refseq_gene_id
    else:  # kwargs["database_select"] == "ensembl"
        gene_id = StructuralVariantGeneAnnotation.sa.ensembl_gene_id
    return QueryParts(
        fields=[
            StructuralVariant.sa.id,
            StructuralVariant.sa.release,
            StructuralVariant.sa.chromosome,
            StructuralVariant.sa.start,
            StructuralVariant.sa.end,
            (StructuralVariant.sa.end - StructuralVariant.sa.start + 1).label("sv_length"),
            StructuralVariant.sa.bin,
            StructuralVariant.sa.start_ci_left,
            StructuralVariant.sa.start_ci_right,
            StructuralVariant.sa.end_ci_left,
            StructuralVariant.sa.end_ci_right,
            StructuralVariant.sa.case_id,
            StructuralVariant.sa.sv_uuid,
            StructuralVariant.sa.caller,
            StructuralVariant.sa.sv_type,
            StructuralVariant.sa.sv_sub_type,
            StructuralVariant.sa.info,
            StructuralVariant.sa.genotype,
            StructuralVariantGeneAnnotation.sa.refseq_gene_id,
            StructuralVariantGeneAnnotation.sa.ensembl_gene_id,
            gene_id.label("gene_id"),
        ],
        selectable=StructuralVariant.sa.table.outerjoin(
            StructuralVariantGeneAnnotation.sa.table,
            and_(
                StructuralVariantGeneAnnotation.sa.sv_uuid == StructuralVariant.sa.sv_uuid,
                StructuralVariantGeneAnnotation.sa.case_id == StructuralVariant.sa.case_id,
            ),
        ),
        conditions=[],
    )


class ExtendQueryPartsCaseJoinAndFilter(_ExtendQueryPartsCaseJoinAndFilter):
    """Join structural variants with case and filter for it."""

    model = StructuralVariant
    model_set = StructuralVariantSet


class ExtendQueryPartsGenotypeFilter(ExtendQueryPartsGenotypeDefaultBase):
    """Extend ``QueryParts`` with genotype and quality."""

    model = StructuralVariant

    def _build_quality_term(self, name):
        if self.quality_term_disabled:
            return True

        genotype = StructuralVariant.sa.genotype
        is_variant = or_(
            genotype[name]["gt"].astext == "0/1",
            genotype[name]["gt"].astext == "0|1",
            genotype[name]["gt"].astext == "1/0",
            genotype[name]["gt"].astext == "1|0",
            genotype[name]["gt"].astext == "1",
            genotype[name]["gt"].astext == "1/1",
            genotype[name]["gt"].astext == "1|1",
        )
        rhs = and_(
            # Genotype quality
            or_(
                or_(self.kwargs.get("%s_gq_min" % name) is None, genotype[name]["gq"].is_(None)),
                genotype[name]["gq"].astext.cast(Integer) >= (self.kwargs["%s_gq_min" % name] or 0),
            ),
            # Split read: min coverage, min/max variant split reads
            or_(
                or_(self.kwargs.get("%s_src_min" % name) is None, genotype[name]["src"].is_(None)),
                genotype[name]["src"].astext.cast(Integer)
                >= (self.kwargs["%s_src_min" % name] or 0),
            ),
            or_(
                # Min variant support terms only apply for non-variant terms.
                not_(is_variant),
                or_(
                    or_(
                        self.kwargs.get("%s_srv_min" % name) is None,
                        genotype[name]["srv"].is_(None),
                    ),
                    genotype[name]["srv"].astext.cast(Integer)
                    >= (self.kwargs["%s_srv_min" % name] or 0),
                ),
            ),
            or_(
                or_(self.kwargs.get("%s_srv_max" % name) is None, genotype[name]["srv"].is_(None)),
                genotype[name]["srv"].astext.cast(Integer)
                <= (self.kwargs["%s_srv_max" % name] or 0),
            ),
            # Paired read: min coverage, min/max variant paired reads
            or_(
                or_(self.kwargs.get("%s_pec_min" % name) is None, genotype[name]["pec"].is_(None)),
                genotype[name]["pec"].astext.cast(Integer)
                >= (self.kwargs["%s_pec_min" % name] or 0),
            ),
            or_(
                # Min variant support terms only apply for non-variant terms.
                not_(is_variant),
                or_(
                    or_(
                        self.kwargs.get("%s_pev_min" % name) is None,
                        genotype[name]["pev"].is_(None),
                    ),
                    genotype[name]["pev"].astext.cast(Integer)
                    >= (self.kwargs["%s_pev_min" % name] or 0),
                ),
            ),
            or_(
                or_(self.kwargs.get("%s_pev_max" % name) is None, genotype[name]["pev"].is_(None)),
                genotype[name]["pev"].astext.cast(Integer)
                <= (self.kwargs["%s_pev_max" % name] or 0),
            ),
            # Overall split OR paired read: min coverage, min/max variant paired reads
            or_(
                or_(
                    self.kwargs.get("%s_cov_min" % name) is None,
                    and_(genotype[name]["src"].is_(None), genotype[name]["pec"].is_(None)),
                ),
                coalesce(genotype[name]["src"].astext.cast(Integer), 0)
                + coalesce(genotype[name]["pec"].astext.cast(Integer), 0)
                >= (self.kwargs["%s_cov_min" % name] or 0),
            ),
            or_(
                or_(
                    # Min variant support terms only apply for non-variant terms.
                    not_(is_variant),
                    or_(
                        self.kwargs.get("%s_var_min" % name) is None,
                        and_(genotype[name]["srv"].is_(None), genotype[name]["pev"].is_(None)),
                    ),
                    coalesce(genotype[name]["srv"].astext.cast(Integer), 0)
                    + coalesce(genotype[name]["pev"].astext.cast(Integer), 0)
                    >= (self.kwargs["%s_var_min" % name] or 0),
                )
            ),
            or_(
                or_(
                    self.kwargs.get("%s_var_max" % name) is None,
                    and_(genotype[name]["srv"].is_(None), genotype[name]["pev"].is_(None)),
                ),
                coalesce(genotype[name]["srv"].astext.cast(Integer), 0)
                + coalesce(genotype[name]["pev"].astext.cast(Integer), 0)
                <= (self.kwargs["%s_var_max" % name] or 0),
            ),
        )
        return or_(genotype[name].is_(None), rhs)


class ExtendQueryPartsGenomicRegionFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with genomic region filter."""

    # TODO: harmonize with small variants, add end position and bin there, remove overlapping bins here

    def extend_conditions(self, _query_parts):
        def normalize_chrom(chrom):
            """Normalize chromosome name."""
            # TODO: properly handle GRCh37 vs. GRCh38
            return chrom.replace("chr", "")

        if self.kwargs["genomic_region"]:
            yield or_(
                *[
                    and_(
                        StructuralVariant.sa.chromosome == normalize_chrom(chrom),
                        (StructuralVariant.sa.end >= start) if start else True,
                        (StructuralVariant.sa.start <= end) if end else True,
                    )
                    for chrom, start, end in self.kwargs["genomic_region"]
                ]
            )


class ExtendQueryPartsSizeFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for the size filter.

    Breakends count as SVs of "infinitely" large size.  Thus, breakends will remain for any given  minimal sizes and
    they will be removed for any given maximal size.
    """

    def extend_conditions(self, _query_parts):
        terms = []
        if self.kwargs.get("sv_size_min") is not None:
            terms.append(
                or_(
                    StructuralVariant.sa.sv_type == "BND",
                    StructuralVariant.sa.end - StructuralVariant.sa.start + 1
                    >= self.kwargs["sv_size_min"],
                )
            )
        if self.kwargs.get("sv_size_max") is not None:
            terms.append(
                and_(
                    StructuralVariant.sa.sv_type != "BND",
                    StructuralVariant.sa.end - StructuralVariant.sa.start + 1
                    <= self.kwargs["sv_size_max"],
                )
            )
        return terms


class ExtendQueryPartsSvTypeFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for filtering for SV type."""

    def extend_conditions(self, _query_parts):
        yield or_(
            or_(
                StructuralVariant.sa.sv_type.is_(None),
                StructuralVariant.sa.sv_type.in_(self.kwargs["sv_type"]),
            ),
            or_(
                StructuralVariant.sa.sv_sub_type.is_(None),
                StructuralVariant.sa.sv_sub_type.in_(self.kwargs["sv_sub_type"]),
            ),
        )


class ExtendQueryPartsPublicDatabaseFrequencyJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for filtering for public database overlap and filter."""

    #: Information for processing the public databases.
    TOKEN_MODEL_FIELD = (
        ("dgv", DgvSvs, func.sum(DgvSvs.sa.observed_gains) + func.sum(DgvSvs.sa.observed_losses)),
        ("dgv_gs", DgvGoldStandardSvs, func.sum(DgvGoldStandardSvs.sa.num_carriers)),
        ("g1k", ThousandGenomesSv, func.sum(ThousandGenomesSv.sa.num_var_alleles)),
        ("exac", ExacCnv, func.count()),
        ("dbvar", DbVarSv, func.sum(DbVarSv.sa.num_carriers)),
        ("gnomad", GnomAdSv, func.sum(GnomAdSv.sa.n_het + GnomAdSv.sa.n_homalt)),
        ("inhouse", BackgroundSv, func.sum(BackgroundSv.sa.carriers)),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subqueries = self._build_subqueries()
        self.fields = self._build_fields(self.subqueries)

    def _build_subqueries(self):
        result = {}
        for token, model, observed_events in self.TOKEN_MODEL_FIELD:
            if hasattr(model, "start_outer"):
                model_start = model.sa.start_outer
                model_end = model.sa.end_inner
            else:
                model_start = model.sa.start
                model_end = model.sa.end
            min_overlap = float(self.kwargs.get("%s_min_overlap" % token, "0.75"))
            where_terms = [
                # TODO: type mapping -- interesting/necessary?
                # StructuralVariant.sa.sv_type == model.sa.sv_type,
                overlaps(
                    StructuralVariant,
                    model,
                    min_overlap=min_overlap,
                    rhs_start=model_start,
                    rhs_end=model_end,
                ),
            ]
            if token == "inhouse":
                latest_set = BackgroundSvSet.objects.latest_active_if_any()
                if not latest_set:
                    LOGGER.warning("Could not find a latest BackgroundSvSet to use")
                    continue  # don't have a set
                else:
                    LOGGER.info("Using latest BackgroundSvSet: %s" % latest_set.sodar_uuid)
                    where_terms.append(model.sa.bg_sv_set_id == latest_set.pk)
            result[token] = (
                select([observed_events.label("observed_events")])
                .select_from(model.sa)
                .where(and_(*where_terms))
                .alias("subquery_%s_inner" % token)
            ).lateral("subquery_%s_outer" % token)
        return result

    def _build_fields(self, subqueries):
        # NB: subqueries is given as a parameter here to highlight the dependency between the two helper functions
        fields = {}
        for token, _, observed_events in self.TOKEN_MODEL_FIELD:
            if token in subqueries:  # e.g., "inhouse" might not exist yet
                field = func.coalesce(subqueries[token].c.observed_events, 0)
                fields["%s_overlap_count" % token] = field.label("%s_overlap_count" % token)
        return fields

    def extend_fields(self, _query_parts):
        return list(self.fields.values())

    def extend_conditions(self, _query_parts):
        result = []
        for token, _, _ in self.TOKEN_MODEL_FIELD:
            entity = "alleles" if token == "g1k" else "carriers"
            if (
                self.kwargs.get("%s_enabled" % token, False)
                and ("%s_overlap_count" % token) in self.fields
                and self.kwargs.get("%s_max_carriers" % token) is not None
            ):
                result.append(
                    self.fields["%s_overlap_count" % token]
                    <= self.kwargs["%s_max_%s" % (token, entity)]
                )
        return result

    def extend_selectable(self, query_parts):
        result = query_parts.selectable
        for subquery in self.subqueries.values():
            result = result.outerjoin(subquery, true())
        return result


class ExtendQueryPartsFlagsJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for joining to user-defined flags and filtering on overlap."""

    #: Minimal reciprocal overlap between SV and flagged interval.
    MIN_OVERLAP = 0.95

    #: The information for processing fields for aggregation.
    TOKEN_FN_DEFAULT_FNAME = (
        ("count", func.count, 0, "id"),
        ("bookmarked", func.bool_or, False, None),
        ("candidate", func.bool_or, False, None),
        ("segregates", func.bool_or, False, None),
        ("doesnt_segregate", func.bool_or, False, None),
        ("final_causative", func.bool_or, False, None),
        ("for_validation", func.bool_or, False, None),
        ("no_disease_association", func.bool_or, False, None),
        ("visual", func.max, "", None),
        ("molecular", func.max, "", None),
        ("validation", func.max, "", None),
        ("phenotype_match", func.max, "", None),
        ("summary", func.max, "", None),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()
        self.fields = self._build_fields(self.subquery)

    def _build_subquery(self):
        fields = []
        for token, fn, _, field_name in self.TOKEN_FN_DEFAULT_FNAME:
            field_label = "flag_%s" % token
            field_name = field_name or field_label
            fields.append(fn(getattr(StructuralVariantFlags.sa, field_name)).label(field_label))
        return (
            select(fields)
            .select_from(StructuralVariantFlags.sa)
            .where(
                and_(
                    StructuralVariant.sa.sv_type == StructuralVariantFlags.sa.sv_type,
                    overlaps(
                        StructuralVariant, StructuralVariantFlags, min_overlap=self.MIN_OVERLAP
                    ),
                )
            )
            .alias("subquery_flags_inner")
            .lateral("subquery_flags_outer")
        )

    def _build_fields(self, subquery):
        # NB: subquery is given as a parameter here to highlight the dependency between the two helper functions
        result = []
        for token, _, default, _ in self.TOKEN_FN_DEFAULT_FNAME:
            field_name = "flag_%s" % token
            result.append(func.coalesce(getattr(subquery.c, field_name), default).label(field_name))
        return result

    def extend_fields(self, _query_parts):
        return self.fields

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsCommentsJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for joining to user comments and filtering on overlap."""

    #: Minimal reciprocal overlap between SV and comment interval.
    MIN_OVERLAP = 0.95

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()

    def _build_subquery(self):
        return (
            select([func.count(StructuralVariantComment.sa.id).label("comment_count")])
            .select_from(StructuralVariantComment.sa)
            .where(
                and_(
                    StructuralVariant.sa.sv_type == StructuralVariantComment.sa.sv_type,
                    overlaps(
                        StructuralVariant, StructuralVariantComment, min_overlap=self.MIN_OVERLAP
                    ),
                )
            )
            .alias("subquery_comments_inner")
            .lateral("subquery_comments_outer")
        )

    def extend_fields(self, _query_parts):
        yield self.subquery.c.comment_count

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsVariantEffectFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for filtering for variant effect, whether a transcript overlap is required, and whether
    coding and/or non-coding transcripts are accepted.
    """

    def extend_conditions(self, _query_parts):
        # Matching variant effect and whether there has to be an overlap.
        effects = cast(self.kwargs["effects"], ARRAY(VARCHAR()))
        result = self._effect_field().overlap(effects)
        if not self.kwargs["require_transcript_overlap"]:
            result = or_(result, self._effect_field().is_(None))
        yield result
        # Whether to include coding/non-coding transcripts.
        if not self.kwargs["transcripts_coding"]:
            yield self._transcript_coding_field() == False  # noqa: E712
        if not self.kwargs["transcripts_noncoding"]:
            yield self._transcript_coding_field() == True  # noqa: E712

    def _effect_field(self):
        """Return the effects field of ``StructuralVariantGeneAnnotation`` to use based on the selected database."""
        if self.kwargs["database_select"] == "refseq":
            return StructuralVariantGeneAnnotation.sa.refseq_effect
        else:  # kwargs["database_select"] == "ensembl"
            return StructuralVariantGeneAnnotation.sa.ensembl_effect

    def _transcript_coding_field(self):
        """Return the "transcript coding" field of ``StructuralVariantGeneAnnotation`` to use based on the selected
        database.
        """
        if self.kwargs["database_select"] == "refseq":
            return StructuralVariantGeneAnnotation.sa.refseq_transcript_coding
        else:  # kwargs["database_select"] == "ensembl"
            return StructuralVariantGeneAnnotation.sa.ensembl_transcript_coding


class ExtendQueryPartsGenesJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` for joining to gene information and filtering on overlap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()
        self.fields = self._build_fields(self.subquery)

    def _build_subquery(self):
        if not self.kwargs.get("tad_set_uuid"):
            return None

        set_pk = TadSet.objects.get(sodar_uuid=self.kwargs["tad_set_uuid"]).pk

        if self.kwargs["database_select"] == "refseq":
            term_join_gene_id = GeneInterval.sa.gene_id == Hgnc.sa.entrez_id
        else:  # kwargs["database_select"] == "ensembl"
            term_join_gene_id = GeneInterval.sa.gene_id == Hgnc.sa.ensembl_gene_id

        query = (
            select(
                [
                    func.array_agg(GeneInterval.sa.gene_id).label("itv_shared_gene_ids"),
                    func.array_agg(Hgnc.sa.symbol).label("itv_shared_gene_symbols"),
                ]
            )
            .select_from(
                GeneInterval.sa.table.outerjoin(Hgnc.sa.table, term_join_gene_id).outerjoin(
                    TadInterval.sa.table,
                    and_(
                        TadInterval.sa.tad_set_id == set_pk,
                        overlaps(TadInterval, StructuralVariant),
                    ),
                )
            )
            .where(
                and_(
                    GeneInterval.sa.database == self.kwargs["database_select"],
                    overlaps(TadInterval, GeneInterval),
                )
            )
            .alias("subquery_genes_intervals_inner")
        ).lateral("subquery_genes_intervals_outer")

        return query

    def _build_fields(self, subquery):
        # NB: subqueries is given as a parameter here to highlight the dependency between the two helper functions
        if subquery is None:
            return []
        else:
            return [subquery.c.itv_shared_gene_ids, subquery.c.itv_shared_gene_symbols]

    def extend_fields(self, _query_parts):
        return self.fields

    def extend_conditions(self, _query_parts):
        for token, fn in (("block", operator.ne), ("allow", operator.eq)):
            if self.kwargs["gene_%slist" % token]:
                hgnc_ids = [
                    hgnc.id
                    for hgnc in Hgnc.objects.filter(
                        Q(symbol__in=self.kwargs["gene_%slist" % token])
                        | Q(entrez_id__in=self.kwargs["gene_%slist" % token])
                        | Q(ensembl_gene_id__in=self.kwargs["gene_%slist" % token])
                    )
                ]
                if (token == "block" and hgnc_ids) or (token == "allow"):
                    yield fn(Hgnc.sa.id, any_(hgnc_ids))

    def extend_selectable(self, query_parts):
        if not self.kwargs.get("tad_set_uuid"):
            return query_parts.selectable
        else:
            return query_parts.selectable.outerjoin(self.subquery, true())


class ExtendQueryPartsTadBoundaryDistanceJoin(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with information to TAD boundary."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()

    def _build_subquery(self):
        if not self.kwargs.get("tad_set_uuid"):
            return None
        else:
            set_pk = TadSet.objects.get(sodar_uuid=self.kwargs["tad_set_uuid"]).pk
            term_interval_center = (
                TadBoundaryInterval.sa.start
                + (TadBoundaryInterval.sa.end - TadBoundaryInterval.sa.start + 1) / 2
            )
            term_overlaps = and_(
                term_interval_center >= StructuralVariant.sa.start,
                term_interval_center <= StructuralVariant.sa.end,
            )
            fields = [
                func.coalesce(
                    func.min(
                        case(
                            [(term_overlaps, 0)],
                            else_=func.least(
                                func.abs(term_interval_center - StructuralVariant.sa.start),
                                func.abs(term_interval_center - StructuralVariant.sa.end),
                            ),
                        )
                    ),
                    -1,
                ).label("distance_to_center")
            ]
            return (
                select(fields)
                .select_from(TadBoundaryInterval.sa)
                .where(
                    and_(
                        TadBoundaryInterval.sa.tad_set_id == set_pk,
                        overlaps(TadBoundaryInterval, StructuralVariant),
                    )
                )
                .alias("subquery_tad_boundaries_inner")
                .lateral("subquery_tad_boundaries_outer")
            )

    def extend_fields(self, _query_parts):
        if not self.kwargs.get("tad_set_uuid"):
            return ()
        else:
            return (self.subquery.c.distance_to_center,)

    def extend_selectable(self, query_parts):
        if self.kwargs.get("tad_set_uuid"):
            return query_parts.selectable.outerjoin(self.subquery, true())
        else:
            return query_parts.selectable


class EnsemblRegulatoryFeatureTypes(enum.Enum):
    CTCF_BINDING_SITE = "CTCF_binding_site"
    ENHANCER = "enhancer"
    OPEN_CHROMATIN_REGION = "open_chromatin_region"
    PROMOTER = "promoter"
    PROMOTER_FLANKING_REGION = "promoter_flanking_region"
    TF_BINDING_SITE = "TF_binding_site"


class ExtendQueryPartsDiseaseGeneJoin(_ExtendQueryPartsDiseaseGeneJoin):

    gene_id_model = StructuralVariantGeneAnnotation


class ExtendQueryPartsEnsemblRegulatoryJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with information for ENSEMBL regulatory region overlap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()

    def _build_subquery(self):
        fields = [
            func.coalesce(
                func.sum(case([(EnsemblRegulatoryFeature.sa.so_term_name == t.value, 1)], else_=0)),
                0,
            ).label("ensembl_%s_count" % t.value)
            for t in EnsemblRegulatoryFeatureTypes
        ]
        subquery = (
            select(fields)
            .select_from(EnsemblRegulatoryFeature.sa)
            .where(
                overlaps(
                    EnsemblRegulatoryFeature,
                    StructuralVariant,
                    padding=self.kwargs.get("regulatory_general_padding"),
                )
            )
            .alias("subquery_ensembl_inner")
        ).lateral("subquery_ensembl_outer")
        return subquery

    def extend_fields(self, _query_parts):
        for t in EnsemblRegulatoryFeatureTypes:
            yield getattr(self.subquery.c, "ensembl_%s_count" % t.value)

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())

    def extend_conditions(self, _query_parts):
        if self.kwargs["regulatory_ensembl"]:
            if "any_feature" in self.kwargs["regulatory_ensembl"]:
                keys = [t.value for t in EnsemblRegulatoryFeatureTypes]
            else:
                keys = self.kwargs["regulatory_ensembl"]
            yield or_(*[getattr(self.subquery.c, "ensembl_%s_count" % k) > 0 for k in keys])


class VistaValidationResults(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"


class ExtendQueryPartsVistaEnhancerJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with information for VISTA enhancer overlap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subquery = self._build_subquery()

    def _build_subquery(self):
        fields = [
            func.coalesce(
                func.sum(case([(VistaEnhancer.sa.validation_result == r.value, 1)], else_=0)), 0
            ).label("vista_%s_count" % r.value)
            for r in VistaValidationResults
        ]
        subquery = (
            select(fields)
            .select_from(VistaEnhancer.sa)
            .where(
                overlaps(
                    VistaEnhancer,
                    StructuralVariant,
                    padding=self.kwargs.get("regulatory_general_padding"),
                )
            )
            .alias("subquery_vista_inner")
        ).lateral("subquery_vista_outer")
        return subquery

    def extend_fields(self, _query_parts):
        for r in VistaValidationResults:
            yield getattr(self.subquery.c, "vista_%s_count" % r.value)

    def extend_selectable(self, query_parts):
        return query_parts.selectable.outerjoin(self.subquery, true())

    def extend_conditions(self, _query_parts):
        if self.kwargs["regulatory_vista"]:
            if "any_validation" in self.kwargs["regulatory_vista"]:
                keys = [r.value for r in VistaValidationResults]
            else:
                keys = self.kwargs["regulatory_vista"]
            yield or_(*[getattr(self.subquery.c, "vista_%s_count" % k) > 0 for k in keys])


class ExtendQueryPartsRegMapJoinAndFilter(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with information for regmap overlap."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subqueries = dict(self._build_subqueries())
        self.fields = dict(self._build_fields())
        self.conditions = dict(self._build_conditions())

    def extend(self, query_parts):
        for key, subquery, fields, conditions in zip(
            self.subqueries.keys(),
            self.subqueries.values(),
            self.fields.values(),
            self.conditions.values(),
        ):
            query_parts = QueryParts(
                fields=tuple(chain(query_parts.fields, fields)),
                selectable=query_parts.selectable.outerjoin(subquery, true()),
                conditions=tuple(chain(query_parts.conditions, [conditions])),
            )
        return query_parts

    def _build_subqueries(self):
        for coll in RegMapCollection.objects.all():
            # regulatory element queries
            for regmap in coll.regmap_set.all():
                fields = [
                    func.coalesce(
                        func.sum(case([(RegElement.sa.elem_type_id == ret.id, 1)], else_=0)), 0
                    ).label("regmap_%s_%s_element_%s_count" % (coll.slug, regmap.slug, ret.slug))
                    for ret in coll.regelementtype_set.all()
                ]
                subquery = (
                    select(fields)
                    .select_from(RegElement.sa)
                    .where(
                        and_(
                            overlaps(
                                RegElement,
                                StructuralVariant,
                                padding=self.kwargs.get("regulatory_general_padding"),
                            ),
                            RegElement.sa.reg_map_id == regmap.id,
                        )
                    )
                    .alias("subquery_regmap_%s_%s_element_inner" % (coll.slug, regmap.slug))
                ).lateral("subquery_regmap_%s_%s_element_outer" % (coll.slug, regmap.slug))
                yield "regmap_%s_%s_element" % (coll.slug, regmap.slug), subquery
                # interaction query
                interaction_fields = [
                    func.coalesce(func.count(), 0).label(
                        "regmap_%s_%s_interaction_count" % (coll.slug, regmap.slug)
                    )
                ]
                interaction_subquery = (
                    select(interaction_fields)
                    .select_from(RegInteraction.sa)
                    .where(
                        and_(
                            overlaps(
                                RegInteraction,
                                StructuralVariant,
                                padding=self.kwargs.get("regulatory_general_padding"),
                            ),
                            RegInteraction.sa.reg_map_id == regmap.id,
                        )
                    )
                    .alias("subquery_regmap_%s_%s_interaction_inner" % (coll.slug, regmap.slug))
                ).lateral("subquery_regmap_%s_%s_interaction_outer" % (coll.slug, regmap.slug))
                yield "regmap_%s_%s_interaction" % (coll.slug, regmap.slug), interaction_subquery

    def _build_fields(self):
        for coll in RegMapCollection.objects.all():
            for regmap in coll.regmap_set.all():
                element_fields = [
                    getattr(
                        self.subqueries["regmap_%s_%s_element" % (coll.slug, regmap.slug)].c,
                        "regmap_%s_%s_element_%s_count" % (coll.slug, regmap.slug, ret.slug),
                    )
                    for ret in coll.regelementtype_set.all()
                ]
                yield "regmap_%s_%s_element" % (coll.slug, regmap.slug), element_fields
                interaction_fields = [
                    getattr(
                        self.subqueries["regmap_%s_%s_interaction" % (coll.slug, regmap.slug)].c,
                        "regmap_%s_%s_interaction_count" % (coll.slug, regmap.slug),
                    )
                ]
                yield "regmap_%s_%s_interaction" % (coll.slug, regmap.slug), interaction_fields

    def _build_conditions(self):
        for coll in RegMapCollection.objects.all():
            for regmap in coll.regmap_set.all():
                selected_maps = self.kwargs.get("regmap_%s_map" % coll.slug, [])
                if "__any__" not in selected_maps and regmap.slug not in selected_maps:
                    yield "regmap_%s_%s" % (coll.slug, regmap.slug), True
                else:
                    kwargs_entry = self.kwargs.get("regmap_%s_element" % coll.slug, [])
                    if not kwargs_entry:
                        keys = []
                    elif "__any__" in kwargs_entry:
                        keys = [ret.slug for ret in coll.regelementtype_set.all()]
                    else:
                        keys = [
                            ret.slug
                            for ret in coll.regelementtype_set.all()
                            if ret.slug in kwargs_entry
                        ]
                    element_conditions = [
                        getattr(
                            self.subqueries["regmap_%s_%s_element" % (coll.slug, regmap.slug)].c,
                            "regmap_%s_%s_element_%s_count" % (coll.slug, regmap.slug, k),
                        )
                        > 0
                        for k in keys
                    ]
                    if self.kwargs.get("regmap_%s_interaction" % coll.slug, False):
                        interaction_conditions = [
                            getattr(
                                self.subqueries[
                                    "regmap_%s_%s_interaction" % (coll.slug, regmap.slug)
                                ].c,
                                "regmap_%s_%s_interaction_count" % (coll.slug, regmap.slug),
                            )
                            > 0
                        ]
                    else:
                        interaction_conditions = []
                    yield "regmap_%s_%s_element" % (coll.slug, regmap.slug), or_(
                        *element_conditions, *interaction_conditions
                    )
                    yield "regmap_%s_%s_interaction" % (coll.slug, regmap.slug), True


class ExtendQueryPartsHgncJoin(ExtendQueryPartsBase):
    """Extend ``QueryParts`` with information from HGNC."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def extend_fields(self, _query_parts):
        return [
            Hgnc.sa.symbol,
            Hgnc.sa.name.label("gene_name"),
            Hgnc.sa.gene_family.label("gene_family"),
        ]

    def extend_selectable(self, query_parts):
        if self.kwargs["database_select"] == "refseq":
            condition = StructuralVariantGeneAnnotation.sa.refseq_gene_id == Hgnc.sa.entrez_id
        else:
            condition = (
                StructuralVariantGeneAnnotation.sa.ensembl_gene_id == Hgnc.sa.ensembl_gene_id
            )
        return query_parts.selectable.outerjoin(Hgnc.sa, condition)


#: The basic ``ExtendQueryPartsBase`` sub classes to apply for all structural variant queries.
extender_classes_base = [
    ExtendQueryPartsCaseJoinAndFilter,
    ExtendQueryPartsGenotypeFilter,
    ExtendQueryPartsGenomicRegionFilter,
    ExtendQueryPartsSizeFilter,
    ExtendQueryPartsSvTypeFilter,
    ExtendQueryPartsPublicDatabaseFrequencyJoinAndFilter,
    ExtendQueryPartsFlagsJoinAndFilter,
    ExtendQueryPartsCommentsJoinAndFilter,
    ExtendQueryPartsVariantEffectFilter,
    ExtendQueryPartsGenesJoinAndFilter,
    ExtendQueryPartsTadBoundaryDistanceJoin,
    ExtendQueryPartsEnsemblRegulatoryJoinAndFilter,
    ExtendQueryPartsVistaEnhancerJoinAndFilter,
    ExtendQueryPartsRegMapJoinAndFilter,
    ExtendQueryPartsHgncJoin,
    ExtendQueryPartsDiseaseGeneJoin,
]


class SvQueryPartsBuilder(QueryPartsBuilder):
    core_query = structural_variant_query
    qp_extender_classes = extender_classes_base


class CasePrefetchQuery:
    builder = QueryPartsBuilder

    def __init__(self, case, engine, query_id=None):
        self.case_or_cases = case
        self.engine = engine
        self.query_id = query_id

    def run(self, kwargs):
        order_by = [
            column("chromosome"),
            column("start"),
            column("end"),
            column("sv_type"),
            column("sv_uuid"),
        ]
        stmt = (
            self.builder(self.case_or_cases, self.query_id).run(kwargs).to_stmt(order_by=order_by)
        )

        if settings.DEBUG:
            print(
                "\n"
                + sqlparse.format(
                    stmt.compile(self.engine).string, reindent=True, keyword_case="upper"
                ),
                file=sys.stderr,
            )
        return self.engine.execute(stmt)


class SingleCaseFilterQuery(CasePrefetchQuery):
    builder = SvQueryPartsBuilder


def best_matching_flags(sa_engine, case_id, sv_uuid, min_overlap=0.95):
    """Find best matching ``StructuralVariantFlags`` object for the given case and SV.

    Returns ``None`` if none could be found.
    """
    sv = StructuralVariant.objects.get(case_id=case_id, sv_uuid=sv_uuid)
    term_overlap = (
        func.least(StructuralVariantFlags.sa.end, sv.end)
        - func.greatest(StructuralVariantFlags.sa.start, sv.start)
        + 1
    )
    query = (
        select(
            [
                StructuralVariantFlags.sa.sodar_uuid.label("flags_uuid"),
                func.least(
                    cast(term_overlap, Float) / func.greatest((sv.end - sv.start + 1), 1),
                    cast(term_overlap, Float)
                    / func.greatest(
                        (StructuralVariantFlags.sa.end - StructuralVariantFlags.sa.start + 1), 1
                    ),
                ).label("reciprocal_overlap"),
            ]
        )
        .select_from(StructuralVariantFlags.sa)
        .where(
            and_(
                StructuralVariantFlags.sa.case_id == case_id,
                StructuralVariantFlags.sa.release == sv.release,
                StructuralVariantFlags.sa.chromosome == sv.chromosome,
                StructuralVariantFlags.sa.bin.in_(
                    select([column("bin")]).select_from(func.overlapping_bins(sv.start - 1, sv.end))
                ),
                StructuralVariantFlags.sa.end >= sv.start,
                StructuralVariantFlags.sa.start <= sv.end,
                StructuralVariantFlags.sa.sv_type == sv.sv_type,
                cast(term_overlap, Float) / func.greatest((sv.end - sv.start + 1), 1) > min_overlap,
                cast(term_overlap, Float)
                / func.greatest(
                    (StructuralVariantFlags.sa.end - StructuralVariantFlags.sa.start + 1), 1
                )
                > min_overlap,
            )
        )
    )
    return sa_engine.execute(query.order_by(desc(text("reciprocal_overlap"))))
