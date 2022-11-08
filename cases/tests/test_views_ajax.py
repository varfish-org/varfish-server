from copy import deepcopy
import json
import re

from django.urls import reverse
import jsonmatch
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.models import CaseComments, CasePhenotypeTerms
from variants.tests.factories import (
    CaseCommentsFactory,
    CaseFactory,
    CaseGeneAnnotationEntryFactory,
    CasePhenotypeTermsFactory,
    PresetSetFactory,
)

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestCaseListAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        url = reverse("cases:ajax-case-list", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0_pedigree = deepcopy(self.case.pedigree)
        for entry in expected0_pedigree:
            entry["name"] = entry["patient"]
            entry.pop("patient")
        expected0 = jsonmatch.compile(
            {
                "annotationreleaseinfo_set": [],
                "casealignmentstats": None,
                "casevariantstats": {},
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "index": self.case.index,
                "name": self.case.name,
                "notes": "",
                "num_small_vars": None,
                "num_svs": None,
                "pedigree": expected0_pedigree,
                "phenotype_terms": [],
                "project": str(self.project.sodar_uuid),
                "relatedness": [],
                "release": self.case.release,
                "sex_errors": {},
                "sodar_uuid": RE_UUID4,
                "status": "initial",
                "svannotationreleaseinfo_set": [],
                "tags": [],
            }
        )
        expected0.assert_matches(res_json[0])


class TestCaseUpdateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.presetset = PresetSetFactory(project=self.project)

    def test_patch_set_presetset_null(self):
        url = reverse("cases:ajax-case-update", kwargs={"case": self.case.sodar_uuid})
        data = {"presetset": ""}
        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertIsNone(res_json.get("presetset"))
        self.case.refresh_from_db()
        self.assertIsNone(self.case.presetset_id)

    def test_patch_set_presetset_not_null(self):
        url = reverse("cases:ajax-case-update", kwargs={"case": self.case.sodar_uuid})
        data = {"presetset": str(self.presetset.sodar_uuid)}
        with self.login(self.contributor_as.user):
            response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(res_json["presetset"], str(self.presetset.sodar_uuid))


class TestCasePhenotypeTermsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)

    def test_get(self):
        casephenotypeterms = CasePhenotypeTermsFactory(case=self.case)
        url = reverse(
            "cases:ajax-casephenotypeterms-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                "case": str(casephenotypeterms.case.sodar_uuid),
                "individual": casephenotypeterms.individual,
                "date_created": casephenotypeterms.date_created.strftime(TIMEF),
                "date_modified": casephenotypeterms.date_modified.strftime(TIMEF),
                "sodar_uuid": str(casephenotypeterms.sodar_uuid),
                "terms": casephenotypeterms.terms,
            }
        )
        expected0.assert_matches(res_json[0])

    def test_post(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-listcreate",
            kwargs={"case": self.case.sodar_uuid},
        )

        casephenotypeterms_other = CasePhenotypeTermsFactory.build(
            individual=self.case.pedigree[0]["patient"]
        )
        self.assertEqual(CasePhenotypeTerms.objects.count(), 0)

        with self.login(self.contributor_as.user):
            response = self.client.post(
                url,
                {
                    "individual": casephenotypeterms_other.individual,
                    "terms": json.dumps(casephenotypeterms_other.terms),
                },
            )

        self.assertEqual(response.status_code, 201)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.case.sodar_uuid),
                "individual": casephenotypeterms_other.individual,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "sodar_uuid": RE_UUID4,
                "terms": casephenotypeterms_other.terms,
            }
        )
        expected.assert_matches(res_json)

        self.assertEqual(CasePhenotypeTerms.objects.count(), 1)


class TestCasePhenotypeTermsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.casephenotypeterms = CasePhenotypeTermsFactory(case=self.case)

    def test_get(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs={"casephenotypeterms": self.casephenotypeterms.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.casephenotypeterms.case.sodar_uuid),
                "individual": self.casephenotypeterms.individual,
                "date_created": self.casephenotypeterms.date_created.strftime(TIMEF),
                "date_modified": self.casephenotypeterms.date_modified.strftime(TIMEF),
                "sodar_uuid": str(self.casephenotypeterms.sodar_uuid),
                "terms": self.casephenotypeterms.terms,
            }
        )
        expected.assert_matches(res_json)

    def test_patch(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs={"casephenotypeterms": self.casephenotypeterms.sodar_uuid},
        )

        casephenotypeterms_other = CasePhenotypeTermsFactory.build()
        self.assertEqual(CasePhenotypeTerms.objects.count(), 1)

        with self.login(self.contributor_as.user):
            response = self.client.patch(url, {"terms": json.dumps(casephenotypeterms_other.terms)})

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.casephenotypeterms.case.sodar_uuid),
                "individual": self.casephenotypeterms.individual,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "sodar_uuid": str(self.casephenotypeterms.sodar_uuid),
                "terms": casephenotypeterms_other.terms,
            }
        )
        expected.assert_matches(res_json)

        self.assertEqual(CasePhenotypeTerms.objects.count(), 1)

    def test_delete(self):
        url = reverse(
            "cases:ajax-casephenotypeterms-retrieveupdatedestroy",
            kwargs={"casephenotypeterms": self.casephenotypeterms.sodar_uuid},
        )

        self.assertEqual(CasePhenotypeTerms.objects.count(), 1)

        with self.login(self.contributor_as.user):
            response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(CasePhenotypeTerms.objects.count(), 0)


class TestCaseCommentListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.casecomment = CaseCommentsFactory(case__project=self.project)

    def test_get(self):
        url = reverse(
            "cases:ajax-casecomment-listcreate", kwargs={"case": self.casecomment.case.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                "case": str(self.casecomment.case.sodar_uuid),
                "comment": self.casecomment.comment,
                "date_created": self.casecomment.date_created.strftime(TIMEF),
                "date_modified": self.casecomment.date_modified.strftime(TIMEF),
                "sodar_uuid": str(self.casecomment.sodar_uuid),
                "user": None,
            }
        )
        expected0.assert_matches(res_json[0])

    def test_post(self):
        url = reverse(
            "cases:ajax-casecomment-listcreate", kwargs={"case": self.casecomment.case.sodar_uuid}
        )

        case_comment_other = CaseCommentsFactory.build()
        self.assertEqual(CaseComments.objects.count(), 1)

        with self.login(self.contributor_as.user):
            response = self.client.post(url, {"comment": case_comment_other.comment})

        self.assertEqual(response.status_code, 201)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.casecomment.case.sodar_uuid),
                "comment": case_comment_other.comment,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "sodar_uuid": RE_UUID4,
                "user": self.contributor_as.user.username,
            }
        )
        expected.assert_matches(res_json)

        self.assertEqual(CaseComments.objects.count(), 2)


class TestCaseCommentRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.casecomment = CaseCommentsFactory(
            user=self.contributor_as.user, case__project=self.project
        )

    def test_get(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.casecomment.case.sodar_uuid),
                "comment": self.casecomment.comment,
                "date_created": self.casecomment.date_created.strftime(TIMEF),
                "date_modified": self.casecomment.date_modified.strftime(TIMEF),
                "sodar_uuid": str(self.casecomment.sodar_uuid),
                "user": self.casecomment.user.username,
            }
        )
        expected.assert_matches(res_json)

    def test_patch(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )

        case_comment_other = CaseCommentsFactory.build()
        self.assertEqual(CaseComments.objects.count(), 1)

        with self.login(self.contributor_as.user):
            response = self.client.patch(url, {"comment": case_comment_other.comment})

        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        expected = jsonmatch.compile(
            {
                "case": str(self.casecomment.case.sodar_uuid),
                "comment": case_comment_other.comment,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "sodar_uuid": RE_UUID4,
                "user": self.contributor_as.user.username,
            }
        )
        expected.assert_matches(res_json)

        self.assertEqual(CaseComments.objects.count(), 1)

    def test_delete(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )

        self.assertEqual(CaseComments.objects.count(), 1)

        with self.login(self.contributor_as.user):
            response = self.client.delete(url)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(CaseComments.objects.count(), 0)


class TestCaseGeneAnnotationListAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case_gene_annotation = CaseGeneAnnotationEntryFactory(case__project=self.project)

    def test_get(self):
        url = reverse(
            "cases:ajax-casegeneannotation-list",
            kwargs={"case": self.case_gene_annotation.case.sodar_uuid},
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                "annotation": self.case_gene_annotation.annotation,
                "case": str(self.case_gene_annotation.case.sodar_uuid),
                "ensembl_gene_id": self.case_gene_annotation.ensembl_gene_id,
                "entrez_id": self.case_gene_annotation.entrez_id,
                "gene_symbol": self.case_gene_annotation.gene_symbol,
                "sodar_uuid": str(self.case_gene_annotation.sodar_uuid),
            }
        )
        expected0.assert_matches(res_json[0])


class TestProjectUserPermissionsAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()

    def test_get_with_superuser(self):
        users = [
            self.superuser,
        ]
        expected_perms = [
            "cases.view_data",
            "cases.add_case",
            "cases.update_case",
            "cases.sync_remote",
            "cases.delete_case",
        ]

        url = reverse(
            "cases:ajax-userpermissions",
            kwargs={"project": self.project.sodar_uuid},
        )
        for user in users:
            with self.login(user):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, expected_perms, f"user={user}")

    def test_get_with_powerful_users(self):
        users = [
            self.owner_as_cat.user,
            self.owner_as.user,
            self.delegate_as.user,
            self.contributor_as.user,
        ]
        expected_perms = [
            "cases.view_data",
            "cases.add_case",
            "cases.update_case",
            "cases.sync_remote",
        ]

        url = reverse(
            "cases:ajax-userpermissions",
            kwargs={"project": self.project.sodar_uuid},
        )
        for user in users:
            with self.login(user):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, expected_perms, f"user={user}")

    def test_get_with_guest_user(self):
        users = [
            self.guest_as.user,
        ]
        expected_perms = ["cases.view_data"]

        url = reverse(
            "cases:ajax-userpermissions",
            kwargs={"project": self.project.sodar_uuid},
        )
        for user in users:
            with self.login(user):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, expected_perms, f"user={user}")

    def test_get_with_other_users(self):
        users = [
            self.user_no_roles,
        ]
        expected_perms = []

        url = reverse(
            "cases:ajax-userpermissions",
            kwargs={"project": self.project.sodar_uuid},
        )
        for user in users:
            with self.login(user):
                response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data, expected_perms, f"user={user}")
