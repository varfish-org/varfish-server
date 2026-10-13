import copy

from django.forms import model_to_dict
from django.urls import reverse

from svs.models import StructuralVariantAcmgRating, StructuralVariantComment, StructuralVariantFlags
from svs.tests.factories import (
    StructuralVariantCommentFactory,
    StructuralVariantFlagsFactory,
    SvQueryFactory,
    SvQueryResultRowFactory,
    SvQueryResultSetFactory,
)
from variants.query_schemas import SCHEMA_QUERY, DefaultValidatingDraft7Validator
from variants.tests.factories import CaseFactory, CaseWithVariantSetFactory
from variants.tests.helpers import ApiViewTestBase


class TestStructuralVariantQueryBase(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get(
            "structural", project=self.project
        )

    def _construct_request_data(self, query_settings):
        """Helper to construct valid request data with defaults set based on ``query_settings``."""
        query_settings = copy.deepcopy(query_settings)
        DefaultValidatingDraft7Validator(SCHEMA_QUERY).validate(query_settings)
        request_data = {
            "name": "my test query",
            "public": True,
            "query_settings": query_settings,
        }
        return request_data


class TestStructuralVariantCommentListCreateApiView(TestStructuralVariantQueryBase):
    """Tests for case query preset generation"""

    def test_get_empty(self):
        url = reverse(
            "svs:ajax-structuralvariantcomment-listcreate", kwargs={"case": self.case.sodar_uuid}
        )
        response = self.request_knox(url)

        expected = []
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)

    def _test_get_comments_as_user(self, user):
        with self.login(user):
            StructuralVariantCommentFactory.create_batch(
                2,
                case=CaseFactory(project=self.project),
                user=self.user_contributor,
            )
            comments = StructuralVariantCommentFactory.create_batch(
                2,
                case=self.case,
                user=self.user_contributor,
            )
            url = reverse(
                "svs:ajax-structuralvariantcomment-listcreate",
                kwargs={"case": self.case.sodar_uuid},
            )
            response = self.request_knox(url)

            expected = []
            for comment in comments:
                expected.append(model_to_dict(comment, exclude=["id", "bin"]))
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


class TestStructuralVariantFlagsListCreateApiView(TestStructuralVariantQueryBase):
    """Tests for case query preset generation"""

    def test_get_empty(self):
        url = reverse(
            "svs:ajax-structuralvariantflags-listcreate", kwargs={"case": self.case.sodar_uuid}
        )
        response = self.request_knox(url)

        expected = []
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected)

    def _test_get_flags_as_user(self, user):
        with self.login(user):
            StructuralVariantFlagsFactory.create_batch(
                2,
                case=CaseFactory(project=self.project),
            )
            flags = StructuralVariantFlagsFactory.create_batch(
                2,
                case=self.case,
            )
            url = reverse(
                "svs:ajax-structuralvariantflags-listcreate",
                kwargs={"case": self.case.sodar_uuid},
            )
            response = self.request_knox(url)

            expected = []
            for flag in flags:
                expected.append(model_to_dict(flag, exclude=["id", "bin"]))
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


class TestCaseAnnotationOverviewResultRowOrigin(TestStructuralVariantQueryBase):
    """Annotations only copy a result row of the annotated case and SV into the overview.

    A rejected request does not save the annotation.
    """

    def setUp(self):
        super().setUp()
        self.coords = {
            "release": "GRCh37",
            "chromosome": "1",
            "start": 1000,
            "end": 2000,
            "sv_type": "DEL",
            "sv_sub_type": "DEL",
        }
        self.result_row = SvQueryResultRowFactory(
            svqueryresultset=SvQueryResultSetFactory(svquery=SvQueryFactory(case=self.case)),
            chromosome_no=1,
            **self.coords,
        )
        self.other_case_result_row = SvQueryResultRowFactory(
            svqueryresultset=SvQueryResultSetFactory(
                case=CaseFactory(project=self.project), svquery=None
            ),
            chromosome_no=1,
            **self.coords,
        )
        self.other_position_result_row = SvQueryResultRowFactory(
            svqueryresultset=self.result_row.svqueryresultset,
            chromosome_no=1,
            **{**self.coords, "start": 5000, "end": 6000},
        )
        self.overview = SvQueryResultSetFactory(svquery=None, case=self.case)

    def _assert_overview_rows(self, count):
        self.overview.refresh_from_db()
        self.assertEqual(self.overview.svqueryresultrow_set.count(), count)
        self.assertEqual(self.overview.result_row_count, count)

    def _create(self, url_name, data, result_row_uuid, coords=None):
        coords = coords or self.coords
        url = reverse(url_name, kwargs={"case": self.case.sodar_uuid})
        # The annotations take the coordinates from the query string.
        query = "&".join(f"{key}={value}" for key, value in coords.items())
        return self.request_knox(
            f"{url}?{query}",
            method="POST",
            data={**coords, **data, "sodar_uuid": result_row_uuid},
        )

    def _create_flags(self, result_row_uuid, coords=None):
        return self._create(
            "svs:ajax-structuralvariantflags-listcreate",
            {"flag_bookmarked": True},
            result_row_uuid,
            coords,
        )

    def test_create_flags_with_result_row_of_case(self):
        response = self._create_flags(str(self.result_row.sodar_uuid))

        self.assertEqual(response.status_code, 201)
        self._assert_overview_rows(1)

    def test_create_flags_with_breakend_result_row_of_case(self):
        """The frontend strips ``chr`` from breakends and sends the start as end."""
        result_row = SvQueryResultRowFactory(
            svqueryresultset=self.result_row.svqueryresultset,
            release="GRCh38",
            chromosome="chr1",
            chromosome_no=1,
            chromosome2="chr2",
            chromosome_no2=2,
            start=1000,
            end=3000,
            sv_type="BND",
            sv_sub_type="BND",
        )
        coords = {
            "release": "GRCh38",
            "chromosome": "1",
            "start": 1000,
            "end": 1000,
            "sv_type": "BND",
            "sv_sub_type": "BND",
        }

        response = self._create_flags(str(result_row.sodar_uuid), coords)

        self.assertEqual(response.status_code, 201)
        self._assert_overview_rows(1)

    def test_create_flags_with_mobile_element_result_row_of_case(self):
        """The frontend sends the SV type as SV sub type."""
        result_row = SvQueryResultRowFactory(
            svqueryresultset=self.result_row.svqueryresultset,
            chromosome_no=1,
            **{
                **self.coords,
                "start": 8000,
                "end": 8001,
                "sv_type": "INS",
                "sv_sub_type": "INS:ME:ALU",
            },
        )
        coords = {**self.coords, "start": 8000, "end": 8000, "sv_type": "INS", "sv_sub_type": "INS"}

        response = self._create_flags(str(result_row.sodar_uuid), coords)

        self.assertEqual(response.status_code, 201)
        self._assert_overview_rows(1)

    def test_create_flags_with_result_row_of_other_case(self):
        response = self._create_flags(str(self.other_case_result_row.sodar_uuid))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantFlags.objects.filter(case=self.case).exists())
        self._assert_overview_rows(0)

    def test_create_flags_with_result_row_at_other_position(self):
        response = self._create_flags(str(self.other_position_result_row.sodar_uuid))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantFlags.objects.filter(case=self.case).exists())
        self._assert_overview_rows(0)

    def test_create_flags_with_unknown_result_row(self):
        response = self._create_flags("00000000-0000-4000-8000-000000000000")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantFlags.objects.filter(case=self.case).exists())

    def test_create_flags_with_malformed_result_row_uuid(self):
        response = self._create_flags("not-a-uuid")

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantFlags.objects.filter(case=self.case).exists())

    def test_create_comment_with_result_row_of_other_case(self):
        response = self._create(
            "svs:ajax-structuralvariantcomment-listcreate",
            {"text": "comment"},
            str(self.other_case_result_row.sodar_uuid),
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantComment.objects.filter(case=self.case).exists())
        self._assert_overview_rows(0)

    def test_create_acmg_rating_with_result_row_of_other_case(self):
        response = self._create(
            "svs:ajax-structuralvariantacmgrating-listcreate",
            {"class_override": 3},
            str(self.other_case_result_row.sodar_uuid),
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(StructuralVariantAcmgRating.objects.filter(case=self.case).exists())
        self._assert_overview_rows(0)
