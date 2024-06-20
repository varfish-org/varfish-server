from django.urls import path
from django.urls import include
from rest_framework.routers import DefaultRouter

from seqvars import views_api

# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'seqvarsresultset', views_api.SnippetViewSet, basename='seqvarsresultset')

# Below is the usual URL pattern boilerplate.
app_name = "seqvars"
api_urlpatterns = [
    path('', include(router.urls)),
]
urlpatterns = api_urlpatterns
