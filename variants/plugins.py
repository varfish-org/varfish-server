from projectroles.plugins import ProjectAppPluginPoint
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "variants"
    title = "VarFish"
    urls = urlpatterns
    # ...

    icon = "ship"

    entry_point_url_id = "variants:case"

    description = "VarFish"

    #: Required permission for accessing the app
    app_permission = "variants.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: List of search object types for the app
    search_types = []

    #: Search results template
    search_template = None

    #: App card template for the project details page
    details_template = "variants/_details_card.html"

    #: App card title for the project details page
    details_title = "VarFish App Overview"

    #: Position in plugin ordering
    plugin_ordering = 100
