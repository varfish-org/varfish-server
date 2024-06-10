from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
import requests_mock

from geneinfo.tests.factories import HpoFactory, HpoNameFactory
from variants.tests.factories import CaseFactory, SmallVariantCommentFactory

from ..models import Family
from ..views_ajax import CLINVAR_SUBMISSION_URL_PREFIX
from .factories import (
    CLINVAR_SUBMITTER_REPORT_HEADER,
    AssertionMethodFactory,
    FamilyFactory,
    IndividualFactory,
    OrganisationFactory,
    SubmissionFactory,
    SubmissionSetFactory,
    SubmissionSetWithOrgFactory,
    SubmissionWithIndividualFactory,
    SubmitterFactory,
    SubmittingOrgFactory,
)
from .test_views_ajax import CLINVAR_SUBMITTER_REPORT_RECORD


class TestOrganisationAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with Organisation."""

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-organisation-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")


class TestSubmitterAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with Submitter."""

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submitter-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")


class TestAssertionMethodAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with AssertionMethod."""

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-assertionmethod-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")


class TestIndividualAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with Individual."""

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-individual-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")


class TestFamilyAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with Family."""

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-family-list",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")


class TestSubmissionSetAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with SubmissionSet."""

    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.submitter = SubmitterFactory()

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_create(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        data = {
            "state": "pending",
            "title": "My Submission",
            "submitter": str(self.submitter.sodar_uuid),
        }
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users, 403, method="POST", data=data)

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": self.submissionset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": self.submissionset.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users, 403, method="PATCH")

    def test_delete(self):
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        for user in good_users:
            submissionset = SubmissionSetFactory(project=self.project)
            url = reverse(
                "clinvar_export:ajax-submissionset-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submissionset": submissionset.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 204, method="DELETE")

        submissionset = SubmissionSetFactory(project=self.project)
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": submissionset.sodar_uuid,
            },
        )
        for user in bad_users:
            self.assert_response(url, [user], 403, method="DELETE")


class TestSubmissionAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with SubmissionSet."""

    def setUp(self):
        super().setUp()
        self.assertionmethod = AssertionMethodFactory()
        self.submission = SubmissionFactory(submission_set__project=self.project)

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submission-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_create(self):
        data = {
            "assertion_method": self.assertionmethod.sodar_uuid,
            "sort_order": 42,
            "significance_status": "criteria provided, single submitter",
            "significance_description": "Pathogenic",
            "significance_last_evaluation": "2020-01-21",
            "variant_allele_count": 3,
            "variant_zygosity": "Heterozygote",
            "variant_assembly": "GRCh37",
            "variant_chromosome": "22",
            "variant_gene": "XXX",
            "variant_hgvs": "p.W32A",
        }

        url = reverse(
            "clinvar_export:ajax-submission-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        self.assert_response(
            url,
            good_users,
            201,
            method="POST",
            data={
                "submission_set": self.submission.submission_set.sodar_uuid,
                **data,
            },
        )
        self.assert_response(
            url,
            bad_users,
            403,
            method="POST",
            data={
                "submission_set": self.submission.submission_set.sodar_uuid,
                **data,
            },
        )

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": self.submission.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": self.submission.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users, 403, method="PATCH")

    def test_delete(self):
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        for user in good_users:
            submission = SubmissionFactory(submission_set__project=self.project)
            url = reverse(
                "clinvar_export:ajax-submission-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submission": submission.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 204, method="DELETE")

        submission = SubmissionFactory(submission_set__project=self.project)
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": submission.sodar_uuid,
            },
        )
        for user in bad_users:
            self.assert_response(url, [user], 403, method="DELETE")


class TestSubmissionIndividualAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with SubmissionSet."""

    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.submission = SubmissionWithIndividualFactory(submission_set=self.submissionset)
        self.submissionindividual = self.submission.submission_individuals.first()

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_create(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        for user in good_users:
            extra_family = FamilyFactory(project=self.project)
            extra_individual = IndividualFactory(family=extra_family)
            self.assert_response(
                url,
                [user],
                201,
                method="POST",
                data={
                    "sort_order": 1,
                    "individual": extra_individual.sodar_uuid,
                    "submission": self.submission.sodar_uuid,
                    "source": "research",
                },
            )
        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        for user in bad_users:
            extra_family = FamilyFactory(project=self.project)
            extra_individual = IndividualFactory(family=extra_family)
            self.assert_response(
                url,
                [user],
                403,
                method="POST",
                data={
                    "sort_order": 1,
                    "individual": extra_individual.sodar_uuid,
                    "submission": self.submission.sodar_uuid,
                    "source": "research",
                },
            )

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionindividual": self.submissionindividual.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionindividual": self.submissionindividual.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users, 403, method="PATCH")

    def test_delete(self):
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        for user in good_users:
            submission = SubmissionWithIndividualFactory(submission_set=self.submissionset)
            submissionindividual = submission.submission_individuals.first()
            url = reverse(
                "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submissionindividual": submissionindividual.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 204, method="DELETE")

        bad_users = [self.user_guest, self.anonymous, self.user_no_roles]
        for user in bad_users:
            submission = SubmissionWithIndividualFactory(submission_set=self.submissionset)
            submissionindividual = submission.submission_individuals.first()
            url = reverse(
                "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submissionindividual": submissionindividual.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 403, method="DELETE")


class TestSubmittingOrgAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views dealing with SubmittingOrg."""

    def setUp(self):
        super().setUp()
        self.submission_set = SubmissionSetWithOrgFactory(project=self.project)
        self.submittingorg = self.submission_set.submitting_orgs.all()[0]
        self.organisation = OrganisationFactory()

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_create(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.anonymous, self.user_no_roles, self.user_guest]
        for user in good_users:
            extra_org = OrganisationFactory()
            self.assert_response(
                url,
                [user],
                201,
                method="POST",
                data={
                    "sort_order": 0,
                    "organisation": extra_org.sodar_uuid,
                    "submission_set": self.submission_set.sodar_uuid,
                },
            )
        for user in bad_users:
            extra_org = OrganisationFactory()
            self.assert_response(
                url,
                [user],
                403,
                method="POST",
                data={
                    "sort_order": 0,
                    "organisation": extra_org.sodar_uuid,
                    "submission_set": self.submission_set.sodar_uuid,
                },
            )

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submittingorg": self.submittingorg.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submittingorg": self.submittingorg.sodar_uuid,
            },
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.anonymous, self.user_no_roles, self.user_guest]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users, 403, method="PATCH")

    def test_delete(self):
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [self.anonymous, self.user_no_roles, self.user_guest]
        for user in good_users:
            extra_org = OrganisationFactory()
            submittingorg = SubmittingOrgFactory(
                organisation=extra_org, submission_set=self.submission_set, sort_order=0
            )
            url = reverse(
                "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submittingorg": submittingorg.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 204, method="DELETE")
        for user in bad_users:
            extra_org = OrganisationFactory()
            submittingorg = SubmittingOrgFactory(
                organisation=extra_org, submission_set=self.submission_set, sort_order=0
            )
            url = reverse(
                "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
                kwargs={
                    "project": self.project.sodar_uuid,
                    "submittingorg": submittingorg.sodar_uuid,
                },
            )
            self.assert_response(url, [user], 403, method="DELETE")


class TestQueryOmimAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for OMIM term AJAX views"""

    def test(self):
        hpo_record = HpoFactory()
        url = (
            reverse(
                "clinvar_export:query-omim-term",
                kwargs={
                    "project": self.project.sodar_uuid,
                },
            )
            + "?query="
            + hpo_record.database_id
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
        ]
        bad_users = [self.anonymous]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 302, method="GET")  # redirect to login


class TestQueryHpoAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views for querying for HPO terms."""

    def test(self):
        hpo_record = HpoNameFactory()
        url = (
            reverse(
                "clinvar_export:query-hpo-term",
                kwargs={
                    "project": self.project.sodar_uuid,
                },
            )
            + "?query="
            + hpo_record.hpo_id
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
        ]
        bad_users = [self.anonymous]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 302, method="GET")  # redirect to login


class TestAnnotatedSmallVariantsAjaxViews(TestProjectAPIPermissionBase):
    """Permission tests for the AJAX views for querying user-annotated small variants."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.family = Family.objects.get_or_create_in_project(project=self.project, case=self.case)


class TestFetchClinVarReportApiView(TestProjectAPIPermissionBase):
    """Permission tests for ``FetchClinVarReportApiView``."""

    def setUp(self):
        super().setUp()
        self.submission_set = SubmissionSetFactory(project=self.project)

    @requests_mock.Mocker()
    def test_fetch_submitter_report_with_submitter_report(self, r_mock):
        report_url = CLINVAR_SUBMISSION_URL_PREFIX + "some/suffix"
        data = {"report_url": report_url}
        record = CLINVAR_SUBMITTER_REPORT_RECORD
        report_content = CLINVAR_SUBMITTER_REPORT_HEADER + "\t".join(record.values())
        r_mock.get(
            report_url,
            status_code=200,
            text=report_content,
        )
        url = reverse(
            "clinvar_export:clinvar-report-fetch",
            kwargs={"submissionset": self.submission_set.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 204, method="POST", data=data)
        self.assert_response(url, bad_users, 403, method="POST", data=data)


class TestClinVarReportListView(TestProjectAPIPermissionBase):
    """Permission tests for ``ClinVarReportListView``."""

    def setUp(self):
        super().setUp()
        self.submission_set = SubmissionSetFactory(project=self.project)

    def test(self):
        SmallVariantCommentFactory()
        url = reverse(
            "clinvar_export:clinvar-report-list",
            kwargs={"submissionset": self.submission_set.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users, 403, method="GET")
