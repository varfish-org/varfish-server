from django.urls import include, path
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/seqvarpresetsset/(?P<project>[0-9a-f-]+)",
    views_api.SeqvarQueryPresetsSetViewSet,
    basename="api-seqvarquerypresetsset",
)
router.register(
    r"api/seqvarpresetsfrequency/(?P<seqvarquerypresetsset>[0-9a-f-]+)",
    views_api.SeqvarPresetsFrequencyViewSet,
    basename="api-seqvarpresetsfrequency",
)
# router.register(
#     r"api/seqvarpresetsconsequence/(?P<project>[0-9a-f-]+)",
#     views_api.SeqvarPresetsConsequenceViewSet,
#     basename="api-seqvarpresetsconsequence",
# )
# router.register(
#     r"api/seqvarpresetslocus/(?P<project>[0-9a-f-]+)", views_api.SeqvarPresetsLocusViewSet, basename="api-seqvarpresetslocus"
# )
# router.register(
#     r"api/seqvarpresetsphenotypeprio/(?P<project>[0-9a-f-]+)",
#     views_api.SeqvarPresetsPhenotypePrioViewSet,
#     basename="api-seqvarpresetsphenotypeprio",
# )
# router.register(
#     r"api/seqvarpresetsvariantprio/(?P<project>[0-9a-f-]+)",
#     views_api.SeqvarPresetsVariantPrioViewSet,
#     basename="api-seqvarpresetsvariantprio",
# )
# router.register(
#     r"api/seqvarpresetscolumns/(?P<project>[0-9a-f-]+)",
#     views_api.SeqvarPresetsColumnsViewSet,
#     basename="api-seqvarpresetscolumns",
# )
# router.register(
#     r"api/seqvarpresetsmisc/(?P<project>[0-9a-f-]+)", views_api.SeqvarPresetsMiscViewSet, basename="api-seqvarpresetsmisc"
# )
router.register(
    r"api/seqvarquerysettings/(?P<case>[0-9a-f-]+)",
    views_api.SeqvarQuerySettingsViewSet,
    basename="api-seqvarquerysettings",
)
router.register(
    r"api/seqvarquery/(?P<case>[0-9a-f-]+)",
    views_api.SeqvarQueryViewSet,
    basename="api-seqvarquery",
)
router.register(
    r"api/seqvarqueryexecution/(?P<seqvarquery>[0-9a-f-]+)",
    views_api.SeqvarQueryExecutionViewSet,
    basename="api-seqvarqueryexecution",
)
router.register(
    r"api/seqvarresultset/(?P<seqvarquery>[0-9a-f-]+)",
    views_api.SeqvarResultSetViewSet,
    basename="api-seqvarresultset",
)
router.register(
    r"api/seqvarresultrow/(?P<seqvarresultset>[0-9a-f-]+)",
    views_api.SeqvarResultRowViewSet,
    basename="api-seqvarresultrow",
)


# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns = api_urlpatterns
