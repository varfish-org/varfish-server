import aldjemy
from sqlalchemy import select, func

from config.celery import app
from celery.schedules import crontab

from svs import models as sv_models
from variants.models import Case
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
def filter_task(_self, filter_job_pk):
    """Task to submit filter and storing job for single case."""
    return submit_filter.case_filter(models.FilterBgJob.objects.get(pk=filter_job_pk))


@app.task(bind=True)
def clinvar_task(_self, clinvar_job_pk):
    """Task to submit filter and storing job for clinvar."""
    return submit_filter.clinvar_filter(models.ClinvarBgJob.objects.get(pk=clinvar_job_pk))


@app.task(bind=True)
def project_cases_filter_task(_self, project_cases_filter_job_pk):
    """Task to submit filter and storing job for project."""
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
    # Rebuild materialized view on sundays.
    sender.add_periodic_task(
        schedule=crontab(day_of_week=0), signature=refresh_variants_smallvariantsummary.s()
    )


# TODO: move to a helpers module?
def update_variant_counts(case):
    """Update the variant counts for the given case.

    This is done without changing the ``date_modified`` field.
    """
    stmt = (
        select([func.count()])
        .select_from(models.SmallVariant.sa.table)
        .where(models.SmallVariant.sa.case_id == case.pk)
    )
    num_small_vars = SQLALCHEMY_ENGINE.scalar(stmt) or None
    stmt = (
        select([func.count()])
        .select_from(sv_models.StructuralVariant.sa.table)
        .where(sv_models.StructuralVariant.sa.case_id == case.pk)
    )
    num_svs = SQLALCHEMY_ENGINE.scalar(stmt) or None
    # Use the ``update()`` trick such that ``date_modified`` remains untouched.
    Case.objects.filter(pk=case.pk).update(num_small_vars=num_small_vars, num_svs=num_svs)
