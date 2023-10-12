from projectroles.plugins import SiteAppPluginPoint

from seqmeta.urls import urlpatterns


class SiteAppPlugin(SiteAppPluginPoint):
    """Projectroles plugin for registering the app"""

    #: Name (identifier-safe, used in URLs)
    name = "seqmeta"

    #: Title (used in templates)
    title = "Seq. Meta"

    #: App URLs (will be included in settings by djangoplugins)
    urls = urlpatterns

    #: FontAwesome icon ID string
    icon = "mdi:factory"

    #: Description string
    description = "Sequencing Metadata"

    #: Entry point URL ID
    entry_point_url_id = "seqmeta:index"

    #: Required permission for displaying the app
    app_permission = "seqmeta.view_data"

    def get_messages(self, user=None):
        """
        Return a list of messages to be shown to users.
        :param user: User object (optional)
        :return: List of dicts or and empty list if no messages
        """
        messages = []
        return messages
