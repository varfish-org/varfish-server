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
    query_args = json.loads(job.query_args)
    query_runner = FilterQueryRunner(
        job.case, query_args, include_conservation=True
    )
    # Get names of selected pedigree members.
    members = [
        m["patient"]
        for m in query_runner.pedigree
        if query_args.get('%s_export' % m["patient"], False)
    ]
    header_ext = []
    for member in members:
        for key in ("gt", "gq", "ad", "dp", "aaf"):
            header_ext.append("%s.%s" % (member, key))
    # Generate output
    header = HEADER_FIXED + header_ext
    tmp_file.write(line(header).encode())
    prev_chrom = None
    job.add_log_entry("Executing database query...")
    result = query_runner.run()
    job.add_log_entry("Writing output file...")
    for small_var in result:
        if small_var.chromosome != prev_chrom:
            job.add_log_entry("Now on chromosome chr{}".format(small_var.chromosome))
            prev_chrom = small_var.chromosome
        # Build first, fixed-number columns.
        row = [getattr(small_var, name) for name in HEADER_FIXED]
        row[0] = "chr" + row[0]
        # Add further, dynamic columns.
        for header in header_ext:
            member, field = header.rsplit('.', 1)
            if field == 'aaf':
                ad = small_var.ad.get(member, 0)
                dp = small_var.dp.get(member, 0)
                if dp == 0:
                    aaf = 0.0
                else:
                    aaf = ad / dp
                row.append(str(aaf))
            else:
                row.append(to_str(getattr(small_var, field, {}).get(member, '.')))
        # Write row to output.
        tmp_file.write(line(row).encode())
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
