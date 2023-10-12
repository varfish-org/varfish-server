from django.urls import path

from cases_qc import views_api

app_name = "cases_qc"

ui_urlpatterns = []

ajax_urlpatterns = []

api_urlpatterns = [
    path(
        route="api/caseqc/retrieve/<case>/",
        view=views_api.CaseQcRetrieveApiView.as_view(),
        name="api-caseqc-retrieve",
    ),
    path(
        route="api/varfishstats/retrieve/<case>/",
        view=views_api.VarfishStatsRetrieveApiView.as_view(),
        name="api-varfishstats-retrieve",
    ),
]

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
