"""This module contains the code for file export"""

import json

from datetime import timedelta
from tempfile import TemporaryFile

from django.utils import timezone

from .models import ExportFileJobResult
from .views import FilterQueryRunner

#: Constant that determines how many days generated files should stay.  Note for the actual removal, a separate
#: Celery job must be ran.
EXPIRY_DAYS = 14


def export_case_xlsx(job):
    """Export a ``Case`` to a temporary file.

    Returns rewound temporary file stream.
    """
    tmp_file = TemporaryFile()
    job.add_log_entry("Writing to XLSX file...")
    tmp_file.write("Foo".encode())
    tmp_file.seek(0)
    return tmp_file


def to_str(val):
    if val is None:
        return "."
    elif isinstance(val, set):
        return ";".join(sorted(map(to_str, val)))
    elif isinstance(val, list):
        return ";".join(map(to_str, val))
    else:
        return str(val)


def line(arr):
    return "\t".join(map(to_str, arr)) + "\n"


#: Names of the fixed header columns.
HEADER_FIXED = [
    "chromosome",
    "position",
    "reference",
    "alternative",
    "var_type",
    "rsid",
    "in_clinvar",
    "exac_frequency",
    "gnomad_exomes_frequency",
    "gnomad_genomes_frequency",
    "thousand_genomes_frequency",
    "exac_homozygous",
    "gnomad_exomes_homozygous",
    "gnomad_genomes_homozygous",
    "thousand_genomes_homozygous",
    "symbol",
    "gene_id",
    "effect",
    "hgvs_p",
    "hgvs_c",
    "known_gene_aa",
]


def export_case_tsv(job):
    """Export a ``Case`` to a temporary file.

    Returns rewound temporary file stream.
    """
    tmp_file = TemporaryFile()
    job.add_log_entry("Writing to TSV file...")
    query_runner = FilterQueryRunner(
        job.case, json.loads(job.query_args), include_conservation=True
    )
    header = HEADER_FIXED
    tmp_file.write(line(header).encode())
    prev_chrom = None
    for small_var in query_runner.run():
        if small_var.chromosome != prev_chrom:
            job.add_log_entry("Now on chromosome chr{}".format(small_var.chromosome))
            prev_chrom = small_var.chromosome
        # Build first, fixed-number columns.
        row = [getattr(small_var, name) for name in HEADER_FIXED]
        row[0] = "chr" + row[0]
        row += [str(small_var.gt)]
        # Add further, dynamic columns.
        tmp_file.write(line(row).encode())
        # gt
        # gq
        # var
        # dp
    tmp_file.seek(0)
    return tmp_file


def export_case(job):
    """Export a ``Case`` object, store result in a new ``ExportFileJobResult``."""
    job.mark_start()
    try:
        if job.file_type == "xlsx":
            tmp_file = export_case_xlsx(job)
        else:
            tmp_file = export_case_tsv(job)
        ExportFileJobResult.objects.create(
            job=job,
            expiry_time=timezone.now() + timedelta(days=EXPIRY_DAYS),
            payload=tmp_file.read(),
        )
    except Exception as e:
        job.mark_error(e)
        raise
    else:
        job.mark_success()
