"""Tests for the filter view"""

from django.core.urlresolvers import reverse
from django.test import RequestFactory
from django.utils import timezone
from test_plus.test import TestCase

from projectroles.models import Project
from variants.models import SmallVariant, ExportFileBgJob, Case, ExportFileJobResult
from clinvar.models import Clinvar
from frequencies.models import Exac, GnomadGenomes, GnomadExomes, ThousandGenomes

from ._fixtures import CLINVAR_DEFAULTS, CLINVAR_FORM_DEFAULTS

import json

# Shared project settings
PROJECT_DICT = {
    "title": "project",
    "type": "PROJECT",
    "parent_id": None,
    "description": "",
    "readme": "",
    "submit_status": "OK",
    "sodar_uuid": "7c599407-6c44-4d9e-81aa-cd8cf3d817a4",
}

# Default form settings
DEFAULT_FILTER_FORM_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "compound_recessive_enabled": False,
    "effect_coding_transcript_intron_variant": True,
    "effect_complex_substitution": True,
    "effect_direct_tandem_duplication": True,
    "effect_disruptive_inframe_deletion": True,
    "effect_disruptive_inframe_insertion": True,
    "effect_downstream_gene_variant": True,
    "effect_feature_truncation": True,
    "effect_five_prime_UTR_exon_variant": True,
    "effect_five_prime_UTR_intron_variant": True,
    "effect_frameshift_elongation": True,
    "effect_frameshift_truncation": True,
    "effect_frameshift_variant": True,
    "effect_inframe_deletion": True,
    "effect_inframe_insertion": True,
    "effect_intergenic_variant": True,
    "effect_internal_feature_elongation": True,
    "effect_missense_variant": True,
    "effect_mnv": True,
    "effect_non_coding_transcript_exon_variant": True,
    "effect_non_coding_transcript_intron_variant": True,
    "effect_splice_acceptor_variant": True,
    "effect_splice_donor_variant": True,
    "effect_splice_region_variant": True,
    "effect_start_lost": True,
    "effect_stop_gained": True,
    "effect_stop_lost": True,
    "effect_stop_retained_variant": True,
    "effect_structural_variant": True,
    "effect_synonymous_variant": True,
    "effect_three_prime_UTR_exon_variant": True,
    "effect_three_prime_UTR_intron_variant": True,
    "effect_transcript_ablation": True,
    "effect_upstream_gene_variant": True,
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "gene_blacklist": "",
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "clinvar_include_benign": False,
    "clinvar_include_likely_benign": False,
    "clinvar_include_uncertain_significance": False,
    "clinvar_include_likely_pathogenic": True,
    "clinvar_include_pathogenic": True,
    "submit": "display",
}

DEFAULT_RESUBMIT_SETTING = {
    "database_select": "refseq",
    "A_fail": "ignore",
    "A_gt": "any",
    "A_dp_het": 0,
    "A_dp_hom": 0,
    "A_gq": 0,
    "A_ad": 0,
    "A_ab": 0.0,
    "compound_recessive_enabled": False,
    "effects": [
        "coding_transcript_intron_variant",
        "complex_substitution",
        "direct_tandem_duplication",
        "disruptive_inframe_deletion",
        "disruptive_inframe_insertion",
        "downstream_gene_variant",
        "feature_truncation",
        "five_prime_UTR_exon_variant",
        "five_prime_UTR_intron_variant",
        "frameshift_elongation",
        "frameshift_truncation",
        "frameshift_variant",
        "inframe_deletion",
        "inframe_insertion",
        "intergenic_variant",
        "internal_feature_elongation",
        "missense_variant",
        "mnv",
        "non_coding_transcript_exon_variant",
        "non_coding_transcript_intron_variant",
        "splice_acceptor_variant",
        "splice_donor_variant",
        "splice_region_variant",
        "start_lost",
        "stop_gained",
        "stop_lost",
        "stop_retained_variant",
        "structural_variant",
        "synonymous_variant",
        "three_prime_UTR_exon_variant",
        "three_prime_UTR_intron_variant",
        "transcript_ablation",
        "upstream_gene_variant",
    ],
    "exac_enabled": False,
    "exac_frequency": 1.0,
    "exac_heterozygous": 1000,
    "exac_homozygous": 1000,
    "file_type": "xlsx",
    "gene_blacklist": "",
    "gnomad_exomes_enabled": False,
    "gnomad_exomes_frequency": 1.0,
    "gnomad_exomes_heterozygous": 1000,
    "gnomad_exomes_homozygous": 1000,
    "gnomad_genomes_enabled": False,
    "gnomad_genomes_frequency": 1.0,
    "gnomad_genomes_heterozygous": 1000,
    "gnomad_genomes_homozygous": 1000,
    "result_rows_limit": 80,
    "thousand_genomes_enabled": False,
    "thousand_genomes_frequency": 1.0,
    "thousand_genomes_heterozygous": 1000,
    "thousand_genomes_homozygous": 1000,
    "var_type_indel": True,
    "var_type_mnv": True,
    "var_type_snv": True,
    "transcripts_noncoding": True,
    "transcripts_coding": True,
    "require_in_clinvar": False,
    "submit": "display",
}


def fixture_setup_case(user):
    """Set up test case for filter tests. Contains a case with three variants."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    )

    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "position": None,
        "reference": "A",
        "alternative": "G",
        "var_type": "snv",
        "genotype": {"A": {"ad": 15, "dp": 30, "gq": 99, "gt": "0/1"}},
        "in_clinvar": False,
        # frequencies
        "exac_frequency": 0.01,
        "exac_homozygous": 0,
        "exac_heterozygous": 0,
        "exac_hemizygous": 0,
        "thousand_genomes_frequency": 0.01,
        "thousand_genomes_homozygous": 0,
        "thousand_genomes_heterozygous": 0,
        "thousand_genomes_hemizygous": 0,
        "gnomad_exomes_frequency": 0.01,
        "gnomad_exomes_homozygous": 0,
        "gnomad_exomes_heterozygous": 0,
        "gnomad_exomes_hemizygous": 0,
        "gnomad_genomes_frequency": 0.01,
        "gnomad_genomes_homozygous": 0,
        "gnomad_genomes_heterozygous": 0,
        "gnomad_genomes_hemizygous": 0,
        # RefSeq
        "refseq_gene_id": "1234",
        "refseq_transcript_id": "NR_00001.1",
        "refseq_transcript_coding": False,
        "refseq_hgvs_c": "n.111+2T>C",
        "refseq_hgvs_p": "p.=",
        "refseq_effect": ["synonymous_variant"],
        # ENSEMBL
        "ensembl_gene_id": "ENSG0001",
        "ensembl_transcript_id": "ENST00001",
        "ensembl_transcript_coding": False,
        "ensembl_hgvs_c": "n.111+2T>C",
        "ensembl_hgvs_p": "p.=",
        "ensembl_effect": ["synonymous_variant"],
    }

    SmallVariant.objects.create(**{**basic_var, **{"position": 100}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 200, "in_clinvar": True}})
    SmallVariant.objects.create(**{**basic_var, **{"position": 300}})

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "position": 200,
            "start": 200,
            "stop": 200,
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )


class TestViewBase(TestCase):
    """Base class for view testing (and file export)"""

    setup_case_in_db = None

    def setUp(self):
        self.request_factory = RequestFactory()

        # setup super user
        self.user = self.make_user("superuser")
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        # some fixtures need the created user
        self.__class__.setup_case_in_db(self.user)


class TestCaseListView(TestViewBase):
    """Test case list view"""

    setup_case_in_db = fixture_setup_case

    def test_render(self):
        """Test display of case list page."""
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.get(
                reverse("variants:case-list", kwargs={"project": project.sodar_uuid})
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(response.context["case_list"]), 1)


class TestCaseDetailView(TestViewBase):
    """Test case detail view"""

    setup_case_in_db = fixture_setup_case

    def test_render(self):
        """Test display of case detail view page."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()

            response = self.client.get(
                reverse(
                    "variants:case-detail",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context["object"].name, "A")


class TestCaseFilterView(TestViewBase):
    """Test case filter view"""

    setup_case_in_db = fixture_setup_case

    def test_get(self):
        """Test display of the filter forms, no form applied."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )

            self.assertEqual(response.status_code, 200)

    def test_form_valid_post_display(self):
        """Test form submit to display results table."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                DEFAULT_FILTER_FORM_SETTING,
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context["form"].is_valid())
            self.assertEqual(response.context["result_count"], 3)

    def test_form_invalid_post_display(self):
        """Test invalid form submit."""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "gnomad_exomes_heterozygous": None},
            )
            self.assertEqual(response.status_code, 200)
            self.assertFalse(response.context["form"].is_valid())

    def test_post_download(self):
        """Test form submit for download as file."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 0)
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-filter",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**DEFAULT_FILTER_FORM_SETTING, "submit": "download"},
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            created_job = ExportFileBgJob.objects.first()
            self.assertRedirects(
                response,
                reverse(
                    "variants:export-job-detail",
                    kwargs={"project": case.project.sodar_uuid, "job": created_job.sodar_uuid},
                ),
            )


class TestCaseClinvarReportView(TestViewBase):
    """Test case Clinvar report view"""

    setup_case_in_db = fixture_setup_case

    def test_get_renders_form(self):
        """Test that GET returns the form"""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:case-clinvar",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.context[-1].get("form"))

    def test_post_returns_report(self):
        """Test that an appropriate POST returns a report"""
        with self.login(self.user):
            case = Case.objects.select_related("project").first()
            response = self.client.post(
                reverse(
                    "variants:case-clinvar",
                    kwargs={"project": case.project.sodar_uuid, "case": case.sodar_uuid},
                ),
                {**CLINVAR_FORM_DEFAULTS, "submit": "display"},
            )
            self.assertEqual(response.status_code, 200)
            result_rows = list(response.context[-1].get("result_rows"))
            self.assertEquals(len(result_rows), 1)


def fixture_setup_expand(user):
    """Setup test case for expand view. Contains project and frequency objects"""
    project = Project.objects.create(**PROJECT_DICT)
    basic_var = {
        "release": "GRCh37",
        "chromosome": "1",
        "position": 100,
        "reference": "A",
        "alternative": "G",
        "ac": None,
        "ac_afr": 1,
        "ac_amr": 0,
        "ac_eas": 0,
        "ac_fin": 0,
        "ac_nfe": 0,
        "ac_oth": 0,
        "an": None,
        "an_afr": 8726,
        "an_amr": 838,
        "an_eas": 1620,
        "an_fin": 3464,
        "an_nfe": 14996,
        "an_oth": 982,
        "hemi": None,
        "hemi_afr": None,
        "hemi_amr": None,
        "hemi_eas": None,
        "hemi_fin": None,
        "hemi_nfe": None,
        "hemi_oth": None,
        "hom": 0,
        "hom_afr": 0,
        "hom_amr": 0,
        "hom_eas": 0,
        "hom_fin": 0,
        "hom_nfe": 0,
        "hom_oth": 0,
        "popmax": "AFR",
        "ac_popmax": 1,
        "an_popmax": 8726,
        "af_popmax": 0.0001146,
        "hemi_popmax": None,
        "hom_popmax": 0,
        "af": None,
        "af_afr": 0.0001146,
        "af_amr": 0.0,
        "af_eas": 0.0,
        "af_fin": 0.0,
        "af_nfe": 0.0,
        "af_oth": 0.0,
    }

    Exac.objects.create(
        **{
            **basic_var,
            **{"ac_sas": 0, "an_sas": 323, "hemi_sas": None, "hom_sas": 0, "af_sas": 0.0},
        }
    )
    ThousandGenomes.objects.create(
        release="GRCh37",
        chromosome="1",
        position=100,
        reference="A",
        alternative="G",
        ac=3,
        an=5008,
        het=3,
        hom=0,
        af=0.000058,
        af_afr=0.0,
        af_amr=0.0054,
        af_eas=0.0,
        af_eur=0.0,
        af_sas=0.0,
    )
    GnomadExomes.objects.create(
        **{
            **basic_var,
            **{
                "ac_asj": 0,
                "ac_sas": 0,
                "an_asj": 323,
                "an_sas": 932,
                "hemi_asj": None,
                "hemi_sas": None,
                "hom_asj": 0,
                "hom_sas": 0,
                "af_asj": 0.0,
                "af_sas": 0.0,
            },
        }
    )
    GnomadGenomes.objects.create(
        **{
            **basic_var,
            **{"ac_asj": 0, "an_asj": 323, "hemi_asj": None, "hom_asj": 0, "af_asj": 0.0},
        }
    )


class TestExpandView(TestViewBase):
    """Test table expansion view"""

    setup_case_in_db = fixture_setup_expand

    def test_render(self):
        """Test rendering of the expansion"""
        with self.login(self.user):
            project = Project.objects.first()
            response = self.client.get(
                reverse(
                    "variants:extend",
                    kwargs={
                        "project": project.sodar_uuid,
                        "release": "GRCh37",
                        "chromosome": "1",
                        "position": 100,
                        "reference": "A",
                        "alternative": "G",
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content.decode("utf-8"))
            self.assertEqual(content["position"], "100")
            self.assertEqual(content["gnomadexomes"]["an_sas"], 932)
            self.assertEqual(content["exac"]["an_sas"], 323)
            self.assertEqual(content["gnomadgenomes"]["an_asj"], 323)
            self.assertEqual(content["thousandgenomes"]["af_amr"], 0.0054)
            # TODO: test clinvar and knowngeneaa


def fixture_setup_bgjob(user):
    """Setup for background job database (no associated file is generated!)"""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[{"sex": 1, "father": "0", "mother": "0", "patient": "A", "affected": 1}],
    )
    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a961", user=user, job_type="type"
    )
    return project.exportfilebgjob_set.create(
        sodar_uuid="10aabb75-7d61-46a9-955a-f385824b3200",
        bg_job=job,
        case=case,
        query_args=DEFAULT_RESUBMIT_SETTING,
        file_type="xlsx",
    )


class TestExportFileJobDetailView(TestViewBase):
    """Test export file job detail view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_render(self):
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)


class TestExportFileJobResubmitView(TestViewBase):
    """Test export file job resubmit view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.user):
            self.assertEquals(ExportFileBgJob.objects.count(), 1)
            existing_job = ExportFileBgJob.objects.first()
            response = self.client.post(
                reverse(
                    "variants:export-job-resubmit",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                ),
                {"file_type": "xlsx"},
            )
            self.assertEquals(ExportFileBgJob.objects.count(), 2)
            created_job = ExportFileBgJob.objects.last()
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
            existing_job = ExportFileBgJob.objects.first()
            response = self.client.get(
                reverse(
                    "variants:export-job-detail",
                    kwargs={
                        "project": existing_job.project.sodar_uuid,
                        "job": existing_job.sodar_uuid,
                    },
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportFileJobDownloadView(TestViewBase):
    """Test export file job download view"""

    setup_case_in_db = fixture_setup_bgjob

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 404)


def fixture_setup_bgjob_result(user):
    job = fixture_setup_bgjob(user)

    ExportFileJobResult.objects.create(job=job, expiry_time=timezone.now(), payload=b"Testcontent")


class TestExportFileJobDownloadViewResult(TestViewBase):
    """Test export file download view"""

    setup_case_in_db = fixture_setup_bgjob_result

    def test_download(self):
        """Test file download"""
        with self.login(self.user):
            created_job = ExportFileBgJob.objects.select_related("project").first()
            response = self.client.get(
                reverse(
                    "variants:export-job-download",
                    kwargs={
                        "project": created_job.project.sodar_uuid,
                        "job": created_job.sodar_uuid,
                    },
                )
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content, b"Testcontent")
