import logging

from celery.schedules import crontab
from django.conf import settings
from django.core.management import call_command

from config.celery import app


#: Logger to use in this module.
LOGGER = logging.getLogger(__name__)


@app.task(bind=True)
def sodar_sync_remote(_self):
    try:
        call_command("syncremote")
    except Exception as e:
        LOGGER.error("Problem with syncremote job: %s", e)


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
