from django.conf.urls import url

from seqmeta import views, views_api

app_name = "seqmeta"

ui_urlpatterns = [
    url(
        regex=r"^$",
        view=views.IndexView.as_view(),
        name="index",
    ),
    url(
        regex=r"^enrichmentkit/?$",
        view=views.EnrichmentKitListView.as_view(),
        name="enrichmentkit-list",
    ),
    url(
        regex=r"^enrichmentkit/(?P<enrichmentkit>[0-9a-f-]+)/?$",
        view=views.EnrichmentKitDetailView.as_view(),
        name="enrichmentkit-detail",
    ),
]

ajax_urlpatterns = []

api_urlpatterns = [
    url(
        regex=r"^api/enrichmentkit/list-create/?$",
        view=views_api.EnrichmentKitListCreateApiView.as_view(),
        name="api-enrichmentkit-listcreate",
    ),
    url(
        regex=r"^api/enrichmentkit/retrieve-update-destroy/(?P<enrichmentkit>[0-9a-f-]+)/?$",
        view=views_api.EnrichmentKitRetrieveUpdateDestroyApiView.as_view(),
        name="api-enrichmentkit-retrieveupdatedestroy",
    ),
    url(
        regex=r"^api/targetbedfile/list-create/(?P<enrichmenkit>[0-9a-f-]+)/?$",
        view=views_api.TargetBedFileListCreateApiView.as_view(),
        name="api-targetbedfile-listcreate",
    ),
    url(
        regex=r"^api/targetbedfile/retrieve-update-destroy/(?P<targetbedfile>[0-9a-f-]+)/?$",
        view=views_api.TargetBedFileRetrieveUpdateDestroyApiView.as_view(),
        name="api-targetbedfile-retrieveupdatedestroy",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
