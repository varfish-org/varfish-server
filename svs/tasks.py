from bgjobs.models import BackgroundJob
from celery.schedules import crontab
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

from config.celery import app
from svs import bg_db, models

#: The User model to use.
from svs.models import BuildBackgroundSvSetJob, CleanupBackgroundSvSetJob

User = get_user_model()


@app.task(bind=True)
def clear_inactive_structural_variant_sets(_self):
    """Task to cleanup variant sets and their variants that are stuck in a non-active status for a long time."""
    return models.cleanup_variant_sets()


@app.task(bind=True)
def run_import_structural_variants_bg_job(_self, import_variants_bg_job_pk):
    """Task to execute an ``ImportVariantsBgJob``."""
    return models.run_import_structural_variants_bg_job(pk=import_variants_bg_job_pk)


@app.task(bind=True)
def build_bg_sv_set_task(_self, *, log_to_stderr=False, chromosomes=None):
    """Rebuild the background SV set"""
    with transaction.atomic():
        generic_bg_job = BackgroundJob.objects.create(
            name="build background sv set",
            project=None,
            job_type="svs.build_bg_sv_set",
            user=User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER),
        )
        spec_bg_job = BuildBackgroundSvSetJob.objects.create(bg_job=generic_bg_job)

    bg_db.build_bg_sv_set(spec_bg_job, log_to_stderr=log_to_stderr, chromosomes=chromosomes)


@app.task(bind=True)
def cleanup_bg_sv_set_task(_self, *, timeout_hours=None):
    """Cleanup old background SV sets"""
    with transaction.atomic():
        generic_bg_job = BackgroundJob.objects.create(
            name="cleanup background sv sets",
            project=None,
            job_type="svs.cleanup_bg_sv_sets",
            user=User.objects.get(username=settings.PROJECTROLES_ADMIN_OWNER),
        )
        spec_bg_job = CleanupBackgroundSvSetJob.objects.create(bg_job=generic_bg_job)

    bg_db.cleanup_bg_sv_sets(spec_bg_job, timeout_hours=timeout_hours)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Regularly remove old variant that are not active.
    sender.add_periodic_task(
        schedule=crontab(minute=11), sig=clear_inactive_structural_variant_sets.s()
    )
    # Regularly create new bg sv set and clean up old ones
    sender.add_periodic_task(schedule=crontab(day_of_week="sunday"), sig=build_bg_sv_set_task.s())
    sender.add_periodic_task(schedule=crontab(day_of_week="sunday"), sig=cleanup_bg_sv_set_task.s())
