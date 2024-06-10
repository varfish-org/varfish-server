"""Tests for the filter view"""

from django.urls import reverse
from projectroles.app_settings import AppSettingAPI
from projectroles.templatetags.projectroles_common_tags import site_version
from requests_mock import Mocker

from clinvar.tests.factories import ClinvarFactory
from cohorts.tests.factories import TestCohortBase
from geneinfo.tests.factories import HpoFactory, HpoNameFactory
from variants.models import (
    Case,
    ComputeProjectVariantsStatsBgJob,
    DistillerSubmissionBgJob,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    FilterBgJob,
    ProjectCasesFilterBgJob,
)
from variants.tests.factories import (
    CaseFactory,
    CaseWithVariantSetFactory,
    DeleteCaseBgJobFactory,
    DistillerSubmissionBgJobFactory,
    ExportFileBgJobFactory,
    ExportFileJobResultFactory,
    ExportProjectCasesFileBgJobFactory,
    ExportProjectCasesFileBgJobResultFactory,
    FilterBgJobFactory,
    FormDataFactory,
    ProjectCasesFilterBgJobFactory,
    ProjectFactory,
    SmallVariantFactory,
    SmallVariantQueryFactory,
)
from variants.tests.helpers import ViewTestBase


class TestCaseDeleteJobDetailView(ViewTestBase):
    """Test ProjectStatsJobDetailView."""

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.case_1 = CaseFactory(project=self.project)
        self.case_2 = CaseFactory(project=self.project)
        self.bgjob = DeleteCaseBgJobFactory(
            project=self.project, case=self.case_2, user=self.superuser
        )

    def test_render(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:case-delete-job-detail",
                    kwargs={"project": self.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)


class GenerateSmallVariantResultMixin:
    def setUp(self):
        super().setUp()
        self.case, self.variant_set, _ = CaseWithVariantSetFactory.get("small")
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
        ClinvarFactory(
            release=self.small_vars[-1].release,
            chromosome=self.small_vars[-1].chromosome,
            start=self.small_vars[-1].start,
            end=self.small_vars[-1].end,
            bin=self.small_vars[-1].bin,
            reference=self.small_vars[-1].reference,
            alternative=self.small_vars[-1].alternative,
            summary_clinvar_review_status_label="criteria provided, single committer",
            summary_clinvar_pathogenicity_label="pathogenic",
            summary_clinvar_pathogenicity=["pathogenic"],
        )
        self.bgjob = FilterBgJobFactory(case=self.case, user=self.superuser, bg_job__status="done")
        self.hpo_term = HpoNameFactory(hpo_id="HP:0000001")
        self.omim_term = [
            HpoFactory(
                database_id="OMIM:000001",
                hpo_id="HP:0000002",
                name="Disease 1;;Alternative Description",
            ),
            HpoFactory(
                database_id="OMIM:000001",
                hpo_id="HP:0000003",
                name="Disease 1;;Alternative Description",
            ),
        ]
        self.decipher_term = HpoFactory(
            database_id="DECIPHER:1",
            hpo_id="HP:0000004",
            name="Disease 2",
        )
        self.orpha_term = HpoFactory(
            database_id="ORPHA:1",
            hpo_id="HP:0000005",
            name="Disease 3",
        )
        self.bgjob.smallvariantquery.query_results.add(self.small_vars[0], self.small_vars[2])
        self.bgjob.smallvariantquery.query_settings["prio_hpo_terms"] = [
            self.hpo_term.hpo_id,
            self.omim_term[0].database_id,
            self.decipher_term.database_id,
            self.orpha_term.database_id,
        ]
        self.bgjob.smallvariantquery.save()


class TestFilterJobDetailView(ViewTestBase):
    """Tests for FilterJobDetailView."""

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.superuser)

    def test_status_code_200(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, self.bgjob.case.name)


class TestFilterJobResubmitView(ViewTestBase):
    """Tests for FilterJobResubmitView."""

    def setUp(self):
        super().setUp()
        case, _, _ = CaseWithVariantSetFactory.get("small")
        self.bgjob = FilterBgJobFactory(user=self.superuser, case=case)

    def test_redirect(self):
        with self.login(self.superuser):
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


# class TestCohortFilterView(TestCohortBase):
#     # def test_render_form_filter_cohort_as_superuser(self):
#     #     user = self.superuser
#     #     project = self.project1
#     #     cohort = self._create_cohort_all_possible_cases(user, project)
#     #     with self.login(user):
#     #         response = self.client.get(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #         )
#     #         self.assertEqual(response.status_code, 200)
#     #         for member in self.project1.get_members() + self.project2.get_members():
#     #             self.assertIsNotNone(response.context["form"].fields.get("%s_gt" % member))
#
#     # def test_render_form_filter_cohort_as_contributor(self):
#     #     user = self.contributor
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(user, project)
#     #     with self.login(user):
#     #         response = self.client.get(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #         )
#     #         self.assertEqual(response.status_code, 200)
#     #         for member in self.project2.get_members():
#     #             self.assertIsNotNone(response.context["form"].fields.get("%s_gt" % member))
#     #         for member in self.project1.get_members():
#     #             self.assertIsNone(response.context["form"].fields.get("%s_gt" % member))
#
#     # def test_render_form_filter_cohort_as_superuser_for_cohort_by_contributor(self):
#     #     user = self.superuser
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(self.contributor, project)
#     #     with self.login(user):
#     #         response = self.client.get(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #         )
#     #         for member in self.project2.get_members():
#     #             self.assertIsNotNone(response.context["form"].fields.get("%s_gt" % member))
#     #         for member in self.project1.get_members():
#     #             self.assertIsNone(response.context["form"].fields.get("%s_gt" % member))
#
#     # def test_render_form_filter_cohort_as_contributor_for_cohort_by_superuser(self):
#     #     user = self.contributor
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(self.superuser, project)
#     #     with self.login(user):
#     #         response = self.client.get(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #         )
#     #         for member in self.project2.get_members():
#     #             self.assertIsNotNone(response.context["form"].fields.get("%s_gt" % member))
#     #         for member in self.project1.get_members():
#     #             self.assertIsNone(response.context["form"].fields.get("%s_gt" % member))
#
#     # def test_download_filter_cohort_as_superuser(self):
#     #     """Test form submit for download as file."""
#     #     user = self.superuser
#     #     project = self.project1
#     #     cohort = self._create_cohort_all_possible_cases(user, project)
#     #     with self.login(user):
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
#     #         response = self.client.post(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #             vars(
#     #                 FormDataFactory(
#     #                     submit="download", names=cohort.get_members(user), cohort=cohort.sodar_uuid
#     #                 )
#     #             ),
#     #         )
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
#     #         created_job = ExportProjectCasesFileBgJob.objects.first()
#     #         self.assertRedirects(
#     #             response,
#     #             reverse(
#     #                 "variants:project-cases-export-job-detail",
#     #                 kwargs={
#     #                     "project": project.sodar_uuid,
#     #                     "job": created_job.sodar_uuid,
#     #                 },
#     #             ),
#     #         )
#
#     # def test_download_filter_cohort_as_contributor(self):
#     #     """Test form submit for download as file."""
#     #     user = self.contributor
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(user, project)
#     #     with self.login(user):
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
#     #         response = self.client.post(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #             vars(
#     #                 FormDataFactory(
#     #                     submit="download", names=cohort.get_members(user), cohort=cohort.sodar_uuid
#     #                 )
#     #             ),
#     #         )
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
#     #         created_job = ExportProjectCasesFileBgJob.objects.first()
#     #         self.assertRedirects(
#     #             response,
#     #             reverse(
#     #                 "variants:project-cases-export-job-detail",
#     #                 kwargs={
#     #                     "project": project.sodar_uuid,
#     #                     "job": created_job.sodar_uuid,
#     #                 },
#     #             ),
#     #         )
#
#     # def test_download_filter_cohort_as_superuser_for_cohort_by_contributor(self):
#     #     """Test form submit for download as file."""
#     #     user = self.superuser
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(self.contributor, project)
#     #     with self.login(user):
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
#     #         response = self.client.post(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #             vars(
#     #                 FormDataFactory(
#     #                     submit="download", names=cohort.get_members(user), cohort=cohort.sodar_uuid
#     #                 )
#     #             ),
#     #         )
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
#     #         created_job = ExportProjectCasesFileBgJob.objects.first()
#     #         self.assertRedirects(
#     #             response,
#     #             reverse(
#     #                 "variants:project-cases-export-job-detail",
#     #                 kwargs={
#     #                     "project": project.sodar_uuid,
#     #                     "job": created_job.sodar_uuid,
#     #                 },
#     #             ),
#     #         )
#
#     # def test_download_filter_cohort_as_contributor_for_cohort_by_superuser(self):
#     #     """Test form submit for download as file."""
#     #     user = self.contributor
#     #     project = self.project2
#     #     cohort = self._create_cohort_all_possible_cases(self.superuser, project)
#     #     with self.login(user):
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 0)
#     #         response = self.client.post(
#     #             reverse(
#     #                 "variants:project-cases-filter-cohort",
#     #                 kwargs={"project": project.sodar_uuid, "cohort": cohort.sodar_uuid},
#     #             ),
#     #             vars(
#     #                 FormDataFactory(
#     #                     submit="download", names=cohort.get_members(user), cohort=cohort.sodar_uuid
#     #                 )
#     #             ),
#     #         )
#     #         self.assertEquals(ExportProjectCasesFileBgJob.objects.count(), 1)
#     #         created_job = ExportProjectCasesFileBgJob.objects.first()
#     #         self.assertRedirects(
#     #             response,
#     #             reverse(
#     #                 "variants:project-cases-export-job-detail",
#     #                 kwargs={
#     #                     "project": project.sodar_uuid,
#     #                     "job": created_job.sodar_uuid,
#     #                 },
#     #             ),
#     #         )


class TestProjectCasesFilterJobDetailView(ViewTestBase):
    """Tests for ProjectCasesFilterJobDetailView."""

    def setUp(self):
        super().setUp()
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.superuser)

    def test_status_code_200(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_project_name(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:project-cases-filter-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].project.title, self.bgjob.project.title)


class TestProjectCasesFilterJobResubmitView(ViewTestBase):
    """Tests for ProjectCasesFilterJobResubmitView."""

    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        CaseWithVariantSetFactory.get("small", project=project)
        CaseWithVariantSetFactory.get("small", project=project)
        self.bgjob = ProjectCasesFilterBgJobFactory(user=self.superuser, project=project)

    def test_redirect(self):
        with self.login(self.superuser):
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


class TestDistillerSubmissionJobDetailView(ViewTestBase):
    """Tests for DistillerSubmissionJobDetailView."""

    def setUp(self):
        super().setUp()
        self.bgjob = DistillerSubmissionBgJobFactory(user=self.superuser)

    def test_status_code_200(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.status_code, 200)

    def test_correct_case_name(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:distiller-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEqual(response.context["object"].case.name, self.bgjob.case.name)


class TestExportFileJobDetailView(ViewTestBase):
    """Test export file job detail view"""

    def setUp(self):
        super().setUp()
        self.bgjob = ExportFileBgJobFactory(user=self.superuser)

    def test_render(self):
        with self.login(self.superuser):
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
        case, _, _ = CaseWithVariantSetFactory.get("small")
        self.bgjob = ExportFileBgJobFactory(user=self.superuser, case=case)

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.superuser):
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
        with self.login(self.superuser):
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
        self.bgjob = ExportFileBgJobFactory(user=self.superuser)

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.superuser):
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
        self.results = ExportFileJobResultFactory(user=self.superuser)

    def test_download(self):
        """Test file download"""
        with self.login(self.superuser):
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
    """Test ExportProjectCasesFileJobResubmitView."""

    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        CaseWithVariantSetFactory.get("small", project=project)
        CaseWithVariantSetFactory.get("small", project=project)
        self.bgjob = ExportProjectCasesFileBgJobFactory(user=self.superuser, project=project)

    def test_resubmission(self):
        """Test if file resubmission works."""
        with self.login(self.superuser):
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
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:project-cases-export-job-detail",
                    kwargs={"project": self.bgjob.project.sodar_uuid, "job": self.bgjob.sodar_uuid},
                )
            )
            self.assertEquals(response.status_code, 200)


class TestExportProjectCasesFileJobDownloadView(ViewTestBase):
    """Test ExportProjectCasesFileJobDownloadView."""

    def setUp(self):
        super().setUp()
        project = ProjectFactory()
        CaseFactory(project=project)
        CaseFactory(project=project)
        self.bgjob = ExportProjectCasesFileBgJobFactory(user=self.superuser, project=project)

    def test_no_file(self):
        """Test if database entries exist, but no file is generated"""
        with self.login(self.superuser):
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
        self.results = ExportProjectCasesFileBgJobResultFactory(user=self.superuser)

    def test_download(self):
        """Test file download"""
        with self.login(self.superuser):
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


# Todo create project stats job tests
# class TestProjectStatsJobDetailView(ViewTestBase):
#     """Test ProjectStatsJobDetailView."""
#
#     def setUp(self):
#         super().setUp()
#         self.project = ProjectFactory()
#         CaseFactory(project=self.project)
#         CaseFactory(project=self.project)
#
#     def test_render(self):
#         with self.login(self.superuser):
#             self.client.post(
#                 reverse(
#                     "variants:project-stats-job-create", kwargs={"project": self.project.sodar_uuid}
#                 )
#             )
#             created_job = ComputeProjectVariantsStatsBgJob.objects.last()
#             response = self.client.get(
#                 reverse(
#                     "variants:project-stats-job-detail",
#                     kwargs={"project": self.project.sodar_uuid, "job": created_job.sodar_uuid},
#                 )
#             )
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(
#                 response.context["object"].bg_job.name,
#                 "Recreate variant statistic for whole project",
#             )


class TestBackgroundJobListView(ViewTestBase):
    """Test BackgroundJobListView."""

    def setUp(self):
        super().setUp()
        self.bgjob = FilterBgJobFactory(user=self.superuser)

    def test_render(self):
        with self.login(self.superuser):
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
        with self.login(self.superuser):
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


class TestNewFeaturesView(ViewTestBase):
    """Test NewFeaturesView."""

    def test_response(self):
        with self.login(self.superuser):
            response = self.client.get(reverse("variants:new-features"))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, "/manual/history.html")
            settings_api = AppSettingAPI()
            value = settings_api.get(
                "variants", "latest_version_seen_changelog", user=self.superuser
            )
            self.assertEqual(value, site_version())
