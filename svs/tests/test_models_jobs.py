"""Tests for the ``svs.models.jobs`` module."""

from unittest.mock import patch

from bgjobs.models import BackgroundJob

from svs.models.jobs import FilterSvBgJob, create_sv_query_bg_job, run_sv_query_bg_job
from svs.models.queries import SvQuery, SvQueryResultSet
from svs.tests.factories import BackgroundSvSetFactory, StructuralVariantSetFactory, SvQueryFactory
from svs.tests.helpers import StructuralVariantQueryTestBase


class TestCreateSvQueryBgJob(StructuralVariantQueryTestBase):
    """Test the ``svs.models.queries.create_sv_query_bg_job`` function"""

    def setUp(self):
        super().setUp()
        self.variant_set = StructuralVariantSetFactory(
            case__structure="trio", case__inheritance="denovo"
        )
        self.bg_sv_set = BackgroundSvSetFactory()
        self.case = self.variant_set.case
        self.project = self.case.project
        self.user = self.make_user()
        self.svquery = SvQueryFactory(user=self.user, case=self.case, query_settings={})

    def test_run(self):
        self.assertEquals(FilterSvBgJob.objects.count(), 0)
        self.assertEquals(BackgroundJob.objects.count(), 0)
        self.assertEqual(SvQuery.objects.count(), 1)

        filter_sv_bg_job = create_sv_query_bg_job(
            case=self.case, svquery=self.svquery, user=self.user
        )

        self.assertIsNotNone(filter_sv_bg_job)
        self.assertEquals(filter_sv_bg_job.svquery.id, self.svquery.id)

        self.assertEquals(FilterSvBgJob.objects.count(), 1)
        self.assertEquals(BackgroundJob.objects.count(), 1)
        self.assertEqual(SvQuery.objects.count(), 1)
