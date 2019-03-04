from config.celery import app
from celery.schedules import crontab

import aldjemy.core

from . import file_export
from . import models
from . import submit_external
from . import variant_stats
from . import submit_filter

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


@app.task(bind=True)
def distiller_submission_task(_self, submission_job_pk):
    """Task to submit a case to MutationDistiller"""
    submit_external.submit_distiller(
        models.DistillerSubmissionBgJob.objects.get(pk=submission_job_pk)
    )


@app.task(bind=True)
def export_file_task(_self, export_job_pk):
    """Task to export single case to a file"""
    file_export.export_case(models.ExportFileBgJob.objects.get(pk=export_job_pk))


@app.task(bind=True)
def export_project_cases_file_task(_self, export_job_pk):
    """Task to export all project's cases to a file"""
    file_export.export_project_cases(
        models.ExportProjectCasesFileBgJob.objects.get(pk=export_job_pk)
    )


@app.task(bind=True)
def clear_expired_exported_files(_self):
    file_export.clear_expired_exported_files()


@app.task(bind=True)
def compute_project_variants_stats(_self, export_job_pk):
    variant_stats.execute_rebuild_project_variant_stats_job(
        SQLALCHEMY_ENGINE.connect(),
        models.ComputeProjectVariantsStatsBgJob.objects.get(pk=export_job_pk),
    )


@app.task(bind=True)
def filter_task(_self, filter_job_pk):
    """Task to submit storing the query results"""
    return submit_filter.case_filter(models.FilterBgJob.objects.get(pk=filter_job_pk))


@app.task(bind=True)
def project_cases_filter_task(_self, project_cases_filter_job_pk):
    return submit_filter.project_cases_filter(
        models.ProjectCasesFilterBgJob.objects.get(pk=project_cases_filter_job_pk)
    )


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Clear out old files nightly.
    sender.add_periodic_task(
        schedule=crontab(hour=1, minute=11), signature=clear_expired_exported_files.s()
    )
