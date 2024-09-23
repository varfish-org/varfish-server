from cases_import import models
from config.celery import app


@app.task(bind=True)
def run_seqvarsqueryexecutionbackgroundjob(_self, *, seqvarsqueryexecutionbackgroundjob_pk: int):
    """Task to execute a ``cases_import.models.SeqvarsQueryExecutionBackgroundJob``."""
    return models.run_seqvarsqueryexecutionbackgroundjob(pk=seqvarsqueryexecutionbackgroundjob_pk)
