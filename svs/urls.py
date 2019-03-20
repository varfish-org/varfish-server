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
        regex=r"^(?P<project>[0-9a-f-]+)/gene-details/(?P<case>[0-9a-f-]+)/$",
        view=views.GeneDetailsView.as_view(),
        name="gene-details",
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
]
