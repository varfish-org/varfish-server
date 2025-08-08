from django.urls import include, path
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/querypresetsset/(?P<project>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsSetViewSet,
    basename="api-querypresetsset",
)
router.register(
    r"api/querypresetssetversion/(?P<querypresetsset>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsSetVersionViewSet,
    basename="api-querypresetssetversion",
)
router.register(
    r"api/querypresetsquality/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsQualityViewSet,
    basename="api-querypresetsquality",
)
router.register(
    r"api/querypresetsfrequency/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsFrequencyViewSet,
    basename="api-querypresetsfrequency",
)
router.register(
    r"api/querypresetsconsequence/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsConsequenceViewSet,
    basename="api-querypresetsconsequence",
)
router.register(
    r"api/querypresetslocus/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsLocusViewSet,
    basename="api-querypresetslocus",
)
router.register(
    r"api/querypresetsphenotypeprio/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsPhenotypePrioViewSet,
    basename="api-querypresetsphenotypeprio",
)
router.register(
    r"api/querypresetsvariantprio/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsVariantPrioViewSet,
    basename="api-querypresetsvariantprio",
)
router.register(
    r"api/querypresetsclinvar/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsClinvarViewSet,
    basename="api-querypresetsclinvar",
)
router.register(
    r"api/querypresetscolumns/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsQueryPresetsColumnsViewSet,
    basename="api-querypresetscolumns",
)
router.register(
    r"api/predefinedquery/(?P<querypresetssetversion>[0-9a-f-]+)",
    views_api.SeqvarsPredefinedQueryViewSet,
    basename="api-predefinedquery",
)
router.register(
    r"api/querysettings/(?P<session>[0-9a-f-]+)",
    views_api.SeqvarsQuerySettingsViewSet,
    basename="api-querysettings",
)
router.register(
    r"api/query/(?P<session>[0-9a-f-]+)",
    views_api.SeqvarsQueryViewSet,
    basename="api-query",
)
router.register(
    r"api/queryexecution/(?P<query>[0-9a-f-]+)",
    views_api.SeqvarsQueryExecutionViewSet,
    basename="api-queryexecution",
)
router.register(
    r"api/resultset/(?P<queryexecution>[0-9a-f-]+)",
    views_api.SeqvarsResultSetViewSet,
    basename="api-resultset",
)
router.register(
    r"api/resultrow/(?P<resultset>[0-9a-f-]+)",
    views_api.SeqvarsResultRowViewSet,
    basename="api-resultrow",
)

# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns = api_urlpatterns
