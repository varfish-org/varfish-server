from django.conf.urls import url

from geneinfo import views_api

app_name = "geneinfo"
api_urlpatterns = [
    url(
        regex=r"^api/lookup-genepanel/$",
        view=views_api.LookupGenePanelApiView.as_view(),
        name="lookup-genepanel",
    ),
    url(
        regex=r"^api/genepanel-category/list/$",
        view=views_api.GenePanelCategoryListApiView.as_view(),
        name="gene-panel-category-list",
    ),
]

urlpatterns = api_urlpatterns
