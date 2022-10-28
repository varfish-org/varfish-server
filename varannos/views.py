"""The views for the ``varannos`` app."""

from django.views.generic import DetailView, ListView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from varannos.models import VarAnnoSet


class VarAnnoSetListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display entry point into site-wide app."""

    permission_required = "varannos.view_data"
    model = VarAnnoSet
    template_name = "varannos/varannoset_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__sodar_uuid=self.kwargs["project"])
            .prefetch_related("varannosetentry_set")
        )


class VarAnnoSetDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    permission_required = "varannos.view_data"
    model = VarAnnoSet
    template_name = "varannos/varannoset_detail.html"

    slug_url_kwarg = "varannoset"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # The number of columns in annotations table, depends on number of fields in set.
        result["table_col_count"] = 5 + len(self.get_object().fields)
        return result
