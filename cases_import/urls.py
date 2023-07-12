from django.urls import path

from cases_import import views

# from cases_import import views_api

app_name = "cases_import"

ui_urlpatterns = [
    path(route="index/", view=views.IndexView.as_view(), name="ui-index"),
]

ajax_urlpatterns = []

api_urlpatterns = [
    # url(
    #     regex=r"^api/case-import-action/list-create/(?P<project>[0-9a-f-]+)/?$",
    #     view=views_api.CaseImportActionListCreateApiView.as_view(),
    #     name="api-caseimportaction-listcreate",
    # ),
    # url(
    #     regex=r"^api/case-import-action/retrieve-update-destroy/(?P<caseimportaction>[0-9a-f-]+)/?$",
    #     view=views_api.CaseImportActionRetrieveUpdateDestroyApiView.as_view(),
    #     name="api-caseimportaction-retrieveupdatedestroy",
    # ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
