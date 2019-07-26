"""Tests for the filter view"""

import json

import aldjemy.core
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from projectroles.templatetags.projectroles_common_tags import site_version

from requests_mock import Mocker
from unittest.mock import patch
from django.conf import settings

from projectroles.models import Project
from projectroles.app_settings import AppSettingAPI
from clinvar.tests.factories import (
    ProcessedClinvarFormDataFactory,
    ClinvarFormDataFactory,
    ClinvarFactory,
)
from conservation.tests.factories import KnownGeneAAFactory
from frequencies.tests.factories import (
    ThousandGenomesFactory,
    GnomadExomesFactory,
    GnomadGenomesFactory,
    ExacFactory,
)
from geneinfo.tests.factories import (
    HpoFactory,
    HgncFactory,
    Mim2geneMedgenFactory,
    HpoNameFactory,
    GnomadConstraintsFactory,
    ExacConstraintsFactory,
    EnsemblToRefseqFactory,
    RefseqToEnsemblFactory,
)
from variants.models import (
    Case,
    ExportFileBgJob,
    FilterBgJob,
    ProjectCasesFilterBgJob,
    ExportProjectCasesFileBgJob,
    DistillerSubmissionBgJob,
    ComputeProjectVariantsStatsBgJob,
    SmallVariantFlags,
    SmallVariantComment,
    ClinvarBgJob,
    AcmgCriteriaRating,
)
from variants.tests.factories import (
    CaseFactory,
    SmallVariantFactory,
    FormDataFactory,
    FilterBgJobFactory,
    ProjectCasesFilterBgJobFactory,
    ProjectFactory,
    ClinvarBgJobFactory,
    DistillerSubmissionBgJobFactory,
    ExportFileBgJobFactory,
    ExportFileJobResultFactory,
    ExportProjectCasesFileBgJobFactory,
    SmallVariantFlagsFormDataFactory,
    SmallVariantCommentFormDataFactory,
    ExportProjectCasesFileBgJobResultFactory,
    AcmgCriteriaRatingFormDataFactory,
    SmallVariantFlagsFactory,
    SmallVariantCommentFactory,
    SmallVariantSetFactory,
)
from variants.tests.helpers import ViewTestBase
from variants.variant_stats import rebuild_case_variant_stats, rebuild_project_variant_stats
from geneinfo.models import HpoName, Hgnc, RefseqToHgnc

#: The SQL Alchemy engine to use
SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


# TODO: This base class is still used by geneinfo view tests.
class TestViewBase:
    pass


class TestCaseListView(ViewTestBase):
    """Test case list view"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_render_no_variant_stats(self):
        """Test display of case list page."""
        with self.login(self.user):
            response = self.client.get(
                reverse("variants:case-list", kwargs={"project": self.case.project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 1)

    def test_render_with_variant_stats(self):
        """Test display of case list page."""
        rebuild_case_variant_stats(SQLALCHEMY_ENGINE, self.variant_set)
        with self.login(self.user):
            response = self.client.get(
                reverse("variants:case-list", kwargs={"project": self.case.project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 1)

    def test_render_caseless_project(self):
        project = self.case.project.sodar_uuid
        self.case.delete()
        with self.login(self.user):
            response = self.client.get(reverse("variants:case-list", kwargs={"project": project}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 0)

    def test_render_caseless_project_with_variant_stats(self):
        project = self.case.project.sodar_uuid
        rebuild_case_variant_stats(SQLALCHEMY_ENGINE, self.variant_set)
        self.case.delete()
        with self.login(self.user):
            response = self.client.get(reverse("variants:case-list", kwargs={"project": project}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 0)


class TestCaseListQcStatsApiView(ViewTestBase):
    """Test the QC API view for case lists."""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_render_no_variant_stats(self):
        """Test display of case list page."""
        with self.login(self.user):
            response = self.client.get(
                reverse("variants:api-project-qc", kwargs={"project": self.case.project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)

            result = response.json()
            self.assertIn("pedigree", result)
            self.assertIn("relData", result)
            self.assertIn("sexErrors", result)
            self.assertIn("chrXHetHomRatio", result)
            self.assertIn("dps", result)
            self.assertIn("dpQuantiles", result)
            self.assertIn("hetRatioQuantiles", result)
            self.assertIn("dpHetData", result)

    def test_render_with_variant_stats(self):
        """Test display of case list page."""
        rebuild_case_variant_stats(SQLALCHEMY_ENGINE, self.variant_set)
        rebuild_project_variant_stats(SQLALCHEMY_ENGINE, self.case.project, self.user)
        with self.login(self.user):
            response = self.client.get(
                reverse("variants:api-project-qc", kwargs={"project": self.case.project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)

            result = response.json()
            self.assertIn("pedigree", result)
            self.assertIn("relData", result)
            self.assertIn("sexErrors", result)
            self.assertIn("chrXHetHomRatio", result)
            self.assertIn("dps", result)
            self.assertIn("dpQuantiles", result)
            self.assertIn("hetRatioQuantiles", result)
            self.assertIn("dpHetData", result)


class TestCaseDetailView(ViewTestBase):
    """Test case detail view"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_render_no_variant_stats(self):
        """Test display of case detail view page."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-detail",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].name, self.case.name)

    def test_render_with_variant_stats(self):
        """Test display of case detail view page."""
        with self.login(self.user):
            rebuild_case_variant_stats(SQLALCHEMY_ENGINE, self.variant_set)
            response = self.client.get(
                reverse(
                    "variants:case-detail",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].name, self.case.name)


class TestCaseUpdateView(ViewTestBase):
    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_render_form(self):
        """Test rendering of update form."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-update",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].name, self.case.name)
            self.assertEqual(response.context["form"].instance.name, self.case.name)

    def test_post_form_success(self):
        """Test update of case with the result."""
        with self.login(self.user):
            form_data = {"name": self.case.name + "x", "index": 0}
            for i, line in enumerate(self.case.pedigree):
                self.col_names = ("patient", "father", "mother", "sex", "affected")
                form_data.update(
                    {
                        "member_%d_patient" % i: line["patient"] + "x",
                        "member_%d_father" % i: -1,
                        "member_%d_mother" % i: -1,
                        "member_%d_sex" % i: 0,
                        "member_%d_affected" % i: 0,
                    }
                )

            response = self.client.post(
                reverse(
                    "variants:case-update",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                form_data,
            )

            self.assertRedirects(
                response,
                reverse(
                    "variants:case-detail",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
            )

            case = Case.objects.get(id=self.case.id)
            self.assertEqual(case.name, form_data["name"])
            self.assertEqual(case.index, case.pedigree[0]["patient"])
            self.assertEqual(case.pedigree[0]["patient"], self.case.pedigree[0]["patient"] + "x")
            self.assertEqual(case.pedigree[0]["affected"], 0)
            self.assertEqual(case.pedigree[0]["sex"], 0)


class TestCaseDetailQcStatsApiView(ViewTestBase):
    """Test the QC API view for single case."""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_get_no_variant_stats(self):
        """Test fetching information through API if there is no variant stats."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:api-case-qc",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

            result = response.json()
            self.assertIn("pedigree", result)
            self.assertIn("relData", result)
            self.assertIn("sexErrors", result)
            self.assertIn("chrXHetHomRatio", result)
            self.assertIn("dps", result)
            self.assertIn("dpQuantiles", result)
            self.assertIn("hetRatioQuantiles", result)
            self.assertIn("dpHetData", result)
            self.assertIn("variantTypeData", result)
            self.assertIn("variantEffectData", result)
            self.assertIn("indelSizeData", result)

    def test_render_with_variant_stats(self):
        """Test fetching information through API if there are variant stats."""
        with self.login(self.user):
            rebuild_case_variant_stats(SQLALCHEMY_ENGINE, self.variant_set)
            response = self.client.get(
                reverse(
                    "variants:api-case-qc",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

            result = response.json()
            self.assertIn("pedigree", result)
            self.assertIn("relData", result)
            self.assertIn("sexErrors", result)
            self.assertIn("chrXHetHomRatio", result)
            self.assertIn("dps", result)
            self.assertIn("dpQuantiles", result)
            self.assertIn("hetRatioQuantiles", result)
            self.assertIn("dpHetData", result)
            self.assertIn("variantTypeData", result)
            self.assertIn("variantEffectData", result)
            self.assertIn("indelSizeData", result)


class TestCaseFilterView(ViewTestBase):
    """Test case filter view"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        SmallVariantFactory(variant_set=self.variant_set)

    def test_status_code_200(self):
        """Test display of the filter forms, no submit."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)

    def test_provoke_form_error(self):
        with self.login(self.user), self.assertRaises(ValidationError):
            self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(FormDataFactory(thousand_genomes_frequency="I'm supposed to be a float!")),
            )

    def test_post_download(self):
        """Test form submit for download as file."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(FormDataFactory(submit="download", names=self.case.get_members())),
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            created_job = ExportFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:export-job-detail",
                    kwargs={"project": self.case.project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )

    @Mocker()
    def test_post_mutation_distiller(self, mock):
        with self.login(self.user):
            from ..submit_external import DISTILLER_POST_URL

            mock.post(
                DISTILLER_POST_URL,
                status_code=200,
                text=(
                    '\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<HTM'
                    'L>\n<HEAD>\n<TITLE>testsubmission - QueryEngine initialising</TITLE>\n<meta http-equiv="refresh" content="5; U'
                    'RL=/temp/QE/vcf_10585_21541/progress.html">\n<link href="/MutationTaster/css.css" rel="stylesheet" type="text/'
                    'css">\n</head><body>\n\n\t\t<table  border="0" width="100%" cellspacing="20">\n\t\t\t<tr>\n\t\t\t\t<td style="'
                    'text-align:center"><img src="/MutationTaster/MutationTaster_small.png" alt="Yum, tasty mutations..." align="le'
                    'ft"></td>\n\t\t\t\t<td ><h1>testsubmission - QueryEngine initialising</h1></td>\n\t\t\t\t<td><A HREF="/Mutatio'
                    'nTaster/info/MTQE_documentation.html" TARGET="_blank">MTQE documentation</A></td>\n\t\t\t</tr>\n\t\t</table> <'
                    "h1>testsubmission - QueryEngine initialising</h1>\n<h2>We are uploading your file. NEVER press reload or F5 - "
                    "unless you want to start from the very beginning. </h2>MutationTaster QueryEngine: vcf number 10585<br>"
                ),
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    FormDataFactory(
                        submit="submit-mutationdistiller", names=self.case.get_members()
                    )
                ),
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 1)
            created_job = DistillerSubmissionBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": self.case.project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )


class TestCasePrefetchFilterView(ViewTestBase):
    """Tests for CasePrefetchFilterView.
    """

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        SmallVariantFactory(variant_set=self.variant_set)

    def test_get_job_id(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(FormDataFactory(names=self.case.get_members())),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(FilterBgJob.objects.last().sodar_uuid),
            )

    def test_invalid_form(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(FormDataFactory(exac_frequency="I am supposed to be a float.")),
            )

            self.assertEqual(response.status_code, 400)
            self.assertTrue("exac_frequency" in json.loads(response.content.decode("utf-8")))


class TestCaseFilterJobView(ViewTestBase):
    """Tests for CaseFilterJobView.
    """

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.bgjob = FilterBgJobFactory(case=self.case, user=self.user)

    def test_status_code_200(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-filter-job",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "job": self.bgjob.sodar_uuid,
                    },
                ),
                vars(FormDataFactory(names=self.case.get_members())),
            )
            self.assertEqual(response.status_code, 200)


class TestCaseLoadPrefetchedFilterView(ViewTestBase):
    """Tests for CaseLoadPrefetchedFilterView.
    """

    def setUp(self):
        super().setUp()
        self.hpo_id = "HP:0000001"
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.small_vars = [
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="1234", variant_set=self.variant_set
            ),
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="2234", variant_set=self.variant_set
            ),
            SmallVariantFactory(
                chromosome="1", refseq_gene_id="2234", variant_set=self.variant_set
            ),
        ]
        self.bgjob = FilterBgJobFactory(case=self.case, user=self.user)
        self.bgjob.smallvariantquery.query_results.add(self.small_vars[0], self.small_vars[2])
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms"] = [self.hpo_id]
        self.bgjob.smallvariantquery.save()

    def test_count_results(self):
        hpo_name = HpoNameFactory(hpo_id=self.hpo_id)
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 2)
            self.assertFalse(response.context["training_mode"])
            self.assertEqual(response.context["hpoterms"], {self.hpo_id: hpo_name.name})

    def test_training_mode(self):
        with self.login(self.user):
            self.bgjob.smallvariantquery.query_settings["training_mode"] = True
            self.bgjob.smallvariantquery.save()
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertTrue(response.context["training_mode"])

    @patch("django.conf.settings.VARFISH_ENABLE_EXOMISER_PRIORITISER", True)
    @patch("django.conf.settings.VARFISH_ENABLE_CADD", True)
    @patch("django.conf.settings.VARFISH_EXOMISER_PRIORITISER_API_URL", "https://exomiser.com")
    @patch("django.conf.settings.VARFISH_CADD_REST_API_URL", "https://cadd.com")
    @Mocker()
    def test_ranking_results(self, mock):
        mock.get(
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
            settings.VARFISH_CADD_REST_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "scores": {
                        _key_gen(self.small_vars[0]): [0.345146, 7.773],
                        _key_gen(self.small_vars[1]): [0.345179, 7.773],
                        _key_gen(self.small_vars[2]): [0.345212, 7.774],
                    }
                }
            ),
        )
        with self.login(self.user):
            self.client.post(
                reverse(
                    "variants:case-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    FormDataFactory(
                        prio_enabled=True,
                        prio_algorithm="phenix",
                        prio_hpo_terms=["HP:0000001"],
                        patho_enabled=True,
                        patho_score="phenix",  # ?
                        names=self.case.get_members(),
                    )
                ),
            )
            response = self.client.post(
                reverse(
                    "variants:case-load-filter-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {"filter_job_uuid": FilterBgJob.objects.last().sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 3)
            self.assertEqual(response.context["training_mode"], False)
            self.assertEqual(response.context["has_phenotype_scores"], True)
            self.assertEqual(response.context["has_pathogenicity_scores"], True)
            self.assertEqual(response.context["result_rows"][0].pathogenicity_score, 7.774)
            self.assertEqual(response.context["result_rows"][0].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][0].joint_score, 0.1 * 7.774)
            self.assertEqual(response.context["result_rows"][0].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][0].pathogenicity_rank, 1)
            self.assertEqual(response.context["result_rows"][0].joint_rank, 1)
            self.assertEqual(response.context["result_rows"][1].pathogenicity_score, 7.773)
            self.assertEqual(response.context["result_rows"][1].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][1].joint_score, 0.1 * 7.773)
            self.assertEqual(response.context["result_rows"][1].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][1].pathogenicity_rank, 1)
            self.assertEqual(response.context["result_rows"][1].joint_rank, 1)
            self.assertEqual(response.context["result_rows"][2].pathogenicity_score, 7.773)
            self.assertEqual(response.context["result_rows"][2].phenotype_score, 0.1)
            self.assertEqual(response.context["result_rows"][2].joint_score, 0.1 * 7.773)
            self.assertEqual(response.context["result_rows"][2].phenotype_rank, 1)
            self.assertEqual(response.context["result_rows"][2].pathogenicity_rank, 2)
            self.assertEqual(response.context["result_rows"][2].joint_rank, 2)


class TestFilterJobDetailView(ViewTestBase):
    """Tests for FilterJobDetailView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.user)

    def test_status_code_200(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, self.bgjob.case.name)


class TestFilterJobResubmitView(ViewTestBase):
    """Tests for FilterJobResubmitView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.user)

    def test_redirect(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:filter-job-resubmit",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            created_job = FilterBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:filter-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestFilterJobGetStatus(ViewTestBase):
    """Tests for FilterJobGetStatusView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.user)

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:filter-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:filter-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:filter-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestFilterJobGetPrevious(ViewTestBase):
    """Tests for FilterJobGetPreviousView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.user)

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:filter-job-previous",
                    kwargs={
                        "project": self.bgjob.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(self.bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            project = self.bgjob.project.sodar_uuid
            case = self.bgjob.case.sodar_uuid
            self.bgjob.delete()
            response = self.client.get(
                reverse("variants:filter-job-previous", kwargs={"project": project, "case": case})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestProjectCasesFilterJobGetStatus(ViewTestBase):
    """Tests for ProjectCasesFilterJobGetStatusView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-status",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestProjectCasesFilterJobGetPrevious(ViewTestBase):
    """Tests for ProjectCasesFilterJobGetPreviousView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-previous",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(self.bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            project = self.bgjob.project.sodar_uuid
            self.bgjob.delete()
            response = self.client.get(
                reverse("variants:project-cases-filter-job-previous", kwargs={"project": project})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestProjectCasesFilterView(ViewTestBase):
    """Tests for FilterProjectCasesFilterView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)

    def test_status_code_200(self):
        """Test display of the filter forms, no submit."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)

    def test_post_download(self):
        """Test form submit for download as file."""
        with self.login(self.user):
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                ),
                vars(FormDataFactory(submit="download")),
            )
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
            created_job = ExportProjectCasesFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={
                        "project": self.bgjob.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestProjectCasesPrefetchFilterView(ViewTestBase):
    """Tests for FilterProjectCasesPrefetchFilterView.
    """

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        CaseFactory(project=self.project)
        CaseFactory(project=self.project)

    def test_valid_form(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-results",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                vars(FormDataFactory(names=self.project.get_members())),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(ProjectCasesFilterBgJob.objects.last().sodar_uuid),
            )

    def test_invalid_form(self):
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-results", kwargs={"project": project.sodar_uuid}
                ),
                vars(
                    FormDataFactory(
                        names=self.project.get_members(),
                        exac_frequency="I am supposed to be a float.",
                    )
                ),
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("exac_frequency" in json.loads(response.content.decode("utf-8")))


class TestProjectCasesFilterJobDetailView(ViewTestBase):
    """Tests for ProjectCasesFilterJobDetailView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)

    def test_status_code_200(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_project_name(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].project.title, self.bgjob.project.title)


class TestProjectCasesLoadPrefetchedFilterView(ViewTestBase):
    """Tests for ProjectCasesLoadPrefetchedFilterView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)
        variant_sets = SmallVariantSetFactory.create_batch(2, case__project=self.bgjob.project)
        small_vars = [
            *SmallVariantFactory.create_batch(3, variant_set=variant_sets[0]),
            *SmallVariantFactory.create_batch(3, variant_set=variant_sets[1]),
        ]
        self.bgjob.projectcasessmallvariantquery.query_results.add(small_vars[0], *small_vars[2:6])

    def test_count_results(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-load-filter-results",
                    kwargs={"project": self.bgjob.project.sodar_uuid},
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 5)
            self.assertEqual(len(response.context["result_rows"]), 5)


class TestProjectCasesFilterJobResubmitView(ViewTestBase):
    """Tests for ProjectCasesFilterJobResubmitView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.user)

    def test_redirect(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-cases-filter-job-resubmit",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            created_job = ProjectCasesFilterBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestCaseClinvarReportView(ViewTestBase):
    """Test case Clinvar report view"""

    def setUp(self):
        super().setUp()
        self.bgjob = ClinvarBgJobFactory(user=self.user)

    def test_get_renders_form(self):
        """Test that GET returns the form"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-clinvar",
                    kwargs={
                        "project": self.bgjob.case.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context[-1].get("form"))

    def test_get_renders_form_with_given_job(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:case-clinvar-job",
                    kwargs={
                        "project": self.bgjob.case.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                        "job": self.bgjob.sodar_uuid,
                    },
                ),
                vars(ProcessedClinvarFormDataFactory(names=self.bgjob.case.get_members())),
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context[-1].get("form"))


class TestCasePrefetchClinvarReportView(ViewTestBase):
    """Test CasePrefetchClinvarReportView"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    def test_get_job_id(self):
        """Test that an appropriate POST returns a report"""
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(ClinvarFormDataFactory(names=self.case.get_members())),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(ClinvarBgJob.objects.last().sodar_uuid),
            )

    def test_form_error(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-results",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    ClinvarFormDataFactory(
                        result_rows_limit="I'm supposed to be an integer!",
                        names=self.case.get_members(),
                    )
                ),
            )
            self.assertEqual(response.status_code, 400)


class TestClinvarReportJobDetailView(ViewTestBase):
    """Test ClinvarReportJobDetailView"""

    def setUp(self):
        super().setUp()
        self.bgjob = ClinvarBgJobFactory(user=self.user)

    def test_status_code_200(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:clinvar-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)


class TestClinvarReportJobResubmitView(ViewTestBase):
    """Test ClinvarReportJobResubmitView"""

    def setUp(self):
        super().setUp()
        self.bgjob = ClinvarBgJobFactory(user=self.user)

    def test_redirect(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-resubmit",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            created_job = ClinvarBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:clinvar-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestCaseLoadPrefetchedClinvarReportView(ViewTestBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    def setUp(self):
        super().setUp()
        variant_set = SmallVariantSetFactory()
        self.case = variant_set.case
        self.bgjob = ClinvarBgJobFactory(user=self.user, case=self.case)
        small_var = SmallVariantFactory(in_clinvar=True, variant_set=variant_set)
        # Create two entries in the same position to test the grouping.
        # First record: \wo any significance information (such record doesn't exist in clinvar).
        ClinvarFactory(
            release=small_var.release,
            chromosome=small_var.chromosome,
            start=small_var.start,
            end=small_var.end,
            bin=small_var.bin,
            reference=small_var.reference,
            alternative=small_var.alternative,
            clinical_significance_ordered=[],
            review_status_ordered=[],
        )
        # Second record: \w significance information
        ClinvarFactory(
            release=small_var.release,
            chromosome=small_var.chromosome,
            start=small_var.start,
            end=small_var.end,
            bin=small_var.bin,
            reference=small_var.reference,
            alternative=small_var.alternative,
            clinical_significance_ordered=["pathogenic", "likely_pathogenic"],
            review_status_ordered=["practice guideline", "practice guideline"],
        )
        self.bgjob.clinvarquery.query_results.add(small_var)

    def test_count_results(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:load-clinvar-results",
                    kwargs={
                        "project": self.bgjob.case.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["result_count"], 1)
            self.assertEqual(response.context["result_rows"][0]["max_significance"], "pathogenic")


class TestCaseClinvarReportJobGetStatus(ViewTestBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    def setUp(self):
        super().setUp()
        self.bgjob = ClinvarBgJobFactory(user=self.user)

    def test_getting_status_valid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": self.bgjob.sodar_uuid},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["status"], "initial")

    def test_getting_status_invalid_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": "cccccccc-cccc-cccc-cccc-cccccccccccc"},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))

    def test_getting_status_missing_uuid(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:clinvar-job-status", kwargs={"project": self.bgjob.project.sodar_uuid}
                ),
                {"filter_job_uuid": None},
            )
            self.assertEqual(response.status_code, 400)
            self.assertTrue("error" in json.loads(response.content.decode("utf-8")))


class TestCaseClinvarReportJobGetPrevious(ViewTestBase):
    """Test CaseLoadPrefetchedClinvarReportView"""

    def setUp(self):
        super().setUp()
        self.bgjob = ClinvarBgJobFactory(user=self.user)

    def test_getting_previous_job_existing(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:clinvar-job-previous",
                    kwargs={
                        "project": self.bgjob.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                json.loads(response.content.decode("utf-8"))["filter_job_uuid"],
                str(self.bgjob.sodar_uuid),
            )

    def test_getting_previous_job_non_existing(self):
        with self.login(self.user):
            project = self.bgjob.project.sodar_uuid
            case = self.bgjob.case.sodar_uuid
            self.bgjob.delete()
            response = self.client.get(
                reverse("variants:clinvar-job-previous", kwargs={"project": project, "case": case})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["filter_job_uuid"], None)


class TestDistillerSubmissionJobDetailView(ViewTestBase):
    """Tests for DistillerSubmissionJobDetailView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = DistillerSubmissionBgJobFactory(user=self.user)

    def test_status_code_200(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, self.bgjob.case.name)


class TestDistillerSubmissionJobResubmitView(ViewTestBase):
    """Tests for DistillerSubmissionJobResubmitView.
    """

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case

    @Mocker()
    def test_resubmission(self, mock):
        with self.login(self.user):
            # Mock post
            from ..submit_external import DISTILLER_POST_URL

            mock.post(
                DISTILLER_POST_URL,
                status_code=200,
                text=(
                    '\n<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">\n<HTM'
                    'L>\n<HEAD>\n<TITLE>testsubmission - QueryEngine initialising</TITLE>\n<meta http-equiv="refresh" content="5; U'
                    'RL=/temp/QE/vcf_10585_21541/progress.html">\n<link href="/MutationTaster/css.css" rel="stylesheet" type="text/'
                    'css">\n</head><body>\n\n\t\t<table  border="0" width="100%" cellspacing="20">\n\t\t\t<tr>\n\t\t\t\t<td style="'
                    'text-align:center"><img src="/MutationTaster/MutationTaster_small.png" alt="Yum, tasty mutations..." align="le'
                    'ft"></td>\n\t\t\t\t<td ><h1>testsubmission - QueryEngine initialising</h1></td>\n\t\t\t\t<td><A HREF="/Mutatio'
                    'nTaster/info/MTQE_documentation.html" TARGET="_blank">MTQE documentation</A></td>\n\t\t\t</tr>\n\t\t</table> <'
                    "h1>testsubmission - QueryEngine initialising</h1>\n<h2>We are uploading your file. NEVER press reload or F5 - "
                    "unless you want to start from the very beginning. </h2>MutationTaster QueryEngine: vcf number 10585<br>"
                ),
            )
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 0)
            # Create background job
            self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    FormDataFactory(
                        submit="submit-mutationdistiller", names=self.case.get_members()
                    )
                ),
            )
            first_bgjob = DistillerSubmissionBgJob.objects.last()
            # Re-submit background job
            response = self.client.post(
                reverse(
                    "variants:distiller-job-resubmit",
                    kwargs={"project": self.case.project.sodar_uuid, "job": first_bgjob.sodar_uuid},
                )
            )
            # Check existence of resubmitted job
            self.assertEquals(DistillerSubmissionBgJob.objects.count(), 2)
            second_bgjob = DistillerSubmissionBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "job": second_bgjob.sodar_uuid,
                    },
                ),
            )


class TestSmallVariantDetailsView(ViewTestBase):
    """Test variant details view"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.small_var = SmallVariantFactory(variant_set=self.variant_set)
        coords = {
            "chromosome": self.small_var.chromosome,
            "start": self.small_var.start,
            "end": self.small_var.end,
            "bin": self.small_var.bin,
            "reference": self.small_var.reference,
            "alternative": self.small_var.alternative,
        }
        self.thousand_genomes = ThousandGenomesFactory(**coords)
        self.exac = ExacFactory(**coords)
        self.gnomad_exomes = GnomadExomesFactory(**coords)
        self.gnomad_genomes = GnomadGenomesFactory(**coords)
        self.knowngeneaa = KnownGeneAAFactory(
            chromosome=self.small_var.chromosome,
            start=self.small_var.start,
            transcript_id=self.small_var.ensembl_transcript_id,
        )
        self.clinvar = ClinvarFactory(release=self.small_var.release, **coords)
        self.hgnc = HgncFactory(
            ensembl_gene_id=self.small_var.ensembl_gene_id, entrez_id=self.small_var.refseq_gene_id
        )
        self.mim2genemedgen_pheno = Mim2geneMedgenFactory(entrez_id=self.small_var.refseq_gene_id)
        self.mim2genemedgen_gene = Mim2geneMedgenFactory(
            entrez_id=self.small_var.refseq_gene_id, omim_type="gene"
        )
        # Fix the both HPO terms to clearly distinguish between inheritance term and no inheritance term.
        self.hpo = HpoFactory(
            database_id="OMIM:%d" % self.mim2genemedgen_pheno.omim_id,
            hpo_id="HP:0000001",
            name="Disease 1;;Alternative Description",
        )
        self.hpo_inheritance = HpoFactory(
            database_id="OMIM:%d" % self.mim2genemedgen_pheno.omim_id,
            hpo_name="AR",
            hpo_id="HP:0000007",
            name="Disease 2; AR",
        )
        EnsemblToRefseqFactory(
            ensembl_gene_id=self.small_var.ensembl_gene_id,
            ensembl_transcript_id=self.small_var.ensembl_transcript_id,
            entrez_id=self.small_var.refseq_gene_id,
        )
        RefseqToEnsemblFactory(
            entrez_id=self.small_var.refseq_gene_id,
            ensembl_gene_id=self.small_var.ensembl_gene_id,
            ensembl_transcript_id=self.small_var.ensembl_transcript_id,
        )
        self.gnomadconstraints = GnomadConstraintsFactory(
            ensembl_gene_id=self.small_var.ensembl_gene_id
        )
        self.exacconstraints = ExacConstraintsFactory(
            ensembl_transcript_id=self.small_var.ensembl_transcript_id
        )
        self.smallvariantflags = SmallVariantFlagsFactory(
            case=self.case, release=self.small_var.release, **coords
        )
        self.smallvariantcomment = SmallVariantCommentFactory(
            case=self.case, user=self.user, release=self.small_var.release, **coords
        )

    def test_render(self):
        """Test rendering of the variant detail view"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "refseq",
                        "gene_id": self.small_var.refseq_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["base_template"], "empty_base.html")

    def test_render_full(self):
        """Smoke test for rendering in full mode. This was introduced to help debugging
        and this part of the code is not used in production mode.
        """
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "refseq",
                        "gene_id": self.small_var.refseq_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                ),
                {"render_full": "yes"},
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["base_template"], "projectroles/project_base.html")

    def _base_test_content(self, db):
        """Base function to test both transcript databases, ensembl and refseq."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": db,
                        "gene_id": getattr(self.small_var, "%s_gene_id" % db),
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["af"],
                self.gnomad_exomes.af_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["het"],
                self.gnomad_exomes.het_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["AFR"]["hom"],
                self.gnomad_exomes.hom_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["Total"]["af"], self.gnomad_exomes.af
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["Total"]["het"],
                self.gnomad_exomes.het,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Exomes"]["Total"]["hom"],
                self.gnomad_exomes.hom,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["af"],
                self.gnomad_genomes.af_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["het"],
                self.gnomad_genomes.het_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["AFR"]["hom"],
                self.gnomad_genomes.hom_afr,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["Total"]["af"],
                self.gnomad_genomes.af,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["Total"]["het"],
                self.gnomad_genomes.het,
            )
            self.assertEqual(
                response.context["pop_freqs"]["gnomAD Genomes"]["Total"]["hom"],
                self.gnomad_genomes.hom,
            )
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["af"], self.exac.af_afr)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["het"], self.exac.het_afr)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["AFR"]["hom"], self.exac.hom_afr)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["Total"]["af"], self.exac.af)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["Total"]["het"], self.exac.het)
            self.assertEqual(response.context["pop_freqs"]["ExAC"]["Total"]["hom"], self.exac.hom)
            self.assertEqual(
                response.context["pop_freqs"]["1000GP"]["AMR"]["af"], self.thousand_genomes.af_amr
            )
            self.assertEqual(
                response.context["pop_freqs"]["1000GP"]["Total"]["af"], self.thousand_genomes.af
            )
            self.assertEqual(
                response.context["clinvar"][0]["clinical_significance"],
                self.clinvar.clinical_significance,
            )
            self.assertEqual(
                response.context["knowngeneaa"][0]["alignment"], self.knowngeneaa.alignment
            )
            self.assertEqual(response.context["gene"]["hpo_terms"][0][0], self.hpo.hpo_id)
            self.assertEqual(
                response.context["gene"]["hpo_terms"][0][1],
                HpoName.objects.get(hpo_id=self.hpo.hpo_id).name,
            )
            self.assertEqual(
                response.context["gene"]["hpo_inheritance"][0][0], self.hpo_inheritance.hpo_id
            )
            self.assertEqual(
                response.context["gene"]["hpo_inheritance"][0][1],
                HpoName.objects.get(hpo_id=self.hpo_inheritance.hpo_id).name,
            )
            omim_name = self.hpo.name.split(";;")
            self.assertEqual(
                response.context["gene"]["omim"][self.mim2genemedgen_pheno.omim_id][0], omim_name[0]
            )
            self.assertEqual(
                response.context["gene"]["omim"][self.mim2genemedgen_pheno.omim_id][1][0],
                omim_name[1],
            )
            self.assertEqual(
                list(response.context["gene"]["omim_genes"])[0], self.mim2genemedgen_gene.omim_id
            )
            self.assertEqual(response.context["gene"]["symbol"], self.hgnc.symbol)
            self.assertEqual(
                response.context["gene"]["exac_constraints"].exp_syn, self.exacconstraints.exp_syn
            )
            self.assertEqual(
                response.context["gene"]["gnomad_constraints"].exp_syn,
                self.gnomadconstraints.exp_syn,
            )
            self.assertTrue(response.context["flags"].flag_bookmarked)
            self.assertEqual(response.context["comments"][0].text, self.smallvariantcomment.text)
            self.assertEqual(response.context["comments"][0].user, self.user)

    def test_content_refseq(self):
        self._base_test_content("refseq")

    def test_content_ensembl(self):
        self._base_test_content("ensembl")

    def test_content_refseq_missing_hgnc(self):
        Hgnc.objects.first().delete()
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "refseq",
                        "gene_id": self.small_var.refseq_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.context["gene"]["entrez_id"], self.small_var.refseq_gene_id)
            self.assertFalse("hpo_terms" in response.context["gene"])

    def test_content_ensembl_missing_hgnc(self):
        Hgnc.objects.first().delete()
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "ensembl",
                        "gene_id": self.small_var.ensembl_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(
                response.context["gene"]["ensembl_gene_id"], self.small_var.ensembl_gene_id
            )
            self.assertFalse("hpo_terms" in response.context["gene"])

    # No need to test this for refseq as entrez_id is always available.
    # The entrez ID, given the ensembl_gene_id, is retrieved via hgnc_id -> RefseqToHgnc.
    # As every record in RefseqToHgnc has a mapping, this case can only appear when the hgnc_id is not available in RefseqToHgnc.
    def test_content_ensembl_missing_entrez_id(self):
        o = RefseqToHgnc.objects.first()
        o.hgnc_id = "Not existing"
        o.save()
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "ensembl",
                        "gene_id": self.small_var.ensembl_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertListEqual(response.context["gene"]["hpo_terms"], [])
            self.assertListEqual(response.context["gene"]["hpo_inheritance"], [])
            self.assertDictEqual(response.context["gene"]["omim"], {})
            self.assertListEqual(response.context["gene"]["omim_genes"], [])

    def test_with_jannovar_disabled(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "ensembl",
                        "gene_id": self.small_var.ensembl_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["effect_details"], [])

    @patch("django.conf.settings.VARFISH_ENABLE_JANNOVAR", True)
    @patch("django.conf.settings.VARFISH_JANNOVAR_REST_API_URL", "https://jannovar.example.com/")
    @Mocker()
    def test_with_jannovar_enabled(self, mock):
        with self.login(self.user):
            mock.get(
                "https://jannovar.example.com/annotate-var/ensembl/hg19/%s/%s/%s/%s"
                % (
                    self.small_var.chromosome,
                    self.small_var.start,
                    self.small_var.reference,
                    self.small_var.alternative,
                ),
                status_code=200,
                json=[
                    {
                        "transcriptId": "NM_058167.2",
                        "variantEffects": ["three_prime_utr_exon_variant"],
                        "isCoding": True,
                        "hgvsProtein": "p.(=)",
                        "hgvsNucleotides": "c.*60G>A",
                    },
                    {
                        "transcriptId": "NM_194315.1",
                        "variantEffects": ["three_prime_utr_exon_variant"],
                        "isCoding": True,
                        "hgvsProtein": "p.(=)",
                        "hgvsNucleotides": "c.*60G>A",
                    },
                ],
            )
            response = self.client.get(
                reverse(
                    "variants:small-variant-details",
                    kwargs={
                        "project": self.case.project.sodar_uuid,
                        "case": self.case.sodar_uuid,
                        "release": self.small_var.release,
                        "chromosome": self.small_var.chromosome,
                        "start": self.small_var.start,
                        "end": self.small_var.end,
                        "reference": self.small_var.reference,
                        "alternative": self.small_var.alternative,
                        "database": "ensembl",
                        "gene_id": self.small_var.ensembl_gene_id,
                        "ensembl_transcript_id": self.small_var.ensembl_transcript_id,
                        "training_mode": 0,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["effect_details"]), 2)
            self.assertEqual(response.context["effect_details"][0]["transcriptId"], "NM_058167.2")
            self.assertEqual(response.context["effect_details"][1]["transcriptId"], "NM_194315.1")


class TestExportFileJobDetailView(ViewTestBase):
    """Test export file job detail view"""

    def setUp(self):
        super().setUp()
        self.bgjob = ExportFileBgJobFactory(user=self.user)

    def test_render(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)


class TestExportFileJobResubmitView(ViewTestBase):
    """Test export file job resubmit view"""

    def setUp(self):
        super().setUp()
        self.bgjob = ExportFileBgJobFactory(user=self.user)

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            response = self.client.post(
                reverse(
                    "variants:export-job-resubmit",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                ),
                {"file_type": "xlsx"},
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 2)
            # Take first job as they are ordered descending by date
            created_job = ExportFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )

    def test_render_detail_view(self):
        """Test if rendering works."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportFileJobDownloadView(ViewTestBase):
    """Test export file job download view"""

    def setUp(self):
        super().setUp()
        self.bgjob = ExportFileBgJobFactory(user=self.user)

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 404)


class TestExportFileJobDownloadViewResult(ViewTestBase):
    """Test export file download view"""

    def setUp(self):
        super().setUp()
        self.results = ExportFileJobResultFactory(user=self.user)

    def test_download(self):
        """Test file download"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={
                        "project": self.results.job.project.sodar_uuid,
                        "job": self.results.job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, self.results.payload)


class TestExportProjectCasesFileJobResubmitView(ViewTestBase):
    """Test ExportProjectCasesFileJobResubmitView.
    """

    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        CaseFactory(project=project)
        CaseFactory(project=project)
        self.bgjob = ExportProjectCasesFileBgJobFactory(user=self.user, project=project)

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.user):
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
            response = self.client.post(
                reverse(
                    "variants:project-cases-export-job-resubmit",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                ),
                {"file_type": "xlsx"},
            )
            self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 2)
            created_job = ExportProjectCasesFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )

    def test_render_detail_view(self):
        """Test if rendering works."""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportProjectCasesFileJobDownloadView(ViewTestBase):
    """Test ExportProjectCasesFileJobDownloadView.
    """

    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        CaseFactory(project=project)
        CaseFactory(project=project)
        self.bgjob = ExportProjectCasesFileBgJobFactory(user=self.user, project=project)

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-download",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 404)


class TestExportProjectCasesFileJobDownloadViewResult(ViewTestBase):
    """Test project cases file download view"""

    def setUp(self):
        super().setUp()
        self.results = ExportProjectCasesFileBgJobResultFactory(user=self.user)

    def test_download(self):
        """Test file download"""
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-download",
                    kwargs={
                        "project": self.results.job.project.sodar_uuid,
                        "job": self.results.job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, self.results.payload)


class TestProjectStatsJobCreateView(ViewTestBase):
    """Test ProjectStatsJobCreateView.
    """

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        CaseFactory(project=self.project)
        CaseFactory(project=self.project)

    def test_project_stat_job_creation(self):
        with self.login(self.user):
            response = self.client.post(
                reverse(
                    "variants:project-stats-job-create", kwargs={"project": self.project.sodar_uuid}
                )
            )
            created_job = ComputeProjectVariantsStatsBgJob.objects.last()
            self.assertRedirects(
                response,
                reverse(
                    "variants:project-stats-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                ),
            )


class TestProjectStatsJobDetailView(ViewTestBase):
    """Test ProjectStatsJobDetailView.
    """

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        CaseFactory(project=self.project)
        CaseFactory(project=self.project)

    def test_render(self):
        with self.login(self.user):
            self.client.post(
                reverse(
                    "variants:project-stats-job-create", kwargs={"project": self.project.sodar_uuid}
                )
            )
            created_job = ComputeProjectVariantsStatsBgJob.objects.last()
            response = self.client.get(
                reverse(
                    "variants:project-stats-job-detail",
                    kwargs={"project": self.project.sodar_uuid, "job": created_job.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response.context["object"].bg_job.name,
                "Recreate variant statistic for whole project",
            )


class TestSmallVariantFlagsApiView(ViewTestBase):
    """Test SmallVariantFlagsApiView.
    """

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.small_var = SmallVariantFactory(variant_set=self.variant_set)

    def test_get_json_response_non_existing(self):
        with self.login(self.user):
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            response = self.client.get(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {
                    "release": self.small_var.release,
                    "chromosome": self.small_var.chromosome,
                    "start": self.small_var.start,
                    "end": self.small_var.end,
                    "reference": self.small_var.reference,
                    "alternative": self.small_var.alternative,
                },
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            self.assertEqual(response.status_code, 404)

    def test_post_json_response_non_existing(self):
        with self.login(self.user):
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 1)
            self.assertEqual(response.status_code, 200)

    def test_get_json_response_existing(self):
        with self.login(self.user):
            # Create variant
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            # Query variant
            response = self.client.get(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {
                    "release": self.small_var.release,
                    "chromosome": self.small_var.chromosome,
                    "start": self.small_var.start,
                    "end": self.small_var.end,
                    "reference": self.small_var.reference,
                    "alternative": self.small_var.alternative,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(json.loads(response.content.decode("utf-8"))["flag_bookmarked"])

    def test_post_json_response_existing(self):
        with self.login(self.user):
            # Create variant
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            # Query variant
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        flag_bookmarked=False,
                        flag_candidate=True,
                    )
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(json.loads(response.content.decode("utf-8"))["flag_bookmarked"])
            self.assertTrue(json.loads(response.content.decode("utf-8"))["flag_candidate"])

    def test_post_remove_flags(self):
        with self.login(self.user):
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            # Create flags
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 1)
            # Delete flags
            response = self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        flag_bookmarked=False,
                    )
                ),
            )
            self.assertEqual(SmallVariantFlags.objects.count(), 0)
            self.assertEqual(response.status_code, 200)

    def test_post_provoke_form_error(self):
        with self.login(self.user), self.assertRaises(Exception):
            self.client.post(
                reverse(
                    "variants:small-variant-flags-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantFlagsFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        flag_visual=100,
                    )
                ),
            )


class TestSmallVariantCommentApiView(ViewTestBase):
    """Test SmallVariantCommentApiView.
    """

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.small_var = SmallVariantFactory(variant_set=self.variant_set)

    def test_json_response(self):
        with self.login(self.user):
            self.assertEqual(SmallVariantComment.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:small-variant-comment-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    SmallVariantCommentFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            self.assertEqual(SmallVariantComment.objects.count(), 1)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["result"], "OK")


class TestBackgroundJobListView(ViewTestBase):
    """Test BackgroundJobListView.
    """

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.user)

    def test_render(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:job-list",
                    kwargs={
                        "project": self.bgjob.case.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_resulting_list_length(self):
        with self.login(self.user):
            response = self.client.get(
                reverse(
                    "variants:job-list",
                    kwargs={
                        "project": self.bgjob.case.project.sodar_uuid,
                        "case": self.bgjob.case.sodar_uuid,
                    },
                )
            )
            self.assertEqual(len(response.context["object_list"]), 1)


class TestAcmgCriteriaRatingApiView(ViewTestBase):
    """Test AcmgCriteriaRatingApiView"""

    def setUp(self):
        super().setUp()
        self.variant_set = SmallVariantSetFactory()
        self.case = self.variant_set.case
        self.small_var = SmallVariantFactory(variant_set=self.variant_set)

    def test_get_response_not_existing(self):
        with self.login(self.user):
            self.assertEqual(AcmgCriteriaRating.objects.count(), 0)
            response = self.client.get(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {
                    "release": self.small_var.release,
                    "chromosome": self.small_var.chromosome,
                    "start": self.small_var.start,
                    "end": self.small_var.end,
                    "reference": self.small_var.reference,
                    "alternative": self.small_var.alternative,
                },
            )
            self.assertEqual(AcmgCriteriaRating.objects.count(), 0)
            self.assertEqual(response.status_code, 404)

    def test_post_response_not_existing(self):
        with self.login(self.user):
            self.assertEqual(AcmgCriteriaRating.objects.count(), 0)
            response = self.client.post(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    AcmgCriteriaRatingFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                    )
                ),
            )
            self.assertEqual(AcmgCriteriaRating.objects.count(), 1)
            self.assertEqual(response.status_code, 200)

    def test_get_response_existing(self):
        with self.login(self.user):
            self.client.post(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    AcmgCriteriaRatingFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        ps1=2,
                    )
                ),
            )
            response = self.client.get(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                {
                    "release": self.small_var.release,
                    "chromosome": self.small_var.chromosome,
                    "start": self.small_var.start,
                    "end": self.small_var.end,
                    "reference": self.small_var.reference,
                    "alternative": self.small_var.alternative,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["ps1"], 2)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["user"], self.user.id)

    def test_post_response_existing(self):
        with self.login(self.user):
            self.client.post(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    AcmgCriteriaRatingFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        ps1=1,
                    )
                ),
            )
            response = self.client.post(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    AcmgCriteriaRatingFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        ps2=1,
                    )
                ),
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["ps1"], 0)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["ps2"], 1)
            self.assertEqual(json.loads(response.content.decode("utf-8"))["user"], self.user.id)

    def test_post_provoke_form_error(self):
        with self.login(self.user), self.assertRaises(Exception):
            self.client.post(
                reverse(
                    "variants:acmg-rating-api",
                    kwargs={"project": self.case.project.sodar_uuid, "case": self.case.sodar_uuid},
                ),
                vars(
                    AcmgCriteriaRatingFormDataFactory(
                        release=self.small_var.release,
                        chromosome=self.small_var.chromosome,
                        start=self.small_var.start,
                        end=self.small_var.end,
                        bin=self.small_var.bin,
                        reference=self.small_var.reference,
                        alternative=self.small_var.alternative,
                        ps1="I'm supposed to be an integer!",
                    )
                ),
            )


class TestNewFeaturesView(ViewTestBase):
    """Test NewFeaturesView."""

    def test_response(self):
        with self.login(self.user):
            response = self.client.get(reverse("variants:new-features"))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/manual/history.html")
            settings_api = AppSettingAPI()
            value = settings_api.get_app_setting(
                "variants", "latest_version_seen_changelog", user=self.user
            )
            self.assertEqual(value, site_version())
