from projectroles.plugins import get_backend_api
from variants.file_export import SQLALCHEMY_ENGINE
from .models_support import PrefetchFilterQuery, ProjectCasesPrefetchFilterQuery


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
        self._alchemy_connection = None
        #: Is set in inherited classes
        self.assembled_query = self._get_assembled_query()

    def _get_assembled_query(self):
        """Override me!"""
        pass

    def get_alchemy_connection(self):
        """Construct and return the alchemy connection."""
        if not self._alchemy_connection:
            self._alchemy_connection = SQLALCHEMY_ENGINE.connect()
        return self._alchemy_connection

    def run(self, kwargs={}):
        """Run filter query"""
        # Patch query args, if available
        _query_args = {**self.variant_query.query_settings, **kwargs}
        # Run query
        results = self.assembled_query.run(_query_args)
        # Obtain smallvariant ids to store them in ManyToMany field
        smallvariant_pks = [row["id"] for row in results]
        # Delete previously stored results (note: this only disassociates them, it doesn't delete objects itself.)
        self.variant_query.query_results.clear()
        # Bulk-insert Many-to-Many relationship
        self.variant_query.query_results.add(*smallvariant_pks)


class CaseFilter(FilterBase):
    """Class for storing query results for a single case.
    """

    def _get_assembled_query(self):
        """Render filter query for a single case"""
        return PrefetchFilterQuery(self.variant_query.case, self.get_alchemy_connection())


class ProjectCasesFilter(FilterBase):
    """Class for storing query results for cases of a project.
    """

    def _get_assembled_query(self):
        """Render filter query for a project"""
        return ProjectCasesPrefetchFilterQuery(
            self.variant_query.project, self.get_alchemy_connection()
        )


def case_filter(job):
    """Store the results of a query."""

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
