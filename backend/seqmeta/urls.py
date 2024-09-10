from django.urls import path

from seqmeta import views, views_api

app_name = "seqmeta"

ui_urlpatterns = [
    path(
        "",
        view=views.IndexView.as_view(),
        name="index",
    ),
    path(
        "enrichmentkit/",
        view=views.EnrichmentKitListView.as_view(),
        name="enrichmentkit-list",
    ),
    path(
        "enrichmentkit/<uuid:enrichmentkit>/",
        view=views.EnrichmentKitDetailView.as_view(),
        name="enrichmentkit-detail",
    ),
]

ajax_urlpatterns = []

api_urlpatterns = [
    path(
        "api/enrichmentkit/list-create/",
        view=views_api.EnrichmentKitListCreateApiView.as_view(),
        name="api-enrichmentkit-listcreate",
    ),
    path(
        "api/enrichmentkit/retrieve-update-destroy/<uuid:enrichmentkit>/",
        view=views_api.EnrichmentKitRetrieveUpdateDestroyApiView.as_view(),
        name="api-enrichmentkit-retrieveupdatedestroy",
    ),
    path(
        "api/targetbedfile/list-create/<uuid:enrichmentkit>/",
        view=views_api.TargetBedFileListCreateApiView.as_view(),
        name="api-targetbedfile-listcreate",
    ),
    path(
        "api/targetbedfile/retrieve-update-destroy/<uuid:targetbedfile>/",
        view=views_api.TargetBedFileRetrieveUpdateDestroyApiView.as_view(),
        name="api-targetbedfile-retrieveupdatedestroy",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
