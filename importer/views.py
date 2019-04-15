from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from projectroles.views import LoggedInPermissionMixin

from .models import ImportInfo


class ImportInfoView(LoginRequiredMixin, LoggedInPermissionMixin, ListView):
    """Display all ``ImportInfo`` records."""

    template_name = "importer/importinfo.html"
    permission_required = "importer.view_data"
    model = ImportInfo
