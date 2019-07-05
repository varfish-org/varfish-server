import aldjemy

from config.celery import app
from celery.schedules import crontab

from . import file_export
from . import models
from . import submit_external
from . import variant_stats
from . import submit_filter
from . import sync_upstream

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


@app.task(bind=True)
def refresh_variants_smallvariantsummary(_self):
    models.refresh_variants_smallvariantsummary()


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
        SQLALCHEMY_ENGINE, models.ComputeProjectVariantsStatsBgJob.objects.get(pk=export_job_pk)
    )


@app.task(bind=True)
def sync_project_upstream(_self, sync_job_pk):
    sync_upstream.execute_sync_case_list_job(models.SyncCaseListBgJob.objects.get(pk=sync_job_pk))


@app.task(bind=True)
def single_case_filter_task(_self, filter_job_pk):
    """Task to submit filter and storing job for single case."""
    return submit_filter.case_filter(models.FilterBgJob.objects.get(pk=filter_job_pk))


@app.task(bind=True)
def clinvar_filter_task(_self, clinvar_job_pk):
    """Task to submit filter and storing job for clinvar."""
    return submit_filter.clinvar_filter(models.ClinvarBgJob.objects.get(pk=clinvar_job_pk))


@app.task(bind=True)
def project_cases_filter_task(_self, project_cases_filter_job_pk):
    """Task to submit filter and storing job for project."""
    return submit_filter.project_cases_filter(
        models.ProjectCasesFilterBgJob.objects.get(pk=project_cases_filter_job_pk)
    )


@app.task(bind=True)
def clear_inactive_variant_sets(_self):
    """Task to cleanup variant sets and their variants that are stuck in a non-active status for a long time."""
    return models.cleanup_variant_sets()


@app.task(bind=True)
def run_import_variants_bg_job(_self, import_variants_bg_job_pk):
    """Task to execute an ``ImportVariantsBgJob``."""
    return models.run_import_variants_bg_job(pk=import_variants_bg_job_pk)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Clear out old files nightly.
    sender.add_periodic_task(
        schedule=crontab(hour=1, minute=11), signature=clear_expired_exported_files.s()
    )
    # Regularly remove old variant that are not active.
    sender.add_periodic_task(schedule=crontab(minute=11), signature=clear_inactive_variant_sets.s())
    # Rebuild materialized view on sundays.
    sender.add_periodic_task(
        schedule=crontab(day_of_week=0), signature=refresh_variants_smallvariantsummary.s()
    )
