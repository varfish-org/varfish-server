import json
import re

from django.forms import model_to_dict
from django.urls import reverse
import jsonmatch
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
import requests_mock
from rest_framework.exceptions import ParseError

from clinvar_export import views_ajax
from clinvar_export.models import (
    AssertionMethod,
    ClinVarReport,
    Family,
    Individual,
    Submission,
    SubmissionIndividual,
    SubmissionSet,
    SubmittingOrg,
    create_families_and_individuals,
)
from clinvar_export.tests.factories import (
    CLINVAR_ERROR_REPORT_HEADER,
    CLINVAR_SUBMITTER_REPORT_HEADER,
    ClinVarReportFactory,
    OrganisationFactory,
    SubmissionFactory,
    SubmissionIndividualFactory,
    SubmissionSetFactory,
    SubmitterFactory,
    SubmittingOrgFactory,
)
from clinvar_export.views_ajax import CLINVAR_SUBMISSION_URL_PREFIX
from geneinfo.tests.factories import HpoFactory, HpoNameFactory
from variants.tests.factories import (
    AcmgCriteriaRatingFactory,
    CaseFactory,
    SmallVariantCommentFactory,
    SmallVariantFactory,
    SmallVariantFlagsFactory,
)

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestOrganisationAjaxViews(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-organisation-list", kwargs={"project": self.project.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 2)
        expected0 = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "clinvar_id": 505735,
                "name": (
                    "Institute for Medical Genetics and Human Genetics (Charité - Universitätsmedizin "
                    "Berlin), Charité - Universitätsmedizin"
                ),
            }
        )
        expected0.assert_matches(res_json[0])
        expected1 = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "clinvar_id": 507461,
                "name": "CUBI - Core Unit Bioinformatics (Berlin Institute of Health)",
            }
        )
        expected1.assert_matches(res_json[1])


class TestSubmitterAjaxViews(TestProjectAPIPermissionBase):
    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submitter-list", kwargs={"project": self.project.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "clinvar_id": 9131,
                "name": "Manuel Holtgrewe",
            }
        )
        expected.assert_matches(res_json[0])


class TestAssertionMethodAjaxViews(TestProjectAPIPermissionBase):
    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-assertionmethod-list", kwargs={"project": self.project.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "sodar_uuid": RE_UUID4,
                "is_builtin": True,
                "title": "ACMG Guidelines, 2015",
                "reference": "PMID:25741868",
            }
        )
        expected.assert_matches(res_json[0])


class TestIndividualListView(TestProjectAPIPermissionBase):
    """Test the AJAX views dealing with Individual."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Individual.objects.count(), 0)
        url = reverse(
            "clinvar_export:ajax-individual-list", kwargs={"project": self.project.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        re_name = re.compile(r"^index_\d\d\d-N1-DNA1-WES1$")
        expected = jsonmatch.compile(
            {
                "affected": "yes",
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "family": RE_UUID4,
                "name": re_name,
                "project": RE_UUID4,
                "phenotype_terms": None,
                "sex": "male",
                "sodar_uuid": RE_UUID4,
                "taxonomy_id": 9606,
            }
        )
        expected.assert_matches(res_json[0])
        self.assertEqual(Family.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 1)


class TestFamilyListView(TestProjectAPIPermissionBase):
    """Test the AJAX views dealing with Family."""

    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_list(self):
        self.assertEqual(Family.objects.count(), 0)
        self.assertEqual(Individual.objects.count(), 0)
        url = reverse(
            "clinvar_export:ajax-family-list", kwargs={"project": self.project.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        re_case = re.compile(r"^case \d\d\d: singleton$")
        expected = jsonmatch.compile(
            {
                "case": RE_UUID4,
                "case_name": re_case,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "project": RE_UUID4,
                "sodar_uuid": RE_UUID4,
                "pedigree": self.case.pedigree,
            }
        )
        expected.assert_matches(res_json[0])
        self.assertEqual(Family.objects.count(), 1)
        self.assertEqual(Individual.objects.count(), 1)


class TestSubmissionSetListCreateView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.organisation = OrganisationFactory()
        self.submittingorg = SubmittingOrgFactory(
            organisation=self.organisation, submission_set=self.submissionset
        )
        self.submission = SubmissionFactory(submission_set=self.submissionset)
        self.submitter = SubmitterFactory()

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": RE_UUID4,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "project": str(self.project.sodar_uuid),
                "title": re.compile(r"^Submission #\d+$"),
                "submitting_orgs": [str(self.submittingorg.sodar_uuid)],
                "submissions": [str(self.submission.sodar_uuid)],
                "state": self.submissionset.state,
                "submitter": str(self.submissionset.submitter.sodar_uuid),
            }
        )
        expected.assert_matches(res_json[0])

    def test_create(self):
        self.assertEqual(SubmissionSet.objects.count(), 1)
        url = reverse(
            "clinvar_export:ajax-submissionset-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        data = {
            "state": "pending",
            "title": "My Submission",
            "submitter": str(self.submitter.sodar_uuid),  # XXX
        }
        with self.login(self.contributor_as.user):
            response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SubmissionSet.objects.count(), 2)
        submissionset = SubmissionSet.objects.all()[1]
        for k, v in data.items():
            if k == "submitter":
                self.assertEqual(str(getattr(submissionset, k).sodar_uuid), v)
            else:
                self.assertEqual(getattr(submissionset, k), v, msg="k = %s" % k)


class TestSubmissionSetRetrieveUpdateDestroyView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.organisation = OrganisationFactory()
        self.submittingorg = SubmittingOrgFactory(
            organisation=self.organisation, submission_set=self.submissionset
        )
        self.submission = SubmissionFactory(submission_set=self.submissionset)

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": self.submissionset.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.submissionset.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "project": str(self.project.sodar_uuid),
                "title": self.submissionset.title,
                "submitting_orgs": [str(self.submittingorg.sodar_uuid)],
                "submissions": [str(self.submission.sodar_uuid)],
                "state": self.submissionset.state,
                "submitter": str(self.submissionset.submitter.sodar_uuid),
            }
        )
        expected.assert_matches(res_json)

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": self.submissionset.sodar_uuid,
            },
        )
        data = {
            "title": "Brand New Title",
            "state": "submitted",
        }
        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.submissionset.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "project": str(self.project.sodar_uuid),
                "title": data["title"],
                "submitting_orgs": [str(self.submittingorg.sodar_uuid)],
                "submissions": [str(self.submission.sodar_uuid)],
                "state": data["state"],
                "submitter": str(self.submissionset.submitter.sodar_uuid),
            }
        )
        expected.assert_matches(res_json)

    def test_destroy(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": self.submissionset.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SubmissionSet.objects.count(), 0)


class TestSubmissionListCreateView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.organisation = OrganisationFactory()
        self.submittingorg = SubmittingOrgFactory(
            organisation=self.organisation, submission_set=self.submissionset
        )
        self.submission = SubmissionFactory(submission_set=self.submissionset)
        self.individual = Individual.objects.get_or_create_in_project(
            project=self.project, case=self.case, name=self.case.pedigree[0]["patient"]
        )
        self.submission_individual = SubmissionIndividualFactory(
            submission=self.submission, individual=self.individual
        )

    def test_list(self):
        url = reverse(
            "clinvar_export:ajax-submission-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "age_of_onset": "Antenatal",
                "inheritance": "Other",
                "variant_type": "Variation",
                "assertion_method": str(self.submission.assertion_method.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "diseases": [
                    {"term_id": re.compile(r"OMIM:\d+"), "term_name": re.compile(r"Disease \d+")}
                ],
                "project": str(self.project.sodar_uuid),
                "record_status": self.submission.record_status,
                "release_status": self.submission.release_status,
                "significance_description": self.submission.significance_description,
                "significance_last_evaluation": self.submission.significance_last_evaluation.strftime(
                    "%Y-%m-%d"
                ),
                "significance_status": self.submission.significance_status,
                "sodar_uuid": str(self.submission.sodar_uuid),
                "sort_order": self.submission.sort_order,
                "submission_individuals": [str(self.submission_individual.sodar_uuid)],
                "submission_set": str(self.submissionset.sodar_uuid),
                "variant_assembly": "GRCh37",
                "variant_chromosome": self.submission.variant_chromosome,
                "variant_gene": self.submission.variant_gene,
                "variant_hgvs": self.submission.variant_hgvs,
                "variant_start": self.submission.variant_start,
                "variant_stop": self.submission.variant_stop,
                "variant_reference": re.compile(r"[ACGT]+$"),
                "variant_alternative": re.compile(r"[ACGT]+$"),
                "clinvar_error_report": None,
                "clinvar_submitter_report": None,
            }
        )
        expected.assert_matches(res_json[0])

    def test_create(self):
        self.assertEqual(Submission.objects.count(), 1)
        url = reverse(
            "clinvar_export:ajax-submission-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        data = {
            "submission_set": str(self.submissionset.sodar_uuid),
            "sort_order": 0,
            "significance_status": "criteria provided, single submitter",
            "significance_description": "Pathogenic",
            "significance_last_evaluation": "2020-10-10",
            "assertion_method": str(AssertionMethod.objects.first().sodar_uuid),
            "variant_assembly": "GRCh37",
            "variant_chromosome": "1",
            "variant_start": 1_000_000,
            "variant_stop": 1_000_000,
            "variant_reference": "C",
            "variant_alternative": "T",
            "variant_gene": ["GENE0"],
            "variant_hgvs": ["p.W23T"],
            "diseases": json.dumps([{"term_id": "HP:1234567", "term_name": "Phenotype 1234567"}]),
        }
        with self.login(self.contributor_as.user):
            response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Submission.objects.count(), 2)
        submission = Submission.objects.order_by("-date_created").first()
        for k, v in data.items():
            if k in ("assertion_method", "submission_set"):
                self.assertEqual(str(getattr(submission, k).sodar_uuid), v)
            elif k == "diseases":
                self.assertEqual(json.dumps(getattr(submission, k)), v)
            elif k == "significance_last_evaluation":
                self.assertEqual(getattr(submission, k).strftime("%Y-%m-%d"), v)
            else:
                self.assertEqual(getattr(submission, k), v, msg="k = %s" % k)


class TestSubmissionRetrieveUpdateDestroyView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.submission = SubmissionFactory(submission_set=self.submissionset)

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": self.submission.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "age_of_onset": "Antenatal",
                "inheritance": "Other",
                "variant_type": "Variation",
                "assertion_method": str(self.submission.assertion_method.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "diseases": self.submission.diseases,
                "project": str(self.project.sodar_uuid),
                "record_status": self.submission.record_status,
                "release_status": self.submission.release_status,
                "significance_description": self.submission.significance_description,
                "significance_last_evaluation": self.submission.significance_last_evaluation.strftime(
                    "%Y-%m-%d"
                ),
                "significance_status": self.submission.significance_status,
                "sodar_uuid": str(self.submission.sodar_uuid),
                "sort_order": self.submission.sort_order,
                "submission_individuals": [],  # TODO: fill me!
                "submission_set": str(self.submission.submission_set.sodar_uuid),
                "variant_alternative": self.submission.variant_alternative,
                "variant_assembly": self.submission.variant_assembly,
                "variant_chromosome": self.submission.variant_chromosome,
                "variant_gene": self.submission.variant_gene,
                "variant_hgvs": self.submission.variant_hgvs,
                "variant_reference": self.submission.variant_reference,
                "variant_start": self.submission.variant_start,
                "variant_stop": self.submission.variant_stop,
                "clinvar_error_report": None,
                "clinvar_submitter_report": None,
            }
        )
        expected.assert_matches(res_json)

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": self.submission.sodar_uuid,
            },
        )
        data = {
            "age_of_onset": "Antenatal",
            "inheritance": "Other",
            "variant_type": "Variation",
            "date_created": RE_DATETIME,
            "date_modified": RE_DATETIME,
            "project": str(self.project.sodar_uuid),
            "sodar_uuid": str(self.submission.sodar_uuid),
            "sort_order": -1,
            "significance_status": "no criteria provided, single submitter",
            "significance_description": "Pathogenic",
            "significance_last_evaluation": "2020-10-10",
            "record_status": "pending",
            "release_status": "public",
            "assertion_method": str(AssertionMethod.objects.first().sodar_uuid),
            "variant_assembly": "GRCh37",
            "variant_chromosome": "1",
            "variant_start": 1_000_000,
            "variant_stop": 1_000_000,
            "variant_reference": "C",
            "variant_alternative": "T",
            "variant_gene": ["GENE0"],
            "variant_hgvs": ["p.W23T"],
            "diseases": json.dumps([{"term_id": "OMIM:1234567", "term_name": "Disease 1234567"}]),
            "submission_individuals": [],
            "submission_set": str(self.submission.submission_set.sodar_uuid),
        }
        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                **data,
                "diseases": json.loads(data["diseases"]),
                "clinvar_error_report": None,
                "clinvar_submitter_report": None,
            }
        )
        expected.assert_matches(res_json)

    def test_destroy(self):
        url = reverse(
            "clinvar_export:ajax-submission-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submission": self.submission.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Submission.objects.count(), 0)


class TestSubmissionIndividualCreateListView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.submission = SubmissionFactory(submission_set=self.submissionset)
        self.case = CaseFactory(project=self.project)
        create_families_and_individuals(self.project)
        self.individual = Individual.objects.filter(family__project=self.project).order_by(
            "-date_created"
        )[0]

    def test_list(self):
        submissionindividual = SubmissionIndividualFactory(
            submission=self.submission, individual=self.individual
        )

        url = reverse(
            "clinvar_export:ajax-submissionindividual-list-create",
            kwargs={"project": self.submission.submission_set.project.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "individual": str(self.individual.sodar_uuid),
                "phenotypes": submissionindividual.phenotypes,
                "project": str(self.project.sodar_uuid),
                "sodar_uuid": str(submissionindividual.sodar_uuid),
                "sort_order": submissionindividual.sort_order,
                "submission": str(self.submission.sodar_uuid),
                "citations": [],
                "source": re.compile(r"(clinical testing|research|not provided)$"),
                "tissue": re.compile(r"^(blood|saliva)$"),
                "variant_allele_count": 1,
                "variant_origin": "germline",
                "variant_zygosity": "Homozygote",
            }
        )
        expected.assert_matches(res_json[0])

    def test_create(self):
        self.assertEqual(SubmissionIndividual.objects.count(), 0)
        url = reverse(
            "clinvar_export:ajax-submissionindividual-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        data = {
            "sort_order": 0,
            "individual": str(self.individual.sodar_uuid),
            "submission": str(self.submission.sodar_uuid),
            "source": "research",
            "phenotypes": json.dumps([{"term_id": "HP:1234567", "term_name": "Phenotype 1234567"}]),
        }
        with self.login(self.contributor_as.user):
            response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SubmissionIndividual.objects.count(), 1)
        submissionindividual = SubmissionIndividual.objects.order_by("-date_created").first()
        self.assertEqual(submissionindividual.phenotypes, json.loads(data["phenotypes"]))
        self.assertEqual(submissionindividual.sort_order, data["sort_order"])


class TestSubmissionIndividualRetrieveUpdateDestroyView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.submission = SubmissionFactory(submission_set=self.submissionset)
        self.case = CaseFactory(project=self.project)
        create_families_and_individuals(self.project)
        self.individual = Individual.objects.filter(family__project=self.project).order_by(
            "-date_created"
        )[0]
        self.submissionindividual = SubmissionIndividualFactory(
            submission=self.submission, individual=self.individual
        )

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionindividual": self.submissionindividual.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "individual": str(self.submissionindividual.individual.sodar_uuid),
                "phenotypes": self.submissionindividual.phenotypes,
                "project": str(self.project.sodar_uuid),
                "sodar_uuid": str(self.submissionindividual.sodar_uuid),
                "sort_order": self.submissionindividual.sort_order,
                "submission": str(self.submission.sodar_uuid),
                "citations": [],
                "source": re.compile(r"(clinical testing|research|not provided)$"),
                "tissue": re.compile(r"^(blood|saliva)$"),
                "variant_allele_count": 1,
                "variant_origin": "germline",
                "variant_zygosity": "Homozygote",
            }
        )
        expected.assert_matches(res_json)

    def test_update(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionindividual": self.submissionindividual.sodar_uuid,
            },
        )
        data = {
            "phenotypes": json.dumps([{"term_id": "HP:XXX", "term_name": "Updated Term"}]),
            "sort_order": 42,
            "date_created": RE_DATETIME,
            "date_modified": RE_DATETIME,
            "individual": RE_UUID4,
            "project": RE_UUID4,
            "sodar_uuid": RE_UUID4,
            "submission": RE_UUID4,
            "citations": [],
            "source": "clinical testing",
            "tissue": "saliva",
            "variant_allele_count": 1,
            "variant_origin": "germline",
            "variant_zygosity": "Homozygote",
        }

        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile({**data, "phenotypes": json.loads(data["phenotypes"])})
        expected.assert_matches(res_json)

    def test_destroy(self):
        url = reverse(
            "clinvar_export:ajax-submissionindividual-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionindividual": self.submissionindividual.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SubmissionIndividual.objects.count(), 0)


class TestSubmittingOrgCreateListView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.organisation = OrganisationFactory()

    def test_list(self):
        submittingorg = SubmittingOrgFactory(
            organisation=self.organisation, submission_set=self.submissionset
        )
        url = reverse(
            "clinvar_export:ajax-submittingorg-list-create",
            kwargs={"project": self.submissionset.project.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected = jsonmatch.compile(
            {
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "organisation": str(self.organisation.sodar_uuid),
                "sodar_uuid": str(submittingorg.sodar_uuid),
                "sort_order": submittingorg.sort_order,
                "submission_set": str(self.submissionset.sodar_uuid),
            }
        )
        expected.assert_matches(res_json[0])

    def test_create(self):
        self.assertEqual(SubmittingOrg.objects.count(), 0)
        url = reverse(
            "clinvar_export:ajax-submittingorg-list-create",
            kwargs={"project": self.project.sodar_uuid},
        )
        data = {
            "sort_order": 0,
            "organisation": str(self.organisation.sodar_uuid),
            "submission_set": str(self.submissionset.sodar_uuid),
        }
        with self.login(self.contributor_as.user):
            response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(SubmittingOrg.objects.count(), 1)
        submittingorg = SubmittingOrg.objects.order_by("-date_created").first()
        self.assertEqual(submittingorg.sort_order, 0)


class TestSubmittingOrgRetrieveUpdateDestroyView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.submissionset = SubmissionSetFactory(project=self.project)
        self.organisation = OrganisationFactory()
        self.submittingorg = SubmittingOrgFactory(
            organisation=self.organisation, submission_set=self.submissionset
        )

    def test_retrieve(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submittingorg": self.submittingorg.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "organisation": str(self.organisation.sodar_uuid),
                "sodar_uuid": str(self.submittingorg.sodar_uuid),
                "sort_order": self.submittingorg.sort_order,
                "submission_set": str(self.submissionset.sodar_uuid),
            }
        )
        expected.assert_matches(res_json)

    def test_update(self):
        organisation2 = OrganisationFactory()
        url = reverse(
            "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submittingorg": self.submittingorg.sodar_uuid,
            },
        )
        data = {
            "date_created": RE_DATETIME,
            "date_modified": RE_DATETIME,
            "sort_order": 42,
            "organisation": str(organisation2.sodar_uuid),
            "sodar_uuid": str(self.submittingorg.sodar_uuid),
            "submission_set": str(self.submissionset.sodar_uuid),
        }

        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile({**data})
        expected.assert_matches(res_json)

    def test_destroy(self):
        url = reverse(
            "clinvar_export:ajax-submittingorg-retrieve-update-destroy",
            kwargs={
                "project": self.project.sodar_uuid,
                "submittingorg": self.submittingorg.sodar_uuid,
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(SubmittingOrg.objects.count(), 0)


class TestQueryOmimAjaxViews(TestProjectAPIPermissionBase):
    def test_query(self):
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
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        lst = [x.strip() for x in hpo_record.name.split(";") if x.strip()]
        expected = jsonmatch.compile(
            {
                "query": hpo_record.database_id,
                "result": [
                    {"term_id": hpo_record.database_id, "term_name": lst[2]},
                    {"term_id": hpo_record.database_id, "term_name": lst[0]},
                    {"term_id": hpo_record.database_id, "term_name": lst[1]},
                ],
            }
        )
        expected.assert_matches(res_json)


class TestQueryHpoAjaxViews(TestProjectAPIPermissionBase):
    def test_query(self):
        hpo_name_record = HpoNameFactory()
        url = (
            reverse(
                "clinvar_export:query-hpo-term",
                kwargs={
                    "project": self.project.sodar_uuid,
                },
            )
            + "?query="
            + hpo_name_record.hpo_id
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "query": hpo_name_record.hpo_id,
                "result": [{"term_id": hpo_name_record.hpo_id, "term_name": hpo_name_record.name}],
            }
        )
        expected.assert_matches(res_json)


class TestAnnotatedSmallVariantsAjaxViews(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.family = Family.objects.get_or_create_in_project(project=self.project, case=self.case)
        self.small_variant = SmallVariantFactory(case_id=self.case.id)
        kwargs = {
            key: getattr(self.small_variant, key)
            for key in ("release", "chromosome", "start", "end", "bin", "reference", "alternative")
        }
        self.comment = SmallVariantCommentFactory(user=self.superuser, case=self.case, **kwargs)
        self.flags = SmallVariantFlagsFactory(case=self.case, **kwargs)
        self.rating = AcmgCriteriaRatingFactory(user=self.superuser, case=self.case, **kwargs)

    def test_query(self):
        url = reverse(
            "clinvar_export:user-annotations",
            kwargs={"project": self.project.sodar_uuid, "family": self.family.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "acmg_criteria_rating": [
                    {
                        "alternative": self.small_variant.alternative,
                        "ba1": 0,
                        "bp1": 0,
                        "bp2": 0,
                        "bp3": 0,
                        "bp4": 0,
                        "bp6": 0,
                        "bp7": 0,
                        "bs2": 0,
                        "bs3": 0,
                        "bs4": 0,
                        "case_name": self.case.name,
                        "chromosome": self.small_variant.chromosome,
                        "class_auto": None,
                        "class_override": None,
                        "end": self.small_variant.end,
                        "pm1": 0,
                        "pm2": 0,
                        "pm3": 0,
                        "pm4": 0,
                        "pm5": 0,
                        "pm6": 0,
                        "pp1": 0,
                        "pp2": 0,
                        "pp3": 0,
                        "pp4": 0,
                        "pp5": 0,
                        "ps1": 0,
                        "ps2": 0,
                        "ps3": 0,
                        "ps4": 0,
                        "pvs1": 0,
                        "reference": self.small_variant.reference,
                        "release": "GRCh37",
                        "sodar_uuid": RE_UUID4,
                        "start": self.small_variant.start,
                        "user": "superuser",
                    }
                ],
                "small_variant_comments": [
                    {
                        "alternative": self.small_variant.alternative,
                        "case_name": self.case.name,
                        "chromosome": self.small_variant.chromosome,
                        "end": self.small_variant.end,
                        "reference": self.small_variant.reference,
                        "release": "GRCh37",
                        "sodar_uuid": RE_UUID4,
                        "start": self.small_variant.start,
                        "text": self.comment.text,
                        "user": self.comment.user.username,
                    }
                ],
                "small_variant_flags": [
                    {
                        "alternative": self.small_variant.alternative,
                        "case_name": self.case.name,
                        "chromosome": self.small_variant.chromosome,
                        "end": self.small_variant.end,
                        "flag_bookmarked": True,
                        "flag_candidate": False,
                        "flag_doesnt_segregate": False,
                        "flag_final_causative": False,
                        "flag_for_validation": False,
                        "flag_molecular": "",
                        "flag_no_disease_association": False,
                        "flag_phenotype_match": "",
                        "flag_segregates": False,
                        "flag_summary": "",
                        "flag_validation": "",
                        "flag_visual": "",
                        "reference": self.small_variant.reference,
                        "release": "GRCh37",
                        "sodar_uuid": RE_UUID4,
                        "start": self.small_variant.start,
                    }
                ],
                "small_variants": [
                    {
                        "alternative": self.small_variant.alternative,
                        "case_name": self.case.name,
                        "chromosome": self.small_variant.chromosome,
                        "chromosome_no": self.small_variant.chromosome_no,
                        "end": self.small_variant.end,
                        "ensembl_effect": ["synonymous_variant"],
                        "ensembl_exon_dist": 0,
                        "ensembl_gene_id": self.small_variant.ensembl_gene_id,
                        "ensembl_gene_symbol": None,
                        "ensembl_hgvs_c": self.small_variant.ensembl_hgvs_c,
                        "ensembl_hgvs_p": self.small_variant.ensembl_hgvs_p,
                        "ensembl_transcript_coding": self.small_variant.ensembl_transcript_coding,
                        "ensembl_transcript_id": self.small_variant.ensembl_transcript_id,
                        "genotype": self.small_variant.genotype,
                        "reference": self.small_variant.reference,
                        "refseq_effect": ["synonymous_variant"],
                        "refseq_exon_dist": 0,
                        "refseq_gene_id": self.small_variant.refseq_gene_id,
                        "refseq_gene_symbol": None,
                        "refseq_hgvs_c": self.small_variant.refseq_hgvs_c,
                        "refseq_hgvs_p": self.small_variant.refseq_hgvs_p,
                        "refseq_transcript_coding": self.small_variant.refseq_transcript_coding,
                        "refseq_transcript_id": self.small_variant.refseq_transcript_id,
                        "release": "GRCh37",
                        "start": self.small_variant.start,
                    }
                ],
            }
        )
        expected.assert_matches(res_json)


class TestOrganisationAjaxViews(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.clinvar_report = ClinVarReportFactory(submission_set__project=self.project)

    def test_list(self):
        url = reverse(
            "clinvar_export:clinvar-report-list",
            kwargs={"submissionset": self.clinvar_report.submission_set.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                **model_to_dict(self.clinvar_report, exclude=["id"]),
                "sodar_uuid": str(self.clinvar_report.sodar_uuid),
                "date_created": self.clinvar_report.date_created.strftime(TIMEF),
                "date_modified": self.clinvar_report.date_modified.strftime(TIMEF),
                "submission_set": str(self.clinvar_report.submission_set.sodar_uuid),
            }
        )
        expected0.assert_matches(res_json[0])


class SubmissionSetRenderClinvarXml(TestProjectAPIPermissionBase):
    """Test for rendering ClinVar XML."""

    def setUp(self):
        super().setUp()
        self.submission = SubmissionFactory(submission_set__project=self.project)

    def test(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-clinvar-xml",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": str(self.submission.submission_set.sodar_uuid),
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        text = response.content.decode("utf-8")
        self.assertTrue(text.startswith("<ClinvarSubmissionSet"))
        self.assertTrue(text.endswith("</ClinvarSubmissionSet>\n"))


class SubmissionSetValidateClinvarXml(TestProjectAPIPermissionBase):
    """Test for validating ClinVar XML."""

    def setUp(self):
        super().setUp()
        self.submissionindividual = SubmissionIndividualFactory(
            submission__submission_set__project=self.project
        )
        self.submission = self.submissionindividual.submission

    def test(self):
        url = reverse(
            "clinvar_export:ajax-submissionset-clinvar-validate",
            kwargs={
                "project": self.project.sodar_uuid,
                "submissionset": str(self.submission.submission_set.sodar_uuid),
            },
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), {"valid": True})


CLINVAR_SUBMITTER_REPORT_RECORD = {
    "Your_variant_id": "",
    "VariantID": "1064649",
    "AlleleID": "1052897",
    "Your_record_id": "f86d55c2-fe65-43e8-9920-3c9b22b1195b",
    "SCV": "SCV001571589.1",
    "RCV": "RCV001374665.1",
    "Your_variant_description": (
        '"<SequenceLocation Assembly="GRCh37" Chr="12" start="109536396" stop="109536397" '
        'referenceAllele="TG" alternateAllele="T"/>'
    ),
    "Preferred_variant_name": "NM_080911.3(UNG):c.294del (p.Ser97_Trp98insTer)",
    "Your_condition_name": "",
    "Your_condition_identifier": "OMIM:608106",
    "ClinVar_condition_name": "Hyper-IgM syndrome type 5",
    "Assigned_Concept_ID": "C1720958",
    "Clinical_significance": "Pathogenic",
    "Date_last_evaluated": "Apr 07, 2021",
    "Assertion_criteria": "ACMG Guidelines, 2015",
    "Submission_date": "Apr 07, 2021",
    "Submitted_gene": "UNG",
    "Novelty": "new allele",
    "Status": "current",
    "Info": "",
    "Invalid": "",
}

CLINVAR_ERROR_REPORT_RECORD = {
    "Your VariantID": "No local_id submitted",
    "RecordID": "af55859f-2008-4160-9a5d-387ce82c7940",
    "Accession": "na",
    "SubmissionStatus": "novel",
    "Submitted HGVS": "not submitted",
    "Submitted location": (
        '<SequenceLocation Assembly="GRCh37" Chr="7" start="2985588" stop="2985588" '
        'referenceAllele="G" alternateAllele="A"/>'
    ),
    "Condition identifiers": "OMIM:617638",
    "Info": (
        "- This record is submitted as novel but it should be submitted as an update, including "
        "the SCV accession, because your organization previously submitted SCV002574813 for the "
        "same variant and condition."
    ),
}


class FetchClinVarReportApiViewHelpersTest(TestProjectAPIPermissionBase):
    """Test the helpers for ``FetchClinVarReportApiView``."""

    maxDiff = None

    def test_guess_clinvar_report_type_submitter(self):
        self.assertEqual(
            views_ajax.guess_clinvar_report_type(CLINVAR_SUBMITTER_REPORT_HEADER),
            views_ajax.SUBMITTER_REPORT,
        )

    def test_guess_clinvar_report_type_error(self):
        self.assertEqual(
            views_ajax.guess_clinvar_report_type(CLINVAR_ERROR_REPORT_HEADER),
            views_ajax.ERROR_REPORT,
        )

    def test_parse_clinvar_tsv_submitter(self):
        report_text = CLINVAR_SUBMITTER_REPORT_HEADER + "\t".join(
            CLINVAR_SUBMITTER_REPORT_RECORD.values()
        )
        result = views_ajax.parse_clinvar_tsv(report_text)
        self.assertEqual(len(result), 1)
        self.assertDictEqual(result[0], CLINVAR_SUBMITTER_REPORT_RECORD)

    def test_parse_clinvar_tsv_error(self):
        report_text = CLINVAR_ERROR_REPORT_HEADER + "\t".join(CLINVAR_ERROR_REPORT_RECORD.values())
        result = views_ajax.parse_clinvar_tsv(report_text)
        self.assertEqual(len(result), 1)

        self.assertDictEqual(result[0], CLINVAR_ERROR_REPORT_RECORD)

    def test_checked_report_url(self):
        report_url = "https://example.com/some/api"
        with self.assertRaises(ParseError):
            views_ajax.checked_report_url(report_url)

    @requests_mock.Mocker()
    def test_fetch_clinvar_report_good(self, r_mock):
        report_url = CLINVAR_SUBMISSION_URL_PREFIX + "some/suffix"
        report_content = CLINVAR_SUBMITTER_REPORT_HEADER + "\t".join(
            CLINVAR_SUBMITTER_REPORT_RECORD.values()
        )
        r_mock.get(
            report_url,
            status_code=200,
            text=report_content,
        )
        result = views_ajax.fetch_clinvar_report(report_url)
        self.assertEqual(result, report_content)


class FetchClinVarReportApiViewTest(TestProjectAPIPermissionBase):
    """Test the ``FetchClinVarReportApiView`` itself."""

    def setUp(self):
        super().setUp()
        self.submission = SubmissionFactory(submission_set__project=self.project)
        self.submission_set = self.submission.submission_set

    @requests_mock.Mocker()
    def test_fetch_submitter_report_with_submitter_report(self, r_mock):
        report_url = CLINVAR_SUBMISSION_URL_PREFIX + "some/suffix"
        record = {
            **CLINVAR_SUBMITTER_REPORT_RECORD,
            "Your_record_id": str(self.submission.sodar_uuid),
        }
        report_content = CLINVAR_SUBMITTER_REPORT_HEADER + "\t".join(record.values())
        r_mock.get(
            report_url,
            status_code=200,
            text=report_content,
        )
        url = reverse(
            "clinvar_export:clinvar-report-fetch",
            kwargs={
                "submissionset": str(self.submission_set.sodar_uuid),
            },
        )

        self.assertEqual(ClinVarReport.objects.count(), 0)

        with self.login(self.contributor_as.user):
            response = self.client.post(url, {"report_url": report_url})
        self.assertEqual(response.status_code, 204)

        clinvar_report = ClinVarReport.objects.all()[0]
        self.assertEqual(clinvar_report.source_url, report_url)
        self.assertEqual(clinvar_report.payload, report_content)

        self.submission.refresh_from_db()
        self.assertEquals(self.submission.clinvar_submitter_report, record)
        self.assertEquals(self.submission.clinvar_error_report, None)

    @requests_mock.Mocker()
    def test_fetch_submitter_report_with_error_report(self, r_mock):
        report_url = CLINVAR_SUBMISSION_URL_PREFIX + "some/suffix"
        record = {
            **CLINVAR_ERROR_REPORT_RECORD,
            "RecordID": str(self.submission.sodar_uuid),
        }
        report_content = CLINVAR_ERROR_REPORT_HEADER + "\t".join(record.values())
        r_mock.get(
            report_url,
            status_code=200,
            text=report_content,
        )
        url = reverse(
            "clinvar_export:clinvar-report-fetch",
            kwargs={
                "submissionset": str(self.submission_set.sodar_uuid),
            },
        )

        self.assertEqual(ClinVarReport.objects.count(), 0)

        with self.login(self.contributor_as.user):
            response = self.client.post(url, {"report_url": report_url})
        self.assertEqual(response.status_code, 204)

        clinvar_report = ClinVarReport.objects.all()[0]
        self.assertEqual(clinvar_report.source_url, report_url)
        self.assertEqual(clinvar_report.payload, report_content)

        self.submission.refresh_from_db()
        self.assertEquals(self.submission.clinvar_submitter_report, None)
        self.assertEquals(self.submission.clinvar_error_report, record)
