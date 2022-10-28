from projectroles.plugins import ProjectAppPluginPoint

from varannos.models import VarAnnoSetEntry
from varannos.urls import urlpatterns
from variants.plugins import VariantsDetailsPluginPoint, VariantsExtendQueryInfoColPluginPoint


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "varannos"
    title = "VarAnnos"
    urls = urlpatterns

    details_template = "varannos/_details_card.html"

    details_title = "Variant Annotation Sets (top 5 most recently updated)"

    plugin_ordering = 100

    icon = "mdi:notebook-heart"

    entry_point_url_id = "varannos:varannoset-list"

    description = "Case independent variant annotations"

    #: Required permission for accessing the app
    app_permission = "varannos.view_data"

    #: Enable or disable general search from project title bar
    search_enable = False

    #: List of search object types for the app
    search_types = []

    #: No settings for this app.
    app_settings = {}

    def get_object_link(self, model_str, uuid):
        """
        Return URL for referring to a object used by the app, along with a
        label to be shown to the user for linking.
        :param model_str: Object class (string)
        :param uuid: sodar_uuid of the referred object
        :return: Dict or None if not found
        """
        return None  # pragma: no cover


class VariantsDetailsPlugin(VariantsDetailsPluginPoint):
    """Plugin for providing variant details information."""

    plugin_ordering = 100

    def load_details(self, *, release, chromosome, start, end, reference, alternative, **kwargs):
        qs = VarAnnoSetEntry.objects.filter(
            release=release,
            chromosome=chromosome,
            start=start,
            end=end,
            reference=reference,
            alternative=alternative,
        ).prefetch_related("varannoset")

        content = []
        entries = list(qs.all())
        entry_count = len(entries)
        for entry in entries:
            if entry_count > 1:
                content.append({"label": "VarAnno Set", "value": entry.varannoset.title})
            content += [{"label": label, "value": value} for label, value in entry.payload.items()]

        return {
            "title": "VarAnnos",
            "plugin_type": "variant",
            "help_text": "This card displays variants from the VarAnnos app.",
            "content": content,
        }


class VariantsExtendQueryInfoColPlugin(VariantsExtendQueryInfoColPluginPoint):
    """Plugin for extending query with informative columns."""

    #: Define the one extra column that we add with the VarAnnoSetEntry count for a variant.
    columns = [{"field_name": "varannos_varannosetentry_count", "label": "VarAnnos",}]

    #: Define the classes to extend the query with.
    def get_extend_query_part_classes(self):
        return [
            "varannos.queries.ExtendQueryPartsVarAnnosJoin",
        ]

    #: Specify explicit ordering
    plugin_ordering = 100
