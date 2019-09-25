"""Tests for the ``file_export`` module."""

import json
from unittest.mock import patch

from requests_mock import Mocker

from test_plus.test import TestCase

from variants.tests.factories import (
    SmallVariantSetFactory,
    SmallVariantFactory,
    FilterBgJobFactory,
    ProjectCasesFilterBgJobFactory,
    FormDataFactory,
)
from ..models import SmallVariantQuery, ProjectCasesSmallVariantQuery
from ..submit_filter import CaseFilter, ProjectCasesFilter
from variants.models import SmallVariantQueryGeneScores
from variants.models import SmallVariantQueryVariantScores
from django.conf import settings


class CaseFilterTest(TestCase):
    """Test running single-case filter job."""

    def setUp(self):
        super().setUp()
        variant_set = SmallVariantSetFactory()
        user = self.make_user("superuser")
        SmallVariantFactory.create_batch(3, variant_set=variant_set)
        self.bgjob = FilterBgJobFactory(case=variant_set.case, user=user)
        self.bgjob.smallvariantquery.query_settings.update(
            {
                "prio_enabled": True,
                "prio_algorithm": "phenix",
                "prio_hpo_terms": ["HP:0000001"],
                "patho_enabled": True,
                "patho_score": "cadd",
            }
        )
        self.bgjob.smallvariantquery.save()

    @patch("django.conf.settings.VARFISH_ENABLE_EXOMISER_PRIORITISER", True)
    @patch("django.conf.settings.VARFISH_ENABLE_CADD", True)
    @patch("django.conf.settings.VARFISH_EXOMISER_PRIORITISER_API_URL", "https://exomiser.com")
    @patch("django.conf.settings.VARFISH_CADD_REST_API_URL", "https://cadd.com")
    @Mocker()
    def test_submit_case_filter(self, mock):
        mock.get(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "results": [
                        {
                            "geneId": 1234,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        }
                    ]
                }
            ),
        )
        mock.post(
            settings.VARFISH_CADD_REST_API_URL + "/annotate/",
            status_code=200,
            text=json.dumps({"uuid": "xxxxxxxx-xxxx-xxxx-xxxxxxxxxxxx"}),
        )
        mock.post(
            settings.VARFISH_CADD_REST_API_URL + "/result/",
            status_code=200,
            text=json.dumps(
                {
                    "status": "finished",
                    "scores": {
                        "1-100-A-G": [0.345146, 7.772],
                        "1-200-A-G": [0.345179, 7.773],
                        "1-300-A-G": [0.345212, 7.774],
                    },
                }
            ),
        )
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        self.assertEqual(SmallVariantQueryGeneScores.objects.count(), 1)
        gene_scores = SmallVariantQueryGeneScores.objects.all()
        self.assertEqual(gene_scores[0].gene_id, "1234")
        self.assertEqual(gene_scores[0].gene_symbol, "API")
        self.assertEqual(gene_scores[0].priority_type, "PHENIX_PRIORITY")
        self.assertEqual(gene_scores[0].score, 0.1)

        self.assertEqual(SmallVariantQueryVariantScores.objects.count(), 3)
        variant_scores = SmallVariantQueryVariantScores.objects.all()
        self.assertEqual(variant_scores[0].score, 7.772)
        self.assertEqual(variant_scores[1].score, 7.773)
        self.assertEqual(variant_scores[2].score, 7.774)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)

        # Watch out. Django does not necessarily keep the order of the list when inserting into many-to-many-relationships.
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)


class ProjectCasesFilterTest(TestCase):
    """Test running joint cases filter job."""

    def setUp(self):
        super().setUp()
        user = self.make_user("superuser")
        self.bgjob = ProjectCasesFilterBgJobFactory(user=user)
        variant_sets = SmallVariantSetFactory.create_batch(2, case__project=self.bgjob.project)
        SmallVariantFactory.create_batch(3, variant_set=variant_sets[0])
        SmallVariantFactory.create_batch(3, variant_set=variant_sets[1])
        self.bgjob.projectcasessmallvariantquery.query_settings.update(
            vars(FormDataFactory(names=self.bgjob.project.get_members()))
        )

    def test_submit_projectcases_filter(self):
        ProjectCasesFilter(self.bgjob, self.bgjob.projectcasessmallvariantquery).run()

        self.assertEqual(ProjectCasesSmallVariantQuery.objects.count(), 1)
        self.assertEqual(ProjectCasesSmallVariantQuery.objects.first().query_results.count(), 6)
