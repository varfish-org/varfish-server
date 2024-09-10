"""URL configuration for the ``importer`` app.
"""

from django.urls import path

from . import views, views_ajax, views_api

app_name = "cohorts"
ui_urlpatterns = [
    path(
        "vueapp/<uuid:project>/",
        view=views.EntrypointView.as_view(),
        name="entrypoint",
    ),
]

ajax_urlpatterns = [
    path(
        "ajax/cohort/list-create/<uuid:project>/",
        view=views_ajax.CohortListCreateAjaxView.as_view(),
        name="ajax-cohort-list-create",
    ),
    path(
        "ajax/cohort/retrieve-update-destroy/<uuid:cohort>/",
        view=views_ajax.CohortRetrieveUpdateDestroyAjaxView.as_view(),
        name="ajax-cohort-retrieve-update-destroy",
    ),
    path(
        "ajax/cohortcase/create/<uuid:project>/",
        view=views_ajax.CohortCaseCreateAjaxView.as_view(),
        name="ajax-cohortcase-create",
    ),
    path(
        "ajax/cohortcase/list/<uuid:cohort>/",
        view=views_ajax.CohortCaseListAjaxView.as_view(),
        name="ajax-cohortcase-list",
    ),
    path(
        "ajax/cohortcase/destroy/<uuid:cohortcase>/",
        view=views_ajax.CohortCaseDestroyAjaxView.as_view(),
        name="ajax-cohortcase-destroy",
    ),
    path(
        "ajax/accessible-projects-cases/list/<uuid:project>/",
        view=views_ajax.AccessibleProjectsCasesAjaxView.as_view(),
        name="ajax-accessible-projects-cases-list",
    ),
    path(
        "ajax/user-permissions/<uuid:project>/",
        view=views_ajax.ProjectUserPermissionsAjaxView.as_view(),
        name="ajax-userpermissions",
    ),
]

api_urlpatterns = [
    path(
        "api/cohort/list-create/<uuid:project>/",
        view=views_api.CohortListCreateApiView.as_view(),
        name="api-cohort-list-create",
    ),
    path(
        "api/cohort/retrieve-update-destroy/<uuid:cohort>/",
        view=views_api.CohortRetrieveUpdateDestroyApiView.as_view(),
        name="api-cohort-retrieve-update-destroy",
    ),
    path(
        "api/cohortcase/create/<uuid:project>/",
        view=views_api.CohortCaseCreateApiView.as_view(),
        name="api-cohortcase-create",
    ),
    path(
        "api/cohortcase/list/<uuid:cohort>/",
        view=views_api.CohortCaseListApiView.as_view(),
        name="api-cohortcase-list",
    ),
    path(
        "api/cohortcase/destroy/<uuid:cohortcase>/",
        view=views_api.CohortCaseDestroyApiView.as_view(),
        name="api-cohortcase-destroy",
    ),
    path(
        "api/accessible-projects-cases/list/<uuid:project>/",
        view=views_api.AccessibleProjectsCasesApiView.as_view(),
        name="api-accessible-projects-cases-list",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
