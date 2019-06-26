"""Tests for the ``file_export`` module."""

import json
import aldjemy
from unittest.mock import patch

import binning
from requests_mock import Mocker

from test_plus.test import TestCase

from .test_views import PROJECT_DICT
from ..forms import ProjectCasesFilterForm, ClinvarForm, FilterForm
from ..models import (
    ClinvarBgJob,
    ProjectCasesFilterBgJob,
    FilterBgJob,
    Case,
    SmallVariantQuery,
    ProjectCasesSmallVariantQuery,
    ClinvarQuery,
    SmallVariant,
)
from bgjobs.models import BackgroundJob
from projectroles.models import Project
from .test_views import (
    DEFAULT_RESUBMIT_SETTING,
    CLINVAR_RESUBMIT_SETTING,
    DEFAULT_JOINT_RESUBMIT_SETTING,
)
from ..submit_filter import CaseFilter, ProjectCasesFilter, ClinvarFilter
from clinvar.models import Clinvar
from variants.variant_stats import rebuild_case_variant_stats
from ._fixtures import CLINVAR_DEFAULTS
from variants.models import SmallVariantQueryGeneScores
from variants.models import SmallVariantQueryVariantScores
from django.conf import settings


SQLALCHEMY_ENGINE = aldjemy.core.get_engine()


def fixture_setup_case(user):
    """Set up test case for filter tests. Contains a case with three variants."""
    project = Project.objects.create(**PROJECT_DICT)
    case = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e3",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )

    basic_var = {
        "case_id": case.pk,
        "release": "GRCh37",
        "chromosome": "1",
        "start": None,
        "end": None,
        "bin": None,
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

    a = SmallVariant.objects.create(
        **{**basic_var, **{"start": 100, "end": 100, "bin": binning.assign_bin(99, 100)}}
    )
    b = SmallVariant.objects.create(
        **{
            **basic_var,
            **{"start": 200, "end": 200, "bin": binning.assign_bin(199, 200), "in_clinvar": True},
        }
    )
    c = SmallVariant.objects.create(
        **{**basic_var, **{"start": 300, "end": 300, "bin": binning.assign_bin(299, 300)}}
    )

    rebuild_case_variant_stats(SQLALCHEMY_ENGINE, case)

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "start": 200,
            "end": 200,
            "bin": binning.assign_bin(199, 200),
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )

    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a962", user=user, job_type="type"
    )


def fixture_setup_projectcases(user):
    """Set up test case for filter tests. Contains a case with three variants."""
    project = Project.objects.create(**PROJECT_DICT)
    case1 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e4",
        name="A",
        index="A",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "A",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )
    case2 = project.case_set.create(
        sodar_uuid="9b90556b-041e-47f1-bdc7-4d5a4f8357e5",
        name="B",
        index="B",
        pedigree=[
            {
                "sex": 1,
                "father": "0",
                "mother": "0",
                "patient": "B",
                "affected": 1,
                "has_gt_entries": True,
            }
        ],
    )

    basic_var = {
        "case_id": None,
        "release": "GRCh37",
        "chromosome": "1",
        "start": None,
        "end": None,
        "bin": None,
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

    a = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "start": 100,
            "end": 100,
            "bin": binning.assign_bin(99, 100),
        }
    )
    b = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "start": 200,
            "end": 200,
            "bin": binning.assign_bin(199, 200),
            "in_clinvar": True,
        }
    )
    c = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case1.pk,
            "start": 300,
            "end": 300,
            "bin": binning.assign_bin(299, 300),
        }
    )
    d = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "start": 100,
            "end": 100,
            "bin": binning.assign_bin(99, 100),
        }
    )
    e = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "start": 200,
            "end": 200,
            "bin": binning.assign_bin(199, 200),
            "in_clinvar": True,
        }
    )
    f = SmallVariant.objects.create(
        **{
            **basic_var,
            "case_id": case2.pk,
            "start": 300,
            "end": 300,
            "bin": binning.assign_bin(299, 300),
        }
    )

    Clinvar.objects.create(
        **{
            **CLINVAR_DEFAULTS,
            "start": 200,
            "end": 200,
            "bin": binning.assign_bin(199, 200),
            "clinical_significance": "pathogenic",
            "clinical_significance_ordered": ["pathogenic"],
            "review_status": ["practice guideline"],
            "review_status_ordered": ["practice guideline"],
        }
    )

    job = project.backgroundjob_set.create(
        sodar_uuid="97a65500-377b-4aa0-880d-9ba56d06a963", user=user, job_type="type"
    )


class FilterTestBase(TestCase):
    """Base class for testing filter jobs.

    Sets up the database fixtures for project, case, and small variants.
    """

    fixture = None

    def setUp(self, bg_job_model, query_model, form, defaults):
        self.user = self.make_user("superuser")
        self.__class__.fixture(self.user)
        self.bg_job = BackgroundJob.objects.create(
            name="job name",
            project=Project.objects.first(),
            job_type=bg_job_model.spec_name,
            user=self.user,
        )
        if query_model.__name__.startswith("Project"):
            query = query_model.objects.create(
                user=self.user,
                form_id=form.form_id,
                form_version=form.form_version,
                query_settings=defaults,
                project=Project.objects.first(),
            )
            self.specified_bg_job = bg_job_model.objects.create(
                **{
                    "project": self.bg_job.project,
                    "bg_job": self.bg_job,
                    query_model.__name__.lower(): query,
                }
            )
        else:
            query = query_model.objects.create(
                user=self.user,
                form_id=form.form_id,
                form_version=form.form_version,
                query_settings=defaults,
                case=Case.objects.first(),
            )
            self.specified_bg_job = bg_job_model.objects.create(
                **{
                    "project": self.bg_job.project,
                    "bg_job": self.bg_job,
                    "case": Case.objects.first(),
                    query_model.__name__.lower(): query,
                }
            )


class CaseFilterTest(FilterTestBase):
    """Test running single-case filter job."""

    fixture = fixture_setup_case

    def setUp(self):
        super().setUp(
            FilterBgJob,
            SmallVariantQuery,
            FilterForm,
            {
                **DEFAULT_RESUBMIT_SETTING,
                "prio_enabled": True,
                "prio_algorithm": "phenix",
                "prio_hpo_terms": ["HP:0000001"],
                "patho_enabled": True,
                "patho_score": "phenix",  # ?
            },
        )

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
            settings.VARFISH_CADD_REST_API_URL,
            status_code=200,
            text=json.dumps(
                {
                    "scores": {
                        "1-100-A-G": [0.345146, 7.772],
                        "1-200-A-G": [0.345179, 7.773],
                        "1-300-A-G": [0.345212, 7.774],
                    }
                }
            ),
        )
        job = FilterBgJob.objects.first()
        CaseFilter(job, job.smallvariantquery).run()

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


class ProjectCasesFilterTest(FilterTestBase):
    """Test running joint cases filter job."""

    fixture = fixture_setup_projectcases

    def setUp(self):
        super().setUp(
            ProjectCasesFilterBgJob,
            ProjectCasesSmallVariantQuery,
            ProjectCasesFilterForm,
            DEFAULT_JOINT_RESUBMIT_SETTING,
        )

    def test_submit_projectcases_filter(self):
        job = ProjectCasesFilterBgJob.objects.first()
        ProjectCasesFilter(job, job.projectcasessmallvariantquery).run()

        self.assertEqual(ProjectCasesSmallVariantQuery.objects.count(), 1)
        self.assertEqual(ProjectCasesSmallVariantQuery.objects.first().query_results.count(), 6)


class ClinvarFilterTest(FilterTestBase):
    """Test running clinvar filter job."""

    fixture = fixture_setup_case

    def setUp(self):
        super().setUp(ClinvarBgJob, ClinvarQuery, ClinvarForm, CLINVAR_RESUBMIT_SETTING)

    def test_submit_clinvar_filter(self):
        job = ClinvarBgJob.objects.first()
        ClinvarFilter(job, job.clinvarquery).run()

        self.assertEqual(ClinvarQuery.objects.count(), 1)
        self.assertEqual(ClinvarQuery.objects.first().query_results.count(), 1)
        self.assertEqual(ClinvarQuery.objects.first().query_results.first().start, 200)
