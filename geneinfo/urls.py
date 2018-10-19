from django.conf.urls import url
from . import views

app_name = "geneinfo"
urlpatterns = [
    url(
        regex=r"^(?P<project>[0-9a-f-]+)/gene/(?P<gene_id>(ENSG)?[0-9]+)/$",
        view=views.GeneView.as_view(),
        name="gene",
    ),
]
