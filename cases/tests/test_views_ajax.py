from copy import deepcopy
import re

from django.urls import reverse
import jsonmatch
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.tests.factories import (
    CaseCommentsFactory,
    CaseFactory,
    CaseGeneAnnotationEntryFactory,
)

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestCaseAjaxView(TestProjectAPIPermissionBase):
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
                "release": "GRCh37",
                "sex_errors": {},
                "sodar_uuid": RE_UUID4,
                "status": "initial",
                "svannotationreleaseinfo_set": [],
                "tags": [],
            }
        )
        expected0.assert_matches(res_json[0])


class TestCaseCommentAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case_comment = CaseCommentsFactory(case__project=self.project)

    def test_get(self):
        url = reverse(
            "cases:ajax-casecomment-list", kwargs={"case": self.case_comment.case.sodar_uuid}
        )
        with self.login(self.contributor_as.user):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                "case": str(self.case_comment.case.sodar_uuid),
                "comment": self.case_comment.comment,
                "date_created": self.case_comment.date_created.strftime(TIMEF),
                "date_modified": self.case_comment.date_modified.strftime(TIMEF),
                "sodar_uuid": str(self.case_comment.sodar_uuid),
                "user": None,
            }
        )
        expected0.assert_matches(res_json[0])


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
