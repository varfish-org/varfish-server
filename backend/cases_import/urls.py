from django.urls import path
from rest_framework.routers import DefaultRouter

from cases_import import views, views_api

app_name = "cases_import"
router = DefaultRouter()

ui_urlpatterns = [
    path(route="index/<project>/", view=views.IndexView.as_view(), name="index"),
    path(
        route="import-case-bg-job/<caseimportbackgroundjob>/",
        view=views.ImportCaseBackgroundsJobDetailView.as_view(),
        name="ui-caseimportbackgroundjob-detail",
    ),
]

ajax_urlpatterns = []

router.register(
    r"api/case-import-action/(?P<project>[0-9a-f-]+)",
    views_api.CaseImportActionViewSet,
    basename="api-caseimportaction",
)


api_urlpatterns = router.urls

urlpatterns = ui_urlpatterns + ajax_urlpatterns + api_urlpatterns
