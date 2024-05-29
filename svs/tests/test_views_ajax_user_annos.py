import copy

from django.forms import model_to_dict
from django.urls import reverse

from svs.tests.factories import StructuralVariantCommentFactory, StructuralVariantFlagsFactory
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
