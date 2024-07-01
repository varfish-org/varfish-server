from dataclasses import asdict, dataclass

from projectroles.app_settings import AppSetting, AppSettingAPI

app_settings = AppSettingAPI()


@dataclass
class SiteSettings:
    """Data class for site settings."""

    test_param: str


@dataclass
class ProjectSettings:
    """Data class for roject settings."""

    user_defined_tags: str
    disable_pedigree_sex_check: bool
    exclude_from_inhouse_db: bool
    ts_tv_valid_range: str
    test_param: str


@dataclass
class ProjectUserSettings:
    """Data class for project user settings."""

    test_param: str


@dataclass
class UserSettings:
    """Data class for user settings."""

    umd_predictor_api_token: str
    ga4gh_beacon_network_widget_enabled: bool
    latest_version_seen_changelog: str
    test_param: str


@dataclass
class AllSettings(SiteSettings, ProjectSettings, ProjectUserSettings, UserSettings):
    """Data class for all settings combined."""


SUFFIX_SITE = "site"
SUFFIX_PROJECT = "project"
SUFFIX_PROJECT_USER = "project_user"
SUFFIX_USER = "user"


def lt(obj1, obj2):
    """Test if obj1 is lower (less worth) in hierachy than obj2.

    The hierarchy is defined as:

        site < user < project < project_user
    """

    if obj1 == obj2:
        return False

    return (
        obj1 == SUFFIX_SITE
        or obj2 == SUFFIX_PROJECT_USER
        or (obj1 == SUFFIX_USER and obj2 == SUFFIX_PROJECT)
    )


class SettingsAPI:
    """API for settings."""

    def __init__(self, project=None, user=None):
        self._project = project
        self._user = user
        self.definitions = self.get_scope_definitions()

    def get_settings_class(self):
        if self.get_project() and self.get_user():
            return ProjectUserSettings
        elif self.get_project():
            return ProjectSettings
        elif self.get_user():
            return UserSettings

        return SiteSettings

    def get_settings_suffix(self):
        if self.get_project() and self.get_user():
            suffix = SUFFIX_PROJECT_USER
        elif self.get_project():
            suffix = SUFFIX_PROJECT
        elif self.get_user():
            suffix = SUFFIX_USER
        else:
            suffix = SUFFIX_SITE

        return f"__{suffix}"

    def get_project(self, suffix=None):
        if suffix in (None, SUFFIX_PROJECT, SUFFIX_PROJECT_USER):
            return self._project

        return None

    def get_user(self, suffix=None):
        if suffix in (None, SUFFIX_USER, SUFFIX_PROJECT_USER):
            return self._user

        return None

    def get_scope_definitions(self):
        result = {}

        for app_name, settings in app_settings.get_all_defs().items():
            for setting, setting_data in settings.items():
                if setting.endswith(self.get_settings_suffix()):
                    result[setting[: -len(self.get_settings_suffix())]] = {
                        **setting_data,
                        "app_name": app_name,
                        "internal_name": setting,
                    }

        return result

    def get_scope_settings(self):
        result = {}

        for setting, setting_data in self.definitions.items():
            result[setting] = app_settings.get(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.get_project(),
                user=self.get_user(),
            )

        return self.get_settings_class()(**result)

    def set_scope_settings(self, settings):
        defaults = self.get_scope_default_settings()
        obj = self.get_settings_class()(**{**asdict(defaults), **settings})

        for k, v in asdict(obj).items():
            if k in settings:
                app_settings.set(
                    self.definitions[k]["app_name"],
                    self.definitions[k]["internal_name"],
                    v,
                    project=self.get_project(),
                    user=self.get_user(),
                )

    def get_scope_default_settings(self):
        result = {}

        for setting, setting_data in self.definitions.items():
            result[setting] = app_settings.get_default(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.get_project(),
                user=self.get_user(),
            )

        return self.get_settings_class()(**result)

    def reset_scope_settings(self):
        for setting_data in self.definitions.values():
            app_settings.delete(
                setting_data["app_name"],
                setting_data["internal_name"],
                project=self.get_project(),
                user=self.get_user(),
            )

    def get_all_settings(self):
        """
        This methods returns all settings combined across all scopes and the value is determined by
        the following cascade:

            site < user < project < project_user

        Explanation:
        - A site setting is set by the admins.
        - A user can override this setting, if available in the users scope.
        - A project setting is set by the project owner or delegate, is specific to a project and
          overrides site and user settings, in case the setting is shared in both scopes.
        - A user can override this setting for a specific project if available in the users scope.
        """
        result = {}
        suffixes_in_results = {}
        parameters = {}

        for app_name, settings in app_settings.get_all_defs().items():
            for setting in settings.keys():
                if setting.endswith(
                    tuple(
                        f"__{s}"
                        for s in (SUFFIX_SITE, SUFFIX_PROJECT, SUFFIX_PROJECT_USER, SUFFIX_USER)
                    )
                ):
                    setting_pre, suffix = setting.rsplit("__", 1)
                    if not setting_pre in parameters:
                        parameters[setting_pre] = []
                    parameters[setting_pre].append((app_name, setting))
                    suffix_in_result = suffixes_in_results.get(setting_pre)
                    # is_set = AppSetting.objects.filter(
                    #     app_plugin__name=app_name,
                    #     name=setting,
                    #     project=self.get_project(suffix),
                    #     user=self.get_user(suffix),
                    # ).exists()

                    if suffix_in_result is None or lt(suffix_in_result, suffix):
                        suffixes_in_results[setting_pre] = suffix
                        result[setting_pre] = app_settings.get(
                            app_name,
                            setting,
                            project=self.get_project(suffix),
                            user=self.get_user(suffix),
                        )

        return AllSettings(**result)
