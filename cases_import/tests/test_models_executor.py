"""Tests for the ``CaseImportBackgroundJobExecutor`` and related code.

This has been broken away from ``test_models.py`` for better structure.
"""
from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus import TestCase

from cases.tests.factories import IndividualFactory, PedigreeFactory
from cases_import.models import CaseImportAction, CaseImportBackgroundJobExecutor
from cases_import.tests.factories import CaseImportActionFactory, CaseImportBackgroundJobFactory
from seqmeta.tests.factories import TargetBedFileFactory
from variants.tests.factories import CaseFactory


class ExecutorTestMixin:
    def _setUpExecutor(self, action):
        super().setUp()
        self.user = self.make_user()
        self.caseimportaction = CaseImportActionFactory(
            action=action,
            state=CaseImportAction.STATE_SUBMITTED,
            overwrite_terms=True,
        )
        self.caseimportbackgroundjob = CaseImportBackgroundJobFactory(
            caseimportaction=self.caseimportaction,
            user=self.user,
        )
        self.project = self.caseimportbackgroundjob.project
        self.executor = CaseImportBackgroundJobExecutor(self.caseimportbackgroundjob.pk)
        self.targetbedfile = TargetBedFileFactory(
            file_uri=self.caseimportaction.payload["proband"]["files"][0]["uri"]
        )


class ImportCreateTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=create"""

    def setUp(self):
        self._setUpExecutor(CaseImportAction.ACTION_CREATE)

    def test_run(self):
        self.executor.run()


class ImportUpdateTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=update"""

    def setUp(self):
        super().setUp()
        self._setUpExecutor(CaseImportAction.ACTION_UPDATE)
        self.case = CaseFactory(
            project=self.project,
            name=self.caseimportaction.payload["pedigree"]["persons"][0]["familyId"],
        )
        self.pedigree = PedigreeFactory(case=self.case)
        self.keep_invidual = IndividualFactory(
            pedigree=self.pedigree,
            name=self.caseimportaction.payload["proband"]["id"],
        )
        self.abundant_individual = IndividualFactory(
            pedigree=self.pedigree,
        )

    def test_run(self):
        self.executor.run()


class ImportDeleteTest(ExecutorTestMixin, TestCaseSnapshot, TestCase):
    """Test the executor with action=delete"""

    def setUp(self):
        super().setUp()
        self._setUpExecutor(CaseImportAction.ACTION_DELETE)
        self.case = CaseFactory(
            project=self.project,
            name=self.caseimportaction.payload["pedigree"]["persons"][0]["familyId"],
        )

    def test_run(self):
        self.executor.run()
