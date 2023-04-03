"""Common helper code for tests"""

import copy

from test_plus import TestCase

from variants.helpers import get_engine


class TestBase(TestCase):
    """Helper base class for the ``svs`` test."""

    #: Callable that sets up the database with the case to use in the test
    setup_case_in_db = None
    #: Set this value to the base query settings to patch
    base_query_settings = None

    def setUp(self):
        self.maxDiff = None  # show full diff
        if self.__class__.setup_case_in_db:
            self.__class__.setup_case_in_db()

    def assertUUIDEquals(self, first, second, msg=None):
        self.assertEqual(str(first), str(second), msg)


class StructuralVariantQueryTestBase(TestBase):
    """Base class for model support queries."""

    def _get_fetch_and_query(self, query_class, case, query_settings):
        merged_query_settings = copy.deepcopy(self.__class__.base_query_settings or {})
        merged_query_settings.update(query_settings)

        engine = get_engine()

        def fetch_case_and_query():
            """Helper function that fetches the ``case`` by UUID and then generates the
            appropriate query.
            """
            query = query_class(case, engine)
            return query.run(merged_query_settings)

        return fetch_case_and_query

    def run_query(self, *, query_class, case, query_settings, expected_count, assert_raises=None):
        """Run query returning a collection of filtration results with ``query_class``.

        This is a helper to be called in all ``test_*()`` functions.  It is a shortcut
        to the following:

        - Create a query settings ``dict`` by patching ``self.__class__.base_query_settings``
          with ``query_settings_patch``.
        - Perform the query.
        - Assert that exactly ``expected_count`` elements are returned (and return list of these
          elements for further testing).
        - If ``assert_raises`` evaluates as ``True`` then instead of checking the result
          length and returning a list of elements, assert that an exception of type
          ``assert_raises`` is raised.
        """
        fetch_case_and_query = self._get_fetch_and_query(query_class, case, query_settings)
        if assert_raises:
            with self.assertRaises(assert_raises):
                fetch_case_and_query()
        else:
            result_wrapper = fetch_case_and_query()
            self.assertEquals(expected_count, len(result_wrapper.result_rows))
            return result_wrapper
