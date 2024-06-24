from django.urls import include, path
from rest_framework.routers import DefaultRouter

from cases_analysis import views_api

app_name = "cases_analysis"

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/caseanalysis/(?P<case>[0-9a-f-]+)",
    views_api.CaseAnalysisViewSet,
    basename="api-caseanalysis",
)
router.register(
    r"api/caseanalysissession/(?P<case>[0-9a-f-]+)",
    views_api.CaseAnalysisSessionViewSet,
    basename="api-caseanalysissession",
)

urlpatterns = [path("", include(router.urls))]
