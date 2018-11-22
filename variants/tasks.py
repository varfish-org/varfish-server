from config.celery import app
from celery.schedules import crontab

from . import models
from . import file_export
from . import submit_external


@app.task(bind=True)
def distiller_submission_task(_self, submission_job_pk):
    """Task to submit a case to MutationDistiller"""
    submit_external.submit_distiller(
        models.DistillerSubmissionBgJob.objects.get(pk=submission_job_pk)
    )


@app.task(bind=True)
def export_file_task(_self, export_job_pk):
    """Task to export a file"""
    file_export.export_case(models.ExportFileBgJob.objects.get(pk=export_job_pk))


@app.task(bind=True)
def clear_expired_exported_files(_self):
    file_export.clear_expired_exported_files()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Clear out old files nightly.
    sender.add_periodic_task(
        schedule=crontab(hour=1, minute=11), signature=clear_expired_exported_files.s()
    )
