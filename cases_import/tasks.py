from cases_import import models
from config.celery import app


@app.task(bind=True)
def run_caseimportactionbackgroundjob(_self, caseimportactionbackgroundjob_pk):
    """Task to execute a ``cases_import.models.CaseImportActionBackgroundJob``."""
    return models.run_caseimportactionbackgroundjob(pk=caseimportactionbackgroundjob_pk)
