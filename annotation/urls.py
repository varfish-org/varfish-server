from django.conf.urls import url
from . import views

app_name = "annotation"
urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/(?P<database>(refseq|ensembl))-(?P<release>(GRCh37|GRCh38))-(?P<chromosome>(chr)?([0-9]{1,2}|[XY]|MT]))-(?P<position>[0-9]+)-(?P<reference>[ACGT]+)-(?P<alternative>[ACGT]+)/$",
        view=views.VariantView.as_view(),
        name="variant",
    )
]
