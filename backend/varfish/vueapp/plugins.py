# Projectroles dependency
from projectroles.plugins import SiteAppPluginPoint


class SiteAppPlugin(SiteAppPluginPoint):
    """Projectroles plugin for registering the app"""

    #: Name (slug-safe, used in URLs)
    name = "vueapp"

    #: Title (used in templates)
    title = "Vueapp Settings"

    #: App URLs (will be included in settings by djangoplugins)
    urls = []

    #: FontAwesome icon ID string
    icon = "mdi:syllabary-hiragana"

    #: Description string
    description = "Vueapp settings"

    #: Entry point URL ID
    entry_point_url_id = "home"

    #: Required permission for displaying the app
    app_permission = "varfish.vueapp.nonexisting"

    app_settings = {
        "filtration_inline_help": {
            "label": "Variant Filtration Inline Help",
            "scope": "USER",
            "type": "BOOLEAN",
            "default": True,
            "description": "Show inline help in filtration forms",
            "user_modifiable": True,
            "local": True,
        },
        "filtration_complexity_mode": {
            "label": "Variant Filtration UI Complexity",
            "scope": "USER",
            "type": "STRING",
            "options": ["simple", "normal", "advanced", "dev"],
            "default": "simple",
            "description": "Select complexity of filtration control",
            "user_modifiable": True,
            "local": True,
        },
    }

    def get_messages(self, user=None):
        _ = user
        return []
