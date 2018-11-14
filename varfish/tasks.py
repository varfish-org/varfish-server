from celery.schedules import crontab
from django.core.management import call_command

from config.celery import app

@app.task(bind=True)
def sodar_sync_remote(_self):
    call_command('syncremote')


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Synchronize from projectroles every 10 minutes
    sender.add_periodic_task(
        schedule=crontab(minute='*/10'), signature=sodar_sync_remote.s(),
        name="Synchronize from remote SODAR site",
    )
