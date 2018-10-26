"""This module contains the code for file export"""

import json

from datetime import timedelta
from tempfile import TemporaryFile

from django.utils import timezone

from .models import ExportFileJobResult

#: Constant that determines how many days generated files should stay.  Note for the actual removal, a separate
#: Celery job must be ran.
EXPIRY_DAYS = 14


def export_case_xlsx(case, job):
    """Export a ``Case`` to a temporary file.

    Returns rewound temporary file stream.
    """
    tmp_file = TemporaryFile()
    pedigree = json.loads(case.pedigree)
    samples = [entry["patient"] for entry in pedigree]
    job.add_log_entry("Writing to XLSX file...")
    tmp_file.write("Foo".encode())
    tmp_file.seek(0)
    return tmp_file


def export_case_tsv(case, job):
    """Export a ``Case`` to a temporary file.

    Returns rewound temporary file stream.
    """
    tmp_file = TemporaryFile()
    job.add_log_entry("Writing to TSV file...")
    tmp_file.write("Foo".encode())
    tmp_file.seek(0)
    return tmp_file


def export_case(job):
    """Export a ``Case`` object, store result in a new ``ExportFileJobResult``."""
    job.mark_start()
    try:
        case = job.case
        if job.file_type == "xlsx":
            tmp_file = export_case_xlsx(case, job)
        else:
            tmp_file = export_case_tsv(case, job)
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
