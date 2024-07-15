"""Tasks for the importer module."""

from config.celery import app
import variants.models

from . import models


@app.task(bind=True)
def refresh_variants_smallvariantsummary(_self):
    variants.models.refresh_variants_smallvariantsummary()


@app.task(bind=True)
def run_import_case_bg_job(_self, pk):
    """Task to execute an ``ImportCaseBgJob``."""
    return models.run_import_case_bg_job(pk=pk)
