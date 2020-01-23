from projectroles.plugins import SiteAppPluginPoint


class ProjectAppPlugin(SiteAppPluginPoint):
    """Plugin for registering app with Projectroles"""

    icon = "key"
    name = "token"

    title = "API Tokens"

    entry_point_url_id = "tokens:token-list"

    description = "API Token Management"

    #: Required permission for accessing the app
    app_permission = "tokens.access"
