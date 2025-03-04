"""URL configuration for the ``beaconsite`` app."""

from django.urls import path

from . import views, views_ajax, views_api

app_name = "beaconsite"

ui_urlpatterns = [
    path(
        route="",
        view=views.IndexView.as_view(),
        name="index",
    ),
    path(
        route="consortium/",
        view=views.ConsortiumListView.as_view(),
        name="consortium-list",
    ),
    path(
        route="consortium/<uuid:consortium>/",
        view=views.ConsortiumDetailView.as_view(),
        name="consortium-detail",
    ),
    path(
        route="consortium/create/",
        view=views.ConsortiumCreateView.as_view(),
        name="consortium-create",
    ),
    path(
        route="consortium/update/<uuid:consortium>/",
        view=views.ConsortiumUpdateView.as_view(),
        name="consortium-update",
    ),
    path(
        route="consortium/delete/<uuid:consortium>/",
        view=views.ConsortiumDeleteView.as_view(),
        name="consortium-delete",
    ),
    path(
        route="site/",
        view=views.SiteListView.as_view(),
        name="site-list",
    ),
    path(
        route="site/<uuid:site>/",
        view=views.SiteDetailView.as_view(),
        name="site-detail",
    ),
    path(
        route="site/create/",
        view=views.SiteCreateView.as_view(),
        name="site-create",
    ),
    path(
        route="site/update/<uuid:site>/",
        view=views.SiteUpdateView.as_view(),
        name="site-update",
    ),
    path(
        route="site/delete/<uuid:site>/",
        view=views.SiteDeleteView.as_view(),
        name="site-delete",
    ),
]

ajax_urlpatterns = [
    path(
        route="ajax/beacon/info/<uuid:site>/",
        view=views_ajax.BeaconInfoAjaxView.as_view(),
        name="ajax-beacon-info",
    ),
    path(
        route="ajax/beacon/query/<uuid:site>/",
        view=views_ajax.BeaconQueryAjaxView.as_view(),
        name="ajax-beacon-query",
    ),
]

beacon_api_urlpatterns = [
    path(route="endpoint", view=views_api.BeaconInfoApiView.as_view(), name="beacon-api-info"),
    path(
        route="endpoint/query/",
        view=views_api.BeaconQueryApiView.as_view(),
        name="beacon-api-query",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + beacon_api_urlpatterns
