"""Models and related code for execution SV query jobs."""

from datetime import datetime, timedelta
from itertools import islice
import json
import os
import subprocess
from tempfile import TemporaryDirectory
import traceback
from typing import Dict, List
import uuid
import uuid as uuid_object

from bgjobs.models import BackgroundJob, JobModelMessageMixin
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils import timezone
from projectroles.models import Project
from pydantic import BaseModel
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


class Contig(BaseModel):
    """A genome contig."""

    name: str
    length: int


CONTIGS_GRCH38: Dict[str, Contig] = {
    "1": Contig(name="chr1", length=248956422),
    "2": Contig(name="chr2", length=242193529),
    "3": Contig(name="chr3", length=198295559),
    "4": Contig(name="chr4", length=190214555),
    "5": Contig(name="chr5", length=181538259),
    "6": Contig(name="chr6", length=170805979),
    "7": Contig(name="chr7", length=159345973),
    "8": Contig(name="chr8", length=145138636),
    "9": Contig(name="chr9", length=138394717),
    "10": Contig(name="chr10", length=133797422),
    "11": Contig(name="chr11", length=135086622),
    "12": Contig(name="chr12", length=133275309),
    "13": Contig(name="chr13", length=114364328),
    "14": Contig(name="chr14", length=107043718),
    "15": Contig(name="chr15", length=101991189),
    "16": Contig(name="chr16", length=90338345),
    "17": Contig(name="chr17", length=83257441),
    "18": Contig(name="chr18", length=80373285),
    "19": Contig(name="chr19", length=58617616),
    "20": Contig(name="chr20", length=64444167),
    "21": Contig(name="chr21", length=46709983),
    "22": Contig(name="chr22", length=50818468),
    "X": Contig(name="chrX", length=156040895),
    "Y": Contig(name="chrY", length=57227415),
    "M": Contig(name="chrM", length=16569),
}

CONTIGS_GRCH37: Dict[str, Contig] = {
    "1": Contig(name="1", length=249250621),
    "2": Contig(name="2", length=243199373),
    "3": Contig(name="3", length=198022430),
    "4": Contig(name="4", length=191154276),
    "5": Contig(name="5", length=180915260),
    "6": Contig(name="6", length=171115067),
    "7": Contig(name="7", length=159138663),
    "8": Contig(name="8", length=146364022),
    "9": Contig(name="9", length=141213431),
    "10": Contig(name="10", length=135534747),
    "11": Contig(name="11", length=135006516),
    "12": Contig(name="12", length=133851895),
    "13": Contig(name="13", length=115169878),
    "14": Contig(name="14", length=107349540),
    "15": Contig(name="15", length=102531392),
    "16": Contig(name="16", length=90354753),
    "17": Contig(name="17", length=81195210),
    "18": Contig(name="18", length=78077248),
    "19": Contig(name="19", length=59128983),
    "20": Contig(name="20", length=63025520),
    "21": Contig(name="21", length=48129895),
    "22": Contig(name="22", length=51304566),
    "X": Contig(name="X", length=155270560),
    "Y": Contig(name="Y", length=59373566),
    "M": Contig(name="MT", length=16569),
}

CONTIGS: Dict[str, Dict[str, Contig]] = {
    "GRCh37": CONTIGS_GRCH37,
    "GRCh38": CONTIGS_GRCH38,
}


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


def _write_header(outputf, case, callers):
    """Write out header to to the given output file for the given release."""
    worker_version = (
        subprocess.check_output([settings.WORKER_EXE_PATH, "--version"])
        .decode("utf-8")
        .split()[-1]
        .strip()
    )
    print(worker_version)

    sample_lines = []
    for entry in case.pedigree:
        sex = {
            1: "Male",
            2: "Female",
        }.get("sex", "Unknown")
        disease = {
            1: "Unaffected",
            2: "Affected",
        }.get("disease", "Unknown")
        sample_lines.append(f"##SAMPLE=<ID={entry['patient']},Sex={sex},Disease={disease}>")

    pedigree_lines = []
    for entry in case.pedigree:
        if entry.get("father", "0") != "0":
            father = f",Father={entry['father']}"
        else:
            father = ""
        if entry.get("mother", "0") != "0":
            mother = f",Mother={entry['mother']}"
        else:
            mother = ""
        pedigree_lines.append(f"##PEDIGREE=<ID={entry['patient']}{father}{mother}>")

    caller_lines = []
    for caller in callers:
        name, version = caller.split("v")
        caller_lines.append(
            f'##x-varfish-version=<ID=orig-caller-{name},Name="{name}",Version="{version}">'
        )

    print(
        "\n".join(
            [
                "##fileformat=VCFv4.4",
                "##fileDate=%s" % datetime.today().strftime("%Y%m%d"),
                '##INFO=<ID=IMPRECISE,Number=0,Type=Flag,Description="Imprecise structural variation">',
                '##INFO=<ID=END,Number=1,Type=Integer,Description="End position of the longest variant described in this record">',
                '##INFO=<ID=SVTYPE,Number=1,Type=String,Description="Type of structural variant">',
                '##INFO=<ID=SVLEN,Number=A,Type=Integer,Description="Length of structural variant">',
                '##INFO=<ID=SVCLAIM,Number=A,Type=String,Description="Claim made by the structural variant call. Valid values are D, J, DJ for abundance, adjacency and both respectively">',
                '##INFO=<ID=callers,Number=.,Type=String,Description="Callers that called the variant">',
                '##INFO=<ID=chr2,Number=1,Type=String,Description="Second chromosome, if not equal to CHROM">',
                "##INFO=<ID=annsv,Number=1,Type=String,Description=\"Effect annotations: 'Allele | Annotation | Gene_Name | Gene_ID'\">",
                '##FILTER=<ID=PASS,Description="All filters passed">',
                '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Conditional genotype quality">',
                '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">',
                '##FORMAT=<ID=pec,Number=1,Type=Integer,Description="Total coverage with paired-end reads">',
                '##FORMAT=<ID=pev,Number=1,Type=Integer,Description="Paired-end reads supporting the variant">',
                '##FORMAT=<ID=src,Number=1,Type=Integer,Description="Total coverage with split reads">',
                '##FORMAT=<ID=srv,Number=1,Type=Integer,Description="Split reads supporting the variant">',
                '##FORMAT=<ID=amq,Number=1,Type=Float,Description="Average mapping quality over the variant">',
                '##FORMAT=<ID=cn,Number=1,Type=Integer,Description="Copy number of the variant in the sample">',
                '##FORMAT=<ID=anc,Number=1,Type=Float,Description="Average normalized coverage over the variant in the sample">',
                '##FORMAT=<ID=pc,Number=1,Type=Integer,Description="Point count (windows/targets/probes)">',
                '##ALT=<ID=DEL,Description="Deletion">',
                '##ALT=<ID=DUP,Description="Duplication">',
                '##ALT=<ID=INS,Description="Insertion">',
                '##ALT=<ID=CNV,Description="Copy Number Variation">',
                '##ALT=<ID=INV,Description="Inversion">',
            ]
            + [
                f'##contig=<ID={contig.name},length={contig.length},assembly="{case.release}",species="Homo sapiens">'
                for contig in CONTIGS[case.release].values()
            ]
            + sample_lines
            + pedigree_lines
            + [
                f"##x-varfish-genome-build={case.release}",
                f"##x-varfish-case-uuid={case.sodar_uuid}",
                f'##x-varfish-version=<ID=varfish-server-worker,Version="{worker_version}">',
            ]
            + caller_lines
            + [
                "\t".join(
                    ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"]
                    + [member["patient"] for member in case.pedigree]
                )
            ]
        ),
        file=outputf,
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

        # Mapping of key from database JSON keys to VCF format keys.
        format_db_to_vcf = {
            "gq": "GQ",
            "gt": "GT",
            "pec": "pec",
            "pev": "pev",
            "src": "src",
            "srv": "srv",
            "amq": "amq",
            "cn": "cn",
            "anc": "anc",
            "pc": "pc",
        }

        # Dump the SVs to a TSV file for processing by the worker
        filter_job.add_log_entry("Dumping SVs and query to temporary files ...")
        with open(os.path.join(tmpdir, "query.json"), "wt") as outputf:
            # Replace empty value strings by None, works around issue with empty string
            # rather than numbers.
            query_settings = {
                key: None if value == "" else value
                for key, value in query_model.query_settings.items()
            }
            print(json.dumps(query_settings), file=outputf)

        samples = [member["patient"] for member in filter_job.case.pedigree]

        with open(os.path.join(tmpdir, "input.vcf"), "wt") as outputf:
            case_id = filter_job.case.id
            variant_set_id = filter_job.case.latest_structural_variant_set_id
            records = StructuralVariant.objects.filter(case_id=case_id, set_id=variant_set_id)
            callers = set()
            for record in records:
                for caller in record.caller.split(";"):
                    callers.add(caller)

            _write_header(outputf, filter_job.case, list(sorted(callers)))
            for record in records:
                keys_in_row = set()
                for gt in record.genotype.values():
                    keys_in_row.update(gt.keys())
                keys_in_row = ["gt"] + [
                    x for x in sorted(keys_in_row & set(format_db_to_vcf.keys())) if x != "gt"
                ]

                info = f"SVTYPE={record.sv_type};END={record.end};callers={record.caller.replace(';', ',')}"
                if record.sv_type == "DEL":
                    info = f"{info};SVLEN={record.end - record.start};SVCLAIM=DJ"
                    alt = "<DEL>"
                elif record.sv_type == "DUP":
                    info = f"{info};SVLEN={record.end - record.start};SVCLAIM=DJ"
                    alt = "<DUP>"
                elif record.sv_type == "INV":
                    info = f"{info};SVLEN={record.end - record.start};SVCLAIM=J"
                    alt = "<INV>"
                elif record.sv_type == "INS":
                    info = f"{info};SVLEN={record.end - record.start};SVCLAIM=J"
                    alt = "<INS>"
                elif record.sv_type == "CNV":
                    info = f"{info};SVLEN={record.end - record.start};SVCLAIM=D"
                    alt = "<CNV>"
                elif record.sv_type == "BND":
                    info = f"{info};chr2={record.chromosome2};SVCLAIM=J"
                    pe_orientation = record.pe_orientation or "NtoN"
                    if pe_orientation == "3to3":
                        alt = f"[{record.chromosome2}:{record.end}[N"
                    elif pe_orientation == "5to5":
                        alt = f"N]{record.chromosome2}:{record.end}]"
                    elif pe_orientation == "3to5" or pe_orientation == "NtoN":
                        alt = f"]{record.chromosome2}:{record.end}]N"
                    elif pe_orientation == "5to3":
                        alt = f"N[{record.chromosome2}:{record.end}["
                    else:
                        raise ValueError(f"Unexpected PE orientation: {pe_orientation}")
                else:
                    raise ValueError(f"Unexpected SV type: {record.sv_type}")

                arr = [
                    record.chromosome,
                    record.start,
                    ".",
                    "N",
                    alt,
                    ".",
                    ".",
                    info,
                    ":".join([format_db_to_vcf[key] for key in keys_in_row]),
                ] + [
                    ":".join([str(record.genotype[sample].get(key, ".")) for key in keys_in_row])
                    for sample in samples
                ]
                print("\t".join(map(str, arr)), file=outputf)
        with open(os.path.join(tmpdir, "input.vcf"), "rt") as inputf:
            data = inputf.read()
            print(data)
            with open("/tmp/x.vcf", "wt") as outputf:
                outputf.write(data)
        filter_job.add_log_entry("... done dumping the SVs and query")

        #: Actually run the worker
        filter_job.add_log_entry("Run the worker on the SVs ...")
        start_time = timezone.now()
        cmd = [
            settings.WORKER_EXE_PATH,
            "-vvv",
            "strucvars",
            "query",
            "--path-db",
            settings.WORKER_DB_PATH,
            "--path-query-json",
            os.path.join(tmpdir, "query.json"),
            "--path-input",
            os.path.join(tmpdir, "input.vcf"),
            "--path-output",
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
