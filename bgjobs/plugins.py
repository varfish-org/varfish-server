from projectroles.plugins import ProjectAppPluginPoint
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "bgjobs"
    title = "Background Jobs"
    urls = urlpatterns
    # ...

    icon = "tasks"

    entry_point_url_id = "bgjobs:job-list"

    description = "Jobs executed in the background"

    #: Required permission for accessing the app
    app_permission = "bgjobs.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: List of search object types for the app
    search_types = []

    #: Search results template
    search_template = None

    #: App card template for the project details page
    details_template = "bgjobs/temp.html"

    #: App card title for the project details page
    details_title = "Background Jobs App Overview"

    #: Position in plugin ordering
    plugin_ordering = 100
