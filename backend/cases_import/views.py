from django.views.generic import DetailView, TemplateView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from cases_import.models.base import CaseImportBackgroundJob


class IndexView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    TemplateView,
):
    permission_required = "cases_import.view_data"
    template_name = "cases_import/index.html"


class ImportCaseBackgroundsJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display status and further details of the sync-project-upstream background job."""

    permission_required = "cases_import.view_data"
    template_name = "cases_import/importcasebackgroudjobdetail.html"
    model = CaseImportBackgroundJob
    slug_url_kwarg = "caseimportbackgroundjob"
    slug_field = "sodar_uuid"
