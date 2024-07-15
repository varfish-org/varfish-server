from django.views.generic import DetailView, ListView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from .models import ImportCaseBgJob, ImportInfo


class ImportInfoView(LoginRequiredMixin, LoggedInPermissionMixin, ListView):
    """Display all ``ImportInfo`` records."""

    template_name = "importer/importinfo.html"
    permission_required = "importer.view_data"
    model = ImportInfo


class ImportCaseBgJobDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    """Display details of an import job."""

    template_name = "importer/import_case_detail.html"
    permission_required = "variants.view_data"
    model = ImportCaseBgJob
    slug_url_kwarg = "job"
    slug_field = "sodar_uuid"
