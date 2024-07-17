"""Models and related code for execution SmallVariant query jobs."""

from datetime import datetime, timedelta
from decimal import Decimal
from itertools import islice
import json
import traceback

from bgjobs.models import BackgroundJob
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from projectroles.plugins import get_backend_api
from sqlalchemy import and_

from ext_gestaltmatcher.models import (
    SmallVariantQueryGestaltMatcherScores,
    SmallVariantQueryPediaScores,
)
from variants.helpers import get_engine, get_meta
from variants.models import SmallVariantQueryGeneScores, SmallVariantQueryVariantScores
from variants.models.queries import (
    FilterBgJob,
    SmallVariantQuery,
    SmallVariantQueryResultRow,
    SmallVariantQueryResultSet,
)
from variants.models.variants import SmallVariantSet
from variants.queries import CaseLoadPrefetchedQuery
from variants.submit_filter import CaseFilter

User = get_user_model()


def batched(iterable, n):
    """Batch data into lists of length n. The last batch may be shorter."""
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    batch = list(islice(it, n))
    while batch:
        yield batch
        batch = list(islice(it, n))


def create_query_bg_job(case, svquery, user):
    """Create a new ``FilterBgJob`` for an existing ``SvQuery``."""
    with transaction.atomic():
        return FilterBgJob.objects.create(
            bg_job=BackgroundJob.objects.create(
                name="SV Query for case %s" % case.name,
                project=case.project,
                job_type=FilterBgJob.spec_name,
                user=user,
            ),
            case=case,
            project=case.project,
            svquery=svquery,
        )


SMALLVARIANT_RECORDS_HEADER = (
    "release",
    "chromosome",
    "chromosome_no",
    "bin",
    "start",
    "end",
    "genotype",
)


class RowEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


def run_query_bg_job(pk):
    """Execute a query for SVs."""
    filter_job = FilterBgJob.objects.select_related("case", "smallvariantquery").get(id=pk)
    filter_job.bg_job.status = "running"
    filter_job.bg_job.save()
    query_model = filter_job.smallvariantquery
    query_model.query_state = SmallVariantQuery.QueryState.RUNNING
    query_model.save()

    timeline = get_backend_api("timeline_backend")
    tl_event = None

    if timeline:
        tl_event = timeline.add_event(
            project=filter_job.project,
            app_name="variants",
            user=filter_job.bg_job.user,
            event_name="case_filter",
            description="run filter query and store results for case {case_name}",
            status_type="INIT",
        )
        tl_event.add_object(obj=filter_job.case, label="case_name", name=filter_job.case.name)

    def _read_records(
        inputf,
        smallvariantqueryresultset,
        pathogenicity_scores=None,
        phenotype_scores=None,
        gm_scores=None,
        pedia_scores=None,
    ):
        """Read and yield ``SmallVariantQueryResultRow`` objects by reading ``inputf`` for the given ``SmallVariantQueryResultSet``."""
        for line in inputf:
            payload = dict(line)
            del payload["id"]

            if pathogenicity_scores:
                payload["pathogenicity_score"] = pathogenicity_scores.get(
                    (line.chromosome, line.start, line.reference, line.alternative), -1
                )

            if phenotype_scores and line.entrez_id:
                payload["phenotype_score"] = phenotype_scores.get(line.entrez_id, -1)

            if gm_scores and line.entrez_id:
                payload["gm_score"] = gm_scores.get(line.entrez_id, 0)

            if pedia_scores and line.entrez_id:
                payload["pedia_score"] = pedia_scores.get(line.entrez_id, -1)

            if pathogenicity_scores and phenotype_scores and line.entrez_id:
                if payload["pathogenicity_score"] == -1 or payload["phenotype_score"] == -1:
                    payload["patho_pheno_score"] = -1
                else:
                    payload["patho_pheno_score"] = (
                        payload["pathogenicity_score"] * payload["phenotype_score"]
                    )

            yield SmallVariantQueryResultRow(
                smallvariantqueryresultset=smallvariantqueryresultset,
                release=line.release,
                chromosome=line.chromosome,
                chromosome_no=line.chromosome_no,
                bin=line.bin,
                start=line.start,
                end=line.end,
                reference=line.reference,
                alternative=line.alternative,
                payload=json.loads(json.dumps(payload, cls=RowEncoder)),
            )

    def _inner():
        """Actual implementation moved into function so we can easily wrap this into try/catch"""
        filter_job.add_log_entry("Starting SmallVariant database query")
        start_time = timezone.now()

        CaseFilter(filter_job, query_model).run()

        end_time = timezone.now()
        filter_job.add_log_entry("... done running the worker")

        #: Create the new query result set, insert the data from the files that the worker wrote into the set.
        filter_job.add_log_entry("Create result set and import worker results ...")

        pathogenicity_scores = None
        if query_model.query_settings.get("patho_enabled"):
            pathogenicity_scores = {
                (row.chromosome, row.start, row.reference, row.alternative): row.score
                for row in SmallVariantQueryVariantScores.objects.filter(
                    query__sodar_uuid=query_model.sodar_uuid
                )
            }
        phenotype_scores = None
        if query_model.query_settings.get("prio_enabled"):
            phenotype_scores = {
                row.gene_id: row.score
                for row in SmallVariantQueryGeneScores.objects.filter(
                    query__sodar_uuid=query_model.sodar_uuid
                )
                if row.gene_id
            }
        gm_scores = None
        pedia_scores = None
        if query_model.query_settings.get("gm_enabled"):
            gm_scores = {
                row.gene_id: row.score
                for row in SmallVariantQueryGestaltMatcherScores.objects.filter(
                    query__sodar_uuid=query_model.sodar_uuid
                )
                if row.gene_id
            }
        if query_model.query_settings.get("pedia_enabled"):
            pedia_scores = {
                row.gene_id: row.score
                for row in SmallVariantQueryPediaScores.objects.filter(
                    query__sodar_uuid=query_model.sodar_uuid
                )
                if row.gene_id
            }

        with transaction.atomic():
            smallvariantqueryresultset = SmallVariantQueryResultSet.objects.create(
                case=query_model.case,
                smallvariantquery=query_model,
                result_row_count=query_model.query_results.count(),
                start_time=start_time,
                end_time=end_time,
                elapsed_seconds=(end_time - start_time).total_seconds(),
            )

            for batch in batched(
                _read_records(
                    CaseLoadPrefetchedQuery(query_model.case, get_engine(), query_model.id).run(
                        query_model.query_settings
                    ),
                    smallvariantqueryresultset,
                    pathogenicity_scores=pathogenicity_scores,
                    phenotype_scores=phenotype_scores,
                    gm_scores=gm_scores,
                    pedia_scores=pedia_scores,
                ),
                n=1000,
            ):
                SmallVariantQueryResultRow.objects.bulk_create(batch)
        filter_job.add_log_entry("... done creating result set and importing worker results")

    try:
        with filter_job.marks():
            _inner()

    except Exception as e:  # generic failure
        query_model.query_state = SmallVariantQuery.QueryState.FAILED
        query_model.query_state_msg = str(e)
        query_model.save()
        print(traceback.format_exc())

    else:
        filter_job.bg_job.status = "done"
        filter_job.bg_job.save()
        query_model.query_state = SmallVariantQuery.QueryState.DONE
        query_model.save()


def cleanup_variant_sets(min_age_hours=12):
    """Cleanup old variant sets."""
    variant_sets = list(
        SmallVariantSet.objects.filter(
            date_created__lte=datetime.now() - timedelta(hours=min_age_hours)
        ).exclude(state="active")
    )
    table_names = ("variants_smallvariant", "variants_smallvariantgeneannotation")
    for variant_set in variant_sets:
        for table_name in table_names:
            table = get_meta().tables[table_name]
            get_engine().execute(
                table.delete().where(
                    and_(table.c.set_id == variant_set.id, table.c.case_id == variant_set.case.id)
                )
            )
        variant_set.delete()
