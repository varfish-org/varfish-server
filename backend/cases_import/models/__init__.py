from cases_import.models.executors import CaseImportBackgroundJobExecutor


def run_caseimportactionbackgroundjob(*, pk: int):
    """Execute the work for a ``CaseImportBackgroundJob``."""
    executor = CaseImportBackgroundJobExecutor(pk)
    executor.run()
