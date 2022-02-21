"""Constants and utility code for the VarFish REST API.
"""

import re

from projectroles.views_api import SODARAPIRenderer, SODARAPIVersioning

from varfish import __version__ as varfish_version

# API constants
VARFISH_API_MEDIA_TYPE = "application/vnd.bihealth.varfish+json"
VARFISH_API_DEFAULT_VERSION = re.match(r"^([0-9.]+)(?:[+|\-][\S]+)?$", varfish_version)[1]
VARFISH_API_ALLOWED_VERSIONS = [
    "0.23.9",
]


class VarfishApiRenderer(SODARAPIRenderer):
    media_type = VARFISH_API_MEDIA_TYPE


class VarfishApiVersioning(SODARAPIVersioning):
    allowed_versions = VARFISH_API_MEDIA_TYPE
    default_version = VARFISH_API_DEFAULT_VERSION
