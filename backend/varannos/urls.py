from django.conf.urls import url

from varannos import views, views_api

app_name = "varannos"
ui_urlpatterns = [
    url(
        regex=r"^varannoset/list/(?P<project>[0-9a-f-]+)/?$",
        view=views.VarAnnoSetListView.as_view(),
        name="varannoset-list",
    ),
    url(
        regex=r"^varannoset/details/(?P<varannoset>[0-9a-f-]+)/?$",
        view=views.VarAnnoSetDetailView.as_view(),
        name="varannoset-detail",
    ),
]

ajax_urlpatterns = []

api_urlpatterns = [
    url(
        regex=r"^api/varannoset/list-create/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.VarAnnoSetListCreateApiView.as_view(),
        name="api-varannoset-listcreate",
    ),
    url(
        regex=r"^api/varannoset/retrieve-update-destroy/(?P<varannoset>[0-9a-f-]+)/?$",
        view=views_api.VarAnnoSetRetrieveUpdateDestroyApiView.as_view(),
        name="api-varannoset-retrieveupdatedestroy",
    ),
    url(
        regex=r"^api/varannosetentry/list-create/(?P<varannoset>[0-9a-f-]+)/?$",
        view=views_api.VarAnnoSetEntryListCreateApiView.as_view(),
        name="api-varannosetentry-listcreate",
    ),
    url(
        regex=r"^api/varannosetentry/retrieve-update-destroy/(?P<varannosetentry>[0-9a-f-]+)/?$",
        view=views_api.VarAnnoSetEntryRetrieveUpdateDestroyApiView.as_view(),
        name="api-varannosetentry-retrieveupdatedestroy",
    ),
]


urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
