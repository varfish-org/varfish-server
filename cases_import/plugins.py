import itertools

from bgjobs.plugins import BackgroundJobsPluginPoint
from django.conf import settings
from projectroles.constants import get_sodar_constants
from projectroles.plugins import ProjectAppPluginPoint

from cases_import.models.base import CaseImportBackgroundJob
from cases_import.urls import urlpatterns

# Global SODAR constants
SODAR_CONSTANTS = get_sodar_constants()


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "cases_import"
    title = "Case Import"
    urls = urlpatterns

    plugin_ordering = 1000

    icon = "mdi:cloud-upload"

    entry_point_url_id = "cases_import:index"

    description = "Case Import Info"

    app_permission = "cases_import.view_data"

    app_settings = {
        "import_data_protocol": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Import Protocol",
            "options": tuple(
                itertools.chain(
                    ("s3", "http", "https"),
                    ("file",) if settings.VARFISH_CASE_IMPORT_ALLOW_FILE else (),
                )
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
        "import_data_path": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "STRING",
            "default": "",
            "label": "Path prefix",
            "description": "Path prefix to use",
        },
        "import_data_port": {
            "scope": SODAR_CONSTANTS["APP_SETTING_SCOPE_PROJECT"],
            "type": "INTEGER",
            "default": 0,
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


class BackgroundJobsPlugin(BackgroundJobsPluginPoint):
    """Plugin for registering background jobs with ``bgjobs`` app."""

    name = "cases_import"
    title = "Cases Import Background Jobs"

    job_specs = {
        CaseImportBackgroundJob.spec_name: CaseImportBackgroundJob,
    }

    def get_extra_data_link(self, _extra_data, _name):
        return None

    def get_object_link(self, *args, **kwargs):
        return None
