from cases_import.models.executors import CaseImportBackgroundJobExecutor


#: Mapping of assay ID from phenopackets to representation in Individual.
def run_caseimportactionbackgroundjob(*, pk: int):
    """Execute the work for a ``CaseImportBackgroundJob``."""
    executor = CaseImportBackgroundJobExecutor(pk)
    executor.run()
