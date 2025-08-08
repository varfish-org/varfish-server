from celery.schedules import crontab

from config.celery import app
from seqvars.models import executors


@app.task(bind=True)
def run_seqvarsqueryexecutionbackgroundjob(_self, *, seqvarsqueryexecutionbackgroundjob_pk: int):
    """Task to execute a ``cases_import.models.SeqvarsQueryExecutionBackgroundJob``."""
    return executors.run_seqvarsqueryexecutionbackgroundjob(
        pk=seqvarsqueryexecutionbackgroundjob_pk
    )


@app.task(bind=True)
def run_seqvarsinhousedbbuildbackgroundjob(_self):
    """Task to execute a ``cases_import.models.SeqvarsInhouseDbBuildBackgroundJob``."""
    return executors.run_seqvarsbuildinhousedbbackgroundjob()


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **_kwargs):
    """Register periodic tasks"""
    # Regularly rebuild the in-house database.
    sender.add_periodic_task(
        schedule=crontab(day_of_week=1, minute=11), sig=run_seqvarsinhousedbbuildbackgroundjob.s()
    )
