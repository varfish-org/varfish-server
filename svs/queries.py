"""SQL Alchemy--based building of queries."""
from sqlalchemy import column
from sqlalchemy.sql import select, func, and_, or_, not_, true, cast, any_, case
from sqlalchemy.sql.functions import coalesce
from sqlalchemy.types import Integer, Float

from .models import (
    StructuralVariant,
    StructuralVariantGeneAnnotation,
    StructuralVariantComment,
    StructuralVariantFlags,
)
from genomicfeatures.models import (
    EnsemblRegulatoryFeature,
    GeneInterval,
    TadSet,
    TadInterval,
    TadBoundaryInterval,
    VistaEnhancer,
)
from geneinfo.models import Hgnc
from svdbs.models import ThousandGenomesSv, DbVarSv, ExacCnv, DgvSvs, DgvGoldStandardSvs, GnomAdSv
from variants.models import Case
from variants.models_support import (
    SingleCaseFilterQueryBase,
    GenotypeTermWhereMixinBase,
    TranscriptCodingTermWhereMixin,
    GeneListsTermWhereMixin,
    VariantEffectTermWhereMixin,
)


class SingleCasePrefetchFilterQueryBase(SingleCaseFilterQueryBase):
    """Base class for the actual query."""

    model_class = StructuralVariant
    annotated_model_class = StructuralVariantGeneAnnotation
    base_table = StructuralVariant.sa.table

    def _from(self, kwargs):
        inner = super()._from(kwargs)
        return inner.outerjoin(
            StructuralVariantGeneAnnotation.sa.table,
            StructuralVariantGeneAnnotation.sa.sv_uuid == StructuralVariant.sa.sv_uuid,
        )

    def is_prefetched(self):
        """Return if the query is prefetched or not."""
        return "LoadPrefetched" in type(self).__name__


class GenotypeTermWhereMixin(GenotypeTermWhereMixinBase):
    """Implementation of ``GenotypeTermWhereMixinBase`` for ``StructuralVariant`` model."""

    def _build_genotype_quality_term(self, name, kwargs):
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
                or_(kwargs.get("%s_gq_min" % name) is None, genotype[name]["gq"].is_(None)),
                genotype[name]["gq"].astext.cast(Integer) >= (kwargs["%s_gq_min" % name] or 0),
            ),
            # Split read: min coverage, min/max variant split reads
            or_(
                or_(kwargs.get("%s_src_min" % name) is None, genotype[name]["src"].is_(None)),
                genotype[name]["src"].astext.cast(Integer) >= (kwargs["%s_src_min" % name] or 0),
            ),
            or_(
                # Min variant support terms only apply for non-variant terms.
                not_(is_variant),
                or_(
                    or_(kwargs.get("%s_srv_min" % name) is None, genotype[name]["srv"].is_(None)),
                    genotype[name]["srv"].astext.cast(Integer)
                    >= (kwargs["%s_srv_min" % name] or 0),
                ),
            ),
            or_(
                or_(kwargs.get("%s_srv_max" % name) is None, genotype[name]["srv"].is_(None)),
                genotype[name]["srv"].astext.cast(Integer) <= (kwargs["%s_srv_max" % name] or 0),
            ),
            # Paired read: min coverage, min/max variant paired reads
            or_(
                or_(kwargs.get("%s_pec_min" % name) is None, genotype[name]["pec"].is_(None)),
                genotype[name]["pec"].astext.cast(Integer) >= (kwargs["%s_pec_min" % name] or 0),
            ),
            or_(
                # Min variant support terms only apply for non-variant terms.
                not_(is_variant),
                or_(
                    or_(kwargs.get("%s_pev_min" % name) is None, genotype[name]["pev"].is_(None)),
                    genotype[name]["pev"].astext.cast(Integer)
                    >= (kwargs["%s_pev_min" % name] or 0),
                ),
            ),
            or_(
                or_(kwargs.get("%s_pev_max" % name) is None, genotype[name]["pev"].is_(None)),
                genotype[name]["pev"].astext.cast(Integer) <= (kwargs["%s_pev_max" % name] or 0),
            ),
            # Overall split OR paired read: min coverage, min/max variant paired reads
            or_(
                or_(
                    kwargs.get("%s_cov_min" % name) is None,
                    and_(genotype[name]["src"].is_(None), genotype[name]["pec"].is_(None)),
                ),
                coalesce(genotype[name]["src"].astext.cast(Integer), 0)
                + coalesce(genotype[name]["pec"].astext.cast(Integer), 0)
                >= (kwargs["%s_cov_min" % name] or 0),
            ),
            or_(
                or_(
                    # Min variant support terms only apply for non-variant terms.
                    not_(is_variant),
                    or_(
                        kwargs.get("%s_var_min" % name) is None,
                        and_(genotype[name]["srv"].is_(None), genotype[name]["pev"].is_(None)),
                    ),
                    coalesce(genotype[name]["srv"].astext.cast(Integer), 0)
                    + coalesce(genotype[name]["pev"].astext.cast(Integer), 0)
                    >= (kwargs["%s_var_min" % name] or 0),
                )
            ),
            or_(
                or_(
                    kwargs.get("%s_var_max" % name) is None,
                    and_(genotype[name]["srv"].is_(None), genotype[name]["pev"].is_(None)),
                ),
                coalesce(genotype[name]["srv"].astext.cast(Integer), 0)
                + coalesce(genotype[name]["pev"].astext.cast(Integer), 0)
                <= (kwargs["%s_var_max" % name] or 0),
            ),
        )
        return or_(genotype[name].is_(None), rhs)


class RegionOverlapWhereMixin:
    """Mixin that adds region overlap to WHERE part of query"""

    def _core_where(self, kwargs, gt_patterns=None):
        terms = []
        for chrom, start, end in kwargs["region_whitelist"] or []:
            # TODO: handle b37 vs b38
            if chrom.startswith("chr"):
                chrom = chrom[3:]
            terms.append(
                and_(
                    StructuralVariant.sa.chromosome == chrom,
                    StructuralVariant.sa.end >= start,
                    StructuralVariant.sa.start <= end,
                )
            )
        return and_(super()._core_where(kwargs, gt_patterns), or_(*terms) if terms else True)


class SizeFilterWhereMixin:
    """Mixin that adds size filter to WHERE part of query"""

    def _core_where(self, kwargs, gt_patterns=None):
        terms = []
        if kwargs.get("sv_size_min") is not None:
            terms.append(
                StructuralVariant.sa.end - StructuralVariant.sa.start + 1 >= kwargs["sv_size_min"]
            )
        if kwargs.get("sv_size_max") is not None:
            terms.append(
                StructuralVariant.sa.end - StructuralVariant.sa.start + 1 <= kwargs["sv_size_max"]
            )
        return and_(super()._core_where(kwargs, gt_patterns), and_(*terms) if terms else True)


class StructuralVariantTypeTermWhereMixin:
    """Mixin that adds the queries for the SV type to the query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_vartype_term(kwargs))

    def _build_vartype_term(self, kwargs):
        return or_(
            or_(
                StructuralVariant.sa.sv_type.is_(None),
                StructuralVariant.sa.sv_type.in_(kwargs["sv_type"]),
            ),
            or_(
                StructuralVariant.sa.sv_sub_type.is_(None),
                StructuralVariant.sa.sv_sub_type.in_(kwargs["sv_sub_type"]),
            ),
        )


class PublicDatabaseFrequencyTermFilterMixin:
    """Mixin that queries for the public data base frequencies and filters by them"""

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)

        self.public_db_fields = {}
        self.public_db_queries = []

        for token, model, observed_events in (
            (
                "dgv",
                DgvSvs,
                func.sum(DgvSvs.sa.observed_gains) + func.sum(DgvSvs.sa.observed_losses),
            ),
            ("dgv_gs", DgvGoldStandardSvs, func.sum(DgvGoldStandardSvs.sa.num_carriers)),
            ("g1k", ThousandGenomesSv, func.sum(ThousandGenomesSv.sa.num_var_alleles)),
            ("exac", ExacCnv, func.count()),
            ("dbvar", DbVarSv, func.sum(DbVarSv.sa.num_carriers)),
            ("gnomad", GnomAdSv, func.sum(GnomAdSv.sa.n_het + GnomAdSv.sa.n_homalt)),
        ):
            if hasattr(model, "start_outer"):
                model_start = model.sa.start_outer
                model_end = model.sa.end_inner
            else:
                model_start = model.sa.start
                model_end = model.sa.end
            subquery = (
                select([observed_events.label("observed_events")])
                .select_from(model.sa)
                .where(
                    and_(
                        # TODO: type mapping -- interesting/necessary?
                        # StructuralVariant.sa.sv_type == model.sa.sv_type,
                        StructuralVariant.sa.release == model.sa.release,
                        StructuralVariant.sa.chromosome == model.sa.chromosome,
                        model.sa.bin.in_(
                            select([column("bin")]).select_from(
                                func.overlapping_bins(
                                    StructuralVariant.sa.start - 1, StructuralVariant.sa.end
                                )
                            )
                        ),
                        StructuralVariant.sa.end >= model_start,
                        StructuralVariant.sa.start <= model_end,
                        cast(
                            func.least(StructuralVariant.sa.end, model_end)
                            - func.greatest(StructuralVariant.sa.start, model_start)
                            + 1,
                            Float,
                        )
                        / func.greatest((model_end - model_start + 1), 1)
                        > float(kwargs.get("%s_min_overlap" % token, "0.75")),
                        cast(
                            func.least(StructuralVariant.sa.end, model_end)
                            - func.greatest(StructuralVariant.sa.start, model_start)
                            + 1,
                            Float,
                        )
                        / func.greatest(
                            (StructuralVariant.sa.end - StructuralVariant.sa.start + 1), 1
                        )
                        > float(kwargs.get("%s_min_overlap" % token, "0.75")),
                    )
                )
            ).lateral("subquery_%s" % token)
            self.public_db_queries.append(subquery)
            self.public_db_fields["%s_overlap_count" % token] = func.coalesce(
                subquery.c.observed_events, 0
            ).label("%s_overlap_count" % token)

        return result + list(self.public_db_fields.values())

    def _from(self, kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        result = super()._from(kwargs)
        for query in self.public_db_queries:
            result = result.outerjoin(query, true())
        return result

    def _core_where(self, kwargs, gt_patterns=None):
        result = []
        for token in ("dgv", "dgv_gs", "g1k", "exac", "dbvar", "gnomad"):
            if (
                kwargs.get("%s_enabled" % token, False)
                and ("%s_overlap_count" % token) in self.public_db_fields
                and kwargs.get("%s_max_carriers" % token) is not None
            ):
                result.append(
                    self.public_db_fields["%s_overlap_count" % token]
                    <= kwargs["%s_max_carriers" % token]
                )
        return and_(super()._core_where(kwargs, gt_patterns), and_(*result))


def overlap_term(lhs, rhs, min_overlap):
    """Return SQL Alchemy term for ``lhs`` and ``rhs`` to have a reciprocal overlap of at least ``min_overlap``."""
    term_overlap = (
        func.least(lhs.sa.end, rhs.sa.end) - func.greatest(lhs.sa.start, rhs.sa.start) + 1
    )
    return and_(
        lhs.sa.release == rhs.sa.release,
        lhs.sa.chromosome == rhs.sa.chromosome,
        rhs.sa.bin.in_(
            select([column("bin")]).select_from(func.overlapping_bins(lhs.sa.start - 1, lhs.sa.end))
        ),
        lhs.sa.end >= rhs.sa.start,
        lhs.sa.start <= rhs.sa.end,
        lhs.sa.sv_type == rhs.sa.sv_type,
        cast(term_overlap, Float) / func.greatest((rhs.sa.end - rhs.sa.start + 1), 1) > min_overlap,
        cast(term_overlap, Float) / func.greatest((lhs.sa.end - lhs.sa.start + 1), 1) > min_overlap,
    )


class FilterQueryFlagsCommentsMixin:
    """Add information about flags and comments for filter queries."""

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)

        self.user_annotation_fields = {}
        self.user_annotation_queries = []

        # StructuralVariantFlags
        subquery = (
            select(
                [
                    func.count(StructuralVariantFlags.sa.id).label("flag_count"),
                    func.bool_or(StructuralVariantFlags.sa.flag_bookmarked).label(
                        "flag_bookmarked"
                    ),
                    func.bool_or(StructuralVariantFlags.sa.flag_candidate).label("flag_candidate"),
                    func.bool_or(StructuralVariantFlags.sa.flag_final_causative).label(
                        "flag_final_causative"
                    ),
                    func.bool_or(StructuralVariantFlags.sa.flag_for_validation).label(
                        "flag_for_validation"
                    ),
                    func.max(StructuralVariantFlags.sa.flag_visual).label("flag_visual"),
                    func.max(StructuralVariantFlags.sa.flag_validation).label("flag_validation"),
                    func.max(StructuralVariantFlags.sa.flag_phenotype_match).label(
                        "flag_phenotype_match"
                    ),
                    func.max(StructuralVariantFlags.sa.flag_summary).label("flag_summary"),
                ]
            )
            .select_from(StructuralVariantFlags.sa)
            .where(overlap_term(StructuralVariant, StructuralVariantFlags, min_overlap=0.95))
        ).lateral("subquery_user_comments")
        self.user_annotation_queries.append(subquery)
        for token, default in (
            ("count", 0),
            ("bookmarked", False),
            ("candidate", False),
            ("final_causative", False),
            ("for_validation", False),
            ("visual", ""),
            ("validation", ""),
            ("phenotype_match", ""),
            ("summary", ""),
        ):
            field_name = "flag_%s" % token
            self.user_annotation_fields[field_name] = func.coalesce(
                getattr(subquery.c, field_name), default
            ).label(field_name)

        # StructuralVariantComment
        subquery = (
            select([func.count(StructuralVariantComment.sa.id).label("comment_count")])
            .select_from(StructuralVariantComment.sa)
            .where(overlap_term(StructuralVariant, StructuralVariantComment, min_overlap=0.95))
        ).lateral("subquery_user_flags")
        self.user_annotation_queries.append(subquery)
        self.user_annotation_fields["comment_count"] = func.coalesce(
            subquery.c.comment_count, 0
        ).label("comment_count")

        return result + list(self.user_annotation_fields.values())

    def _from(self, kwargs):
        result = super()._from(kwargs)
        for query in self.user_annotation_queries:
            result = result.outerjoin(query, true())
        return result


class InHouseDatabaseFrequencyTermWhereMixin:
    """Mixin that adds frequency part of the in-house databases to the query"""

    def _core_where(self, kwargs, gt_patterns=None):
        result = []

        for token in ("affected", "unaffected", "background"):
            for minmax in ("min", "max"):
                if (
                    kwargs["collective_enabled"]
                    and kwargs["cohort_%s_carriers_%s" % (token, minmax)] is not None
                ):
                    field = StructuralVariant.sa.info["%sCarriers" % token].astext.cast(Integer)
                    thresh = kwargs["cohort_%s_carriers_%s" % (token, minmax)]
                    term = field >= thresh if minmax == "min" else field <= thresh
                    result.append(
                        or_(StructuralVariant.sa.info["%sCarriers" % token].is_(None), term)
                    )

        return and_(super()._core_where(kwargs, gt_patterns), and_(*result))


class SvVariantEffectTermWhereMixin(VariantEffectTermWhereMixin):
    """SV-specific variant effect WHERE creation that can allow empty transcripts."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_effects_term(kwargs))

    def _build_effects_term(self, kwargs):
        if kwargs["require_transcript_overlap"]:
            return super()._build_effects_term(kwargs)
        else:
            model_class = self.annotated_model_class or self.model_class
            if kwargs["database_select"] == "refseq":
                effect = model_class.sa.refseq_effect
            else:  # kwargs["database_select"] == "ensembl"
                effect = model_class.sa.ensembl_effect
            return or_(super()._build_effects_term(kwargs), effect.is_(None))


class GenesInIntervalsTermWhereMixin:
    """Mixin that queries for genes sharing overlapping interval sets (e.g., TADs)"""

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)
        if not kwargs.get("tad_set_uuid"):
            return result

        set_pk = TadSet.objects.get(sodar_uuid=kwargs["tad_set_uuid"]).pk

        if kwargs["database_select"] == "refseq":
            term_join_gene_id = GeneInterval.sa.gene_id == Hgnc.sa.entrez_id
        else:  # kwargs["database_select"] == "ensembl"
            term_join_gene_id = GeneInterval.sa.gene_id == Hgnc.sa.ensembl_gene_id

        # IntervalSet, Interval
        self.genes_intervals_db_subquery = (
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
                        TadInterval.sa.release == StructuralVariant.sa.release,
                        TadInterval.sa.chromosome == StructuralVariant.sa.chromosome,
                        TadInterval.sa.bin.in_(
                            select([column("bin")]).select_from(
                                func.overlapping_bins(
                                    StructuralVariant.sa.start - 1, StructuralVariant.sa.end
                                )
                            )
                        ),
                        TadInterval.sa.end >= StructuralVariant.sa.start,
                        TadInterval.sa.start <= StructuralVariant.sa.end,
                    ),
                )
            )
            .where(
                and_(
                    GeneInterval.sa.database == kwargs["database_select"],
                    TadInterval.sa.release == GeneInterval.sa.release,
                    TadInterval.sa.chromosome == GeneInterval.sa.chromosome,
                    GeneInterval.sa.bin.in_(
                        select([column("bin")]).select_from(
                            func.overlapping_bins(TadInterval.sa.start - 1, TadInterval.sa.end)
                        )
                    ),
                    TadInterval.sa.end >= GeneInterval.sa.start,
                    TadInterval.sa.start <= GeneInterval.sa.end,
                )
            )
            .alias("subquery_genes_intervals_inner")
        ).lateral("subquery_genes_intervals_outer")

        return result + [
            self.genes_intervals_db_subquery.c.itv_shared_gene_ids,
            self.genes_intervals_db_subquery.c.itv_shared_gene_symbols,
        ]

    def _from(self, kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        result = super()._from(kwargs)
        if not kwargs.get("tad_set_uuid"):
            return result
        else:
            return result.outerjoin(self.genes_intervals_db_subquery, true())


class IntervalCenterDistanceTermWhereMixin:
    """Mixin that allows for querying distance to intervals (e.g., TAD boundaries)"""

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)
        if not kwargs.get("tad_set_uuid"):
            return result

        set_pk = TadSet.objects.get(sodar_uuid=kwargs["tad_set_uuid"]).pk

        interval_center = (
            TadBoundaryInterval.sa.start
            + (TadBoundaryInterval.sa.end - TadBoundaryInterval.sa.start + 1) / 2
        )
        term_overlaps = and_(
            interval_center >= StructuralVariant.sa.start,
            interval_center <= StructuralVariant.sa.end,
        )
        self.interval_distance_db_subquery = (
            select(
                [
                    func.coalesce(
                        func.min(
                            case(
                                [(term_overlaps, 0)],
                                else_=func.least(
                                    func.abs(interval_center - StructuralVariant.sa.start),
                                    func.abs(interval_center - StructuralVariant.sa.end),
                                ),
                            )
                        ),
                        -1,
                    ).label("distance_to_center")
                ]
            )
            .select_from(TadBoundaryInterval.sa)
            .where(
                and_(
                    TadBoundaryInterval.sa.tad_set_id == set_pk,
                    TadBoundaryInterval.sa.release == StructuralVariant.sa.release,
                    TadBoundaryInterval.sa.chromosome == StructuralVariant.sa.chromosome,
                    TadBoundaryInterval.sa.bin.in_(
                        select([column("bin")]).select_from(
                            func.overlapping_bins(
                                StructuralVariant.sa.start - 1, StructuralVariant.sa.end
                            )
                        )
                    ),
                    TadBoundaryInterval.sa.end >= StructuralVariant.sa.start,
                    TadBoundaryInterval.sa.start <= StructuralVariant.sa.end,
                )
            )
            .alias("subquery_intervals_distance_inner")
        ).lateral("subquery_intervals_distance_outer")

        return result + [self.interval_distance_db_subquery.c.distance_to_center]

    def _from(self, kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        result = super()._from(kwargs)
        if not kwargs.get("tad_set_uuid"):
            return result
        else:
            return result.outerjoin(self.interval_distance_db_subquery, true())


class EnsemblRegulatoryOverlapsTermWhereMixin:
    """Query for overlap with ENSEMBL regulatory regions"""

    FEATURE_TYPES = (
        "CTCF_binding_site",
        "enhancer",
        "open_chromatin_region",
        "promoter",
        "promoter_flanking_region",
        "TF_binding_site",
    )

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)

        self.ensembl_regulatory_db_subquery = (
            select(
                [
                    func.coalesce(
                        func.sum(
                            case(
                                [(EnsemblRegulatoryFeature.sa.so_term_name == feature_type, 1)],
                                else_=0,
                            )
                        ),
                        0,
                    ).label("ensembl_%s_count" % feature_type)
                    for feature_type in self.FEATURE_TYPES
                ]
            )
            .select_from(EnsemblRegulatoryFeature.sa)
            .where(
                and_(
                    EnsemblRegulatoryFeature.sa.release == StructuralVariant.sa.release,
                    EnsemblRegulatoryFeature.sa.chromosome == StructuralVariant.sa.chromosome,
                    EnsemblRegulatoryFeature.sa.bin.in_(
                        select([column("bin")]).select_from(
                            func.overlapping_bins(
                                StructuralVariant.sa.start - 1, StructuralVariant.sa.end
                            )
                        )
                    ),
                    EnsemblRegulatoryFeature.sa.end >= StructuralVariant.sa.start,
                    EnsemblRegulatoryFeature.sa.start <= StructuralVariant.sa.end,
                )
            )
            .alias("subquery_ensembl_inner")
        ).lateral("subquery_ensembl_outer")

        return result + [
            getattr(self.ensembl_regulatory_db_subquery.c, "ensembl_%s_count" % feature_type)
            for feature_type in self.FEATURE_TYPES
        ]

    def _from(self, kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        return super()._from(kwargs).outerjoin(self.ensembl_regulatory_db_subquery, true())

    def _core_where(self, kwargs, gt_patterns=None):
        xs = self._build_feature_type_form_ensembl(kwargs)
        return and_(super()._core_where(kwargs, gt_patterns), xs)

    def _build_feature_type_form_ensembl(self, kwargs):
        if not kwargs["regulatory_ensembl"]:
            return True
        else:
            if "any_feature" in kwargs["regulatory_ensembl"]:
                keys = self.FEATURE_TYPES
            else:
                keys = kwargs["regulatory_ensembl"]
            return or_(
                *[
                    getattr(
                        self.ensembl_regulatory_db_subquery.c, "ensembl_%s_count" % feature_type
                    )
                    > 0
                    for feature_type in keys
                ]
            )


class VistaEnhancerOverlapsTermWhereMixin:
    """Query for overlap with VISTA enhancers"""

    VALIDATION_RESULTS = ("positive", "negative")

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)

        self.vista_enhancer_db_subquery = (
            select(
                [
                    func.coalesce(
                        func.sum(
                            case(
                                [(VistaEnhancer.sa.validation_result == validation_result, 1)],
                                else_=0,
                            )
                        ),
                        0,
                    ).label("vista_%s_count" % validation_result)
                    for validation_result in self.VALIDATION_RESULTS
                ]
            )
            .select_from(VistaEnhancer.sa)
            .where(
                and_(
                    VistaEnhancer.sa.release == StructuralVariant.sa.release,
                    VistaEnhancer.sa.chromosome == StructuralVariant.sa.chromosome,
                    VistaEnhancer.sa.bin.in_(
                        select([column("bin")]).select_from(
                            func.overlapping_bins(
                                StructuralVariant.sa.start - 1, StructuralVariant.sa.end
                            )
                        )
                    ),
                    VistaEnhancer.sa.end >= StructuralVariant.sa.start,
                    VistaEnhancer.sa.start <= StructuralVariant.sa.end,
                )
            )
            .alias("subquery_vista_inner")
        ).lateral("subquery_vista_outer")

        return result + [
            getattr(self.vista_enhancer_db_subquery.c, "vista_%s_count" % validation_result)
            for validation_result in self.VALIDATION_RESULTS
        ]

    def _from(self, kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        return super()._from(kwargs).outerjoin(self.vista_enhancer_db_subquery, true())

    def _core_where(self, kwargs, gt_patterns=None):
        xs = self._build_feature_type_form_vista(kwargs)
        return and_(super()._core_where(kwargs, gt_patterns), xs)

    def _build_feature_type_form_vista(self, kwargs):
        if not kwargs["regulatory_vista"]:
            return True
        else:
            if "any_validation" in kwargs["regulatory_vista"]:
                keys = self.VALIDATION_RESULTS
            else:
                keys = kwargs["regulatory_vista"]
            return or_(
                *[
                    getattr(self.vista_enhancer_db_subquery.c, "vista_%s_count" % validation_result)
                    > 0
                    for validation_result in keys
                ]
            )


class BaseTableQueriesMixin(
    SizeFilterWhereMixin,
    RegionOverlapWhereMixin,
    GenotypeTermWhereMixin,
    PublicDatabaseFrequencyTermFilterMixin,
    InHouseDatabaseFrequencyTermWhereMixin,
    StructuralVariantTypeTermWhereMixin,
    SvVariantEffectTermWhereMixin,
    TranscriptCodingTermWhereMixin,
    IntervalCenterDistanceTermWhereMixin,
    GenesInIntervalsTermWhereMixin,
    EnsemblRegulatoryOverlapsTermWhereMixin,
    VistaEnhancerOverlapsTermWhereMixin,
    GeneListsTermWhereMixin,
):
    """Helper mixin that adds all criteria that can be answered by the base star table."""


# Further helper mixins


class OrderByChromosomalPositionMixin:
    """Order by chromosomal position and reference/alternative allele string."""

    def _add_trailing(self, stmt, _kwargs):
        return stmt.order_by(stmt.c.chromosome, stmt.c.start, stmt.c.end)


# Query class mixins providing fields, possibly joining the extended tables.


class JoinHgncMixin:
    """Enrich with HGNC information for the genes."""

    def _from(self, kwargs):
        if kwargs["database_select"] == "refseq":
            return (
                super()
                ._from(kwargs)
                .outerjoin(
                    Hgnc.sa, StructuralVariantGeneAnnotation.sa.refseq_gene_id == Hgnc.sa.entrez_id
                )
            )
        else:  # kwargs["database_select"] == "ensembl"
            return (
                super()
                ._from(kwargs)
                .outerjoin(
                    Hgnc.sa,
                    StructuralVariantGeneAnnotation.sa.ensembl_gene_id == Hgnc.sa.ensembl_gene_id,
                )
            )


class FilterQueryRenderFieldsMixin(JoinHgncMixin):
    """Mixin for selecting the standard fields for rendering the SV query results in the web app."""

    def _from(self, kwargs):
        return super()._from(kwargs).join(Case.sa.table, Case.sa.id == StructuralVariant.sa.case_id)

    def _get_fields(self, kwargs, which, inner=None):
        if which == "outer":
            if inner is not None:
                return [*inner.c]
            else:
                return "*"
        else:
            result = [
                StructuralVariant.sa.id,
                StructuralVariant.sa.release,
                StructuralVariant.sa.chromosome,
                StructuralVariant.sa.bin,
                StructuralVariant.sa.start,
                StructuralVariant.sa.end,
                (StructuralVariant.sa.end - StructuralVariant.sa.start + 1).label("sv_length"),
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
                StructuralVariantGeneAnnotation.sa.refseq_transcript_id,
                StructuralVariantGeneAnnotation.sa.refseq_transcript_coding,
                StructuralVariantGeneAnnotation.sa.refseq_effect,
                StructuralVariantGeneAnnotation.sa.ensembl_gene_id,
                StructuralVariantGeneAnnotation.sa.ensembl_transcript_id,
                StructuralVariantGeneAnnotation.sa.ensembl_transcript_coding,
                StructuralVariantGeneAnnotation.sa.ensembl_effect,
                Hgnc.sa.symbol,
                Hgnc.sa.name.label("gene_name"),
                Hgnc.sa.gene_family.label("gene_family"),
                Case.sa.sodar_uuid.label("case_uuid"),
            ] + super()._get_fields(kwargs, which, inner)
            if kwargs["database_select"] == "refseq":
                result += [
                    StructuralVariantGeneAnnotation.sa.refseq_transcript_coding.label(
                        "transcript_coding"
                    ),
                    StructuralVariantGeneAnnotation.sa.refseq_effect.label("effect"),
                    StructuralVariantGeneAnnotation.sa.refseq_gene_id.label("gene_id"),
                    StructuralVariantGeneAnnotation.sa.refseq_transcript_id.label("transcript_id"),
                ]
            else:  # if kwargs["database_select"] == "ensembl":
                result += [
                    StructuralVariantGeneAnnotation.sa.ensembl_transcript_coding.label(
                        "transcript_coding"
                    ),
                    StructuralVariantGeneAnnotation.sa.ensembl_effect.label("effect"),
                    StructuralVariantGeneAnnotation.sa.ensembl_gene_id.label("gene_id"),
                    StructuralVariantGeneAnnotation.sa.ensembl_transcript_id.label("transcript_id"),
                ]
            return result


class SingleCaseFilterQuery(
    OrderByChromosomalPositionMixin,
    FilterQueryRenderFieldsMixin,
    FilterQueryFlagsCommentsMixin,
    BaseTableQueriesMixin,
    SingleCasePrefetchFilterQueryBase,
):
    """Run filter query for the interactive SV filtration form."""

    # TODO: this is the place to add the annotation flagging in the future


def best_matching_flags(sa_engine, case_id, sv_uuid, min_overlap=0.95):
    """Find best matching ``StructuralVariantFlags`` object for the given case and SV, ``None`` if none could be found.
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
                    select([column("bin")]).select_from(
                        func.overlapping_bins(sv.sa.start - 1, sv.sa.end)
                    )
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
    return sa_engine.execute(query.order_by(query.c.reciprocal_overlap.desc()))
