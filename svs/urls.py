from django.conf.urls import url
from . import views


app_name = "svs"

urlpatterns = [
    # Filter form and result display for SV queries.
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/case/filter/(?P<case>[0-9a-f-]+)/$",
        view=views.CaseFilterView.as_view(),
        name="case-filter",
    ),
    # Gene-wise details for each variant.
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/sv-details/(?P<case>[0-9a-f-]+)/(?P<sv>[0-9a-f-]+)/$",
        view=views.StructuralVariantDetailsView.as_view(),
        name="sv-details",
    ),
    # API for accessing structural variant flags and comments.
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/case/(?P<case>[0-9a-f-]+)/sv-flags/(?P<sv>[0-9a-f-]+)/$",
        view=views.StructuralVariantFlagsApiView.as_view(),
        name="sv-flags-api",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/case/(?P<case>[0-9a-f-]+)/sv-comment/(?P<sv>[0-9a-f-]+)/$",
        view=views.StructuralVariantCommentApiView.as_view(),
        name="sv-comment-api",
    ),
    # Views for variants import job.
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/import/(?P<job>[0-9a-f-]+)/$",
        view=views.ImportStructuralVariantsJobDetailView.as_view(),
        name="import-job-detail",
    ),
]
