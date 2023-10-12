"""Tests for the ``file_export`` module."""

import json
from unittest.mock import patch

from django.conf import settings
from requests_mock import Mocker
from test_plus.test import TestCase

from variants.models import SmallVariantQueryGeneScores, SmallVariantQueryVariantScores
from variants.tests.factories import (
    CaseWithVariantSetFactory,
    FilterBgJobFactory,
    FormDataFactory,
    ProjectCasesFilterBgJobFactory,
    SmallVariantFactory,
)

from ..models import (
    CaddPathogenicityScoreCache,
    MutationTasterPathogenicityScoreCache,
    ProjectCasesSmallVariantQuery,
    SmallVariantQuery,
    UmdPathogenicityScoreCache,
)
from ..submit_filter import CaseFilter, ProjectCasesFilter


class CaseFilterTest(TestCase):
    """Test running single-case filter job."""

    def setUp(self):
        super().setUp()
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get("small")
        self.hpo_id = "HP:0000001"
        self.superuser = self.make_user("superuser")
        self.small_vars = [
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="1234", variant_set=self.variant_set
            ),
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="2234", variant_set=self.variant_set
            ),
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="2234", variant_set=self.variant_set, in_clinvar=True
            ),
        ]
        self.bgjob = FilterBgJobFactory(case=self.case, user=self.superuser)

    @patch("django.conf.settings.VARFISH_ENABLE_CADA", True)
    @patch("django.conf.settings.VARFISH_CADA_REST_API_URL", "https://cada.com")
    @Mocker()
    def test_submit_case_filter_cada(self, mock):
        mock.post(
            settings.VARFISH_CADA_REST_API_URL,
            status_code=200,
            text=json.dumps(
                [
                    {
                        "geneId": "EntrezId:" + self.small_vars[0].refseq_gene_id,
                        "geneSymbol": "ASPSCR1",
                        "score": "0.1",
                    },
                    {
                        "geneId": "EntrezId:" + self.small_vars[1].refseq_gene_id,
                        "geneSymbol": "NFKBIL1",
                        "score": "0.2",
                    },
                ]
            ),
        )

        # Enable CADA scoring
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms_curated"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["prio_algorithm"] = "CADA"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        self.assertEqual(SmallVariantQueryGeneScores.objects.count(), 2)
        gene_scores = SmallVariantQueryGeneScores.objects.all()
        self.assertEqual(gene_scores[0].gene_id, self.small_vars[0].refseq_gene_id)
        self.assertEqual(gene_scores[0].gene_symbol, "ASPSCR1")
        self.assertEqual(gene_scores[0].priority_type, "CADA")
        self.assertEqual(gene_scores[0].score, 0.1)
        self.assertEqual(gene_scores[1].gene_id, self.small_vars[1].refseq_gene_id)
        self.assertEqual(gene_scores[1].gene_symbol, "NFKBIL1")
        self.assertEqual(gene_scores[1].priority_type, "CADA")
        self.assertEqual(gene_scores[1].score, 0.2)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)

    @patch("django.conf.settings.VARFISH_ENABLE_EXOMISER_PRIORITISER", True)
    @patch("django.conf.settings.VARFISH_EXOMISER_PRIORITISER_API_URL", "https://exomiser.com")
    @Mocker()
    def test_submit_case_filter_exomiser(self, mock):
        mock.post(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "results": [
                        {
                            "geneId": self.small_vars[0].refseq_gene_id,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                        {
                            "geneId": self.small_vars[1].refseq_gene_id,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                    ]
                }
            ),
        )

        # Enable MutationTaster scoring
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms_curated"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["prio_algorithm"] = "phenix"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        self.assertEqual(SmallVariantQueryGeneScores.objects.count(), 2)
        gene_scores = SmallVariantQueryGeneScores.objects.all()
        self.assertEqual(gene_scores[0].gene_id, self.small_vars[0].refseq_gene_id)
        self.assertEqual(gene_scores[0].gene_symbol, "API")
        self.assertEqual(gene_scores[0].priority_type, "PHENIX_PRIORITY")
        self.assertEqual(gene_scores[0].score, 0.1)
        self.assertEqual(gene_scores[1].gene_id, self.small_vars[1].refseq_gene_id)
        self.assertEqual(gene_scores[1].gene_symbol, "API")
        self.assertEqual(gene_scores[1].priority_type, "PHENIX_PRIORITY")
        self.assertEqual(gene_scores[1].score, 0.1)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)

    @patch("django.conf.settings.VARFISH_ENABLE_EXOMISER_PRIORITISER", True)
    @patch("django.conf.settings.VARFISH_ENABLE_CADD", True)
    @patch("django.conf.settings.VARFISH_EXOMISER_PRIORITISER_API_URL", "https://exomiser.com")
    @patch("django.conf.settings.VARFISH_CADD_REST_API_URL", "https://cadd.com")
    @Mocker()
    def test_submit_case_filter_patho_and_pheno(self, mock):
        mock.post(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "results": [
                        {
                            "geneId": self.small_vars[0].refseq_gene_id,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                        {
                            "geneId": self.small_vars[1].refseq_gene_id,
                            "geneSymbol": "API",
                            "score": "0.1",
                            "priorityType": "PHENIX_PRIORITY",
                        },
                    ]
                }
            ),
        )

        def _key_gen(s):
            return "%s-%d-%s-%s" % (s.chromosome, s.start, s.reference, s.alternative)

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
                    "info": {"cadd_rest_api_version": 0.1},
                    "scores": {
                        _key_gen(self.small_vars[0]): [0.345146, 7.773],
                        _key_gen(self.small_vars[1]): [0.345179, 7.773],
                        _key_gen(self.small_vars[2]): [0.345212, 7.774],
                    },
                }
            ),
        )

        # Enable Exomiser and CADD pathogenicity scoring
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms_curated"] = [self.hpo_id]
        self.bgjob.smallvariantquery.query_settings["prio_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["prio_algorithm"] = "phenix"
        self.bgjob.smallvariantquery.query_settings["patho_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["patho_score"] = "cadd"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        self.assertEqual(SmallVariantQueryGeneScores.objects.count(), 2)
        gene_scores = SmallVariantQueryGeneScores.objects.all()
        self.assertEqual(gene_scores[0].gene_id, self.small_vars[0].refseq_gene_id)
        self.assertEqual(gene_scores[0].gene_symbol, "API")
        self.assertEqual(gene_scores[0].priority_type, "PHENIX_PRIORITY")
        self.assertEqual(gene_scores[0].score, 0.1)
        self.assertEqual(gene_scores[1].gene_id, self.small_vars[1].refseq_gene_id)
        self.assertEqual(gene_scores[1].gene_symbol, "API")
        self.assertEqual(gene_scores[1].priority_type, "PHENIX_PRIORITY")
        self.assertEqual(gene_scores[1].score, 0.1)

        # Watch out. Django does not necessarily keep the order of the list when inserting into many-to-many-relationships.
        self.assertEqual(SmallVariantQueryVariantScores.objects.count(), 3)
        variant_scores = SmallVariantQueryVariantScores.objects.all()
        self.assertEqual(variant_scores[0].score, 7.773)
        self.assertEqual(variant_scores[1].score, 7.773)
        self.assertEqual(variant_scores[2].score, 7.774)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)
        self.assertEqual(CaddPathogenicityScoreCache.objects.count(), 3)

    @patch("django.conf.settings.VARFISH_ENABLE_CADD", True)
    @patch("django.conf.settings.VARFISH_CADD_REST_API_URL", "https://cadd.com")
    @Mocker()
    def test_submit_case_filter_cadd(self, mock):
        def _key_gen(s):
            return "%s-%d-%s-%s" % (s.chromosome, s.start, s.reference, s.alternative)

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
                    "info": {"cadd_rest_api_version": 0.1},
                    "scores": {
                        _key_gen(self.small_vars[0]): [0.345146, 7.773],
                        _key_gen(self.small_vars[1]): [0.345179, 7.773],
                        _key_gen(self.small_vars[2]): [0.345212, 7.774],
                    },
                }
            ),
        )

        # Enable CADD pathogenicity scoring
        self.bgjob.smallvariantquery.query_settings["patho_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["patho_score"] = "cadd"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        # Watch out. Django does not necessarily keep the order of the list when inserting into many-to-many-relationships.
        self.assertEqual(SmallVariantQueryVariantScores.objects.count(), 3)
        variant_scores = SmallVariantQueryVariantScores.objects.all()
        self.assertEqual(variant_scores[0].score, 7.773)
        self.assertEqual(variant_scores[1].score, 7.773)
        self.assertEqual(variant_scores[2].score, 7.774)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)
        self.assertEqual(CaddPathogenicityScoreCache.objects.count(), 3)

    @patch("django.conf.settings.VARFISH_MUTATIONTASTER_REST_API_URL", "https://mutationtaster.com")
    @Mocker()
    def test_submit_case_filter_mutationtaster(self, mock):
        return_text = "id\tchr\tpos\tref\talt\ttranscript_stable\tNCBI_geneid\tprediction\tmodel\tbayes_prob_dc\tnote\tsplicesite\tdistance_from_splicesite\tdisease_mutation\tpolymorphism\n"
        return_text += "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "1",
            self.small_vars[0].chromosome,
            str(self.small_vars[0].start),
            self.small_vars[0].reference,
            self.small_vars[0].alternative,
            self.small_vars[0].ensembl_transcript_id,
            "1234",
            "disease causing",
            "complex_aae",
            "998",
            "",
            "",
            "",
            "",
            "",
        )
        return_text += "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "2",
            self.small_vars[1].chromosome,
            str(self.small_vars[1].start),
            self.small_vars[1].reference,
            self.small_vars[1].alternative,
            self.small_vars[1].ensembl_transcript_id,
            "4567",
            "disease causing (automatic)",
            "complex_aae",
            "999",
            "",
            "",
            "",
            "",
            "",
        )
        return_text += "{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "3",
            self.small_vars[2].chromosome,
            str(self.small_vars[2].start),
            self.small_vars[2].reference,
            self.small_vars[2].alternative,
            self.small_vars[2].ensembl_transcript_id,
            "5678",
            "disease causing",
            "simple_aae",
            "999",
            "",
            "",
            "",
            "",
            "",
        )
        mock.post(settings.VARFISH_MUTATIONTASTER_REST_API_URL, status_code=200, text=return_text)

        # Enable CADD pathogenicity scoring
        self.bgjob.smallvariantquery.query_settings["patho_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["patho_score"] = "mutationtaster"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        # Watch out. Django does not necessarily keep the order of the list when inserting into many-to-many-relationships.
        self.assertEqual(SmallVariantQueryVariantScores.objects.count(), 3)
        variant_scores = SmallVariantQueryVariantScores.objects.all()
        self.assertEqual(variant_scores[0].score, 3.0998)
        self.assertEqual(variant_scores[1].score, 4.0999)
        self.assertEqual(variant_scores[2].score, 3.0999)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)
        self.assertEqual(MutationTasterPathogenicityScoreCache.objects.count(), 3)

    @patch("django.conf.settings.VARFISH_UMD_REST_API_URL", "https://umd.com")
    @Mocker()
    def test_submit_case_filter_umd(self, mock):
        from projectroles.app_settings import AppSettingAPI

        app_settings = AppSettingAPI()
        app_settings.set("variants", "umd_predictor_api_token", "FAKETOKEN", user=self.superuser)

        return_text = "This page was created in 0.001 seconds\n\n"
        return_text += "chr{}\t{}\tXXX\t{}\t{}\t1234\t{}\t{}\tW\tY\t{}\t{}\n".format(
            self.small_vars[0].chromosome,
            str(self.small_vars[0].start),
            self.small_vars[0].ensembl_transcript_id,
            self.small_vars[0].ensembl_gene_id,
            self.small_vars[0].reference,
            self.small_vars[0].alternative,
            "98",
            "Likely Pathogenic",
        )
        return_text += "chr{}\t{}\tXXX\t{}\t{}\t1234\t{}\t{}\tW\tY\t{}\t{}\n".format(
            self.small_vars[1].chromosome,
            str(self.small_vars[1].start),
            self.small_vars[1].ensembl_transcript_id,
            self.small_vars[1].ensembl_gene_id,
            self.small_vars[1].reference,
            self.small_vars[1].alternative,
            "100",
            "Pathogenic",
        )
        return_text += "chr{}\t{}\tXXX\t{}\t{}\t1234\t{}\t{}\tW\tY\t{}\t{}\n".format(
            self.small_vars[2].chromosome,
            str(self.small_vars[2].start),
            self.small_vars[2].ensembl_transcript_id,
            self.small_vars[2].ensembl_gene_id,
            self.small_vars[2].reference,
            self.small_vars[2].alternative,
            "99",
            "Pathogenic",
        )
        mock.get(settings.VARFISH_UMD_REST_API_URL, status_code=200, text=return_text)

        # Enable UMD pathogenicity scoring
        self.bgjob.smallvariantquery.query_settings["patho_enabled"] = True
        self.bgjob.smallvariantquery.query_settings["patho_score"] = "umd"
        self.bgjob.smallvariantquery.save()

        # Run query
        CaseFilter(self.bgjob, self.bgjob.smallvariantquery).run()

        # Watch out. Django does not necessarily keep the order of the list when inserting into many-to-many-relationships.
        self.assertEqual(SmallVariantQueryVariantScores.objects.count(), 3)
        variant_scores = SmallVariantQueryVariantScores.objects.all()
        self.assertEqual(variant_scores[0].score, 98)
        self.assertEqual(variant_scores[1].score, 100)
        self.assertEqual(variant_scores[2].score, 99)

        self.assertEqual(SmallVariantQuery.objects.count(), 1)
        self.assertEqual(SmallVariantQuery.objects.first().query_results.count(), 3)
        self.assertEqual(UmdPathogenicityScoreCache.objects.count(), 3)


class ProjectCasesFilterTest(TestCase):
    """Test running joint cases filter job."""

    def setUp(self):
        super().setUp()
        user = self.make_user("superuser")
        self.bgjob = ProjectCasesFilterBgJobFactory(user=user)
        variant_sets = [None, None]
        _, variant_sets[0], _ = CaseWithVariantSetFactory.get(project=self.bgjob.project)
        _, variant_sets[1], _ = CaseWithVariantSetFactory.get(project=self.bgjob.project)
        SmallVariantFactory.create_batch(3, variant_set=variant_sets[0])
        SmallVariantFactory.create_batch(3, variant_set=variant_sets[1])
        self.bgjob.projectcasessmallvariantquery.query_settings.update(
            vars(FormDataFactory(names=self.bgjob.project.get_members()))
        )

    def test_submit_projectcases_filter(self):
        ProjectCasesFilter(self.bgjob, self.bgjob.projectcasessmallvariantquery).run()

        self.assertEqual(ProjectCasesSmallVariantQuery.objects.count(), 1)
        self.assertEqual(ProjectCasesSmallVariantQuery.objects.first().query_results.count(), 6)
