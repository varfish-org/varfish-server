from copy import deepcopy
import json
import re

from django.urls import reverse
import jsonmatch
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from cases.tests.factories import (
    BAM_STATS_SAMPLE,
    CaseAlignmentStatsFactory,
    PedigreeRelatednessFactory,
)
from svs.tests.factories import SvQueryResultSetFactory
from variants.models import CaseComments, CasePhenotypeTerms
from variants.tests.factories import (
    CaseCommentsFactory,
    CaseFactory,
    CaseGeneAnnotationEntryFactory,
    CasePhenotypeTermsFactory,
    CaseWithVariantSetFactory,
    PresetSetFactory,
    SampleVariantStatisticsFactory,
    SmallVariantQueryResultSetFactory,
)

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d\.\d\d\d\d\d\dZ$")

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


class TestCaseListAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.case = CaseFactory(project=self.project, presetset=self.presetset)
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            case=self.case, smallvariantquery=None
        )
        self.svqueryresultset = SvQueryResultSetFactory(case=self.case, svquery=None)

    def test_get(self):
        url = reverse("cases:ajax-case-list", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 4)
        expected0_pedigree = deepcopy(self.case.pedigree)
        for entry in expected0_pedigree:
            entry["name"] = entry["patient"]
            entry.pop("patient")
        expected0_smallvariantqueryresultset = {
            "sodar_uuid": str(self.smallvariantqueryresultset.sodar_uuid),
            "date_created": self.smallvariantqueryresultset.date_created.strftime(TIMEF),
            "date_modified": self.smallvariantqueryresultset.date_modified.strftime(TIMEF),
            "end_time": self.smallvariantqueryresultset.end_time.strftime(TIMEF),
            "start_time": self.smallvariantqueryresultset.start_time.strftime(TIMEF),
            "elapsed_seconds": self.smallvariantqueryresultset.elapsed_seconds,
            "result_row_count": self.smallvariantqueryresultset.result_row_count,
            "case": str(self.case.sodar_uuid),
        }
        expected0_svqueryresultset = {
            "sodar_uuid": str(self.svqueryresultset.sodar_uuid),
            "date_created": self.svqueryresultset.date_created.strftime(TIMEF),
            "date_modified": self.svqueryresultset.date_modified.strftime(TIMEF),
            "end_time": self.svqueryresultset.end_time.strftime(TIMEF),
            "start_time": self.svqueryresultset.start_time.strftime(TIMEF),
            "elapsed_seconds": self.svqueryresultset.elapsed_seconds,
            "result_row_count": self.svqueryresultset.result_row_count,
            "case": str(self.case.sodar_uuid),
        }
        expected0 = jsonmatch.compile(
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "case_version": 1,
                        "caseqc": None,
                        "date_created": RE_DATETIME,
                        "date_modified": RE_DATETIME,
                        "index": self.case.index,
                        "name": self.case.name,
                        "notes": "",
                        "num_small_vars": None,
                        "num_svs": None,
                        "pedigree": expected0_pedigree,
                        "project": str(self.project.sodar_uuid),
                        "presetset": str(self.presetset.sodar_uuid),
                        "release": self.case.release,
                        "sex_errors": {},
                        "sodar_uuid": RE_UUID4,
                        "state": None,
                        "status": "initial",
                        "tags": [],
                        "smallvariantqueryresultset": expected0_smallvariantqueryresultset,
                        "svqueryresultset": expected0_svqueryresultset,
                    }
                ],
            }
        )
        expected0.assert_matches(res_json)

    def test_get_querylimit(self):
        for _ in range(100):
            CaseFactory(project=self.project)

        url = reverse("cases:ajax-case-list", kwargs={"project": self.project.sodar_uuid})
        with self.login(self.user_contributor):
            # NB(2023-09-23): A call to listing all cases via AJAX triggered 47 queries, only 1 for fetching the cases.
            with self.assertNumQueriesLessThan(48):
                response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestCaseUpdateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case = CaseFactory(project=self.project)
        self.presetset = PresetSetFactory(project=self.project)

    def test_patch_set_presetset_null(self):
        url = reverse("cases:ajax-case-retrieveupdate", kwargs={"case": self.case.sodar_uuid})
        data = {"presetset": ""}
        with self.login(self.user_contributor):
            response = self.client.patch(url, data=data)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertIsNone(res_json.get("presetset"))
        self.case.refresh_from_db()
        self.assertIsNone(self.case.presetset_id)

    def test_patch_set_presetset_not_null(self):
        url = reverse("cases:ajax-case-retrieveupdate", kwargs={"case": self.case.sodar_uuid})
        data = {"presetset": str(self.presetset.sodar_uuid)}
        with self.login(self.user_contributor):
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
        with self.login(self.user_contributor):
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

        with self.login(self.user_contributor):
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
        with self.login(self.user_contributor):
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

        with self.login(self.user_contributor):
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

        with self.login(self.user_contributor):
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
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(len(res_json), 1)
        expected0 = jsonmatch.compile(
            {
                "case": str(self.casecomment.case.sodar_uuid),
                "comment": self.casecomment.comment,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
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

        with self.login(self.user_contributor):
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
                "user": self.user_contributor.username,
            }
        )
        expected.assert_matches(res_json)

        self.assertEqual(CaseComments.objects.count(), 2)


class TestCaseCommentRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.casecomment = CaseCommentsFactory(
            user=self.user_contributor, case__project=self.project
        )

    def test_get(self):
        url = reverse(
            "cases:ajax-casecomment-retrieveupdatedestroy",
            kwargs={"casecomment": self.casecomment.sodar_uuid},
        )
        with self.login(self.user_contributor):
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

        with self.login(self.user_contributor):
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
                "user": self.user_contributor.username,
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

        with self.login(self.user_contributor):
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
        with self.login(self.user_contributor):
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
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
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
            self.user_guest,
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


class TestCaseAlignmentStatsListApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.casealignmentstats = CaseAlignmentStatsFactory(case__project=self.project)
        self.case = self.casealignmentstats.case

    def test_get(self):
        url = reverse(
            "cases:ajax-casealignmentstats-list",
            kwargs={"case": self.casealignmentstats.case.sodar_uuid},
        )
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(
            res_json,
            [
                {
                    "case": str(self.case.sodar_uuid),
                    "bam_stats": {self.case.pedigree[0]["patient"]: BAM_STATS_SAMPLE},
                }
            ],
        )


class TestSampleVariantStatisticsListApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.case, variant_set, _ = CaseWithVariantSetFactory.get("small", project=self.project)
        self.samplevariantstatistics = SampleVariantStatisticsFactory(
            variant_set=variant_set, sample_name=variant_set.case.index
        )

    def test_get(self):
        url = reverse(
            "cases:ajax-casevariantstats-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.assertEqual(
            res_json,
            [
                {
                    "case": str(self.case.sodar_uuid),
                    "chrx_het_hom": 1.0,
                    "het_ratio": 1.0,
                    "ontarget_dp_quantiles": [0.1, 0.2, 0.3, 0.4, 0.5],
                    "ontarget_dps": {},
                    "ontarget_effect_counts": {},
                    "ontarget_indel_sizes": {},
                    "ontarget_indels": 1,
                    "ontarget_mnvs": 1,
                    "ontarget_snvs": 1,
                    "ontarget_transitions": 1,
                    "ontarget_transversions": 1,
                    "ontarget_ts_tv_ratio": 1.0,
                    "sample_name": self.case.pedigree[0]["patient"],
                }
            ],
        )


class TestPedigreeRelatednessListApiView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.pedigreerelatedness = PedigreeRelatednessFactory(
            stats__variant_set__case__project=self.project
        )
        self.case = self.pedigreerelatedness.stats.variant_set.case

    def test_get(self):
        url = reverse(
            "cases:ajax-caserelatedness-list",
            kwargs={"case": self.case.sodar_uuid},
        )
        with self.login(self.user_contributor):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        res_json = response.json()
        self.maxDiff = None
        self.assertEqual(
            res_json,
            [
                {
                    "case": str(self.case.sodar_uuid),
                    "het_1": 1,
                    "het_1_2": 1,
                    "het_2": 1,
                    "n_ibs0": 1,
                    "n_ibs1": 1,
                    "n_ibs2": 1,
                    "relatedness": -2.0,
                    "sample1": self.case.pedigree[0]["patient"],
                    "sample2": self.case.pedigree[0]["patient"]
                    if len(self.case.pedigree) == 1
                    else self.case.pedigree[1]["patient"],
                }
            ],
        )
