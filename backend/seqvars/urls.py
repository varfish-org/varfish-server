from django.urls import include, path
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/querypresetsset/(?P<project>[0-9a-f-]+)",
    views_api.QueryPresetsSetViewSet,
    basename="api-querypresetsset",
)
router.register(
    r"api/querypresetssetversion/(?P<querypresetsset>[0-9a-f-]+)",
    views_api.QueryPresetsSetVersionViewSet,
    basename="api-querypresetssetversion",
)
router.register(
    r"api/querypresetsquality/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsQualityViewSet,
    basename="api-querypresetsquality",
)
router.register(
    r"api/querypresetsfrequency/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsFrequencyViewSet,
    basename="api-querypresetsfrequency",
)
router.register(
    r"api/querypresetsconsequence/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsConsequenceViewSet,
    basename="api-querypresetsconsequence",
)
router.register(
    r"api/querypresetslocus/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsLocusViewSet,
    basename="api-querypresetslocus",
)
router.register(
    r"api/querypresetsphenotypeprio/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsPhenotypePrioViewSet,
    basename="api-querypresetsphenotypeprio",
)
router.register(
    r"api/querypresetsvariantprio/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsVariantPrioViewSet,
    basename="api-querypresetsvariantprio",
)
router.register(
    r"api/querypresetsclinvar/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsClinvarViewSet,
    basename="api-querypresetsclinvar",
)
router.register(
    r"api/querypresetscolumns/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.QueryPresetsColumnsViewSet,
    basename="api-querypresetscolumns",
)
router.register(
    r"api/querysettings/(?P<session>[0-9a-f-]+)",
    views_api.QuerySettingsViewSet,
    basename="api-querysettings",
)
router.register(
    r"api/query/(?P<session>[0-9a-f-]+)",
    views_api.QueryViewSet,
    basename="api-query",
)
router.register(
    r"api/queryexecution/(?P<query>[0-9a-f-]+)",
    views_api.QueryExecutionViewSet,
    basename="api-queryexecution",
)
router.register(
    r"api/resultset/(?P<query>[0-9a-f-]+)",
    views_api.ResultSetViewSet,
    basename="api-resultset",
)
router.register(
    r"api/resultrow/(?P<resultset>[0-9a-f-]+)",
    views_api.ResultRowViewSet,
    basename="api-resultrow",
)

# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns = api_urlpatterns
