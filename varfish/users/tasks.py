from celery.schedules import crontab
from django.conf import settings
from django.core.management import call_command

from config.celery import app


@app.task(bind=True)
def sodar_sync_remote(_self):
    call_command("syncremote")


if settings.VARFISH_PROJECTROLES_SYNC_REMOTE:

    @app.on_after_finalize.connect
    def setup_periodic_tasks(sender, **_kwargs):
        """Register periodic tasks"""
        # Synchronize from projectroles every 2 minutes
        sender.add_periodic_task(
            schedule=crontab(minute="*/2"),
            sig=sodar_sync_remote.s(),
            name="Synchronize from remote SODAR site",
        )
