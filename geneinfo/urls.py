from django.conf.urls import url

from geneinfo import views_api

app_name = "geneinfo"
api_urlpatterns = [
    url(
        regex=r"^api/lookup-gene/$", view=views_api.LookupGeneApiView.as_view(), name="lookup-gene"
    ),
]

urlpatterns = api_urlpatterns
