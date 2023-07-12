from django.urls import path

from cases_import import views, views_api

app_name = "cases_import"

ui_urlpatterns = [
    path(route="index/", view=views.IndexView.as_view(), name="ui-index"),
]

ajax_urlpatterns = []

api_urlpatterns = [
    path(
        route="api/case-import-action/list-create/<project>/",
        view=views_api.CaseImportActionListCreateApiView.as_view(),
        name="api-caseimportaction-listcreate",
    ),
    path(
        route="api/case-import-action/retrieve-update-destroy/<caseimportaction>/",
        view=views_api.CaseImportActionRetrieveUpdateDestroyApiView.as_view(),
        name="api-caseimportaction-retrieveupdatedestroy",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
