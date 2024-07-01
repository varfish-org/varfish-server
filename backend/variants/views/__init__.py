import json
import uuid

from bgjobs.models import BackgroundJob
from bgjobs.views import DEFAULT_PAGINATION as BGJOBS_DEFAULT_PAGINATION
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.utils import timezone
from django.views.generic import DetailView, FormView, ListView, RedirectView
from django.views.generic.detail import SingleObjectMixin, SingleObjectTemplateResponseMixin
from projectroles.app_settings import AppSettingAPI
from projectroles.templatetags.projectroles_common_tags import site_version
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from variants.forms import EmptyForm, ExportFileResubmitForm, ExportProjectCasesFileResubmitForm
from variants.models import (
    CaddSubmissionBgJob,
    Case,
    ClearExpiredExportedFilesBgJob,
    ClearInactiveVariantSetsBgJob,
    ClearOldKioskCasesBgJob,
    ComputeProjectVariantsStatsBgJob,
    DeleteCaseBgJob,
    DistillerSubmissionBgJob,
    ExportFileBgJob,
    ExportProjectCasesFileBgJob,
    FilterBgJob,
    ImportVariantsBgJob,
    ProjectCasesFilterBgJob,
    RefreshSmallVariantSummaryBgJob,
    SpanrSubmissionBgJob,
    SyncCaseListBgJob,
)
from variants.tasks import (
    cadd_submission_task,
    distiller_submission_task,
    export_file_task,
    export_project_cases_file_task,
    project_cases_filter_task,
    single_case_filter_task,
    spanr_submission_task,
)


class UUIDEncoder(json.JSONEncoder):
    """JSON encoder for UUIds"""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # If the obj is uuid, we simply return the value of uuid
            return obj.hex
        # Default implementation raises not-serializable TypeError exception
        return json.JSONEncoder.default(self, obj)  # pragma: no cover


# TODO keep
class BackgroundJobListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    SingleObjectMixin,
    SingleObjectTemplateResponseMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display list of export jobs for case."""

    permission_required = "variants.view_data"
    template_name = "variants/background_job_list.html"
    model = Case
    slug_url_kwarg = "case"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        self.object = self.get_object()
        return super().get(*args, **kwargs)


# TODO keep
class SyncJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the sync-project-upstream background job."""

    permission_required = "variants.view_data"
    template_name = "variants/sync_job_detail.html"
    model = SyncCaseListBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


# TODO keep
class ImportVariantsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the import case background job."""

    permission_required = "variants.view_data"
    template_name = "variants/import_job_detail.html"
    model = ImportVariantsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


# TODO keep
class CaseDeleteJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the import case background job."""

    permission_required = "variants.view_data"
    template_name = "variants/case_delete_job_detail.html"
    model = DeleteCaseBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        try:
            self.object = self.get_object()
            return super().get(*args, **kwargs)
        # Object is not available when case was deleted successfully
        except Exception:
            messages.info(self.request, "Case deleted successfully.")
            return redirect(
                reverse("variants:case-list", kwargs={"project": self.get_project().sodar_uuid})
            )


# TODO keep
class ExportFileJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the file export background job."""

    permission_required = "variants.view_data"
    template_name = "variants/export_job_detail.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = ExportFileResubmitForm(
            initial={"file_type": result["object"].query_args["file_type"]}
        )
        return result


# TODO keep
class ExportFileJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit export file job."""

    permission_required = "variants.view_data"
    form_class = ExportFileResubmitForm

    def form_valid(self, form):
        job = get_object_or_404(ExportFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for case {} (Resubmission)".format(
                    form.cleaned_data["file_type"], job.case
                ),
                project=job.bg_job.project,
                job_type=ExportFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportFileBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                case=job.case,
                query_args={**job.query_args, "file_type": form.cleaned_data["file_type"]},
                file_type=form.cleaned_data["file_type"],
            )
        export_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())


# TODO keep
class ExportProjectCasesFileJobDownloadView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Download the file generated, if generated.

    Otherwise, thrown 404.
    """

    http_method_names = ["get"]

    permission_required = "variants.view_data"
    template_name = "variants/export_project_cases_job_detail.html"
    model = ExportProjectCasesFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        try:
            content_types = {
                "tsv": "text/tab-separated-values",
                "vcf": "text/plain+gzip",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            extensions = {"tsv": ".tsv", "vcf": ".vcf.gz", "xlsx": ".xlsx"}
            obj = self.get_object()
            response = HttpResponse(
                obj.export_result.payload, content_type=content_types[obj.file_type]
            )
            response["Content-Disposition"] = 'attachment; filename="%(name)s%(ext)s"' % {
                "name": "varfish_%s_%s"
                % (timezone.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), obj.project.sodar_uuid),
                "ext": extensions[obj.file_type],
            }
            return response
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e


# TODO keep
class ExportProjectCasesFileJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the file export background job."""

    permission_required = "variants.view_data"
    template_name = "variants/export_project_cases_job_detail.html"
    model = ExportProjectCasesFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = ExportProjectCasesFileResubmitForm(
            initial={"file_type": result["object"].query_args["file_type"]}
        )
        return result


# TODO keep
class ExportProjectCasesFileJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit export file job."""

    permission_required = "variants.view_data"
    form_class = ExportProjectCasesFileResubmitForm

    def form_valid(self, form):
        job = get_object_or_404(ExportProjectCasesFileBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Create {} file for all cases in project (Resubmission)".format(
                    form.cleaned_data["file_type"]
                ),
                project=job.bg_job.project,
                job_type=ExportProjectCasesFileBgJob.spec_name,
                user=self.request.user,
            )
            export_job = ExportProjectCasesFileBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                cohort=job.cohort,
                query_args={**job.query_args, "file_type": form.cleaned_data["file_type"]},
                file_type=form.cleaned_data["file_type"],
            )
        export_project_cases_file_task.delay(export_job_pk=export_job.pk)
        return redirect(export_job.get_absolute_url())


# TODO keep
class ExportFileJobDownloadView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Download the file generated, if generated.

    Otherwise, thrown 404.
    """

    http_method_names = ["get"]

    permission_required = "variants.view_data"
    template_name = "variants/export_job_detail.html"
    model = ExportFileBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get(self, *args, **kwargs):
        try:
            content_types = {
                "tsv": "text/tab-separated-values",
                "vcf": "text/plain+gzip",
                "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            }
            extensions = {"tsv": ".tsv", "vcf": ".vcf.gz", "xlsx": ".xlsx"}
            obj = self.get_object()
            response = HttpResponse(
                obj.export_result.payload, content_type=content_types[obj.file_type]
            )
            response["Content-Disposition"] = 'attachment; filename="%(name)s%(ext)s"' % {
                "name": "varfish_%s_%s"
                % (timezone.now().strftime("%Y-%m-%d_%H:%M:%S.%f"), obj.case.sodar_uuid),
                "ext": extensions[obj.file_type],
            }
            return response
        except ObjectDoesNotExist as e:
            raise Http404("File has not been generated (yet)!") from e


# TODO keep
class DistillerSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the MutationDistiller submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/distiller_job_detail.html"
    model = DistillerSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


# TODO keep
class DistillerSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to MutationDistiller."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(DistillerSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to MutationDistiller".format(job.case),
                project=job.bg_job.project,
                job_type=DistillerSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = DistillerSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            distiller_submission_task.delay(submission_job_pk=submission_job.pk)
        return redirect(submission_job.get_absolute_url())


# TODO keep
class CaddSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the CADD submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/cadd_job_detail.html"
    model = CaddSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


# TODO keep
class CaddSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to CADD."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(CaddSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to CADD".format(job.case),
                project=job.bg_job.project,
                job_type=CaddSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = CaddSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            cadd_submission_task.delay(submission_job_pk=submission_job.pk)
        return redirect(submission_job.get_absolute_url())


# TODO keep
class SpanrSubmissionJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the SPANR submission background job."""

    permission_required = "variants.view_data"
    template_name = "variants/spanr_job_detail.html"
    model = SpanrSubmissionBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        result["resubmit_form"] = EmptyForm()
        return result


# TODO keep
class SpanrSubmissionJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit to SPANR."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(SpanrSubmissionBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting case {} to SPANR".format(job.case),
                project=job.bg_job.project,
                job_type=SpanrSubmissionBgJob.spec_name,
                user=self.request.user,
            )
            submission_job = SpanrSubmissionBgJob.objects.create(
                project=job.project, bg_job=bg_job, case=job.case, query_args=job.query_args
            )
            spanr_submission_task.delay(submission_job_pk=submission_job.pk)
        return redirect(submission_job.get_absolute_url())


# TODO keep
class FilterJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the FilterBgJob background job."""

    permission_required = "variants.view_data"
    template_name = "variants/filter_job_detail.html"
    model = FilterBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    query_type = "case"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["query_type"] = self.query_type
        return context


# TODO keep
class ProjectCasesFilterJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the FilterBgJob background job."""

    permission_required = "variants.view_data"
    template_name = "variants/filter_job_detail.html"
    model = ProjectCasesFilterBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    query_type = "project"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["query_type"] = self.query_type
        return context


# TODO keep
class FilterJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit the filter query job and redirect to filter view."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(FilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter case {}".format(job.case),
                project=job.bg_job.project,
                job_type=FilterBgJob.spec_name,
                user=self.request.user,
            )
            filter_job = FilterBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                case=job.case,
                smallvariantquery=job.smallvariantquery,
            )
            single_case_filter_task.delay(filter_job_pk=filter_job.pk)
        return redirect(
            reverse(
                "variants:filter-job-detail",
                kwargs={"project": job.project.sodar_uuid, "job": filter_job.sodar_uuid},
            )
        )


# TODO keep
class ProjectCasesFilterJobResubmitView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    FormView,
):
    """Resubmit the filter query job and redirect to filter view."""

    permission_required = "variants.view_data"
    form_class = EmptyForm

    def form_valid(self, form):
        job = get_object_or_404(ProjectCasesFilterBgJob, sodar_uuid=self.kwargs["job"])
        with transaction.atomic():
            bg_job = BackgroundJob.objects.create(
                name="Resubmitting filter project",
                project=job.bg_job.project,
                job_type=ProjectCasesFilterBgJob.spec_name,
                user=self.request.user,
            )
            filter_job = ProjectCasesFilterBgJob.objects.create(
                project=job.project,
                bg_job=bg_job,
                projectcasessmallvariantquery=job.projectcasessmallvariantquery,
            )
            project_cases_filter_task.delay(project_cases_filter_job_pk=filter_job.pk)
        return redirect(
            reverse(
                "variants:project-cases-filter-job-detail",
                kwargs={"project": job.project.sodar_uuid, "job": filter_job.sodar_uuid},
            )
        )


# TODO keep
class ProjectStatsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of project-wide statistics computation job."""

    permission_required = "variants.view_data"
    template_name = "variants/project_stats_job_detail.html"
    model = ComputeProjectVariantsStatsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"


# TODO keep
class NewFeaturesView(LoginRequiredMixin, RedirectView):
    """Store "latest seen changelog version" for user and redirect."""

    url = "/manual/history.html"

    def get(self, *args, **kwargs):
        setting_api = AppSettingAPI()
        setting_api.set(
            "variants",
            "latest_version_seen_changelog__user",
            site_version(),
            user=self.request.user,
        )
        return super().get(*args, **kwargs)


# TODO keep
class ClearExpiredExportedFilesJobDetailView(
    LoggedInPermissionMixin,
    DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearExpiredExportedFilesBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


# TODO keep
class ClearInactiveVariantSetsJobDetailView(
    LoggedInPermissionMixin,
    DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearInactiveVariantSetsBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


# TODO keep
class ClearOldKioskCasesJobDetailView(
    LoggedInPermissionMixin,
    DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = ClearOldKioskCasesBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)


# TODO keep
class RefreshSmallVariantSummaryJobDetailView(
    LoggedInPermissionMixin,
    DetailView,
):
    permission_required = "bgjobs.view_site_bgjobs"
    template_name = "variants/maintenance_job_detail.html"
    model = RefreshSmallVariantSummaryBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
    paginate_by = getattr(settings, "BGJOBS_PAGINATION", BGJOBS_DEFAULT_PAGINATION)
