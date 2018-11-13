"""Common helper code for tests"""

import aldjemy.core
from django.test import TestCase

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


class TestBase(TestCase):
    #: Callable that sets up the database with the case to use in the test
    setup_case_in_db = None
    #: Set this value to the base cleaned data to patch
    base_cleaned_data = None

    def setUp(self):
        self.maxDiff = None  # show full diff
        self.__class__.setup_case_in_db()
