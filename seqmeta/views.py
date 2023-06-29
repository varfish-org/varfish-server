"""The views for the ``seqmeta`` app."""

from django.views.generic import DetailView, ListView
from projectroles.views import (
    LoggedInPermissionMixin,
    LoginRequiredMixin,
    ProjectContextMixin,
    ProjectPermissionMixin,
)

from seqmeta.models import EnrichmentKit


class EnrichmentKitListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    ListView,
):
    """Display entry point into site-wide app."""

    permission_required = "seqmeta.view_data"
    model = EnrichmentKit
    template_name = "seqmeta/enrichmentkit_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(project__sodar_uuid=self.kwargs["project"])
            .prefetch_related("seqmetaetentry_set")
        )


class EnrichmentKitDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ProjectPermissionMixin,
    ProjectContextMixin,
    DetailView,
):
    permission_required = "seqmeta.view_data"
    model = EnrichmentKit
    template_name = "seqmeta/enrichmentkit_detail.html"

    slug_url_kwarg = "enrichmentkit"
    slug_field = "sodar_uuid"

    def get_context_data(self, *args, **kwargs):
        result = super().get_context_data(*args, **kwargs)
        # The number of columns in annotations table, depends on number of fields in set.
        result["table_col_count"] = 5 + len(self.get_object().fields)
        return result
