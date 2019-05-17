from contextlib import contextmanager
import json

from aldjemy import core, table
import psycopg2.extras
from sqlalchemy import Table
from sqlalchemy.sql import select, func, and_, not_, or_, cast, union, literal_column
from sqlalchemy.types import ARRAY, VARCHAR, Integer, Float
import sqlparse

from clinvar.models import Clinvar
from conservation.models import KnowngeneAA
from dbsnp.models import Dbsnp
from geneinfo.models import Hgnc, RefseqToHgnc, Acmg
from hgmd.models import HgmdPublicLocus
from variants.models import (
    Case,
    SmallVariant,
    SmallVariantComment,
    SmallVariantFlags,
    SmallVariantSummary,
    AcmgCriteriaRating,
)
from frequencies.models import GnomadExomes, GnomadGenomes, Exac, ThousandGenomes
from variants.forms import (
    FILTER_FORM_TRANSLATE_INHERITANCE,
    FILTER_FORM_TRANSLATE_CLINVAR_STATUS,
    FILTER_FORM_TRANSLATE_SIGNIFICANCE,
)
from django.core.exceptions import ImproperlyConfigured


@contextmanager
def disable_json_psycopg2():
    """Context manager for temporarily switching off automated JSON decoding in psycopg2.

    SQL Alchemy does not like this.
    """
    # TODO: this has to be done on a per-connection limit, otherwise concurrent queries in same thread break in JSON through Django ORM
    psycopg2.extras.register_default_json(loads=lambda x: x)
    psycopg2.extras.register_default_jsonb(loads=lambda x: x)
    yield
    psycopg2.extras.register_default_json(loads=json.loads)
    psycopg2.extras.register_default_jsonb(loads=json.loads)


class SingleCaseFilterQueryBase:
    """Base class for running different variants of filter queries on one case only.

    For each particular query, a sub class is created that implements and/or overrides some fields.

    All filter queries contain a "core" part that consists of the central table ``variants_smallvariant``, joins to
    other tables such as the HGNC information, table and conditions on this. These are constructed with the
    ``_core_where`` functions.

    Through subclassing (including mixin), the ``_build_stmt()`` can be overridden such that more nested statements
    can be built.

    ::

        SELECT <fields>
        FROM variants_smallvariant
        [optional JOINs]
        WHERE <conditions>
        [trailing such as ORDER BY or LIMIT]
    """

    #: The model with variants to query
    model_class = None
    #: The model with gene-based annotations to query, fallback is model_class
    annotated_model_class = None
    #: Table that the query is based on
    base_table = None

    def __init__(self, case, engine, debug=False):
        #: The case that the query is for.
        self.case = case
        #: The Aldjemy engine to use
        self.engine = engine
        #: Whether or not to print queries before issuing them
        self.debug = debug

    def run(self, kwargs):
        """Perform the query with the given ``kwargs``."""
        stmt = self._build_stmt(kwargs)
        if self.debug:  # pragma: no cover
            sql = stmt.compile(self.engine).string
            print(sqlparse.format(sql, reindent=True, keyword_case="upper"))
        with disable_json_psycopg2():
            return self.engine.execute(stmt)

    def _build_stmt(self, kwargs):
        """Build the statement and reutrn it"""
        if kwargs.get("compound_recessive_enabled"):
            raise NotImplementedError("%s does not have het. comp. support!" % self.__class__)
        return self._add_trailing(self._build_simple_stmt(kwargs), kwargs)

    def _build_simple_stmt(self, kwargs):
        """Build the simple, non-comp.-het. statement"""
        # Fields must be computed before "_core_where" in case of sub queries.
        fields = self._get_fields(kwargs, "single")
        stmt = select(fields).select_from(self._from(kwargs)).where(self._core_where(kwargs))
        return self._add_trailing(stmt, kwargs)

    def _get_fields(self, _kwargs, _which, _inner=None):
        """Return fields to ``select()`` with SQLAlchemy.

        ``_which`` is "outer" or "inner".
        """
        return []

    def _from(self, _kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        return self.base_table

    def _core_where(self, _kwargs, _gt_patterns=None):
        """Return ``WHERE`` clause for the core.

        If ``_gt_pattern`` is given then the selected individual's genotype will be forced
        as given in this parameter.  Examples for the values are:

        - ``{}`` -- empty
        - ``{"child": "het", "father": "het", "mother": "hom"}``
        - ``{"child": "het", "father": "hom", "mother": "het"}``

        The default implementation queries for variants for the particular case only.
        """
        return self.model_class.sa.case_id == self.case.pk

    def _add_trailing(self, stmt, _kwargs):
        """Optionally add trailing parts of statement.

        The default implementation does not change ``stmt``.
        """
        return stmt

    def _add_trailing_inner(self, stmt, _kwargs):
        """Optionally add trailing parts of inner statement.

        The default implementation does not change ``stmt``.
        """
        return stmt

    def get_base_table(self):
        """Return base_table"""
        if self.base_table is None:
            raise ImproperlyConfigured("Set base_table or override get_base_table().")
        else:
            return self.base_table

    def _get_pedigree(self):
        """Return list with lines from pedigree."""
        return self.case.pedigree

    def _get_filtered_pedigree_with_samples(self):
        """Return list with lines from pedigree that have samples."""
        return self.case.get_filtered_pedigree_with_samples()

    def is_prefetched(self):
        """Return if the query is prefetched or not."""
        return "LoadPrefetched" in type(self).__name__


class SingleCaseFilterQueryWithHetCompBase(SingleCaseFilterQueryBase):
    """Base class for queries with het. comp. query support."""

    def _get_trio_names(self):
        """Return (index, father, mother) names from trio"""
        index_lines = [
            rec
            for rec in self.case.pedigree
            if rec["patient"] == self.case.index and rec["has_gt_entries"]
        ]
        if len(index_lines) != 1:  # pragma: no cover
            raise RuntimeError("Could not find index line from pedigree")
        return index_lines[0]["patient"], index_lines[0]["father"], index_lines[0]["mother"]

    def _build_stmt(self, kwargs):
        """Build the statement, both simple and compound recessive"""
        if kwargs.get("compound_recessive_enabled", False) and not self.is_prefetched():
            return self._build_comp_het_stmt(kwargs)
        else:
            stmt = self._build_simple_stmt(kwargs)
            stmt = self._add_trailing_inner(stmt, kwargs)
            return self._add_trailing(stmt, kwargs)

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
            .where(self._core_where(kwargs, gt_patterns))
        )
        inner_father_stmt = self._add_trailing_inner(inner_father_stmt, kwargs)
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
            .where(self._core_where(kwargs, gt_patterns))
        )
        inner_mother_stmt = self._add_trailing_inner(inner_mother_stmt, kwargs)
        inner_mother_stmt = self._add_trailing(inner_mother_stmt, kwargs)
        # Build the union statement
        union_stmt = union(inner_father_stmt, inner_mother_stmt).alias("the_union")
        # Build the outer statement
        middle_stmt = (
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
            .alias("the_middle")
        )
        # Build the outer statement
        stmt = (
            select(self._get_fields(kwargs, "outer", middle_stmt))
            .select_from(middle_stmt)
            .where(and_(middle_stmt.c.father_count > 0, middle_stmt.c.mother_count > 0))
        )
        return self._add_trailing(stmt, kwargs)


class SingleCasePrefetchFilterQueryBase(SingleCaseFilterQueryWithHetCompBase):
    """Base class for the actual query."""

    model_class = SmallVariant
    base_table = SmallVariant.sa.table


class SingleCaseLoadPrefetchedFilterQueryBase(SingleCaseFilterQueryWithHetCompBase):
    """Class to load previous filter results."""

    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    def __init__(self, case, engine, smallvariantquery_pk, debug=False):
        """Constructor"""
        super().__init__(case, engine, debug=False)
        #: Store the smallvariantquery id to access previous results in 'where' part of the statement
        self.smallvariantquery_pk = smallvariantquery_pk
        #: Get the intermediate table where Django stores the ManyToMany relation / query results
        self.query_results = Table("variants_smallvariantquery_query_results", core.get_meta())

    def get_base_table(self):
        """Render the base table by joining the smallvariant entries by id onto the stored result ids"""
        return self.query_results.join(
            SmallVariant.sa.table, self.query_results.c.smallvariant_id == SmallVariant.sa.id
        )

    def _core_where(self, _kwargs, _gt_patterns=None):
        """OVERRIDE the where clause"""
        return self.query_results.c.smallvariantquery_id == self.smallvariantquery_pk


class ProjectCasesFilterQueryBase:
    """Base class for running different variants of filter queries on all cases of a project.

    The architecture is very similar to the one of ``SingleCaseFilterQueryBase`` and most mixins in this module
    are written to be re-useable.  See that class' docstring for more information.

    The main difference is that more than one case is selected.  Note that additional postprocessing is required
    as the returned rows can have different keys in the "genotype" column (e.g., splitting of the rows such that
    there is one row for each genotype entry or merging rows with the same variant.

    Further, compound heterozygous queries are not supported when performing queries across cohorts.
    """

    #: The model with variants to query
    model_class = None
    #: The model with gene-based annotations to query, fallback is model_class
    annotated_model_class = None
    #: Table that the query is based on
    base_table = None

    def __init__(self, project, engine, debug=False):
        #: The project that the query is for.
        self.project = project
        #: The Aldjemy engine to use
        self.engine = engine
        #: Whether or not to print queries before issuing them
        self.debug = debug

    def run(self, kwargs):
        """Perform the query with the given ``kwargs``."""
        stmt = self._build_stmt(kwargs)
        if self.debug:  # pragma: no cover
            sql = stmt.compile(self.engine).string
            print(sqlparse.format(sql, reindent=True, keyword_case="upper"))
        with disable_json_psycopg2():
            return self.engine.execute(stmt)

    def _build_stmt(self, kwargs):
        stmt = (
            select(self._get_fields(kwargs, "inner"))
            .select_from(self._from(kwargs))
            .where(self._core_where(kwargs))
        )
        stmt = self._add_trailing_inner(stmt, kwargs)
        return self._add_trailing(stmt, kwargs)

    def _get_fields(self, _kwargs, _which, _inner=None):
        """Return fields to ``select()`` with SQLAlchemy.

        ``_which`` is "outer" or "inner".
        """
        return []

    def _from(self, _kwargs):
        """Return the selectable object (e.g., a ``Join``)."""
        raise NotImplementedError("Override me!")

    def _core_where(self, _kwargs, _gt_patterns=None):
        """Return ``WHERE`` clause for the core.

        If ``_gt_pattern`` is given then the selected individual's genotype will be forced
        as given in this parameter.  Examples for the values are:

        - ``{}`` -- empty
        - ``{"child": "het", "father": "het", "mother": "hom"}``
        - ``{"child": "het", "father": "hom", "mother": "het"}``

        The default implementation queries for variants for the particular case only.
        """
        return SmallVariant.sa.case_id.in_(self.project.get_case_pks())

    def _add_trailing(self, stmt, _kwargs):
        """Optionally add trailing parts of statement.

        The default implementation does not change ``stmt``.
        """
        return stmt

    def _add_trailing_inner(self, stmt, _kwargs):
        """Optionally add trailing parts of inner statement.

        The default implementation does not change ``stmt``.
        """
        return stmt

    def _get_pedigree(self):
        """Return list with lines from pedigree."""
        return self.project.get_pedigree()

    def _get_filtered_pedigree_with_samples(self):
        """Return list with lines from pedigree that have samples."""
        return self.project.get_filtered_pedigree_with_samples()

    def get_base_table(self):
        """Return base_table"""
        if self.base_table is None:
            raise ImproperlyConfigured("Set base_table or override get_base_table().")
        else:
            return self.base_table

    def is_prefetched(self):
        """Return if the query is prefetched or not."""
        return "LoadPrefetched" in type(self).__name__


class ProjectCasesPrefetchFilterQueryBase(ProjectCasesFilterQueryBase):
    model_class = SmallVariant
    base_table = SmallVariant.sa.table


class ProjectCasesLoadPrefetchedFilterQueryBase(ProjectCasesFilterQueryBase):
    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    def __init__(self, case, engine, projectcasessmallvariantquery_pk, debug=False):
        """Constructor"""
        super().__init__(case, engine, debug=False)
        #: Store the smallvariantquery id to access previous results in 'where' part of the statement
        self.projectcasessmallvariantquery_pk = projectcasessmallvariantquery_pk
        #: Get the intermediate table where Django stores the ManyToMany relation / query results
        self.query_results = Table(
            "variants_projectcasessmallvariantquery_query_results", core.get_meta()
        )

    def get_base_table(self):
        """Render the base table by joining the smallvariant entries by id onto the stored result ids"""
        return self.query_results.join(
            SmallVariant.sa.table, self.query_results.c.smallvariant_id == SmallVariant.sa.id
        )

    def _core_where(self, _kwargs, _gt_patterns=None):
        """OVERRIDE the where clause"""
        return (
            self.query_results.c.projectcasessmallvariantquery_id
            == self.projectcasessmallvariantquery_pk
        )


# Query class mixins that add to the WHERE clause.


class GenotypeTermWhereMixinBase:
    """Mixin providing genotype term creation for WHERE clause."""

    def _core_where(self, kwargs, gt_patterns=None):
        """Extend super class' WHERE term with genotype and genotype quality terms."""
        return and_(
            super()._core_where(kwargs, gt_patterns),
            *self._yield_genotype_terms(kwargs, gt_patterns)
        )

    def _yield_genotype_terms(self, kwargs, gt_patterns=None):
        """Build term for checking called genotypes and genotype qualities"""
        # Limit members to those in ``gt_patterns`` if given and use all members from pedigree otherwise.
        if gt_patterns:
            members = [
                m
                for m in self._get_pedigree()
                if m["patient"] in gt_patterns and m["has_gt_entries"]
            ]
        else:
            members = self._get_filtered_pedigree_with_samples()
        for m in members:
            name = m["patient"]
            # Use genotype pattern ``gt_patterns`` override if given and use the patterns from ``kwargs`` otherwise.
            if name in (gt_patterns or ()):
                gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[gt_patterns[name]]
            else:
                gt_list = FILTER_FORM_TRANSLATE_INHERITANCE[kwargs["%s_gt" % name]]
            # Build quality and genotype term and combine as configured in ``kwargs``.
            quality_term = self._build_genotype_quality_term(name, kwargs)
            genotype_term = self._build_genotype_gt_term(name, gt_list)
            if kwargs.get("%s_fail" % name) == "drop-variant":
                yield and_(quality_term, genotype_term)
            elif kwargs.get("%s_fail" % name) == "no-call":
                yield or_(not_(quality_term), genotype_term)  # implication
            else:  # elif kwargs["%s_fail" % name] == "ignore"
                yield genotype_term

    def _build_genotype_gt_term(self, name, gt_list):
        """Build genotype term for the given sample.

        In the case that ``name`` does not have an entry in the ``genotype`` column, no check is performed.  Otherwise,
        this would exclude the variant if the sample name is not in the ``genotype`` dict.
        """
        if gt_list:
            return or_(
                self.model_class.sa.genotype[name].is_(None),
                self.model_class.sa.genotype[name]["gt"].astext.in_(gt_list),
            )
        else:
            return True

    def _build_genotype_quality_term(self, name, kwargs):
        """Build genotype quality term for the given sample.

        Similar to ``_build_genotype_gt_term()``, only sample that have the ``genotype`` set are checked for.
        """
        raise NotImplementedError("Override me!")


class GenotypeTermWhereMixin(GenotypeTermWhereMixinBase):
    """Implementation of ``GenotypeTermWhereMixinBase`` for ``SmallVariant`` model."""

    def _build_genotype_quality_term(self, name, kwargs):
        rhs = and_(
            # Genotype quality is simple.
            SmallVariant.sa.genotype[name]["gq"].astext.cast(Integer) >= kwargs["%s_gq" % name],
            # The depth setting depends on whether the variant is in homozygous or heterozygous state.
            or_(  # heterozygous or hemizygous state
                not_(
                    or_(
                        SmallVariant.sa.genotype[name]["gt"].astext == "0/1",
                        SmallVariant.sa.genotype[name]["gt"].astext == "1/0",
                        SmallVariant.sa.genotype[name]["gt"].astext == "1",
                        # TODO: recognize hemizygous from 'sex="M" and chr="X" and gt="1/1"'?
                    )
                ),
                SmallVariant.sa.genotype[name]["dp"].astext.cast(Integer)
                >= kwargs["%s_dp_het" % name],
            ),
            or_(  # homozygous state
                not_(
                    or_(
                        SmallVariant.sa.genotype[name]["gt"].astext == "0/0",
                        SmallVariant.sa.genotype[name]["gt"].astext == "1/1",
                    )
                ),
                SmallVariant.sa.genotype[name]["dp"].astext.cast(Integer)
                >= kwargs["%s_dp_hom" % name],
            ),
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
        return or_(SmallVariant.sa.genotype[name].is_(None), rhs)


class FrequencyTermWhereMixin:
    """Mixin that adds the frequency part and homozygous/heterozygous counts to the WHERE query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(
            super()._core_where(kwargs, gt_patterns),
            self._build_population_db_term(kwargs, "frequency"),
            self._build_population_db_term(kwargs, "homozygous"),
            self._build_population_db_term(kwargs, "heterozygous"),
        )

    def _build_population_db_term(self, kwargs, metric):
        """Build term to limit by frequency or homozygous or heterozygous count."""
        terms = []
        for db in ("exac", "thousand_genomes", "gnomad_exomes", "gnomad_genomes"):
            field_name = "%s_%s" % (db, metric)
            if kwargs["%s_enabled" % db] and kwargs.get(field_name) is not None:
                terms.append(getattr(SmallVariant.sa, field_name) <= kwargs[field_name])
        return and_(*terms)


class VariantTypeTermWhereMixin:
    """Mixin that adds the variant type part to the WHERE query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_vartype_term(kwargs))

    def _build_vartype_term(self, kwargs):
        values = list()
        if kwargs["var_type_snv"]:
            values.append("snv")
        if kwargs["var_type_mnv"]:
            values.append("mnv")
        if kwargs["var_type_indel"]:
            values.append("indel")
        return or_(SmallVariant.sa.var_type.is_(None), SmallVariant.sa.var_type.in_(values))


class VariantEffectTermWhereMixin:
    """Mixin that adds the effect type part to the WHERE query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_effects_term(kwargs))

    def _build_effects_term(self, kwargs):
        effects = cast(kwargs["effects"], ARRAY(VARCHAR()))
        model_class = self.annotated_model_class or self.model_class
        if kwargs["database_select"] == "refseq":
            return model_class.sa.refseq_effect.overlap(effects)
        else:  # kwargs["database_select"] == "ensembl"
            return model_class.sa.ensembl_effect.overlap(effects)


class TranscriptCodingTermWhereMixin:
    """Mixin that adds the transcript coding/non-coding part to the WHERE query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(
            super()._core_where(kwargs, gt_patterns), self._build_transcripts_coding_term(kwargs)
        )

    def _build_transcripts_coding_term(self, kwargs):
        sub_terms = []
        model_class = self.annotated_model_class or self.model_class
        if kwargs["database_select"] == "refseq":
            field = model_class.sa.refseq_transcript_coding
        else:
            field = model_class.sa.ensembl_transcript_coding
        if not kwargs["transcripts_coding"]:
            sub_terms.append(field == False)  # equality from SQL Alchemy
        if not kwargs["transcripts_noncoding"]:
            sub_terms.append(field == True)  # equality from SQL Alchemy
        return and_(*sub_terms)


class GeneListsTermWhereMixin:
    """Mixin that adds the gene whitelist/blacklist part to the WHERE query."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(
            super()._core_where(kwargs, gt_patterns),
            self._build_gene_blacklist_term(kwargs["gene_blacklist"]),
            self._build_gene_whitelist_term(kwargs["gene_whitelist"]),
        )

    def _build_gene_blacklist_term(self, gene_list):
        if not gene_list:
            return True
        else:
            return not_(self._build_gene_whitelist_term(gene_list))

    def _build_gene_whitelist_term(self, gene_list):
        model_class = self.annotated_model_class or self.model_class
        if not gene_list:
            return True
        else:
            return or_(
                model_class.sa.ensembl_gene_id.in_(
                    self._build_gene_sub_query("ensembl_gene_id", gene_list)
                ),
                model_class.sa.refseq_gene_id.in_(
                    self._build_gene_sub_query("entrez_id", gene_list)
                ),
            )

    def _build_gene_sub_query(self, hgnc_field, gene_list):
        """Return query that selects gene ID from ENSEMBL in gene list.

        Will query for ENSEMBL gene ID, Entrez ID, and HUGO symbol.
        """
        return (
            select([getattr(Hgnc.sa, hgnc_field)])
            .select_from(Hgnc.sa.table)
            .where(
                and_(
                    or_(
                        Hgnc.sa.ensembl_gene_id.in_(gene_list),
                        Hgnc.sa.entrez_id.in_(gene_list),
                        Hgnc.sa.symbol.in_(gene_list),
                    ),
                    getattr(Hgnc.sa, hgnc_field) != None,  # SQL Alchemy forces us to use ``!=``
                )
            )
            .distinct()
        )


class GenomicRegionTermWhereMixin:
    """Mixin that limits the search query to a specified region."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(
            super()._core_where(kwargs, gt_patterns),
            self._build_genomic_region_term(kwargs["genomic_region"]),
        )

    def _build_genomic_region_term(self, genomic_region):
        if not genomic_region:
            return True
        else:
            return or_(
                *[
                    and_(
                        SmallVariant.sa.chromosome == entry[0],
                        SmallVariant.sa.position >= entry[1],
                        SmallVariant.sa.position <= entry[2],
                    )
                    for entry in genomic_region
                ]
            )


class InClinvarTermWhereMixin:
    """Mixin that adds the "is in clinvar" table."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_in_clinvar_term(kwargs))

    def _build_in_clinvar_term(self, kwargs):
        if kwargs["require_in_clinvar"]:
            return SmallVariant.sa.in_clinvar
        else:
            return True


class NotInDbsnpMixin:
    """Mixin that excludes variants that have a clinvar entry."""

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(super()._core_where(kwargs, gt_patterns), self._build_not_in_dbsnp_term(kwargs))

    def _build_not_in_dbsnp_term(self, kwargs):
        if kwargs["remove_if_in_dbsnp"]:
            return Dbsnp.sa.rsid == None
        else:
            return True


class FilterInHouseCountsMixin:
    """Join in-house variants to the results and threshold on the number of heterozygous/homozygous variants."""

    def _add_trailing_inner(self, stmt, kwargs):
        """Override statement building to add the join with Clinvar information."""
        inner = super()._add_trailing_inner(stmt, kwargs)
        return self._extend_stmt_inhouse_db(inner, kwargs)

    def _extend_stmt_inhouse_db(self, inner, kwargs):
        """Extend the inner statement and augment inhouse count information."""
        inner = inner.alias("inhouse_inner")
        middle = (
            select(
                [
                    *inner.c,
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
                    func.coalesce(
                        func.sum(
                            SmallVariantSummary.sa.count_het
                            + SmallVariantSummary.sa.count_hom_alt
                            + SmallVariantSummary.sa.count_hemi_alt
                        ),
                        0,
                    ).label("inhouse_carriers"),
                ]
            )
            .select_from(
                inner.outerjoin(
                    SmallVariantSummary.sa.table,
                    and_(
                        SmallVariantSummary.sa.release == inner.c.release,
                        SmallVariantSummary.sa.chromosome == inner.c.chromosome,
                        SmallVariantSummary.sa.position == inner.c.position,
                        SmallVariantSummary.sa.reference == inner.c.reference,
                        SmallVariantSummary.sa.alternative == inner.c.alternative,
                    ),
                )
            )
            .group_by(*inner.c)
            .alias("inhouse_middle")
        )
        stmt = select(middle.c).select_from(middle).where(self._where_inhouse_db(kwargs, middle))
        return self._add_trailing(stmt, kwargs)

    def _where_inhouse_db(self, kwargs, stmt):
        """Build WHERE clause for the query based on select het/hom counts in inhouse DB."""
        terms = []
        if kwargs.get("inhouse_enabled"):
            if kwargs.get("inhouse_heterozygous") is not None:
                terms.append(stmt.c.inhouse_het <= kwargs.get("inhouse_heterozygous"))
            if kwargs.get("inhouse_homozygous") is not None:
                terms.append(
                    (stmt.c.inhouse_hom_alt + stmt.c.inhouse_hemi_alt)
                    <= kwargs.get("inhouse_homozygous")
                )
            if kwargs.get("inhouse_carriers") is not None:
                terms.append(
                    (stmt.c.inhouse_het + stmt.c.inhouse_hom_alt + stmt.c.inhouse_hemi_alt)
                    <= kwargs.get("inhouse_carriers")
                )
        return and_(*terms)


class BaseTableQueriesMixin(
    GenotypeTermWhereMixin,
    FrequencyTermWhereMixin,
    VariantTypeTermWhereMixin,
    VariantEffectTermWhereMixin,
    TranscriptCodingTermWhereMixin,
    GeneListsTermWhereMixin,
    GenomicRegionTermWhereMixin,
    InClinvarTermWhereMixin,
    FilterInHouseCountsMixin,
    NotInDbsnpMixin,
):
    """Helper mixin that adds all criteria that can be answered by the base star table."""


# Query class mixins providing fields, possibly joining the extended tables.


class JoinDbsnpAndHgncMixin:
    """Mixin for generating the ``FROM`` and ``WHERE`` clauses for the filter queries.
    """

    def _from(self, kwargs):
        tmp = self.get_base_table().outerjoin(
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
            return (
                tmp.outerjoin(
                    RefseqToHgnc.sa, SmallVariant.sa.refseq_gene_id == RefseqToHgnc.sa.entrez_id
                )
                .outerjoin(Hgnc.sa, RefseqToHgnc.sa.hgnc_id == Hgnc.sa.hgnc_id)
                .outerjoin(Acmg.sa, SmallVariant.sa.refseq_gene_id == Acmg.sa.entrez_id)
            )
        else:  # kwargs["database_select"] == "ensembl"
            return tmp.outerjoin(
                Hgnc.sa, SmallVariant.sa.ensembl_gene_id == Hgnc.sa.ensembl_gene_id
            ).outerjoin(Acmg.sa, SmallVariant.sa.ensembl_gene_id == Acmg.sa.ensembl_gene_id)


class FilterQueryRenderFieldsMixin(JoinDbsnpAndHgncMixin):
    """Mixin for selecting the standard fields for rendering the query reports in the web app."""

    def _from(self, kwargs):
        return super()._from(kwargs).join(Case.sa.table, Case.sa.id == SmallVariant.sa.case_id)

    def _get_fields(self, kwargs, which, inner=None):
        if which == "outer":
            if inner is not None:
                return [*inner.c]
            else:
                return "*"
        else:
            result = [
                SmallVariant.sa.id,
                SmallVariant.sa.release,
                SmallVariant.sa.chromosome,
                SmallVariant.sa.position,
                SmallVariant.sa.reference,
                SmallVariant.sa.alternative,
                SmallVariant.sa.ensembl_gene_id.label("ensembl_gene_id"),
                SmallVariant.sa.refseq_gene_id.label("entrez_id"),
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
                SmallVariant.sa.case_id,
                SmallVariant.sa.in_clinvar,
                Hgnc.sa.symbol,
                Hgnc.sa.name.label("gene_name"),
                Hgnc.sa.gene_family.label("gene_family"),
                Acmg.sa.symbol.label("acmg_symbol"),
                Dbsnp.sa.rsid,
                Case.sa.sodar_uuid.label("case_uuid"),
                (SmallVariant.sa.ensembl_effect != SmallVariant.sa.refseq_effect).label(
                    "effect_ambiguity"
                ),
            ] + super()._get_fields(kwargs, which, inner)
            if kwargs["database_select"] == "refseq":
                result += [
                    SmallVariant.sa.refseq_hgvs_p.label("hgvs_p"),
                    SmallVariant.sa.refseq_hgvs_c.label("hgvs_c"),
                    SmallVariant.sa.refseq_transcript_coding.label("transcript_coding"),
                    SmallVariant.sa.refseq_effect.label("effect"),
                    SmallVariant.sa.refseq_gene_id.label("gene_id"),
                    SmallVariant.sa.refseq_transcript_id.label("transcript_id"),
                ]
            else:  # if kwargs["database_select"] == "ensembl":
                result += [
                    SmallVariant.sa.ensembl_hgvs_p.label("hgvs_p"),
                    SmallVariant.sa.ensembl_hgvs_c.label("hgvs_c"),
                    SmallVariant.sa.ensembl_transcript_coding.label("transcript_coding"),
                    SmallVariant.sa.ensembl_effect.label("effect"),
                    SmallVariant.sa.ensembl_gene_id.label("gene_id"),
                    SmallVariant.sa.ensembl_transcript_id.label("transcript_id"),
                ]
            return result


class JoinKnownGeneAaMixin(FilterQueryRenderFieldsMixin):
    """Adds the fields for exporting to the query."""

    def _build_stmt(self, kwargs):

        inner = super()._build_stmt(kwargs).alias("inner")
        middle = (
            select(
                [
                    *inner.c,
                    KnowngeneAA.sa.start.label("kgaa_start"),
                    KnowngeneAA.sa.alignment.label("kgaa_alignment"),
                ]
            )
            .select_from(
                inner.outerjoin(
                    KnowngeneAA.sa.table,
                    and_(
                        # TODO: add release?
                        KnowngeneAA.sa.chromosome == inner.c.chromosome,
                        KnowngeneAA.sa.start
                        <= (inner.c.position - 1 + func.length(inner.c.reference)),
                        KnowngeneAA.sa.end > (inner.c.position - 1),
                        # TODO: using "LEFT(, -2)" here breaks if version > 9
                        func.left(KnowngeneAA.sa.transcript_id, -2)
                        == func.left(inner.c.ucsc_id, -2),
                    ),
                )
            )
            .order_by(inner.c.chromosome, KnowngeneAA.sa.start)
            .alias("middle")
        )
        # Collect names of middle fields after grouping
        middle_fields = [c for c in middle.c if not c.name.startswith("kgaa_")]
        outer = (
            select(
                [
                    *middle_fields,
                    func.string_agg(middle.c.kgaa_alignment, " / ").label("known_gene_aa"),
                ]
            )
            .select_from(middle)
            .group_by(*middle_fields)
        )
        return self._add_trailing(outer, kwargs)

    def _get_fields(self, kwargs, which, inner=None):
        """Add a few fields for file export"""
        if which == "outer":
            if inner is not None:
                return [*inner.c]
            else:
                return ["*"]
        else:
            # Return additional fields for downloadable files.  When rendered, this additional
            # information is loaded on demand by AJAX.
            return super()._get_fields(kwargs, which, inner) + [
                # Required for joining conservation
                Hgnc.sa.ucsc_id,
                # Additional information for display in downloaded file
                SmallVariant.sa.var_type,
                SmallVariant.sa.ensembl_transcript_id,
                Hgnc.sa.name.label("hgnc_gene_name"),
                Hgnc.sa.gene_family.label("hgnc_gene_family"),
                Hgnc.sa.pubmed_id.label("hgnc_pubmed_id"),
            ]


class FilterQueryHgmdMixin:
    """Add functionality for annotation with ``HgmdPublicLocus`` and filtering for it.

    This class uses ``Hgmd`` and not ``HgmdPublicLocus`` as name part as at some point support for HGMD professional
    could be added and this would be the right place.
    """

    def _build_stmt(self, kwargs):
        """Override statement building to add the join with Clinvar information."""
        inner = super()._build_stmt(kwargs)
        if not kwargs.get("require_in_hgmd_public") and not kwargs.get(
            "display_hgmd_public_membership"
        ):
            return inner
        else:
            return self._extend_stmt_hgmd(inner, kwargs)

    def _extend_stmt_hgmd(self, inner, kwargs):
        """Extend the inner statement and augment with HgmdPublicLocus information."""
        inner = inner.alias("inner_hgmd")
        stmt = (
            select(
                [
                    *inner.c,
                    func.count(HgmdPublicLocus.sa.variation_name).label("hgmd_public_overlap"),
                    func.max(HgmdPublicLocus.sa.variation_name).label("hgmd_accession"),
                ]
            )
            .select_from(
                inner.outerjoin(
                    HgmdPublicLocus.sa.table,
                    and_(
                        HgmdPublicLocus.sa.release == inner.c.release,
                        HgmdPublicLocus.sa.chromosome == inner.c.chromosome,
                        HgmdPublicLocus.sa.start
                        <= (inner.c.position - 1 + func.length(inner.c.reference)),
                        HgmdPublicLocus.sa.end > (inner.c.position - 1),
                    ),
                )
            )
            .group_by(*inner.c)
        )
        stmt = self._add_outer_having_condition(inner, stmt, kwargs)
        return self._add_trailing(stmt, kwargs)

    def _add_outer_having_condition(self, inner, stmt, kwargs):
        """Build HAVING condition for outermost query."""
        if kwargs["require_in_hgmd_public"]:
            return stmt.having(func.count(HgmdPublicLocus.sa.variation_name) > 0)
        else:
            return stmt


class FilterQueryClinvarDetailsMixin(InClinvarTermWhereMixin):
    """Add functionality for filtering that goes beyond the "present in ClinVar" query.

    For this, the Clinvar database table must be joint to the central table.
    """

    patho_keys = (
        "pathogenic",
        "likely_pathogenic",
        "uncertain_significance",
        "likely_benign",
        "benign",
    )

    def _build_stmt(self, kwargs):
        """Override statement building to add the join with Clinvar information."""
        inner = super()._build_stmt(kwargs)
        if not kwargs["require_in_clinvar"]:
            return inner
        else:
            return self._extend_stmt_clinvar(inner, kwargs)

    def _extend_stmt_clinvar(self, inner, kwargs):
        """Extend the inner statement and augment with Clinvar information."""
        inner = inner.alias("inner_clinvar")
        stmt = (
            select(
                [
                    *inner.c,
                    *(
                        func.sum(getattr(Clinvar.sa, key)).label("clinvar_%s" % key)
                        for key in self.patho_keys
                    ),
                ]
            )
            .select_from(
                inner.outerjoin(
                    Clinvar.sa.table,
                    and_(
                        Clinvar.sa.release == inner.c.release,
                        Clinvar.sa.chromosome == inner.c.chromosome,
                        Clinvar.sa.position == inner.c.position,
                        Clinvar.sa.reference == inner.c.reference,
                        Clinvar.sa.alternative == inner.c.alternative,
                    ),
                )
            )
            .group_by(*inner.c)
        )
        stmt = stmt.having(self._outer_having_condition(inner, kwargs))
        return self._add_trailing(stmt, kwargs)

    def _outer_having_condition(self, inner, kwargs):
        """Build HAVING condition for outermost query."""
        terms = []
        for key in self.patho_keys:
            if kwargs["clinvar_include_%s" % key]:
                terms.append(func.sum(getattr(Clinvar.sa, key)) > 0)
        return or_(*terms)


class FilterQueryFlagsCommentsMixin:
    """Add information about flags, comments, and ACMG ratings for filter queries."""

    def _build_stmt(self, kwargs):
        """Override statement building to add the join with Clinvar information."""
        inner = super()._build_stmt(kwargs)
        return self._extend_stmt_comments_flags(inner, kwargs)

    def _extend_stmt_comments_flags(self, inner, kwargs):
        """Extend the inner statement and augment flag and comments information."""
        inner = inner.alias("inner_comments_flags")
        stmt = (
            select(
                [
                    *inner.c,
                    func.count(SmallVariantFlags.sa.id).label("flag_count"),
                    func.count(SmallVariantComment.sa.id).label("comment_count"),
                    # TODO: actually it would be better to use DISTINCT ON which requires more sorting...
                    func.bool_or(SmallVariantFlags.sa.flag_bookmarked).label("flag_bookmarked"),
                    func.bool_or(SmallVariantFlags.sa.flag_candidate).label("flag_candidate"),
                    func.bool_or(SmallVariantFlags.sa.flag_final_causative).label(
                        "flag_final_causative"
                    ),
                    func.bool_or(SmallVariantFlags.sa.flag_for_validation).label(
                        "flag_for_validation"
                    ),
                    func.max(SmallVariantFlags.sa.flag_visual).label("flag_visual"),
                    func.max(SmallVariantFlags.sa.flag_validation).label("flag_validation"),
                    func.max(SmallVariantFlags.sa.flag_phenotype_match).label(
                        "flag_phenotype_match"
                    ),
                    func.max(SmallVariantFlags.sa.flag_summary).label("flag_summary"),
                    func.max(AcmgCriteriaRating.sa.class_auto).label("acmg_class_auto"),
                    func.max(AcmgCriteriaRating.sa.class_override).label("acmg_class_override"),
                ]
            )
            .select_from(
                inner.outerjoin(
                    SmallVariantFlags.sa.table,
                    and_(
                        SmallVariantFlags.sa.case_id == inner.c.case_id,
                        SmallVariantFlags.sa.release == inner.c.release,
                        SmallVariantFlags.sa.chromosome == inner.c.chromosome,
                        SmallVariantFlags.sa.position == inner.c.position,
                        SmallVariantFlags.sa.reference == inner.c.reference,
                        SmallVariantFlags.sa.alternative == inner.c.alternative,
                    ),
                )
                .outerjoin(
                    SmallVariantComment.sa.table,
                    and_(
                        SmallVariantComment.sa.case_id == inner.c.case_id,
                        SmallVariantComment.sa.release == inner.c.release,
                        SmallVariantComment.sa.chromosome == inner.c.chromosome,
                        SmallVariantComment.sa.position == inner.c.position,
                        SmallVariantComment.sa.reference == inner.c.reference,
                        SmallVariantComment.sa.alternative == inner.c.alternative,
                    ),
                )
                .outerjoin(
                    AcmgCriteriaRating.sa.table,
                    and_(
                        AcmgCriteriaRating.sa.case_id == inner.c.case_id,
                        AcmgCriteriaRating.sa.release == inner.c.release,
                        AcmgCriteriaRating.sa.chromosome == inner.c.chromosome,
                        AcmgCriteriaRating.sa.position == inner.c.position,
                        AcmgCriteriaRating.sa.reference == inner.c.reference,
                        AcmgCriteriaRating.sa.alternative == inner.c.alternative,
                    ),
                )
            )
            .where(self._flags_comments_where(kwargs))
            .group_by(*inner.c)
        )
        return self._add_trailing(stmt, kwargs)

    def _flags_comments_where(self, kwargs, gt_patterns=None):
        """Build WHERE clause for the query based on the ``SmallVariantFlags`` and ``SmallVariantComment``."""
        terms = []
        # Add terms for the simple, boolean-valued flags.
        flag_names = ("bookmarked", "candidate", "final_causative", "for_validation")
        for flag in flag_names:
            flag_name = "flag_%s" % flag
            if kwargs.get(flag_name):
                terms.append(getattr(SmallVariantFlags.sa, flag_name))
        if kwargs.get("flag_simple_empty"):
            terms.append(and_(not getattr(SmallVariantFlags.sa, "flag_%s" % flag)))
        # Add terms for the valued flags.
        flag_names = ("visual", "validation", "phenotype_match", "summary")
        for flag in flag_names:
            flag_name = "flag_%s" % flag
            for value in ("positive", "uncertain", "negative", "empty"):
                field_name = "%s_%s" % (flag_name, value)
                if kwargs.get(field_name):
                    terms.append(getattr(SmallVariantFlags.sa, flag_name) == value)
                    if value == "empty":
                        terms.append(getattr(SmallVariantFlags.sa, flag_name).is_(None))
        return or_(*terms)


class JoinAndQueryCommonAdditionalTables(
    FilterQueryFlagsCommentsMixin,
    FilterQueryHgmdMixin,
    FilterQueryClinvarDetailsMixin,
    FilterInHouseCountsMixin,
):
    """Join to common common additional tables and query.

    - ClinVar
    - HGMD
    - User comments and flags
    """


# Helper query class mixins.


class OrderByChromosomalPositionMixin:
    """Order by chromosomal position and reference/alternative allele string."""

    def _add_trailing(self, stmt, _kwargs):
        return stmt.order_by(
            stmt.c.chromosome, stmt.c.position, stmt.c.reference, stmt.c.alternative
        )


class FilterQueryCountRecordsMixin(FilterQueryClinvarDetailsMixin, FilterQueryRenderFieldsMixin):
    """Mixin for selecting the number of records (``COUNT(*)``) only."""

    def _build_stmt(self, kwargs):
        return select([func.count()]).select_from(super()._build_stmt(kwargs).alias("inner_count"))


# Actual Query classes, composed from base query class and mixins.


class PrefetchFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    FilterQueryRenderFieldsMixin,
    BaseTableQueriesMixin,
    SingleCasePrefetchFilterQueryBase,
):
    """Run filter query for the interactive filtration form."""


class ExportTableFileFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    JoinKnownGeneAaMixin,
    FilterQueryRenderFieldsMixin,
    BaseTableQueriesMixin,
    SingleCaseFilterQueryWithHetCompBase,
):
    """Run filter query for creating tabular file (TSV, Excel) to export for a single case.

    Compared to ``RenderFilterQuery``, this only adds the ``knownGeneAA`` information.
    """

    model_class = SmallVariant
    base_table = SmallVariant.sa.table


class ExportVcfFileFilterQuery(
    OrderByChromosomalPositionMixin, BaseTableQueriesMixin, SingleCaseFilterQueryWithHetCompBase
):
    """Run filter query for TSV file with minimal information only for performance.

    Only supports query for genotype, frequency, quality, and gene lists.
    """

    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    def _from(self, kwargs):
        return SmallVariant.sa.table

    def _get_fields(self, kwargs, which, inner=None):
        if which == "outer":
            if inner is not None:
                return [*inner.c]
            else:
                return "*"
        else:
            result = [
                SmallVariant.sa.release,
                SmallVariant.sa.chromosome,
                SmallVariant.sa.position,
                SmallVariant.sa.reference,
                SmallVariant.sa.alternative,
                SmallVariant.sa.genotype,
            ] + super()._get_fields(kwargs, which, inner)
            if kwargs["database_select"] == "refseq":
                result.append(SmallVariant.sa.refseq_gene_id.label("gene_id"))
            else:  # if kwargs["database_select"] == "ensembl":
                result.append(SmallVariant.sa.ensembl_gene_id.label("gene_id"))
            return result


class CountOnlyFilterQuery(
    FilterQueryCountRecordsMixin,
    JoinAndQueryCommonAdditionalTables,
    BaseTableQueriesMixin,
    SingleCasePrefetchFilterQueryBase,
):
    """Run filter query but only count number of results."""

    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    def run(self, kwargs):
        return super().run(kwargs).first()[0]


class LoadPrefetchedFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    FilterQueryRenderFieldsMixin,
    SingleCaseLoadPrefetchedFilterQueryBase,
):
    """Load results from previous single case filter query and join information."""


# Filter query to run against all cases within the same project.


class ProjectCasesLoadPrefetchedFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    FilterQueryRenderFieldsMixin,
    ProjectCasesLoadPrefetchedFilterQueryBase,
):
    """Load results from previous joint project filter query and join information."""


class ProjectCasesPrefetchFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    FilterQueryRenderFieldsMixin,
    BaseTableQueriesMixin,
    ProjectCasesPrefetchFilterQueryBase,
):
    """Run filter query for the interactive filtration form."""


class ProjectCasesExportTableFilterQuery(
    OrderByChromosomalPositionMixin,
    JoinAndQueryCommonAdditionalTables,
    JoinKnownGeneAaMixin,
    FilterQueryRenderFieldsMixin,
    BaseTableQueriesMixin,
    ProjectCasesPrefetchFilterQueryBase,
):
    """Run filter query for creating tabular file (TSV, Excel) to export for multiple cases.

    Compared to ``ProjectCasesRenderFilterQuery``, this only adds the ``knownGeneAA`` information.
    """


# Clinvar report query mixins and classes.


class ClinvarReportFromAndWhereMixin(GenotypeTermWhereMixin):
    """Mixin for generating the ``FROM`` and ``WHERE`` clauses for the clinvar report query.
    """

    def _from(self, kwargs):
        tmp = (
            self.get_base_table()
            .join(Case.sa.table, Case.sa.id == SmallVariant.sa.case_id)
            .outerjoin(
                Clinvar.sa,
                and_(
                    SmallVariant.sa.release == Clinvar.sa.release,
                    SmallVariant.sa.chromosome == Clinvar.sa.chromosome,
                    SmallVariant.sa.position == Clinvar.sa.position,
                    SmallVariant.sa.reference == Clinvar.sa.reference,
                    SmallVariant.sa.alternative == Clinvar.sa.alternative,
                ),
            )
            .outerjoin(
                Dbsnp.sa,
                and_(
                    SmallVariant.sa.release == Dbsnp.sa.release,
                    SmallVariant.sa.chromosome == Dbsnp.sa.chromosome,
                    SmallVariant.sa.position == Dbsnp.sa.position,
                    SmallVariant.sa.reference == Dbsnp.sa.reference,
                    SmallVariant.sa.alternative == Dbsnp.sa.alternative,
                ),
            )
        )
        if kwargs["database_select"] == "refseq":
            return (
                tmp.outerjoin(
                    RefseqToHgnc.sa, SmallVariant.sa.refseq_gene_id == RefseqToHgnc.sa.entrez_id
                )
                .outerjoin(Hgnc.sa, RefseqToHgnc.sa.hgnc_id == Hgnc.sa.hgnc_id)
                .outerjoin(Acmg.sa, SmallVariant.sa.refseq_gene_id == Acmg.sa.entrez_id)
            )
        else:  # kwargs["database_select"] == "ensembl"
            return tmp.outerjoin(
                Hgnc.sa, SmallVariant.sa.ensembl_gene_id == Hgnc.sa.ensembl_gene_id
            ).outerjoin(Acmg.sa, SmallVariant.sa.ensembl_gene_id == Acmg.sa.ensembl_gene_id)

    def _core_where(self, kwargs, gt_patterns=None):
        return and_(
            super()._core_where(kwargs, gt_patterns),
            # Filter variants to those with matching genotype.
            and_(*self._yield_genotype_terms(kwargs, gt_patterns)),
            # Filter variants to those in Clinvar.
            SmallVariant.sa.in_clinvar == True,  # SQL Alchemy requires "== True"
            # Apply Clinvar-specific filters.
            self._build_significance_term(kwargs),
            self._build_origin_term(kwargs),
            self._build_review_status_term(kwargs),
        )

    def _build_in_clinvar_term(self, kwargs):
        if kwargs["require_in_clinvar"]:
            return SmallVariant.sa.in_clinvar
        else:
            return True

    def _build_genotype_quality_term(self, _name, _kwargs):
        """Force genotype quality term to pass ``True``."""
        return True

    def _build_significance_term(self, kwargs):
        result = []
        for key, value in FILTER_FORM_TRANSLATE_SIGNIFICANCE.items():
            if kwargs[key]:
                result.append(getattr(Clinvar.sa, value.replace(" ", "_")) >= 1)
        return or_(*result)

    def _build_origin_term(self, kwargs):
        """Build term for variant origin in Clinvar."""
        origins = []
        if kwargs["clinvar_origin_germline"]:
            origins.append("germline")
        if kwargs["clinvar_origin_somatic"]:
            origins.append("somatic")
        origins = cast(origins, ARRAY(VARCHAR()))
        return Clinvar.sa.origin.overlap(origins)

    def _build_review_status_term(self, kwargs):
        """Build term for review status in Clinvar."""
        review_statuses = [
            value for key, value in FILTER_FORM_TRANSLATE_CLINVAR_STATUS.items() if kwargs[key]
        ]
        review_statuses = cast(review_statuses, ARRAY(VARCHAR()))
        return Clinvar.sa.review_status_ordered.overlap(review_statuses)


class ClinvarReportFieldsMixin(FilterQueryRenderFieldsMixin):
    """Mixin for selecting the standard fields for the filter query."""

    def _get_fields(self, kwargs, which, inner=None):
        result = super()._get_fields(kwargs, which, inner)
        if which == "outer":
            return result
        else:
            result += [
                Clinvar.sa.review_status_ordered,
                Clinvar.sa.clinical_significance_ordered,
                Clinvar.sa.all_traits,
                Clinvar.sa.dates_ordered,
                Clinvar.sa.origin,
                Clinvar.sa.rcv,
            ]
            return result


class PrefetchClinvarReportQueryBase(SingleCaseFilterQueryBase):
    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    #: Table that the query is based on
    base_table = SmallVariant.sa.table


class LoadPrefetchedClinvarReportQueryBase(SingleCaseFilterQueryBase):
    """Class to load previous filter results
    """

    model_class = SmallVariant
    base_table = SmallVariant.sa.table

    def __init__(self, case, engine, clinvarquery_pk, debug=False):
        """Constructor"""
        super().__init__(case, engine, debug=False)
        #: Store the smallvariantquery id to access previous results in 'where' part of the statement
        self.clinvarquery_pk = clinvarquery_pk
        #: Get the intermediate table where Django stores the ManyToMany relation / query results
        table.generate_tables(core.get_meta())
        self.query_results = core.get_meta().tables["variants_clinvarquery_query_results"]

    def get_base_table(self):
        """Render the base table by joining the smallvariant entries by id onto the stored result ids"""
        return self.query_results.join(
            SmallVariant.sa.table, self.query_results.c.smallvariant_id == SmallVariant.sa.id
        )

    def _core_where(self, _kwargs, _gt_patterns=None):
        """OVERRIDE the where clause"""
        return self.query_results.c.clinvarquery_id == self.clinvarquery_pk


class PrefetchClinvarReportQuery(
    FilterQueryFlagsCommentsMixin,
    FilterQueryHgmdMixin,
    FilterQueryClinvarDetailsMixin,
    ClinvarReportFromAndWhereMixin,
    ClinvarReportFieldsMixin,
    OrderByChromosomalPositionMixin,
    PrefetchClinvarReportQueryBase,
):
    """Run query for clinvar report."""


class LoadPrefetchedClinvarReportQuery(
    FilterQueryFlagsCommentsMixin,
    FilterQueryHgmdMixin,
    FilterQueryClinvarDetailsMixin,
    ClinvarReportFromAndWhereMixin,
    ClinvarReportFieldsMixin,
    OrderByChromosomalPositionMixin,
    LoadPrefetchedClinvarReportQueryBase,
):
    """Run query for clinvar report."""

    model_class = SmallVariant
    base_table = SmallVariant.sa.table


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
            # TODO: add release
            KnowngeneAA.sa.chromosome,
            KnowngeneAA.sa.start,
            KnowngeneAA.sa.end,
        ]
        query = (
            select(distinct_fields + [KnowngeneAA.sa.alignment])
            .select_from(KnowngeneAA.sa.table)
            .where(
                and_(
                    KnowngeneAA.sa.chromosome == kwargs["chromosome"],
                    KnowngeneAA.sa.start < int(kwargs["position"]) - 1 + len(kwargs["reference"]),
                    KnowngeneAA.sa.end > int(kwargs["position"]) - 1,
                )
            )
            .order_by(KnowngeneAA.sa.start)
            .distinct(*distinct_fields)
        )
        return self.engine.execute(query)


#: Information about frequency databases used in ``FrequencyQuery``.
FREQUENCY_DB_INFO = {
    "gnomadexomes": {
        "model": GnomadExomes,
        "populations": ("afr", "amr", "asj", "eas", "fin", "nfe", "oth", "sas"),
    },
    "gnomadgenomes": {
        "model": GnomadGenomes,
        "populations": ("afr", "amr", "asj", "eas", "fin", "nfe", "oth"),
    },
    "exac": {"model": Exac, "populations": ("afr", "amr", "eas", "fin", "nfe", "oth", "sas")},
    "thousandgenomes": {
        "model": ThousandGenomes,
        "populations": ("afr", "amr", "eas", "eur", "sas"),
    },
}
