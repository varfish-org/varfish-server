import copy

from django.forms import model_to_dict
from django.urls import reverse
from projectroles.tests.test_views_api import EMPTY_KNOX_TOKEN

from cases_qc.tests.helpers import flatten_via_json
from svs.tests.factories import SvQueryResultSetFactory

from ..query_schemas import SCHEMA_QUERY_V1, DefaultValidatingDraft7Validator
from .factories import (
    AcmgCriteriaRatingFactory,
    CaseFactory,
    CaseWithVariantSetFactory,
    SmallVariantCommentFactory,
    SmallVariantFlagsFactory,
    SmallVariantQueryFactory,
    SmallVariantQueryResultSetFactory,
)
from .helpers import VARFISH_INVALID_MIMETYPE, VARFISH_INVALID_VERSION, ApiViewTestBase

# TODO: add tests that include permission testing
from .test_views import GenerateSmallVariantResultMixin

TIMEF = "%Y-%m-%dT%H:%M:%S.%fZ"


def transmogrify_pedigree(pedigree):
    return [
        {{"patient": "name"}.get(key, key): value for key, value in m.items()} for m in pedigree
    ]


class TestCaseApiViews(ApiViewTestBase):
    """Tests for Case API views."""

    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get("small")
        self.smallvariantqueryresultset = SmallVariantQueryResultSetFactory(
            case=self.case, smallvariantquery=None
        )
        self.svqueryresultset = SvQueryResultSetFactory(case=self.case, svquery=None)

    def _expected_case_data(self, case=None, legacy=False):
        case = case or self.case
        result = {
            "sodar_uuid": str(case.sodar_uuid),
            "caseqc": None,
            "name": case.name,
            "index": case.index,
            "pedigree": transmogrify_pedigree(case.pedigree),
            "num_small_vars": case.num_small_vars,
            "num_svs": case.num_svs,
            "project": case.project.sodar_uuid,
            "notes": case.notes,
            "state": None,
            "status": case.status,
            "tags": case.tags,
            "release": case.release,
            "sex_errors": {},
            "case_version": 1,
            "smallvariantqueryresultset": {
                "sodar_uuid": str(self.smallvariantqueryresultset.sodar_uuid),
                "date_created": self.smallvariantqueryresultset.date_created.strftime(TIMEF),
                "date_modified": self.smallvariantqueryresultset.date_modified.strftime(TIMEF),
                "end_time": self.smallvariantqueryresultset.end_time.strftime(TIMEF),
                "start_time": self.smallvariantqueryresultset.start_time.strftime(TIMEF),
                "elapsed_seconds": self.smallvariantqueryresultset.elapsed_seconds,
                "result_row_count": self.smallvariantqueryresultset.result_row_count,
                "case": self.case.sodar_uuid,
            },
            "svqueryresultset": {
                "sodar_uuid": str(self.svqueryresultset.sodar_uuid),
                "date_created": self.svqueryresultset.date_created.strftime(TIMEF),
                "date_modified": self.svqueryresultset.date_modified.strftime(TIMEF),
                "end_time": self.svqueryresultset.end_time.strftime(TIMEF),
                "start_time": self.svqueryresultset.start_time.strftime(TIMEF),
                "elapsed_seconds": self.svqueryresultset.elapsed_seconds,
                "result_row_count": self.svqueryresultset.result_row_count,
                "case": self.case.sodar_uuid,
            },
        }
        if legacy:
            result.pop("caseqc")
            result.update(
                {
                    "relatedness": [],
                    "phenotype_terms": [],
                    "svannotationreleaseinfo_set": [],
                    "annotationreleaseinfo_set": [],
                    "casealignmentstats": None,
                    "casevariantstats": {},
                }
            )
        return result

    def _test_list_with_invalid_x(self, media_type=None, version=None):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "cases:api-case-list",
                    kwargs={"project": self.case.project.sodar_uuid},
                ),
                media_type=media_type,
                version=version,
            )
        self.assertEqual(response.status_code, 406)

    def test_list_with_invalid_version(self):
        self._test_list_with_invalid_x(version=VARFISH_INVALID_VERSION)

    def test_list_with_invalid_media_type(self):
        self._test_list_with_invalid_x(media_type=VARFISH_INVALID_MIMETYPE)

    def test_list(self):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "cases:api-case-list",
                    kwargs={"project": str(self.case.project.sodar_uuid)},
                ),
            )

            self.assertEqual(response.status_code, 200, response.content)
            expected = [self._expected_case_data()]
            response_content = []
            for entry in response.data["results"]:  # remove some warts
                entry = dict(entry)
                entry.pop("date_created")  # complex; not worth testing
                entry.pop("date_modified")  # the same
                response_content.append(entry)
            self.assertEquals(flatten_via_json(response_content), flatten_via_json(expected))

    def _test_retrieve_with_invalid_x(self, media_type=None, version=None):
        with self.login(self.superuser):
            response = self.request_knox(
                reverse(
                    "variants:api-case-retrieve",
                    kwargs={"case": str(self.case.sodar_uuid)},
                ),
                media_type=media_type,
                version=version,
            )
        self.assertEqual(response.status_code, 406)

    def test_retrieve_with_invalid_version(self):
        self._test_retrieve_with_invalid_x(version=VARFISH_INVALID_VERSION)

    def test_retrieve_with_invalid_media_type(self):
        self._test_retrieve_with_invalid_x(media_type=VARFISH_INVALID_MIMETYPE)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:api-case-retrieve",
                    kwargs={"case": self.case.sodar_uuid},
                )
            )

            expected = self._expected_case_data(legacy=True)
            expected.pop("state")
            response.data.pop("date_created")  # complex; not worth testing
            response.data.pop("date_modified")  # the same
            self.assertEqual(response.status_code, 200)
            self.assertEqual(flatten_via_json(expected), flatten_via_json(response.data))


def small_variant_query_to_dict(query):
    return {
        "sodar_uuid": str(query.sodar_uuid),
        "date_created": query.date_created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "name": query.name,
        "case": query.case.sodar_uuid,
        "public": query.public,
        "query_settings": query.query_settings,
        "user": None if not query.user else query.user.sodar_uuid,
    }


class TestSmallVariantQueryBase(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get(
            "small", project=self.project
        )

    def _construct_request_data(self, query_settings):
        """Helper to construct valid request data with defaults set based on ``query_settings``."""
        query_settings = copy.deepcopy(query_settings)
        DefaultValidatingDraft7Validator(SCHEMA_QUERY_V1).validate(query_settings)
        request_data = {
            "name": "my test query",
            "public": True,
            "query_settings": query_settings,
        }
        return request_data


class TestSmallVariantQueryListApiView(TestSmallVariantQueryBase):
    def test_get_empty(self):
        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})
        response = self.request_knox(url)

        expected = []
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)

    def test_get_single(self):
        queries = [SmallVariantQueryFactory(case=self.case, user=self.superuser)]

        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})
        response = self.request_knox(url)

        self.assertEqual(response.status_code, 200)
        expected = list(map(small_variant_query_to_dict, queries))
        self.assertEqual(flatten_via_json(response.data), flatten_via_json(expected))

    def test_get_multiple(self):
        queries = [
            SmallVariantQueryFactory(case=self.case, user=self.superuser),
            SmallVariantQueryFactory(case=self.case, user=self.superuser),
        ]

        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})
        response = self.request_knox(url)

        self.assertEqual(response.status_code, 200)
        expected = list(reversed(list(map(small_variant_query_to_dict, queries))))
        self.assertEqual(flatten_via_json(response.data), flatten_via_json(expected))

    def test_get_other_user(self):
        _queries = [
            SmallVariantQueryFactory(case=self.case, user=self.superuser),
            SmallVariantQueryFactory(case=self.case, user=self.superuser),
        ]

        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})
        response = self.request_knox(url, token=self.get_token(self.user_guest))

        self.assertEqual(response.status_code, 200)
        expected = []
        self.assertEqual(flatten_via_json(response.data), flatten_via_json(expected))

    def test_get_admin(self):
        _queries = [
            SmallVariantQueryFactory(case=self.case, user=self.user_contributor),
            SmallVariantQueryFactory(case=self.case, user=self.user_owner),
        ]

        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})
        response = self.request_knox(url, token=self.get_token(self.superuser))

        self.assertEqual(response.status_code, 200)
        expected = []
        self.assertEqual(flatten_via_json(response.data), flatten_via_json(expected))

    def test_get_access_allowed(self):
        _queries = [
            SmallVariantQueryFactory(case=self.case, user=self.user_guest),
        ]
        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})

        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]

        for user in good_users:
            response = self.request_knox(url, token=self.get_token(user))
            self.assertEqual(response.status_code, 200, "user = %s" % user)

    def test_get_access_forbidden(self):
        _queries = [
            SmallVariantQueryFactory(case=self.case, user=self.user_guest),
        ]
        url = reverse("variants:api-query-case-list", kwargs={"case": self.case.sodar_uuid})

        bad_users = [
            None,
        ]

        for user in bad_users:
            if user:
                token = self.get_token(user)
            else:
                token = EMPTY_KNOX_TOKEN
            response = self.request_knox(url, token=token)
            self.assertEqual(response.status_code, 401, "user = %s" % user)


# TODO reuse?
# class TestSmallVariantQueryCreateApiView(TestSmallVariantQueryBase):
#     def test_post_valid(self):
#         url = reverse("variants:api-query-case-create", kwargs={"case": self.case.sodar_uuid})
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#         query_settings = {
#             "effects": ["missense_variant"],
#             "quality": {self.case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}},
#             "genotype": {self.case.index: "variant"},
#         }
#         request_data = self._construct_request_data(query_settings)
#
#         response = self.request_knox(url, method="POST", data=request_data)
#
#         self.assertEqual(response.status_code, 201)
#         self.assertEqual(SmallVariantQuery.objects.count(), 1)
#         self.assertEqual(FilterBgJob.objects.count(), 1)
#
#     def test_post_invalid_nonsense(self):
#         url = reverse("variants:api-query-case-create", kwargs={"case": self.case.sodar_uuid})
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#         request_data = {"invalid": "data"}
#         response = self.request_knox(url, method="POST", data=request_data)
#
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#     def test_post_invalid_missing_hpo_terms(self):
#         url = reverse("variants:api-query-case-create", kwargs={"case": self.case.sodar_uuid})
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#         query_settings = {
#             "effects": ["missense_variant"],
#             "quality": {self.case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}},
#             "genotype": {self.case.index: "variant"},
#             "prio_hpo_terms": ["HP:9999999"],
#         }
#         request_data = self._construct_request_data(query_settings)
#         response = self.request_knox(url, method="POST", data=request_data)
#
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#     def test_post_access_allowed(self):
#         url = reverse("variants:api-query-case-create", kwargs={"case": self.case.sodar_uuid})
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#         query_settings = {
#             "effects": ["missense_variant"],
#             "quality": {self.case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}},
#             "genotype": {self.case.index: "variant"},
#         }
#         request_data = self._construct_request_data(query_settings)
#
#         good_users = [
#             self.superuser,
#             self.user_owner,
#             self.user_delegate,
#             self.user_contributor,
#             self.user_guest,
#         ]
#
#         for i, user in enumerate(good_users):
#             response = self.request_knox(url, method="POST", data=request_data)
#
#             self.assertEqual(response.status_code, 201)
#             self.assertEqual(SmallVariantQuery.objects.count(), i + 1)
#             self.assertEqual(FilterBgJob.objects.count(), i + 1)
#
#     def test_post_access_forbidden(self):
#         url = reverse("variants:api-query-case-create", kwargs={"case": self.case.sodar_uuid})
#         self.assertEqual(SmallVariantQuery.objects.count(), 0)
#         self.assertEqual(FilterBgJob.objects.count(), 0)
#
#         query_settings = {
#             "effects": ["missense_variant"],
#             "quality": {self.case.index: {"dp_het": 10, "dp_hom": 5, "ab": 0.3, "gq": 20, "ad": 3}},
#             "genotype": {self.case.index: "variant"},
#         }
#         request_data = self._construct_request_data(query_settings)
#
#         bad_users = [
#             None,
#         ]
#
#         for user in bad_users:
#             if user:
#                 token = self.get_token(user)
#             else:
#                 token = EMPTY_KNOX_TOKEN
#             response = self.request_knox(url, method="POST", data=request_data, token=token)
#             self.assertEqual(response.status_code, 401, "user = %s" % user)


# TODO reuse for similar api view?
# class TestSmallVariantQueryRetrieveApiView(TestSmallVariantQueryBase):
#     def test_get(self):
#         query = SmallVariantQueryFactory(case=self.case, user=self.user_guest)
#         url = reverse(
#             "variants:api-query-case-retrieve", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         response = self.request_knox(url)
#
#         self.assertEqual(response.status_code, 200)
#         expected = small_variant_query_to_dict(query)
#         actual = dict(response.data)
#         self.assertEqual(actual, expected)
#
#     def test_get_access_allowed(self):
#         query = SmallVariantQueryFactory(case=self.case, user=self.user_guest)
#         url = reverse(
#             "variants:api-query-case-retrieve", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         good_users = [
#             self.superuser,
#             self.user_guest,
#         ]
#
#         for user in good_users:
#             response = self.request_knox(url, token=self.get_token(user))
#             self.assertEqual(response.status_code, 200, "user = %s" % user)
#
#     def test_get_access_forbidden(self):
#         query = SmallVariantQueryFactory(case=self.case, user=self.user_guest)
#         url = reverse(
#             "variants:api-query-case-retrieve", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         bad_users = [
#             self.user_owner,
#             self.user_delegate,
#             self.user_contributor,
#             None,
#         ]
#
#         for user in bad_users:
#             if user:
#                 token = self.get_token(user)
#                 expected = 404
#             else:
#                 token = EMPTY_KNOX_TOKEN
#                 expected = 401
#             response = self.request_knox(url, token=token)
#             self.assertEqual(response.status_code, expected, "user = %s" % user)


# TODO reuse for get query?
# class TestSmallVariantQueryStatusApiView(TestSmallVariantQueryBase):
#     def test_get(self):
#         filter_job = FilterBgJobFactory(
#             case=self.case, user=self.user_guest, bg_job__status=JOB_STATE_DONE
#         )
#         query = filter_job.smallvariantquery
#
#         url = reverse(
#             "variants:api-query-case-status", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         response = self.request_knox(url)
#
#         self.assertEqual(response.status_code, 200)
#         expected = {"status": JOB_STATE_DONE, "logs": []}
#         actual = dict(response.data)
#         self.assertEqual(actual, expected)
#
#     def test_get_access_allowed(self):
#         filter_job = FilterBgJobFactory(
#             case=self.case, user=self.user_guest, bg_job__status=JOB_STATE_DONE
#         )
#         query = filter_job.smallvariantquery
#
#         url = reverse(
#             "variants:api-query-case-status", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         good_users = [
#             self.superuser,
#             self.user_guest,
#         ]
#
#         for user in good_users:
#             response = self.request_knox(url, token=self.get_token(user))
#             self.assertEqual(response.status_code, 200, "user = %s" % user)
#
#     def test_get_access_forbidden(self):
#         filter_job = FilterBgJobFactory(
#             case=self.case, user=self.user_guest, bg_job__status=JOB_STATE_DONE
#         )
#         query = filter_job.smallvariantquery
#
#         url = reverse(
#             "variants:api-query-case-status", kwargs={"smallvariantquery": query.sodar_uuid}
#         )
#
#         bad_users = [
#             self.user_owner,
#             self.user_delegate,
#             self.user_contributor,
#             None,
#         ]
#
#         for user in bad_users:
#             if user:
#                 token = self.get_token(user)
#                 expected = 404
#             else:
#                 token = EMPTY_KNOX_TOKEN
#                 expected = 401
#             response = self.request_knox(url, token=token)
#             self.assertEqual(response.status_code, expected, "user = %s" % user)


# TODO reuse?
# class TestSmallVariantQueryFetchResultsApiView(
#     GenerateSmallVariantResultMixin, TestSmallVariantQueryBase
# ):
#     def test_get_success(self):
#         url = reverse(
#             "variants:api-query-case-fetch-results",
#             kwargs={"smallvariantquery": self.bgjob.smallvariantquery.sodar_uuid},
#         )
#         response = self.request_knox(url)
#
#         self.assertEqual(response.status_code, 200)
#         actual = {response.data[0]["start"], response.data[1]["start"]}
#         expected = {self.small_vars[0].start, self.small_vars[2].start}
#         self.assertEqual(actual, expected)
#
#     def test_get_not_ready(self):
#         self.bgjob.bg_job.status = "running"
#         self.bgjob.bg_job.save()
#
#         url = reverse(
#             "variants:api-query-case-fetch-results",
#             kwargs={"smallvariantquery": self.bgjob.smallvariantquery.sodar_uuid},
#         )
#         response = self.request_knox(url)
#
#         self.assertEqual(response.status_code, 503)
#         self.assertEqual(response.data, {"reason": "query result not available yet"})
#
#     def test_get_access_allowed(self):
#         good_users = [
#             self.superuser,
#         ]
#
#         url = reverse(
#             "variants:api-query-case-fetch-results",
#             kwargs={"smallvariantquery": self.bgjob.smallvariantquery.sodar_uuid},
#         )
#
#         for user in good_users:
#             response = self.request_knox(url, token=self.get_token(user))
#
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(len(response.data), 2)
#             actual = {response.data[0]["start"], response.data[1]["start"]}
#             expected = {self.small_vars[0].start, self.small_vars[2].start}
#             self.assertEqual(actual, expected)
#
#     def test_get_access_forbidden(self):
#         bad_users = [
#             self.user_guest,
#             self.user_owner,
#             self.user_delegate,
#             self.user_contributor,
#             None,
#         ]
#
#         url = reverse(
#             "variants:api-query-case-fetch-results",
#             kwargs={"smallvariantquery": self.bgjob.smallvariantquery.sodar_uuid},
#         )
#
#         for user in bad_users:
#             if user:
#                 token = self.get_token(user)
#                 expected = 403
#             else:
#                 token = EMPTY_KNOX_TOKEN
#                 expected = 401
#             response = self.request_knox(url, token=token)
#             self.assertEqual(response.status_code, expected, f"user = {user}")


class TestSmallVariantQuerySettingsShortcutApiView(
    GenerateSmallVariantResultMixin, ApiViewTestBase
):
    """Tests for case query preset generation"""

    def test_get_success(self):
        url = reverse(
            "variants:api-query-settings-shortcut",
            kwargs={"case": self.case.sodar_uuid},
        )
        response = self.request_knox(url)

        self.assertEqual(response.status_code, 200)
        actual = response.data
        expected = {
            "presets": {
                "label": "defaults",
                "inheritance": "any",
                "frequency": "dominant_strict",
                "impact": "aa_change_splicing",
                "quality": "strict",
                "chromosomes": "whole_genome",
                "flagsetc": "defaults",
                "database": "refseq",
            },
            "query_settings": {
                "database": "refseq",
                "recessive_index": None,
                "recessive_mode": None,
                "genotype": {f"{self.case.index}": "any"},
                "thousand_genomes_enabled": True,
                "thousand_genomes_homozygous": 0,
                "thousand_genomes_heterozygous": 4,
                "thousand_genomes_hemizygous": None,
                "thousand_genomes_frequency": 0.002,
                "exac_enabled": True,
                "exac_homozygous": 0,
                "exac_heterozygous": 10,
                "exac_hemizygous": None,
                "exac_frequency": 0.002,
                "gnomad_exomes_enabled": True,
                "gnomad_exomes_homozygous": 0,
                "gnomad_exomes_heterozygous": 20,
                "gnomad_exomes_hemizygous": None,
                "gnomad_exomes_frequency": 0.002,
                "gnomad_genomes_enabled": True,
                "gnomad_genomes_homozygous": 0,
                "gnomad_genomes_heterozygous": 4,
                "gnomad_genomes_hemizygous": None,
                "gnomad_genomes_frequency": 0.002,
                "inhouse_enabled": True,
                "inhouse_homozygous": None,
                "inhouse_heterozygous": None,
                "inhouse_hemizygous": None,
                "inhouse_carriers": 20,
                "mtdb_enabled": True,
                "mtdb_count": 10,
                "mtdb_frequency": 0.01,
                "helixmtdb_enabled": True,
                "helixmtdb_hom_count": 200,
                "helixmtdb_het_count": None,
                "helixmtdb_frequency": 0.01,
                "mitomap_enabled": False,
                "mitomap_count": None,
                "mitomap_frequency": None,
                "var_type_snv": True,
                "var_type_mnv": True,
                "var_type_indel": True,
                "transcripts_coding": True,
                "transcripts_noncoding": False,
                "max_exon_dist": None,
                "effects": [
                    "complex_substitution",
                    "direct_tandem_duplication",
                    "disruptive_inframe_deletion",
                    "disruptive_inframe_insertion",
                    "exon_loss_variant",
                    "feature_truncation",
                    "frameshift_elongation",
                    "frameshift_truncation",
                    "frameshift_variant",
                    "inframe_deletion",
                    "inframe_insertion",
                    "internal_feature_elongation",
                    "missense_variant",
                    "mnv",
                    "splice_acceptor_variant",
                    "splice_donor_variant",
                    "splice_region_variant",
                    "start_lost",
                    "stop_gained",
                    "stop_lost",
                    "structural_variant",
                    "transcript_ablation",
                ],
                "quality": {
                    f"{self.case.index}": {
                        "dp_het": 10,
                        "dp_hom": 5,
                        "ab": 0.2,
                        "gq": 10,
                        "ad": 3,
                        "ad_max": None,
                        "fail": "drop-variant",
                    },
                },
                "genomic_region": [],
                "gene_allowlist": [],
                "gene_blocklist": [],
                "clinvar_include_benign": False,
                "clinvar_include_likely_benign": False,
                "clinvar_include_likely_pathogenic": True,
                "clinvar_include_pathogenic": True,
                "clinvar_include_uncertain_significance": False,
                "flag_bookmarked": True,
                "flag_candidate": True,
                "flag_doesnt_segregate": True,
                "flag_final_causative": True,
                "flag_for_validation": True,
                "flag_no_disease_association": True,
                "flag_molecular_empty": True,
                "flag_molecular_negative": True,
                "flag_molecular_positive": True,
                "flag_molecular_uncertain": True,
                "flag_phenotype_match_empty": True,
                "flag_phenotype_match_negative": True,
                "flag_phenotype_match_positive": True,
                "flag_phenotype_match_uncertain": True,
                "flag_segregates": True,
                "flag_simple_empty": True,
                "flag_summary_empty": True,
                "flag_summary_negative": True,
                "flag_summary_positive": True,
                "flag_summary_uncertain": True,
                "flag_validation_empty": True,
                "flag_validation_negative": True,
                "flag_validation_positive": True,
                "flag_validation_uncertain": True,
                "flag_visual_empty": True,
                "flag_visual_negative": True,
                "flag_visual_positive": True,
                "flag_visual_uncertain": True,
                "remove_if_in_dbsnp": False,
                "require_in_clinvar": False,
                "require_in_hgmd_public": False,
                "clinvar_paranoid_mode": False,
            },
        }
        self.maxDiff = None
        self.assertEqual(actual, expected)

    def test_get_access_allowed(self):
        good_users = [
            self.superuser,
        ]

        url = reverse(
            "variants:api-query-settings-shortcut",
            kwargs={"case": self.case.sodar_uuid},
        )

        for user in good_users:
            response = self.request_knox(url, token=self.get_token(user))

            self.assertEqual(response.status_code, 200, f"user = {user}")

    def test_get_access_forbidden(self):
        bad_users = [
            self.user_guest,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            None,
        ]

        url = reverse(
            "variants:api-query-settings-shortcut",
            kwargs={"case": self.case.sodar_uuid},
        )

        for user in bad_users:
            if user:
                token = self.get_token(user)
                expected = 403
            else:
                token = EMPTY_KNOX_TOKEN
                expected = 401
            response = self.request_knox(url, token=token)
            self.assertEqual(response.status_code, expected, f"user = {user}")


class TestSmallVariantCommentListCreateApiView(TestSmallVariantQueryBase):
    """Tests for case query preset generation"""

    def test_get_empty(self):
        url = reverse(
            "variants:api-small-variant-comment-list-create", kwargs={"case": self.case.sodar_uuid}
        )
        response = self.request_knox(url)

        expected = []
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)

    def _test_get_comments_as_user(self, user):
        with self.login(user):
            SmallVariantCommentFactory.create_batch(
                2,
                case=CaseFactory(project=self.project),
                user=self.user_contributor,
            )
            comments = SmallVariantCommentFactory.create_batch(
                2,
                case=self.case,
                user=self.user_contributor,
            )
            url = reverse(
                "variants:api-small-variant-comment-list-create",
                kwargs={"case": self.case.sodar_uuid},
            )
            response = self.request_knox(url)

            expected = []
            for comment in comments:
                expected.append(model_to_dict(comment, exclude=["id", "bin", "chromosome_no"]))
                expected[-1]["user"] = comment.user.username
                expected[-1]["sodar_uuid"] = str(comment.sodar_uuid)
                expected[-1]["case"] = str(comment.case.sodar_uuid)

            response_json = response.json()
            for comment in response_json:
                del comment["date_created"]
                del comment["date_modified"]
                del comment["user_can_edit"]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json, expected)

    def test_get_comments_superuser(self):
        self._test_get_comments_as_user(self.superuser)

    def test_get_comments_owner(self):
        self._test_get_comments_as_user(self.user_owner)

    def test_get_comments_delegate(self):
        self._test_get_comments_as_user(self.user_delegate)

    def test_get_comments_contributor(self):
        self._test_get_comments_as_user(self.user_contributor)

    def test_get_comments_guest(self):
        self._test_get_comments_as_user(self.user_guest)


class TestSmallVariantFlagsListCreateApiView(TestSmallVariantQueryBase):
    """Tests for case query preset generation"""

    def test_get_empty(self):
        url = reverse(
            "variants:api-small-variant-flags-list-create", kwargs={"case": self.case.sodar_uuid}
        )
        response = self.request_knox(url)

        expected = []
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)

    def _test_get_flags_as_user(self, user):
        with self.login(user):
            SmallVariantFlagsFactory.create_batch(
                2,
                case=CaseFactory(project=self.project),
            )
            flags = SmallVariantFlagsFactory.create_batch(
                2,
                case=self.case,
            )
            url = reverse(
                "variants:api-small-variant-flags-list-create",
                kwargs={"case": self.case.sodar_uuid},
            )
            response = self.request_knox(url)

            expected = []
            for flag in flags:
                expected.append(model_to_dict(flag, exclude=["id", "bin", "chromosome_no"]))
                expected[-1]["sodar_uuid"] = str(flag.sodar_uuid)
                expected[-1]["case"] = str(flag.case.sodar_uuid)

            response_json = response.json()
            for comment in response_json:
                del comment["date_created"]
                del comment["date_modified"]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response_json, expected)

    def test_get_flags_superuser(self):
        self._test_get_flags_as_user(self.superuser)

    def test_get_flags_owner(self):
        self._test_get_flags_as_user(self.user_owner)

    def test_get_flags_delegate(self):
        self._test_get_flags_as_user(self.user_delegate)

    def test_get_flags_contributor(self):
        self._test_get_flags_as_user(self.user_contributor)

    def test_get_flags_guest(self):
        self._test_get_flags_as_user(self.user_guest)


class TestAcmgCriteriaRatingListCreateApiView(TestSmallVariantQueryBase):
    """Tests for case query preset generation"""

    def test_get_empty(self):
        url = reverse(
            "variants:api-acmg-criteria-rating-list-create", kwargs={"case": self.case.sodar_uuid}
        )
        response = self.request_knox(url)

        expected = {"next": None, "previous": None, "results": []}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)
        self.maxDiff = None

    def _test_get_acmg_criteria_rating_as_user(self, user):
        with self.login(user):
            AcmgCriteriaRatingFactory.create_batch(
                2,
                case=CaseFactory(project=self.project),
                user=self.user_contributor,
            )
            ratings = AcmgCriteriaRatingFactory.create_batch(
                2,
                case=self.case,
                user=self.user_contributor,
            )
            url = reverse(
                "variants:api-acmg-criteria-rating-list-create",
                kwargs={"case": self.case.sodar_uuid},
            )
            response = self.request_knox(url)

            expected = []
            for rating in ratings:
                expected.append(model_to_dict(rating, exclude=["id", "bin", "chromosome_no"]))
                expected[-1]["user"] = rating.user.username
                expected[-1]["sodar_uuid"] = str(rating.sodar_uuid)
                expected[-1]["case"] = str(rating.case.sodar_uuid)

            def get_key(record):
                return (
                    record["chromosome"],
                    record["start"],
                    record["reference"],
                    record["alternative"],
                )

            response_json = response.json()
            response_results = response_json["results"]
            for rating in response_results:
                del rating["date_created"]
                del rating["date_modified"]
                del rating["acmg_class"]

            expected.sort(key=get_key)
            response_results.sort(key=get_key)

            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response_results), 2)
            self.assertEqual(len(expected), 2)
            self.assertEqual(response_results[0], expected[0])
            self.assertEqual(response_results[1], expected[1])

    def test_get_acmg_criteria_rating_superuser(self):
        self._test_get_acmg_criteria_rating_as_user(self.superuser)

    def test_get_acmg_criteria_rating_owner(self):
        self._test_get_acmg_criteria_rating_as_user(self.user_owner)

    def test_get_acmg_criteria_rating_delegate(self):
        self._test_get_acmg_criteria_rating_as_user(self.user_delegate)

    def test_get_acmg_criteria_rating_contributor(self):
        self._test_get_acmg_criteria_rating_as_user(self.user_contributor)

    def test_get_acmg_criteria_rating_guest(self):
        self._test_get_acmg_criteria_rating_as_user(self.user_guest)
