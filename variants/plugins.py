from projectroles.plugins import ProjectAppPluginPoint

from .models import Case
from .urls import urlpatterns


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "variants"
    title = "Cases"
    urls = urlpatterns
    # ...

    icon = "hospital-o"

    entry_point_url_id = "variants:case-list"

    description = "Cases"

    #: Required permission for accessing the app
    app_permission = "variants.view_data"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["case"]

    #: Search results template
    search_template = "variants/_search_results.html"

    #: App card template for the project details page
    details_template = "variants/_details_card.html"

    #: App card title for the project details page
    details_title = "VarFish App Overview"

    #: Position in plugin ordering
    plugin_ordering = 10

    def search(self, search_term, user, search_type=None, keywords=None):
        """
        Return app items based on a search term, user, optional type and
        optional keywords
        :param search_term: String
        :param user: User object for user initiating the search
        :param search_type: String
        :param keywords: List (optional)
        :return: Dict
        """
        items = []

        if not search_type:
            cases = Case.objects.find(search_term, keywords)
            items = list(cases)
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "case":
            items = Case.objects.find(search_term, keywords).order_by("name")

        return {"all": {"title": "Cases", "search_types": ["case"], "items": items}}
