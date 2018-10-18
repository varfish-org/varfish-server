from django.conf.urls import url
from . import views

app_name = "main"
urlpatterns = [
    url(regex=r"^(?P<project>[0-9a-f-]+)$", view=views.MainView.as_view(), name="main"),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/case/(?P<case_name>[A-Za-z0-9-_]+)/$",
        view=views.FilterView.as_view(),
        name="filter",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/gene/(?P<gene_id>(ENSG)?[0-9]+)/$",
        view=views.GeneView.as_view(),
        name="gene",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/variant/(?P<database>(refseq|ensembl))-(?P<release>(GRCh37|GRCh38))-(?P<chromosome>(chr)?([0-9]{1,2}|[XY]|MT]))-(?P<position>[0-9]+)-(?P<reference>[ACGT]+)-(?P<alternative>[ACGT]+)/$",
        view=views.VariantView.as_view(),
        name="variant",
    ),
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/api/extend/(?P<release>(GRCh37|GRCh38))-(?P<chromosome>(chr)?([0-9]{1,2}|[XY]|MT]))-(?P<position>[0-9]+)-(?P<reference>[ACGT]+)-(?P<alternative>[ACGT]+)/$",
        view=views.ExtendAPIView.as_view(),
        name="extend",
    ),
]
