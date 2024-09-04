from config.celery import app
from seqvars.models import executors


@app.task(bind=True)
def run_seqvarsqueryexecutionbackgroundjob(_self, *, seqvarsqueryexecutionbackgroundjob_pk: int):
    """Task to execute a ``cases_import.models.SeqvarsQueryExecutionBackgroundJob``."""
    return executors.run_seqvarsqueryexecutionbackgroundjob(
        pk=seqvarsqueryexecutionbackgroundjob_pk
    )
