"""Constants and utility code for the VarFish REST API."""

from projectroles.views_api import SODARAPIRenderer, SODARAPIVersioning
from rest_framework.pagination import PageNumberPagination


class VarfishApiRenderer(SODARAPIRenderer):
    pass


class VarfishApiVersioning(SODARAPIVersioning):
    pass


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
