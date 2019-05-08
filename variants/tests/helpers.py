"""Common helper code for tests"""

import aldjemy.core
from django.test import TestCase

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


class TestBase(TestCase):
    """Base class for all tests."""

    #: Callable that sets up the database with the case to use in the test
    # TODO: remove this in favour of factory boy?
    setup_case_in_db = None
    #: Set this value to the base cleaned data to patch
    # TODO: remove this in favour of factory boy?
    base_cleaned_data = None

    def setUp(self):
        self.maxDiff = None  # show full diff
        if self.__class__.setup_case_in_db:
            self.__class__.setup_case_in_db()


class QueryTestBase(TestBase):
    """Base class with helper code for model queries."""

    def run_get_query(self, model, query, assert_raises=None):
        """Run query using ``get()``."""
        if assert_raises:
            with self.assertRaises(assert_raises):
                model.objects.get(**query)
        else:
            return model.objects.get(**query)

    def run_filter_query(self, model, query_data, length):
        """Run query using ``filter()``."""
        results = model.objects.filter(**query_data)
        self.assertEquals(length, len(results))
        return results
