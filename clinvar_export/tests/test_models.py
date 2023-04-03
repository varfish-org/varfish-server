"""Tests for ``clinvar_export.models``."""

from test_plus.test import TestCase

from clinvar_export.models import (
    REPORT_TYPES,
    AssertionMethod,
    Family,
    Individual,
    Organisation,
    Submission,
    SubmissionSet,
    Submitter,
    SubmittingOrg,
    refresh_individual_sex_affected,
)
from clinvar_export.tests.factories import (
    AssertionMethodFactory,
    ClinVarReportFactory,
    FamilyFactory,
    IndividualFactory,
    OrganisationFactory,
    SubmissionFactory,
    SubmissionSetFactory,
    SubmitterFactory,
    SubmittingOrgFactory,
)
from variants.models import Case
from variants.tests.factories import CaseFactory


class TestFamily(TestCase):
    """Basic tests for the ``Family`` model and manager."""

    def testCreate(self):
        self.assertEquals(Family.objects.count(), 0)
        FamilyFactory()
        self.assertEquals(Family.objects.count(), 1)

    def testGetOrCreateInProjectByCaseName(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        family = Family.objects.get_or_create_in_project(project=case.project, case_name=case.name)

        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(family.case.id, case.id)

    def testGetOrCreateInProjectByCaseNameFails(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        with self.assertRaises(Case.DoesNotExist):
            Family.objects.get_or_create_in_project(project=case.project, case_name=case.name + "_")

        self.assertEquals(Family.objects.count(), 0)

    def testGetOrCreateInProjectByCase(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        family = Family.objects.get_or_create_in_project(project=case.project, case=case)

        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(family.case.id, case.id)


class TestIndividual(TestCase):
    """Basic tests for the ``Individual`` model and manager."""

    def testCreate(self):
        self.assertEquals(Family.objects.count(), 0)
        self.assertEquals(Individual.objects.count(), 0)
        IndividualFactory()
        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(Individual.objects.count(), 1)

    def testGetOrCreateInProjectByCaseName(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        indiv = Individual.objects.get_or_create_in_project(
            project=case.project, name=case.pedigree[0]["patient"], case_name=case.name
        )

        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(indiv.family.case.id, case.id)

    def testGetOrCreateInProjectByCaseNameFails(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        with self.assertRaises(Case.DoesNotExist):
            Individual.objects.get_or_create_in_project(
                project=case.project, name=case.pedigree[0]["patient"], case_name=case.name + "_"
            )

        self.assertEquals(Family.objects.count(), 0)

    def testGetOrCreateInProjectByCase(self):
        case = CaseFactory()
        self.assertEquals(Family.objects.count(), 0)

        indiv = Individual.objects.get_or_create_in_project(
            project=case.project, name=case.pedigree[0]["patient"], case=case
        )

        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(indiv.family.case.id, case.id)

    def testGetOrCreateInProjectByFamily(self):
        family = FamilyFactory()
        self.assertEquals(Family.objects.count(), 1)
        indiv = Individual.objects.get_or_create_in_project(
            project=family.project, name=family.case.pedigree[0]["patient"], family=family
        )

        self.assertEquals(Family.objects.count(), 1)
        self.assertEquals(indiv.family.id, family.id)


class TestAssertionMethod(TestCase):
    """Basic tests for ``AssertionMethod``"""

    def testCreate(self):
        self.assertEquals(AssertionMethod.objects.count(), 1)
        AssertionMethodFactory()
        self.assertEquals(AssertionMethod.objects.count(), 2)


class TestSubmitter(TestCase):
    """Basic tests for ``Submitter``"""

    def testCreate(self):
        self.assertEquals(Submitter.objects.count(), 1)
        SubmitterFactory()
        self.assertEquals(Submitter.objects.count(), 2)


class TestOrganisation(TestCase):
    """Basic tests for ``Organisation``"""

    def testCreate(self):
        self.assertEquals(Organisation.objects.count(), 2)
        OrganisationFactory()
        self.assertEquals(Organisation.objects.count(), 3)


class TestSubmissionSet(TestCase):
    """Basic tests for ``SubmissionSet``."""

    def testCreate(self):
        self.assertEquals(SubmissionSet.objects.count(), 0)
        SubmissionSetFactory()
        self.assertEquals(SubmissionSet.objects.count(), 1)


class TestSubmittingOrg(TestCase):
    """Basic tests for ``SubmittingOrg``."""

    def testCreate(self):
        self.assertEquals(SubmittingOrg.objects.count(), 0)
        SubmittingOrgFactory()
        self.assertEquals(SubmittingOrg.objects.count(), 1)


class TestSubmission(TestCase):
    """Basic tests for ``Submission``."""

    def testCreate(self):
        self.assertEquals(Submission.objects.count(), 0)
        SubmissionFactory()
        self.assertEquals(Submission.objects.count(), 1)


class TestUpdateIndividualSexAffectedTask(TestCase):
    """Test the task that updates the sex/affected of ``Individual`` records from upstream case."""

    def testRun(self):
        individual = IndividualFactory(sex="male", affected="yes")
        individual.sex = "unknown"
        individual.affected = "unknown"
        individual.save()
        self.assertEquals(individual.sex, "unknown")
        self.assertEquals(individual.sex, "unknown")
        refresh_individual_sex_affected()
        individual.refresh_from_db()
        self.assertEquals(individual.sex, "male")
        self.assertEquals(individual.affected, "yes")


class TestClinVarReport(TestCase):
    """Basic tests for ``ClinVarReport``"""

    def testRun(self):
        report = ClinVarReportFactory(report_type=REPORT_TYPES[0])
        report.report_type = REPORT_TYPES[1]
        report.save()
        self.assertEquals(report.report_type, REPORT_TYPES[1])
        report.refresh_from_db()
        self.assertEquals(report.report_type, REPORT_TYPES[1])
