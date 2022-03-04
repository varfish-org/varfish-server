"""Common helper code for tests"""

from django.test import RequestFactory
from test_plus.test import TestCase
from projectroles.tests.test_permissions import TestProjectPermissionBase
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase
from django.conf import settings

from beaconsite.models import Site
from beaconsite.tests.factories import ConsortiumFactory, SiteFactory

from cohorts.models import Cohort
from .factories import ProcessedFormDataFactory, ProjectFactory
from ..models import Case, CaseAwareProject
from variants.helpers import get_engine


#: A known invalid MIME type.
VARFISH_INVALID_MIMETYPE = "application/vnd.bihealth.invalid+json"
#: A known invalid version.
VARFISH_INVALID_VERSION = "0.0.0"


class TestBase(TestCase):
    """Base class for all tests."""


class ViewTestBaseMixin:
    def setUp(self):
        super().setUp()

        self.request_factory = RequestFactory()


class ApiViewTestBase(ViewTestBaseMixin, TestProjectAPIPermissionBase):
    """Base class for API view testing (and file export)"""

    media_type = settings.SODAR_API_MEDIA_TYPE
    api_version = settings.SODAR_API_DEFAULT_VERSION

    def setUp(self):
        super().setUp()

        self.knox_token = self.get_token(self.superuser)


class ViewTestBase(ViewTestBaseMixin, TestProjectPermissionBase):
    """Base class for UI view testing (and file export)"""


class QueryTestBase(TestBase):
    """Base class with helper code for model queries."""

    def run_get_query(self, model, query_data, assert_raises=None):
        """Run query using ``get()``."""
        if assert_raises:
            with self.assertRaises(assert_raises):
                model.objects.get(**query_data)
        else:
            return model.objects.get(**query_data)

    def run_filter_query(self, model, query_data, length):
        """Run query using ``filter()``."""
        results = model.objects.filter(**query_data)
        self.assertEquals(length, len(results))
        return results


class SupportQueryTestBase(TestBase):
    """Base class for model support queries."""

    def _get_fetch_and_query(self, query_class, cleaned_data_patch, query_type="case", user=None):
        engine = get_engine()

        def fetch_case_and_query():
            """Helper function that fetches the ``case`` by UUID and then generates the
            appropriate query.
            """
            if query_type == "case":
                if not "case_uuid" in cleaned_data_patch:
                    obj = Case.objects.first()
                else:
                    obj = Case.objects.get(sodar_uuid=cleaned_data_patch["case_uuid"])
                members = obj.get_members()
            elif query_type == "cohort":
                obj = Cohort.objects.first()
                members = obj.get_members(user)
            else:  # query_type == "project"
                obj = CaseAwareProject.objects.first()
                members = obj.get_members()
            patched_cleaned_data = {
                **vars(ProcessedFormDataFactory(names=members)),
                **cleaned_data_patch,
            }
            previous_query = patched_cleaned_data.get("filter_job_id", None)
            patched_cleaned_data["sodar_uuid"] = obj.sodar_uuid
            if previous_query:
                query = query_class(obj, engine, previous_query)
            else:
                if query_type == "cohort":
                    query = query_class(obj, engine, user=user)
                else:
                    query = query_class(obj, engine)
            return query.run(patched_cleaned_data)

        return fetch_case_and_query

    def run_query(
        self,
        query_class,
        cleaned_data_patch,
        length,
        assert_raises=None,
        query_type="case",
        user=None,
    ):
        """Run query returning a collection of filtration results with ``query_class``.

        This is a helper to be called in all ``test_*()`` functions.  It is a shortcut
        to the following:

        - Create a query kwargs ``dict`` by patching ``self.__class__.base_cleaned_data``
          with ``patch_cleaned_data``.
        - Perform the query.
        - Assert that exactly ``length`` elements are returned (and return list of these
          elements for further testing).
        - If ``assert_raises`` evaluates as ``True`` then instead of checking the result
          length and returning a list of elements, assert that an exception of type
          ``assert_raises`` is raised.
        """
        fetch_case_and_query = self._get_fetch_and_query(
            query_class, cleaned_data_patch, query_type, user
        )
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            results = list(fetch_case_and_query())
            self.assertEquals(length, len(results))
            return results

    def run_count_query(
        self, query_class, kwargs_patch, length, assert_raises=None, query_type="case", user=None
    ):
        """Run query returning a result record count instead of result records."""
        fetch_case_and_query = self._get_fetch_and_query(
            query_class, kwargs_patch, query_type, user
        )
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            result = fetch_case_and_query()
            self.assertEquals(length, result)
            return result


class TestViewsBase(TestCase):
    def setUp(self):
        self.superuser = self.make_user("superuser")
        self.superuser.is_superuser = True
        self.superuser.is_staff = True
        self.superuser.save()

        self.project = ProjectFactory()
        self.consortium = ConsortiumFactory()
        self.site = SiteFactory(role=Site.LOCAL, state=Site.ENABLED)
