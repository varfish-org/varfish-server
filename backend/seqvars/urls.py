from django.urls import include, path
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(
    r"api/seqvarsresultset", views_api.SeqvarResultSetViewSet, basename="seqvarsresultset"
)
router.register(
    r"api/seqvarpresetsset", views_api.SeqvarQueryPresetsSetViewSet, basename="seqvarpresetsset"
)
router.register(
    r"api/seqvarpresetsfrequency",
    views_api.SeqvarPresetsFrequencyViewSet,
    basename="seqvarpresetsfrequency",
)
router.register(
    r"api/seqvarpresetsconsequence",
    views_api.SeqvarPresetsConsequenceViewSet,
    basename="seqvarpresetsconsequence",
)
router.register(
    r"api/seqvarpresetslocus", views_api.SeqvarPresetsLocusViewSet, basename="seqvarpresetslocus"
)
router.register(
    r"api/seqvarpresetsphenotypeprio",
    views_api.SeqvarPresetsPhenotypePrioViewSet,
    basename="seqvarpresetsphenotypeprio",
)
router.register(
    r"api/seqvarpresetsvariantprio",
    views_api.SeqvarPresetsVariantPrioViewSet,
    basename="seqvarpresetsvariantprio",
)
router.register(
    r"api/seqvarpresetscolumns",
    views_api.SeqvarPresetsColumnsViewSet,
    basename="seqvarpresetscolumns",
)
router.register(
    r"api/seqvarpresetsmisc", views_api.SeqvarPresetsMiscViewSet, basename="seqvarpresetsmisc"
)
router.register(
    r"api/seqvarquerysettings", views_api.SeqvarQuerySettingsViewSet, basename="seqvarquerysettings"
)
router.register(r"api/seqvarquery/(?P<caseanalysissession>[0-9a-f-]+)", views_api.SeqvarQueryViewSet, basename="seqvarquery")
router.register(
    r"api/seqvarqueryexecution",
    views_api.SeqvarQueryExecutionViewSet,
    basename="seqvarqueryexecution",
)
router.register(r"api/seqvarquery", views_api.SeqvarQueryViewSet, basename="seqvarquery")
router.register(
    r"api/seqvarqueryexecution",
    views_api.SeqvarQueryExecutionViewSet,
    basename="seqvarqueryexecution",
)
router.register(
    r"api/seqvarresultset", views_api.SeqvarResultSetViewSet, basename="seqvarresultset"
)
router.register(
    r"api/seqvarresultrow", views_api.SeqvarResultRowViewSet, basename="seqvarresultrow"
)


# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path("", include(router.urls)),
]
urlpatterns = api_urlpatterns
