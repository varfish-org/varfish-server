from django.urls import include, path
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/seqvarpresetsset/(?P<project>[0-9a-f-]+)",
    views_api.QueryPresetsSetViewSet,
    basename="api-querypresetsset",
)
router.register(
    r"api/querypresetsfrequency/(?P<querypresetsset>[0-9a-f-]+)",
    views_api.QueryPresetsFrequencyViewSet,
    basename="api-querypresetsfrequency",
)
# router.register(
#     r"api/seqvarpresetsconsequence/(?P<project>[0-9a-f-]+)",
#     views_api.QueryPresetsConsequenceViewSet,
#     basename="api-seqvarpresetsconsequence",
# )
# router.register(
#     r"api/seqvarpresetslocus/(?P<project>[0-9a-f-]+)", views_api.QueryPresetsLocusViewSet, basename="api-seqvarpresetslocus"
# )
# router.register(
#     r"api/seqvarpresetsphenotypeprio/(?P<project>[0-9a-f-]+)",
#     views_api.QueryPresetsPhenotypePrioViewSet,
#     basename="api-seqvarpresetsphenotypeprio",
# )
# router.register(
#     r"api/seqvarpresetsvariantprio/(?P<project>[0-9a-f-]+)",
#     views_api.QueryPresetsVariantPrioViewSet,
#     basename="api-seqvarpresetsvariantprio",
# )
# router.register(
#     r"api/seqvarpresetscolumns/(?P<project>[0-9a-f-]+)",
#     views_api.QueryPresetsColumnsViewSet,
#     basename="api-seqvarpresetscolumns",
# )
# router.register(
#     r"api/seqvarpresetsmisc/(?P<project>[0-9a-f-]+)", views_api.QueryPresetsMiscViewSet, basename="api-seqvarpresetsmisc"
# )
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
    r"api/seqvarresultrow/(?P<resultset>[0-9a-f-]+)",
    views_api.ResultRowViewSet,
    basename="api-seqvarresultrow",
)


# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns = api_urlpatterns
