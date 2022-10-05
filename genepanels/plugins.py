from projectroles.plugins import SiteAppPluginPoint

from .urls import urlpatterns


class SiteAppPlugin(SiteAppPluginPoint):
    """Projectroles plugin for registering the app"""

    #: Name (identifier-safe, used in URLs)
    name = "genepanels"

    #: Title (used in templates)
    title = "Gene Panels"

    #: App URLs (will be included in settings by djangoplugins)
    urls = urlpatterns

    #: Iconify icon ID string
    icon = "mdi:format-list-bulleted-type"

    #: Description string
    description = "Define gene panels based on gene IDs"

    #: Entry point URL ID
    entry_point_url_id = "genepanels:index"

    #: Required permission for displaying the app
    app_permission = "genepanels.view_data"
