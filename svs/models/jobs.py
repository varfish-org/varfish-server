"""Models and related code for execution SV query jobs."""
from datetime import datetime, timedelta
from itertools import islice
import json
import os
import subprocess
from tempfile import TemporaryDirectory
import traceback
import uuid
import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from projectroles.models import Project
from sqlalchemy import and_

from svs.models.queries import SvQuery, SvQueryResultRow, SvQueryResultSet
from svs.models.records import StructuralVariant, StructuralVariantSet
from variants.helpers import get_engine, get_meta
from variants.models import Case

User = get_user_model()


class FilterSvBgJob(JobModelMessageMixin, models.Model):
    """Background job for structural variant query to a single case."""

    #: Task description for logging.
    task_desc = "Run single case filter query for structural variants and store results"

    #: String identifying model in BackgroundJob.
    spec_name = "svs.filter_bg_job"

    #: Query UUID.
    sodar_uuid = models.UUIDField(default=uuid_object.uuid4, unique=True, help_text="Record UUID")
    #: DateTime of record creation.
    date_created = models.DateTimeField(auto_now_add=True, help_text="DateTime of creation")
    #: DateTime of record modification.
    date_modified = models.DateTimeField(auto_now_add=True, help_text="DateTime of modification")

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, help_text="Project in which this objects belongs"
    )

    bg_job = models.ForeignKey(
        BackgroundJob,
        null=False,
        help_text="Background job for filtering and storing query results",
        on_delete=models.CASCADE,
    )

    case = models.ForeignKey(
        Case, on_delete=models.CASCADE, null=False, help_text="The case to filter"
    )

    #: Link to the SvQuery record. Holds query arguments and results
    svquery = models.ForeignKey(
        SvQuery, on_delete=models.CASCADE, null=False, help_text="SV query to be executed"
    )


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


def create_sv_query_bg_job(case, svquery, user):
    """Create a new ``FilterBgJob`` for an existing ``SvQuery``."""
    with transaction.atomic():
        return FilterSvBgJob.objects.create(
            bg_job=BackgroundJob.objects.create(
                name="SV Query for case %s" % case.name,
                project=case.project,
                job_type=FilterSvBgJob.spec_name,
                user=user,
            ),
            case=case,
            project=case.project,
            svquery=svquery,
        )


SV_RECORDS_HEADER = (
    "release",
    "chromosome",
    "chromosome_no",
    "bin",
    "start",
    "caller",
    "sv_type",
    "sv_sub_type",
    "chromosome2",
    "chromosome_no2",
    "bin2",
    "end",
    "pe_orientation",
    "genotype",
)


def run_sv_query_bg_job(pk):
    """Execute a query for SVs."""
    filter_job = FilterSvBgJob.objects.select_related("case", "svquery").get(id=pk)
    filter_job.bg_job.status = "running"
    filter_job.bg_job.save()
    query_model = filter_job.svquery
    query_model.query_state = SvQuery.QueryState.RUNNING
    query_model.save()

    def _read_records(inputf, svqueryresultset):
        """Read and yield ``SvQueryResultRow`` objects by reading ``inputf`` for the given ``SvQueryResultSet``."""
        header = None
        for line in inputf:
            arr = line.strip().split("\t")
            if not header:
                header = arr
            else:
                raw = dict(zip(header, arr))
                yield SvQueryResultRow(
                    sodar_uuid=uuid.UUID(raw["sodar_uuid"]),
                    svqueryresultset=svqueryresultset,
                    release=raw["release"],
                    chromosome=raw["chromosome"],
                    chromosome_no=int(raw["chromosome_no"]),
                    bin=int(raw["bin"]),
                    chromosome2=raw["chromosome2"],
                    chromosome_no2=int(raw["chromosome_no2"]),
                    bin2=int(raw["bin2"]),
                    start=int(raw["start"]),
                    end=int(raw["end"]),
                    pe_orientation=raw["pe_orientation"],
                    sv_type=raw["sv_type"],
                    sv_sub_type=raw["sv_sub_type"],
                    payload=json.loads(raw["payload"]),
                )

    def _inner(tmpdir):
        """Actual implementation moved into function so we can easily wrap this into try/catch"""
        filter_job.add_log_entry("Starting SV database query")

        #: Dump the SVs to a TSV file for processing by the worker
        filter_job.add_log_entry("Dumping SVs and query to temporary files ...")
        with open(os.path.join(tmpdir, "query.json"), "wt") as outputf:
            # Replace empty value strings by None, works around issue with "" rather
            # than numbers.
            query_settings = {
                key: None if value == "" else value
                for key, value in query_model.query_settings.items()
            }
            print(json.dumps(query_settings), file=outputf)
        with open(os.path.join(tmpdir, "input.tsv"), "wt") as outputf:
            print(
                "\t".join(SV_RECORDS_HEADER),
                file=outputf,
            )
            case_id = filter_job.case.id
            variant_set_id = filter_job.case.latest_structural_variant_set_id
            for record in StructuralVariant.objects.filter(case_id=case_id, set_id=variant_set_id):
                arr = (
                    record.release,
                    record.chromosome,
                    str(record.chromosome_no),
                    str(record.bin),
                    str(record.start),
                    record.caller,
                    record.sv_type,
                    record.sv_sub_type or record.sv_type,
                    record.chromosome2 or record.chromosome,
                    str(record.chromosome_no2 or record.chromosome_no),
                    str(record.bin2 or record.bin),
                    str(record.end),
                    record.pe_orientation or "NtoN",
                    json.dumps(record.genotype),
                )
                print("\t".join(arr), file=outputf)
        filter_job.add_log_entry("... done dumping the SVs and query")

        #: Actually run the worker
        filter_job.add_log_entry("Run the worker on the SVs ...")
        start_time = timezone.now()
        cmd = [
            settings.WORKER_EXE_PATH,
            "sv",
            "query",
            "--path-db",
            settings.WORKER_DB_PATH,
            "--path-query-json",
            os.path.join(tmpdir, "query.json"),
            "--path-input-svs",
            os.path.join(tmpdir, "input.tsv"),
            "--path-output-svs",
            os.path.join(tmpdir, "output.tsv"),
            "--genome-release",
            filter_job.case.release.lower(),
        ]
        subprocess.check_call(cmd)
        worker_results = os.path.join(tmpdir, "output.tsv")
        with open(worker_results, "rt") as inputf:
            result_row_count = sum(1 for _line in inputf) - 1
            result_row_count = max(0, result_row_count)
        end_time = timezone.now()
        filter_job.add_log_entry("... done running the worker")

        #: Create the new query result set, insert the data from the files that the worker wrote into the set.
        filter_job.add_log_entry("Create result set and import worker results ...")
        with transaction.atomic():
            svqueryresultset = SvQueryResultSet.objects.create(
                case=query_model.case,
                svquery=query_model,
                result_row_count=result_row_count,
                start_time=start_time,
                end_time=end_time,
                elapsed_seconds=(end_time - start_time).total_seconds(),
            )
            with open(worker_results, "rt") as inputf:
                for batch in batched(_read_records(inputf, svqueryresultset), n=1000):
                    SvQueryResultRow.objects.bulk_create(batch)
        filter_job.add_log_entry("... done creating result set and importing worker results")

    try:
        with TemporaryDirectory() as tmpdir:
            with filter_job.marks():
                _inner(tmpdir)
    except Exception as e:  # generic failure
        query_model.query_state = SvQuery.QueryState.FAILED
        query_model.query_state_msg = str(e)
        query_model.save()
        print(traceback.format_exc())
    else:
        filter_job.bg_job.status = "done"
        filter_job.bg_job.save()
        query_model.query_state = SvQuery.QueryState.DONE
        query_model.save()


def cleanup_variant_sets(min_age_hours=12):
    """Cleanup old variant sets."""
    variant_sets = list(
        StructuralVariantSet.objects.filter(
            date_created__lte=datetime.now() - timedelta(hours=min_age_hours)
        ).exclude(state="active")
    )
    table_names = ("svs_structuralvariant", "svs_structuralvariantgeneannotation")
    for variant_set in variant_sets:
        for table_name in table_names:
            table = get_meta().tables[table_name]
            get_engine().execute(
                table.delete().where(
                    and_(table.c.set_id == variant_set.id, table.c.case_id == variant_set.case.id)
                )
            )
        variant_set.delete()
