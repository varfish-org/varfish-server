from projectroles.constants import get_sodar_constants
from projectroles.plugins import ProjectAppPluginPoint

from cases_import.urls import urlpatterns

# Global SODAR constants
SODAR_CONSTANTS = get_sodar_constants()


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "cases_import"
    title = "Case Import"
    urls = urlpatterns

    plugin_ordering = 1000

    icon = "mdi:cloud-update"

    entry_point_url_id = "cases:entrypoint"

    description = "Case Import Info"

    app_permission = "cases.view_data"

    app_settings = {
        "import_data_protocol": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import Protocol",
            "options": (
                "s3",
                "http",
                "https",
                "file",
            ),
            "description": "Protocol to use for data import",
        },
        "import_data_host": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import Host",
            "description": "Host name of server to import from (ignored if protocol is file)",
        },
        "import_data_port": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import Port",
            "description": "Optional port for import connection (ignored if protocol is file)",
        },
        "import_data_user": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import User",
            "description": (
                "User name to use for opening connection (access key for S3, ignored if "
                "protocol is file)"
            ),
        },
        "import_data_password": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import Password",
            "description": (
                "User name to use for opening connection (secret key for S3, ignored if "
                "protocol is file)",
            ),
        },
    }