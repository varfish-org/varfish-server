from contextlib import contextmanager
import json
import psycopg2.extras
from sqlalchemy.sql import select, func, and_, not_, or_, cast, union, literal_column
from sqlalchemy.types import ARRAY, VARCHAR, Integer, Float

from variants.models import Case, SmallVariant
from geneinfo.models import Hgnc
from dbsnp.models import Dbsnp
from variants.forms import FILTER_FORM_TRANSLATE_EFFECTS, FILTER_FORM_TRANSLATE_INHERITANCE


@contextmanager
def disable_json_psycopg2():
    """Context manager for temporarily switching off automated JSON decoding in psycopg2.

    SQL Alchemy does not like this.
    """
    psycopg2.extras.register_default_json(loads=lambda x: x)
    psycopg2.extras.register_default_jsonb(loads=lambda x: x)
    yield
    psycopg2.extras.register_default_json(loads=json.loads)
    psycopg2.extras.register_default_jsonb(loads=json.loads)


class FilterQueryBase:
    """Base class for running different variants of filter queries.

    For each particular query, a sub class is created that implements and/or overrides some fields.

    The basic form of each query is:

    ::

        SELECT <fields>
        FROM variants_smallvariant
        [optional JOINs]
        WHERE <conditions>
        [trailing such as ORDER BY or LIMIT]
    """

    def __init__(self, case, connection):
        #: The case that the query is for.
        self.case = case
        #: The Aldjemy connection to use
        self.connection = connection

    def run(self, kwargs):
        """Perform the query with the given ``kwargs``."""
        if kwargs.get("compound_recessive_enabled", False):
            stmt = self._build_comp_het_stmt(kwargs)
        else:
            stmt = self._build_simple_stmt(kwargs)
        stmt = self._add_trailing(stmt, kwargs)
        if False:
            import sqlparse

            sql = stmt.compile(self.connection.engine).string
            print(sqlparse.format(sql, reindent=True, keyword_case="upper"))
        with disable_json_psycopg2():
            return self.connection.execute(stmt)

    def _get_trio_names(self):
        """Return (index, father, mother) names from trio"""
        index_lines = [rec for rec in self.case.pedigree if rec["patient"] == self.case.index]
        if len(index_lines) != 1:
            raise RuntimeError("Could not find index line from pedigree")
        return index_lines[0]["patient"], index_lines[0]["father"], index_lines[0]["mother"]

    def _build_comp_het_stmt(self, kwargs):
        """Build the comp.-het. statement"""
        index, father, mother = self._get_trio_names()
        # Build inner query, variant inherited from father
        gt_patterns = {index: "het", father: "het", mother: "ref"}
        inner_father_stmt = (
            select(
                self._get_fields(kwargs, "inner")
                + [
                    literal_column("1", Integer).label("father_marker"),
                    literal_column("0", Integer).label("mother_marker"),
                ]
            )
            .select_from(self._from(kwargs))
            .where(self._where(kwargs, gt_patterns))
        )
        inner_father_stmt = self._add_trailing(inner_father_stmt, kwargs)
        # Build inner query, variant inherited from mother
        gt_patterns = {index: "het", father: "ref", mother: "het"}
        inner_mother_stmt = (
            select(
                self._get_fields(kwargs, "inner")
                + [
                    literal_column("0", Integer).label("father_marker"),
                    literal_column("1", Integer).label("mother_marker"),
                ]
            )
            .select_from(self._from(kwargs))
            .where(self._where(kwargs, gt_patterns))
        )
        inner_mother_stmt = self._add_trailing(inner_mother_stmt, kwargs)
        # Build the union statement
        union_stmt = union(inner_father_stmt, inner_mother_stmt).alias("the_union")
        # Build the outer statement
        middle_stmt = (
            select(
                [
                    "*",
                    func.sum(union_stmt.c.father_marker)
                    .over(partition_by=union_stmt.c.gene_id)
                    .label("father_count"),
                    func.sum(union_stmt.c.mother_marker)
                    .over(partition_by=union_stmt.c.gene_id)
                    .label("mother_count"),
                ]
            )
            .select_from(union_stmt)
            .alias("the_middle")
        )
        # Build the outer statement
        return (
            select(self._get_fields(kwargs, "outer"))
            .select_from(middle_stmt)
            .where(and_(middle_stmt.c.father_count > 0, middle_stmt.c.mother_count > 0))
        )

    def _build_simple_stmt(self, kwargs):
        """Build the simple, non-comp.-het. statement"""
        stmt = (
            select(self._get_fields(kwargs, "single"))
            .select_from(self._from(kwargs))
            .where(self._where(kwargs))
        )
        stmt = self._add_trailing(stmt, kwargs)
        return stmt

    def _get_fields(self, _kwargs, _which):
        """Return fields to ``select()`` with SQLAlchemy.

        ``_which`` is "outer" or "inner".
        """
        raise NotImplementedError("Override me!")

    def _from(self, _kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        raise NotImplementedError("Override me!")

    def _where(self, _kwargs, _gt_patterns=None):
        """Add WHERE clause to the ``_stmt``.

        If ``_gt_pattern`` is given then the selected individual's genotype will be forced
        as given in this parameter.  Examples for the values are:

        - ``{}`` -- empty
        - ``{"child": "het", "father": "het", "mother": "hom"}``
        - ``{"child": "het", "father": "hom", "mother": "het"}``
        """
        raise NotImplementedError("Override me!")

    def _add_trailing(self, stmt, _kwargs):
        """Optionally add trailing parts of statement.

        The default implementation does not change ``stmt``.
        """
        return stmt


class FromAndWhereMixin:
    def _from(self, kwargs):
        # TODO: could also query by case id and not UUID
        tmp = SmallVariant.sa.table.outerjoin(
            Dbsnp.sa,
            and_(
                SmallVariant.sa.release == Dbsnp.sa.release,
                SmallVariant.sa.chromosome == Dbsnp.sa.chromosome,
                SmallVariant.sa.position == Dbsnp.sa.position,
                SmallVariant.sa.reference == Dbsnp.sa.reference,
                SmallVariant.sa.alternative == Dbsnp.sa.alternative,
            ),
        )
        if kwargs["database_select"] == "refseq":
            return tmp.outerjoin(Hgnc.sa, SmallVariant.sa.refseq_gene_id == Hgnc.sa.entrez_id)
        else:  # kwargs["database_select"] == "ensembl"
            return tmp.outerjoin(
                Hgnc.sa, SmallVariant.sa.ensembl_gene_id == Hgnc.sa.ensembl_gene_id
            )

    def _where(self, kwargs, gt_patterns=None):
        return and_(
            # Select only variants from the current case, of course.
            SmallVariant.sa.case_id == self.case.pk,
            # Filter variants down to the criteria provided by the user.
            self._build_vartype_term(kwargs),
            self._build_population_db_term(kwargs, "frequency"),
            self._build_population_db_term(kwargs, "homozygous"),
            self._build_population_db_term(kwargs, "heterozygous"),
            self._build_effects_term(kwargs),
            and_(*self._yield_genotype_terms(kwargs, gt_patterns)),
            self._build_gene_blacklist_term(kwargs),
        )

    def _build_vartype_term(self, kwargs):
        values = list()
        if kwargs["var_type_snv"]:
            values.append("snv")
        if kwargs["var_type_mnv"]:
            values.append("mnv")
        if kwargs["var_type_indel"]:
            values.append("indel")
        return SmallVariant.sa.var_type.in_(values)

    def _build_population_db_term(self, kwargs, metric):
        """Build term to limit by frequency or homozygous or heterozygous count."""
        terms = []
        for db in ("exac", "thousand_genomes", "gnomad_exomes", "gnomad_genomes"):
            field_name = "%s_%s" % (db, metric)
            if kwargs["%s_enabled" % db] and kwargs.get(field_name, None):
                terms.append(getattr(SmallVariant.sa, field_name) <= kwargs[field_name])
        return and_(*terms)

    def _build_effects_term(self, kwargs):
        effects = cast(kwargs["effects"], ARRAY(VARCHAR()))
        if kwargs["database_select"] == "refseq":
            return SmallVariant.sa.refseq_effect.overlap(effects)
        else:  # kwargs["database_select"] == "ensembl"
            return SmallVariant.sa.ensembl_effect.overlap(effects)

    def _yield_genotype_terms(self, kwargs, gt_patterns=None):
        """Build term for checking called genotypes and genotype qualities"""
        # Limit members to those in ``gt_patterns`` if given and use all members from pedigree
        # otherwise.
        if gt_patterns:
            members = [m for m in self.case.pedigree if m["patient"] in gt_patterns]
        else:
            members = self.case.pedigree
        for m in members:
            name = m["patient"]
            # Use genotype pattern ``gt_patterns`` override if given and use the patterns from
            # ``kwargs`` otherwise.
            if name in (gt_patterns or ()):
                gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[gt_patterns[name]]
            else:
                gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[kwargs["%s_gt" % name]]
            # Build quality and genotype term and combine as configured in ``kwargs``.
            quality_term = self._build_genotype_quality_term(name, kwargs)
            genotype_term = self._build_genotype_gt_term(name, gt_list)
            if kwargs["%s_fail" % name] == "drop-variant":
                yield and_(quality_term, genotype_term)
            elif kwargs["%s_fail" % name] == "no-call":
                yield or_(not_(quality_term), genotype_term)  # implication
            else:  # elif kwargs["%s_fail" % name] == "ignore"
                yield genotype_term

    def _build_genotype_quality_term(self, name, kwargs):
        return and_(
            SmallVariant.sa.genotype[name]["dp"].astext.cast(Integer) >= kwargs["%s_dp" % name],
            SmallVariant.sa.genotype[name]["gq"].astext.cast(Integer) >= kwargs["%s_gq" % name],
            # Allelic depth is only checked in case of het.
            or_(
                SmallVariant.sa.genotype[name]["gt"].astext == "0/0",
                SmallVariant.sa.genotype[name]["ad"].astext.cast(Integer) >= kwargs["%s_ad" % name],
            ),
            # Allelic balance is somewhat complicated
            and_(
                SmallVariant.sa.genotype[name]["dp"].astext.cast(Integer) > 0,
                or_(
                    not_(
                        or_(
                            SmallVariant.sa.genotype[name]["gt"].astext == "0/1",
                            SmallVariant.sa.genotype[name]["gt"].astext == "1/0",
                        )
                    ),
                    and_(
                        (
                            SmallVariant.sa.genotype[name]["ad"].astext.cast(Float)
                            / SmallVariant.sa.genotype[name]["dp"].astext.cast(Float)
                        )
                        >= kwargs["%s_ab" % name],
                        (
                            SmallVariant.sa.genotype[name]["ad"].astext.cast(Float)
                            / SmallVariant.sa.genotype[name]["dp"].astext.cast(Float)
                        )
                        <= (1.0 - kwargs["%s_ab" % name]),
                    ),
                ),
            ),
        )

    def _build_genotype_gt_term(self, name, gt_list):
        if gt_list:
            return SmallVariant.sa.genotype[name]["gt"].astext.in_(gt_list)
        else:
            return True

    def _build_gene_blacklist_term(self, kwargs):
        return not_(Hgnc.sa.symbol.in_(kwargs["gene_blacklist"]))


class FilterQueryStandardFieldsMixin(FromAndWhereMixin):
    """Mixin for selecting the standard fields for the filter query."""

    def _get_fields(self, kwargs, which):
        if which == "outer":
            return "*"
        else:
            result = [
                SmallVariant.sa.release,
                SmallVariant.sa.chromosome,
                SmallVariant.sa.position,
                SmallVariant.sa.reference,
                SmallVariant.sa.alternative,
                SmallVariant.sa.exac_frequency,
                SmallVariant.sa.gnomad_exomes_frequency,
                SmallVariant.sa.gnomad_genomes_frequency,
                SmallVariant.sa.thousand_genomes_frequency,
                SmallVariant.sa.exac_homozygous,
                SmallVariant.sa.gnomad_exomes_homozygous,
                SmallVariant.sa.gnomad_genomes_homozygous,
                SmallVariant.sa.thousand_genomes_homozygous,
                SmallVariant.sa.genotype,
                SmallVariant.sa.case_id,
                SmallVariant.sa.in_clinvar,
                Hgnc.sa.symbol,
                Dbsnp.sa.rsid,
            ]
            if kwargs["database_select"] == "refseq":
                result += [
                    SmallVariant.sa.refseq_hgvs_p.label("hgvs_p"),
                    SmallVariant.sa.refseq_hgvs_c.label("hgvs_c"),
                    SmallVariant.sa.refseq_transcript_coding.label("transcript_coding"),
                    SmallVariant.sa.refseq_effect.label("effect"),
                    SmallVariant.sa.refseq_gene_id.label("gene_id"),
                ]
            else:  # if kwargs["database_select"] == "ensembl":
                result += [
                    SmallVariant.sa.ensembl_hgvs_p.label("hgvs_p"),
                    SmallVariant.sa.ensembl_hgvs_c.label("hgvs_c"),
                    SmallVariant.sa.ensembl_transcript_coding.label("transcript_coding"),
                    SmallVariant.sa.ensembl_effect.label("effect"),
                    SmallVariant.sa.refseq_gene_id.label("gene_id"),
                ]
            return result


class FilterQueryFieldsForExportMixin(FilterQueryStandardFieldsMixin, FromAndWhereMixin):
    """Adds the fields for exporting to the query."""

    def _get_fields(self, kwargs, which):
        if which == "outer":
            return "*"
        else:
            return super()._get_fields(kwargs, which) + [SmallVariant.sa.var_type]


class FilterQueryCountRecordsMixin(FilterQueryStandardFieldsMixin, FromAndWhereMixin):
    """Mixin for selecting the number of records (``COUNT(*)``) only."""

    def _get_fields(self, kwargs, which):
        if which == "inner":
            return super()._get_fields(kwargs, which)
        else:
            return [func.count()]


class RenderFilterQuery(FilterQueryStandardFieldsMixin, FilterQueryBase):
    """Run filter query for the interactive filtration form."""


class ExportFileFilterQuery(FilterQueryFieldsForExportMixin, FilterQueryBase):
    """Run filter query for creating file to export."""

    # TODO: add conservation?


class CountOnlyFilterQuery(FilterQueryCountRecordsMixin, FilterQueryBase):
    """Run filter query but only count number of results."""

    def run(self, kwargs):
        return super().run(kwargs).first()[0]


class QueryBuilder:
    pass


class FilterQueryRunner:
    pass
