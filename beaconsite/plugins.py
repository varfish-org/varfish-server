from bgjobs.plugins import BackgroundJobsPluginPoint
from projectroles.plugins import SiteAppPluginPoint

from .urls import urlpatterns


class SiteAppPlugin(SiteAppPluginPoint):
    """Projectroles plugin for registering the app"""

    #: Name (identifier-safe, used in URLs)
    name = "beaconsite"

    #: Title (used in templates)
    title = "Beacon Site"

    #: App URLs (will be included in settings by djangoplugins)
    urls = urlpatterns

    #: FontAwesome icon ID string
    icon = "mdi:lighthouse"

    #: Description string
    description = "Connecting sites with GAGH Beacon API"

    #: Entry point URL ID
    entry_point_url_id = "beaconsite:index"

    #: Required permission for displaying the app
    app_permission = "beaconsite.view_data"

    def get_messages(self, user=None):
        """
        Return a list of messages to be shown to users.
        :param user: User object (optional)
        :return: List of dicts or and empty list if no messages
        """
        messages = []
        return messages
