"""Tests for the ``svs.serializers`` module"""

import re

import jsonmatch
from test_plus import TestCase

from svs.serializers import (
    BackgroundJobSerializer,
    FilterSvBgJobSerializer,
    SvQueryResultSetSerializer,
    SvQuerySerializer,
    SvQueryWithLogsSerializer,
)
from svs.tests.factories import (
    BackgroundJobFactory,
    FilterSvBgJobFactory,
    SvQueryFactory,
    SvQueryResultSetFactory,
)
from variants.tests.factories import CaseFactory

RE_UUID4 = re.compile(r"^[0-9a-f-]+$")
RE_DATETIME = re.compile(r"^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$")


class TestBackgroundJobSerializer(TestCase):
    def setUp(self):
        super().setUp()

        self.user = self.make_user()
        self.bg_job = BackgroundJobFactory(
            user=self.user, job_type="example_job_type", name="Example job"
        )

    def test_serializer_run(self):
        serializer = BackgroundJobSerializer(self.bg_job)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.bg_job.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "status": "initial",
            }
        )
        expected.assert_matches(serializer.data)


class TestFilterSvBgJobSerializer(TestCase):
    def setUp(self):
        super().setUp()

        self.user = self.make_user()
        self.bg_job = BackgroundJobFactory(
            user=self.user, job_type="svs.filter_bg_job", name="Example job"
        )
        self.project = self.bg_job.project
        self.case = CaseFactory(project=self.project)
        self.svquery = SvQueryFactory(case=self.case)
        self.filter_sv_bg_job = FilterSvBgJobFactory(
            project=self.project, bg_job=self.bg_job, case=self.case, svquery=self.svquery
        )

    def test_serializer_run(self):
        serializer = FilterSvBgJobSerializer(self.filter_sv_bg_job)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.filter_sv_bg_job.sodar_uuid),
                "project": self.project.sodar_uuid,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "bg_job": BackgroundJobSerializer(self.bg_job).data,
                "case": self.case.sodar_uuid,
                "svquery": self.svquery.sodar_uuid,
            }
        )
        expected.assert_matches(serializer.data)


class TestSvQuerySerializer(TestCase):
    def setUp(self):
        super().setUp()

        self.user = self.make_user()
        self.case = CaseFactory()
        self.project = self.case.project
        self.svquery = SvQueryFactory(case=self.case, user=self.user)

    def test_serializer_run(self):
        serializer = SvQuerySerializer(self.svquery)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.svquery.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "case": self.case.sodar_uuid,
                "user": self.user.sodar_uuid,
                "query_state": "initial",
                "query_state_msg": None,
                "query_settings": {},
            }
        )
        expected.assert_matches(serializer.data)


class TestSvQueryWithLogsSerializer(TestCase):
    def setUp(self):
        super().setUp()

        self.user = self.make_user()
        self.case = CaseFactory()
        self.project = self.case.project
        self.svquery = SvQueryFactory(case=self.case, user=self.user)

    def test_serializer_run(self):
        serializer = SvQueryWithLogsSerializer(self.svquery)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.svquery.sodar_uuid),
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "case": self.case.sodar_uuid,
                "user": self.user.sodar_uuid,
                "query_state": "initial",
                "query_state_msg": None,
                "query_settings": {},
                "logs": [],
            }
        )
        expected.assert_matches(serializer.data)


class TestSvQueryResultSetSerializer(TestCase):
    def setUp(self):
        super().setUp()

        self.user = self.make_user()
        self.case = CaseFactory()
        self.project = self.case.project
        self.svquery = SvQueryFactory(case=self.case, user=self.user)
        self.query_result = SvQueryResultSetFactory(svquery=self.svquery)

    def test_serializer_run(self):
        serializer = SvQueryResultSetSerializer(self.query_result)
        expected = jsonmatch.compile(
            {
                "sodar_uuid": str(self.query_result.sodar_uuid),
                "svquery": self.svquery.sodar_uuid,
                "date_created": RE_DATETIME,
                "date_modified": RE_DATETIME,
                "start_time": RE_DATETIME,
                "end_time": RE_DATETIME,
                "elapsed_seconds": 3600.0,
                "result_row_count": 0,
            }
        )
        expected.assert_matches(serializer.data)
