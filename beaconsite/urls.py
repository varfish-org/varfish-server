"""URL configuration for the ``beaconsite`` app.
"""

from django.conf.urls import url
from . import views, views_api, views_ajax

app_name = "beaconsite"

ui_urlpatterns = [
    url(regex=r"^$", view=views.IndexView.as_view(), name="index",),
    url(regex=r"^consortium$", view=views.ConsortiumListView.as_view(), name="consortium-list",),
    url(
        regex=r"^consortium/(?P<consortium>[0-9a-f-]+)$",
        view=views.ConsortiumDetailView.as_view(),
        name="consortium-detail",
    ),
    url(
        regex=r"^consortium/create/$",
        view=views.ConsortiumCreateView.as_view(),
        name="consortium-create",
    ),
    url(
        regex=r"^consortium/update/(?P<consortium>[0-9a-f-]+)$",
        view=views.ConsortiumUpdateView.as_view(),
        name="consortium-update",
    ),
    url(
        regex=r"^consortium/delete/(?P<consortium>[0-9a-f-]+)$",
        view=views.ConsortiumDeleteView.as_view(),
        name="consortium-delete",
    ),
    url(regex=r"^site$", view=views.SiteListView.as_view(), name="site-list",),
    url(
        regex=r"^site/(?P<site>[0-9a-f-]+)$",
        view=views.SiteDetailView.as_view(),
        name="site-detail",
    ),
    url(regex=r"^site/create/$", view=views.SiteCreateView.as_view(), name="site-create",),
    url(
        regex=r"^site/update/(?P<site>[0-9a-f-]+)$",
        view=views.SiteUpdateView.as_view(),
        name="site-update",
    ),
    url(
        regex=r"^site/delete/(?P<site>[0-9a-f-]+)$",
        view=views.SiteDeleteView.as_view(),
        name="site-delete",
    ),
]

ajax_urlpatterns = [
    url(
        regex=r"^ajax/beacon/info/(?P<site>[0-9a-f-]+)$",
        view=views_ajax.BeaconInfoAjaxView.as_view(),
        name="ajax-beacon-info",
    ),
    url(
        regex=r"^ajax/beacon/query/(?P<site>[0-9a-f-]+)$",
        view=views_ajax.BeaconQueryAjaxView.as_view(),
        name="ajax-beacon-query",
    ),
]

beacon_api_urlpatterns = [
    url(regex=r"^endpoint/?$", view=views_api.BeaconInfoApiView.as_view(), name="beacon-api-info"),
    url(
        regex=r"^endpoint/query/?$",
        view=views_api.BeaconQueryApiView.as_view(),
        name="beacon-api-query",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + beacon_api_urlpatterns
