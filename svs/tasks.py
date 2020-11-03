from config.celery import app
from celery.schedules import crontab

from . import models


@app.task(bind=True)
def clear_inactive_structural_variant_sets(_self):
    """Task to cleanup variant sets and their variants that are stuck in a non-active status for a long time."""
    return models.cleanup_variant_sets()


@app.task(bind=True)
def run_import_structural_variants_bg_job(_self, import_variants_bg_job_pk):
    """Task to execute an ``ImportVariantsBgJob``."""
    return models.run_import_structural_variants_bg_job(pk=import_variants_bg_job_pk)


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Regularly remove old variant that are not active.
    sender.add_periodic_task(
        schedule=crontab(minute=11), signature=clear_inactive_structural_variant_sets.s()
    )
