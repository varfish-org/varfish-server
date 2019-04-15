# Projectroles dependency
from projectroles.plugins import SiteAppPluginPoint

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
    icon = "info-circle"

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
