from projectroles.plugins import ProjectAppPluginPoint

# APP DISCONTINUTED


class ProjectAppPlugin(ProjectAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    name = "clinvar_export"
    title = "REMOVED"
    plugin_ordering = 100
    icon = "mdi:export-variant"
    entry_point_url_id = "projectroles:detail"
    description = "REMOVED"
    app_permission = "xxx.view_data"  # INVALID => only superusers
    search_enable = False
    search_types = []
    app_settings = {}

    def get_object_link(self, model_str, uuid):
        return None
