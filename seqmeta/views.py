"""The views for the ``seqmeta`` app."""

from django.views.generic import DetailView, ListView, TemplateView
from projectroles.views import LoggedInPermissionMixin, LoginRequiredMixin

from seqmeta.models import EnrichmentKit


class IndexView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    TemplateView,
):
    """Entrypoint for the site-wide app."""

    permission_required = "seqmeta.view_data"
    model = EnrichmentKit
    template_name = "seqmeta/index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result["object_list"] = EnrichmentKit.objects.all()[:5]
        return result


class EnrichmentKitListView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    ListView,
):
    """Display entry point into site-wide app."""

    permission_required = "seqmeta.view_data"
    model = EnrichmentKit
    template_name = "seqmeta/enrichmentkit_list.html"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("targetbedfile_set")


class EnrichmentKitDetailView(
    LoginRequiredMixin,
    LoggedInPermissionMixin,
    DetailView,
):
    permission_required = "seqmeta.view_data"
    model = EnrichmentKit
    template_name = "seqmeta/enrichmentkit_detail.html"

    slug_url_kwarg = "enrichmentkit"
    slug_field = "sodar_uuid"
