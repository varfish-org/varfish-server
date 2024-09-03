from cases_import import models
from config.celery import app


@app.task(bind=True)
def run_caseimportactionbackgroundjob(_self, *, caseimportactionbackgroundjob_pk: int):
    """Task to execute a ``seqvars.models.CaseImportActionBackgroundJob``."""
    return models.run_caseimportactionbackgroundjob(pk=caseimportactionbackgroundjob_pk)
