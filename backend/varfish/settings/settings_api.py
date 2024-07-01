from dataclasses import asdict, dataclass, fields

from projectroles.app_settings import AppSettingAPI

app_settings = AppSettingAPI()


@dataclass
class SiteSettings:
    pass


@dataclass
class ProjectSettings:
    user_defined_tags: str
    disable_pedigree_sex_check: bool
    exclude_from_inhouse_db: bool
    ts_tv_valid_range: str


@dataclass
class ProjectUserSettings:
    pass


@dataclass
class UserSettings:
    umd_predictor_api_token: str
    ga4gh_beacon_network_widget_enabled: bool
    latest_version_seen_changelog: str


SITE_SETTINGS_CLASS = SiteSettings
SITE_SETTINGS_SUFFIX = "__site"

PROJECT_SETTINGS_CLASS = ProjectSettings
PROJECT_SETTINGS_SUFFIX = "__project"

PROJECT_USER_SETTINGS_CLASS = ProjectUserSettings
PROJECT_USER_SETTINGS_SUFFIX = "__project_user"

USER_SETTINGS_CLASS = UserSettings
USER_SETTINGS_SUFFIX = "__user"


def get_settings_class(scope):
    if scope == "SITE":
        return SITE_SETTINGS_CLASS
    elif scope == "PROJECT":
        return PROJECT_SETTINGS_CLASS
    elif scope == "PROJECT_USER":
        return PROJECT_USER_SETTINGS_CLASS
    elif scope == "USER":
        return USER_SETTINGS_CLASS
    return None


def get_settings_suffix(scope):
    if scope == "SITE":
        return SITE_SETTINGS_SUFFIX
    elif scope == "PROJECT":
        return PROJECT_SETTINGS_SUFFIX
    elif scope == "PROJECT_USER":
        return PROJECT_USER_SETTINGS_SUFFIX
    elif scope == "USER":
        return USER_SETTINGS_SUFFIX
    return None


class SettingsAPI:
    """API for settings."""

    def __init__(self, scope, project=None, user=None):
        self.scope = scope
        self.project = project
        self.user = user
        self.settings_class = get_settings_class(scope)
        self.suffix = get_settings_suffix(scope)
        self.definitions = self._get_definitions()

    def _get_definitions(self):
        result = {}

        for app_name, settings in app_settings.get_all_defs().items():
            for setting, setting_data in settings.items():
                if setting.endswith(self.suffix):
                    result[setting[: -len(self.suffix)]] = {
                        **setting_data,
                        "app_name": app_name,
                        "internal_name": setting,
                    }

        return result

    def get_settings(self):
        result = {}

        for setting, setting_data in self.definitions.items():
            result[setting] = app_settings.get(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.project,
                user=self.user,
            )

        return self.settings_class(**result)

    def set_settings(self, settings):
        defaults = self.get_default_settings()
        obj = self.settings_class(**{**asdict(defaults), **settings})

        for k, v in asdict(obj).items():
            if k in settings:
                app_settings.set(
                    self.definitions[k]["app_name"],
                    self.definitions[k]["internal_name"],
                    v,
                    project=self.project,
                    user=self.user,
                )

    def get_default_settings(self):
        result = {}

        for setting, setting_data in self.definitions.items():
            result[setting] = app_settings.get_default(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.project,
                user=self.user,
            )

        return self.settings_class(**result)

    def reset_settings(self):
        for setting_data in self.definitions.values():
            app_settings.delete(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.project,
                user=self.user,
            )
