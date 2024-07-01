from dataclasses import asdict

from test_plus import TestCase

from variants.tests.factories import ProjectFactory
from vf_settings.settings_api import (
    AllSettings,
    ProjectSettings,
    ProjectUserSettings,
    SettingsAPI,
    SiteSettings,
    UserSettings,
    lt,
)
from vf_settings.tests.factories import (
    PROJECT_DEFINITIONS,
    PROJECT_SETTINGS_A,
    PROJECT_USER_DEFINITIONS,
    PROJECT_USER_SETTINGS_A,
    SITE_DEFINITIONS,
    SITE_SETTINGS_A,
    USER_DEFINITIONS,
    USER_SETTINGS_A,
    get_all_defaults,
    get_all_defaults_no_project,
    get_project_defaults,
    get_project_user_defaults,
    get_site_defaults,
    get_user_defaults,
)


class TestSettingsApi(TestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.user = self.make_user("testuser")

    #
    # Tests for `get_settings_class`
    #

    def test_get_settings_class_project(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertEqual(settings_api.get_settings_class(), ProjectSettings)

    def test_get_settings_class_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        self.assertEqual(settings_api.get_settings_class(), ProjectUserSettings)

    def test_get_settings_class_user(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertEqual(settings_api.get_settings_class(), UserSettings)

    def test_get_settings_class_site(self):
        settings_api = SettingsAPI()
        self.assertEqual(settings_api.get_settings_class(), SiteSettings)

    #
    # Tests for `get_settings_suffix`
    #

    def test_get_settings_suffix_project(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertEqual(settings_api.get_settings_suffix(), "__project")

    def test_get_settings_suffix_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        self.assertEqual(settings_api.get_settings_suffix(), "__project_user")

    def test_get_settings_suffix_user(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertEqual(settings_api.get_settings_suffix(), "__user")

    def test_get_settings_suffix_site(self):
        settings_api = SettingsAPI()
        self.assertEqual(settings_api.get_settings_suffix(), "__site")

    def test_get_project_suffix_project(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertEqual(settings_api.get_project("project"), self.project)

    def test_get_project_suffix_project_user(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertEqual(settings_api.get_project("project_user"), self.project)

    def test_get_project_suffix_none(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertEqual(settings_api.get_project(), self.project)

    def test_get_project_suffix_other(self):
        settings_api = SettingsAPI(project=self.project)
        self.assertIsNone(settings_api.get_project("other"))

    def test_get_user_suffix_none(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertEqual(settings_api.get_user(), self.user)

    def test_get_user_suffix_project_user(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertEqual(settings_api.get_user("project_user"), self.user)

    def test_get_user_suffix_user(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertEqual(settings_api.get_user("user"), self.user)

    def test_get_user_suffix_other(self):
        settings_api = SettingsAPI(user=self.user)
        self.assertIsNone(settings_api.get_user("other"))

    #
    # Test for `get_scope_definitions`
    #

    def test_get_scope_definitions_site(self):
        settings_api = SettingsAPI()
        expected = SITE_DEFINITIONS
        definitions = settings_api.get_scope_definitions()
        for key in expected:
            self.assertIn(key, definitions)
            self.assertEqual(definitions[key]["app_name"], expected[key]["app_name"])
            self.assertEqual(definitions[key]["internal_name"], expected[key]["internal_name"])

    def test_get_scope_definitions_project(self):
        settings_api = SettingsAPI(project=self.project)
        expected = PROJECT_DEFINITIONS
        definitions = settings_api.get_scope_definitions()
        for key in expected:
            self.assertIn(key, definitions)
            self.assertEqual(definitions[key]["app_name"], expected[key]["app_name"])
            self.assertEqual(definitions[key]["internal_name"], expected[key]["internal_name"])

    def test_get_scope_definitions_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        expected = PROJECT_USER_DEFINITIONS
        definitions = settings_api.get_scope_definitions()
        for key in expected:
            self.assertIn(key, definitions)
            self.assertEqual(definitions[key]["app_name"], expected[key]["app_name"])
            self.assertEqual(definitions[key]["internal_name"], expected[key]["internal_name"])

    def test_get_scope_definitions_user(self):
        settings_api = SettingsAPI(user=self.user)
        expected = USER_DEFINITIONS
        definitions = settings_api.get_scope_definitions()
        for key in expected:
            self.assertIn(key, definitions)
            self.assertEqual(definitions[key]["app_name"], expected[key]["app_name"])
            self.assertEqual(definitions[key]["internal_name"], expected[key]["internal_name"])

    #
    # Tests for `get_scope_settings`
    #

    def test_get_scope_settings_site(self):
        settings_api = SettingsAPI()
        expected = SiteSettings(**get_site_defaults())
        self.assertEqual(settings_api.get_scope_settings(), expected)

    def test_get_scope_settings_project(self):
        settings_api = SettingsAPI(project=self.project)
        expected = ProjectSettings(**get_project_defaults(self.project))
        self.assertEqual(settings_api.get_scope_settings(), expected)

    def test_get_scope_settings_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        expected = ProjectUserSettings(**get_project_user_defaults(self.project, self.user))
        self.assertEqual(settings_api.get_scope_settings(), expected)

    def test_get_scope_settings_user(self):
        settings_api = SettingsAPI(user=self.user)
        expected = UserSettings(**get_user_defaults(self.user))
        self.assertEqual(settings_api.get_scope_settings(), expected)

    #
    # Tests for `set_scope_settings`
    #

    def test_set_scope_settings_site(self):
        settings_api = SettingsAPI()
        new_settings = SITE_SETTINGS_A
        settings_api.set_scope_settings(new_settings)
        result = settings_api.get_scope_settings()
        self.assertEqual(asdict(result), new_settings)

    def test_set_scope_settings_project(self):
        settings_api = SettingsAPI(project=self.project)
        new_settings = PROJECT_SETTINGS_A
        settings_api.set_scope_settings(new_settings)
        result = settings_api.get_scope_settings()
        self.assertEqual(asdict(result), new_settings)

    def test_set_scope_settings_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        new_settings = PROJECT_USER_SETTINGS_A
        settings_api.set_scope_settings(new_settings)
        result = settings_api.get_scope_settings()
        self.assertEqual(asdict(result), new_settings)

    def test_set_scope_settings_user(self):
        settings_api = SettingsAPI(user=self.user)
        new_settings = USER_SETTINGS_A
        settings_api.set_scope_settings(new_settings)
        result = settings_api.get_scope_settings()
        self.assertEqual(asdict(result), new_settings)

    #
    # Tests for `get_scope_default_settings`
    #

    def test_get_scope_default_settings_site(self):
        settings_api = SettingsAPI()
        expected = SiteSettings(**get_site_defaults())
        self.assertEqual(settings_api.get_scope_default_settings(), expected)

    def test_get_scope_default_settings_project(self):
        settings_api = SettingsAPI(project=self.project)
        expected = ProjectSettings(**get_project_defaults(self.project))
        self.assertEqual(settings_api.get_scope_default_settings(), expected)

    def test_get_scope_default_settings_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        expected = ProjectUserSettings(**get_project_user_defaults(self.project, self.user))
        self.assertEqual(settings_api.get_scope_default_settings(), expected)

    def test_get_scope_default_settings_user(self):
        settings_api = SettingsAPI(user=self.user)
        expected = UserSettings(**get_user_defaults(self.user))
        self.assertEqual(settings_api.get_scope_default_settings(), expected)

    #
    # Tests for `get_reset_scope_settings`
    #

    def test_reset_scope_settings_site(self):
        settings_api = SettingsAPI()
        settings_api.set_scope_settings(SITE_SETTINGS_A)
        settings_api.reset_scope_settings()
        expected = get_site_defaults()
        self.assertEqual(asdict(settings_api.get_scope_settings()), expected)

    def test_reset_scope_settings_project(self):
        settings_api = SettingsAPI(project=self.project)
        settings_api.set_scope_settings(PROJECT_SETTINGS_A)
        settings_api.reset_scope_settings()
        expected = get_project_defaults(self.project)
        self.assertEqual(asdict(settings_api.get_scope_settings()), expected)

    def test_reset_scope_settings_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        settings_api.set_scope_settings(PROJECT_USER_SETTINGS_A)
        settings_api.reset_scope_settings()
        expected = get_project_user_defaults(self.project, self.user)
        self.assertEqual(asdict(settings_api.get_scope_settings()), expected)

    def test_reset_scope_settings_user(self):
        settings_api = SettingsAPI(user=self.user)
        settings_api.set_scope_settings(USER_SETTINGS_A)
        settings_api.reset_scope_settings()
        expected = get_user_defaults(self.user)
        self.assertEqual(asdict(settings_api.get_scope_settings()), expected)

    #
    # Tests for `get_all_settings`
    #

    def test_get_all_settings_defaults(self):
        settings_api = SettingsAPI()
        expected = AllSettings(**get_all_defaults_no_project(self.user))
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_with_project(self):
        settings_api = SettingsAPI(project=self.project)
        new_settings = {
            "user_defined_tags": "test",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults(self.project, self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_with_user(self):
        settings_api = SettingsAPI(user=self.user)
        new_settings = {
            "umd_predictor_api_token": "TOKEN",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults_no_project(self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_param_set_for_project(self):
        settings_api = SettingsAPI(project=self.project)
        new_settings = {
            "test_param": "test",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults(self.project, self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_param_set_for_project_user(self):
        settings_api = SettingsAPI(project=self.project, user=self.user)
        new_settings = {
            "test_param": "test",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults(self.project, self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_param_set_for_user(self):
        settings_api = SettingsAPI(user=self.user)
        new_settings = {
            "test_param": "test",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults_no_project(self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    def test_get_all_settings_param_set_for_site(self):
        settings_api = SettingsAPI()
        new_settings = {
            "test_param": "test",
        }
        settings_api.set_scope_settings(new_settings)
        expected = AllSettings(
            **{
                **get_all_defaults_no_project(self.user),
                **new_settings,
            }
        )
        self.assertEqual(settings_api.get_all_settings(), expected)

    #
    # Tests for `lt` method
    #

    def test_lt_site(self):
        self.assertTrue(lt("site", "user"))
        self.assertTrue(lt("site", "project"))
        self.assertTrue(lt("site", "project_user"))

    def test_lt_user(self):
        self.assertFalse(lt("user", "site"))
        self.assertTrue(lt("user", "project"))
        self.assertTrue(lt("user", "project_user"))

    def test_lt_project(self):
        self.assertFalse(lt("project", "site"))
        self.assertFalse(lt("project", "user"))
        self.assertTrue(lt("project", "project_user"))

    def test_lt_project_user(self):
        self.assertFalse(lt("project_user", "site"))
        self.assertFalse(lt("project_user", "user"))
        self.assertFalse(lt("project_user", "project"))
