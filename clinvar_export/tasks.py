from celery.schedules import crontab
from config.celery import app

from clinvar_export import models


@app.task(bind=True)
def refresh_individual_sex_affected(_self):
    models.refresh_individual_sex_affected()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    sender.add_periodic_task(schedule=crontab(minute=11), sig=refresh_individual_sex_affected.s())
