from django.db.utils import DataError
from projectroles.plugins import ProjectAppPluginPoint

from cases.urls import urlpatterns
from variants.models.case import Case


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "cases"
    title = "Cases"
    urls = urlpatterns

    icon = "mdi:hospital-building"

    entry_point_url_id = "cases:entrypoint"

    description = "Cases"

    #: Required permission for accessing the app
    app_permission = "cases.view_data"

    #: Enable or disable general search from project title bar
    search_enable = True

    #: List of search object types for the app
    search_types = ["case"]

    #: Search results template
    search_template = "cases/_search_results.html"

    #: App card template for the project details page
    details_template = "cases/_details_card.html"

    #: No settings for this app.
    app_settings = {}

    #: Position in plugin ordering
    plugin_ordering = 10

    def search(self, search_terms, user, search_type=None, keywords=None):
        """
        Return app items based on a search term, user, optional type and
        optional keywords
        :param search_terms: List of strings.
        :param user: User object for user initiating the search
        :param search_type: String
        :param keywords: List (optional)
        :return: Dict
        """
        items = []
        cases = Case.objects.find(search_terms, keywords)
        if not search_type:
            try:
                items = [
                    case for case in cases if user.has_perm("variants.view_data", case.project)
                ]
            except DataError:
                items = []
            items.sort(key=lambda x: x.name.lower())
        elif search_type == "case":
            try:
                items = list(cases.order_by("name"))
            except DataError:
                items = []

        return {"all": {"title": "Cases", "search_types": ["case"], "items": items}}

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: sodar_uuid of the referred object
        :return: Dict or None if not found
        """
        return None  # pragma: no cover
