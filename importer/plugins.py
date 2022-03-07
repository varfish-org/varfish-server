# Projectroles dependency
from bgjobs.plugins import BackgroundJobsPluginPoint
from projectroles.plugins import SiteAppPluginPoint

from .models import ImportCaseBgJob
from .urls import urlpatterns


class SiteAppPlugin(SiteAppPluginPoint):
    """Projectroles plugin for registering the app"""

    #: Name (slug-safe, used in URLs)
    name = "import_info_app"

    #: Title (used in templates)
    title = "Import Release Info"

    #: App URLs (will be included in settings by djangoplugins)
    urls = urlpatterns

    #: FontAwesome icon ID string
    icon = "bi:info-circle-fill"

    #: Description string
    description = "Databases release info app"

    #: Entry point URL ID
    entry_point_url_id = "importer:import-info"

    #: Required permission for displaying the app
    app_permission = "importer.view_data"

    def get_messages(self, user=None):
        """
        Return a list of messages to be shown to users.
        :param user: User object (optional)
        :return: List of dicts or and empty list if no messages
        """
        messages = []
        return messages


class BackgroundJobsPlugin(BackgroundJobsPluginPoint):
    """Plugin for registering background jobs with ``bgjobs`` app."""

    #: Slug used in URLs and similar places.
    name = "importer"
    #: Human-readable title.
    title = "Importer Background Jobs"

    #: Return name-to-class mapping for background job class specializations.
    job_specs = {
        ImportCaseBgJob.spec_name: ImportCaseBgJob,
    }

    def get_extra_data_link(self, _extra_data, _name):
        """Return a link for timeline label starting with 'extra-'"""
        return None
