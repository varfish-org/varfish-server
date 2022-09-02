import contextlib

from django.conf import settings
from django.db import transaction

from projectroles.plugins import get_backend_api

from cohorts.models import Cohort
from variants.helpers import get_engine
from variants.forms import PATHO_SCORES_MAPPING
from variants.models import prioritize_genes, VariantScoresFactory
from .queries import CasePrefetchQuery, ProjectPrefetchQuery


class FilterBase:
    """Base class for filtering and storing case query results.
    """

    def __init__(self, job, variant_query):
        """Constructor"""
        #: The ``StoreQueryResultsBgJob`` to use for logging.  Variants are obtained from ``case_or_project``.
        self.job = job
        #: Either SmallVariantQuery or ProjectCasesSmallVariant
        self.variant_query = variant_query
        #: The SQL Alchemy connection to use.
        self._alchemy_engine = None
        #: Is set in inherited classes
        self.assembled_query = self._get_assembled_query()

    def _get_assembled_query(self):
        """Override me!"""
        pass

    def _get_genomebuild(self):
        """Override me!"""
        pass

    def get_alchemy_engine(self):
        """Construct and return the alchemy connection."""
        if not self._alchemy_engine:
            self._alchemy_engine = get_engine()
        return self._alchemy_engine

    def run(self, kwargs={}):
        """Run filter query"""
        # Patch query args, if available
        query_args = {**self.variant_query.query_settings, **kwargs}
        # Run query, store results, and run prioritization query.
        self.job.add_log_entry("Running database query ...")
        with contextlib.closing(self.assembled_query.run(query_args)) as results:
            _results = tuple(results)
            self._store_results(_results)
            self._prioritize_gene_phenotype(_results)
            self._prioritize_variant_pathogenicity(_results)

    def _store_results(self, results):
        """Store results in ManyToMany field."""
        self.job.add_log_entry("Storing results ...")
        # Obtain smallvariant ids to store them in ManyToMany field
        smallvariant_pks = [row["id"] for row in results]
        # Delete previously stored results (note: this only disassociates them, it doesn't delete objects itself.)
        self.variant_query.query_results.clear()
        # Bulk-insert Many-to-Many relationship. THE ORDER IS NOT NECESSARILY PRESERVED!!!
        self.variant_query.query_results.add(*smallvariant_pks)

    def _prioritize_gene_phenotype(self, results):
        """Prioritize genes in ``results`` and store in ``SmallVariantQueryGeneScores``."""

        if not settings.VARFISH_ENABLE_EXOMISER_PRIORITISER and not settings.VARFISH_ENABLE_CADA:
             return

        prio_enabled = self.variant_query.query_settings.get("prio_enabled")
        prio_algorithm = self.variant_query.query_settings.get("prio_algorithm")
        hpo_terms = tuple(
            sorted(self.variant_query.query_settings.get("prio_hpo_terms_curated", []) or [])
        )
        entrez_ids = tuple(
            sorted(set(map(str, [row["entrez_id"] for row in results if row["entrez_id"]])))[
                : settings.VARFISH_EXOMISER_PRIORITISER_MAX_GENES
            ]
        )
        if not all((prio_enabled, prio_algorithm, hpo_terms, entrez_ids)):
            return  # nothing to do

        entrez_ids = [row["entrez_id"] for row in results if row["entrez_id"]]
        try:
            for gene_id, gene_symbol, score, priority_type in prioritize_genes(
                self, entrez_ids, hpo_terms, prio_algorithm
            ):
                self.variant_query.smallvariantquerygenescores_set.create(
                    gene_id=gene_id,
                    gene_symbol=gene_symbol,
                    score=score,
                    priority_type=priority_type,
                )
        except ConnectionError as e:
            self.job.add_log_entry(e)

    def _prioritize_variant_pathogenicity(self, results):
        """Prioritize genes in ``results`` and store in ``SmallVariantQueryVariantScores``."""
        patho_enabled = self.variant_query.query_settings.get("patho_enabled")
        patho_score = self.variant_query.query_settings.get("patho_score")

        def get_var(row):
            """Extract tuple describing variant from row."""
            return (row["chromosome"], row["start"], row["reference"], row["alternative"])

        variants = tuple(sorted(set(map(get_var, results))))

        if not all((patho_enabled, patho_score, variants)):
            return  # nothing to do

        name = PATHO_SCORES_MAPPING.get(patho_score)
        self.job.add_log_entry("Prioritize variant pathogenicity with {} ...".format(name))

        try:
            with transaction.atomic():
                scorer_factory = VariantScoresFactory()
                scorer = scorer_factory.get_scorer(
                    self._get_genomebuild(), patho_score, variants, self.job.bg_job.user
                )
                for score in scorer.score():
                    getattr(
                        self.variant_query, "%svariantscores_set" % self.variant_query.query_type()
                    ).create(**score),
        except ConnectionError as e:
            self.job.add_log_entry(e)


class CaseFilter(FilterBase):
    """Class for storing query results for a single case.
    """

    def _get_genomebuild(self):
        return self.variant_query.case.release

    def _get_assembled_query(self):
        """Render filter query for a single case"""
        return CasePrefetchQuery(self.variant_query.case, self.get_alchemy_engine())


class ProjectCasesFilter(FilterBase):
    """Class for storing query results for cases of a project.
    """

    def _get_genomebuild(self):
        if self.job.cohort:
            cases = [
                case for case in self.job.cohort.get_accessible_cases_for_user(self.job.bg_job.user)
            ]
        else:
            cases = [case for case in self.variant_query.project.case_set.all()]
        if cases:
            return cases[0].release
        else:
            return "GRCh37"

    def _get_assembled_query(self):
        """Render filter query for a project"""
        return ProjectPrefetchQuery(
            self.job.cohort or self.variant_query.project,
            self.get_alchemy_engine(),
            user=self.job.bg_job.user,
        )


def case_filter(job):
    """Execute query for a single case and store the results."""
    job.mark_start()

    timeline = get_backend_api("timeline_backend")
    tl_event = None

    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="case_filter",
            description="run filter query and store results for case {case_name}",
            status_type="INIT",
        )
        tl_event.add_object(obj=job.case, label="case_name", name=job.case.name)
    try:
        # Get and run query
        CaseFilter(job, job.smallvariantquery).run()
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status(
                "FAILED", "Filtering and storing query results failed for case {case_name}"
            )
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status(
                "OK", "Filtering and storing query results complete for case {case_name}"
            )


def project_cases_filter(job):
    """Store the results of a query."""

    job.mark_start()

    timeline = get_backend_api("timeline_backend")
    tl_event = None

    if timeline:
        tl_event = timeline.add_event(
            project=job.project,
            app_name="variants",
            user=job.bg_job.user,
            event_name="project_cases_filter",
            description="run filter query and store results for project",
            status_type="INIT",
        )
    try:
        # Get and run query
        ProjectCasesFilter(job, job.projectcasessmallvariantquery).run()
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status(
                "FAILED", "Filtering and storing query results failed for case {case_name}"
            )
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status(
                "OK", "Filtering and storing query results complete for case {case_name}"
            )
