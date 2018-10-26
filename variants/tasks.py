from config.celery import app

from . import models
from . import file_export


@app.task(bind=True)
def export_file_task(self, export_job_pk):
    """Task to export a file"""
    file_export.export_case(models.ExportFileBgJob.objects.get(pk=export_job_pk))
