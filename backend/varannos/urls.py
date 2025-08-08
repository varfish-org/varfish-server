from django.urls import path

from varannos import views, views_api

app_name = "varannos"
ui_urlpatterns = [
    path(
        "varannoset/list/<uuid:project>/",
        view=views.VarAnnoSetListView.as_view(),
        name="varannoset-list",
    ),
    path(
        "varannoset/details/<uuid:varannoset>/",
        view=views.VarAnnoSetDetailView.as_view(),
        name="varannoset-detail",
    ),
]

ajax_urlpatterns = []

api_urlpatterns = [
    path(
        "api/varannoset/list-create/<uuid:project>/",
        view=views_api.VarAnnoSetListCreateApiView.as_view(),
        name="api-varannoset-listcreate",
    ),
    path(
        "api/varannoset/retrieve-update-destroy/<uuid:varannoset>/",
        view=views_api.VarAnnoSetRetrieveUpdateDestroyApiView.as_view(),
        name="api-varannoset-retrieveupdatedestroy",
    ),
    path(
        "api/varannosetentry/list-create/<uuid:varannoset>/",
        view=views_api.VarAnnoSetEntryListCreateApiView.as_view(),
        name="api-varannosetentry-listcreate",
    ),
    path(
        "api/varannosetentry/retrieve-update-destroy/<uuid:varannosetentry>/",
        view=views_api.VarAnnoSetEntryRetrieveUpdateDestroyApiView.as_view(),
        name="api-varannosetentry-retrieveupdatedestroy",
    ),
]


urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
