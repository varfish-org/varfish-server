"""URL configuration for the ``importer`` app.
"""

from django.conf.urls import url

from . import views, views_ajax, views_api

app_name = "cohorts"
ui_urlpatterns = [
    url(
        regex=r"^vueapp/(?P<project>[0-9a-f-]+)/?$",
        view=views.EntrypointView.as_view(),
        name="entrypoint",
    ),
]

ajax_urlpatterns = [
    url(
        regex=r"^ajax/cohort/list-create/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.CohortListCreateAjaxView.as_view(),
        name="ajax-cohort-list-create",
    ),
    url(
        regex=r"^ajax/cohort/retrieve-update-destroy/(?P<cohort>[0-9a-f-]+)/?$",
        view=views_ajax.CohortRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-cohort-retrieve-update-destroy",
    ),
    url(
        regex=r"^ajax/cohortcase/create/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.CohortCaseCreateAjaxView.as_view(),
        name="ajax-cohortcase-create",
    ),
    url(
        regex=r"^ajax/cohortcase/list/(?P<cohort>[0-9a-f-]+)/?$",
        view=views_ajax.CohortCaseListAjaxView.as_view(),
        name="ajax-cohortcase-list",
    ),
    url(
        regex=r"^ajax/cohortcase/destroy/(?P<cohortcase>[0-9a-f-]+)/?$",
        view=views_ajax.CohortCaseDestroyAjaxView.as_view(),
        name="ajax-cohortcase-destroy",
    ),
    url(
        regex=r"^ajax/accessible-projects-cases/list/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.AccessibleProjectsCasesAjaxView.as_view(),
        name="ajax-accessible-projects-cases-list",
    ),
    url(
        regex=r"ajax/user-permissions/(?P<project>[0-9a-f-]+)/?$",
        view=views_ajax.ProjectUserPermissionsAjaxView.as_view(),
        name="ajax-userpermissions",
    ),
]

api_urlpatterns = [
    url(
        regex=r"^api/cohort/list-create/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.CohortListCreateApiView.as_view(),
        name="api-cohort-list-create",
    ),
    url(
        regex=r"^api/cohort/retrieve-update-destroy/(?P<cohort>[0-9a-f-]+)/?$",
        view=views_api.CohortRetrieveUpdateDestroyApiView.as_view(),
        name="api-cohort-retrieve-update-destroy",
    ),
    url(
        regex=r"^api/cohortcase/create/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.CohortCaseCreateApiView.as_view(),
        name="api-cohortcase-create",
    ),
    url(
        regex=r"^api/cohortcase/list/(?P<cohort>[0-9a-f-]+)/?$",
        view=views_api.CohortCaseListApiView.as_view(),
        name="api-cohortcase-list",
    ),
    url(
        regex=r"^api/cohortcase/destroy/(?P<cohortcase>[0-9a-f-]+)/?$",
        view=views_api.CohortCaseDestroyApiView.as_view(),
        name="api-cohortcase-destroy",
    ),
    url(
        regex=r"^api/accessible-projects-cases/list/(?P<project>[0-9a-f-]+)/?$",
        view=views_api.AccessibleProjectsCasesApiView.as_view(),
        name="api-accessible-projects-cases-list",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
