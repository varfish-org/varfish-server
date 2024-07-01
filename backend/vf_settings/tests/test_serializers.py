from dataclasses import asdict

from test_plus import TestCase

from variants.tests.factories import ProjectFactory
from vf_settings.serializers import (
    AllSettingsSerializer,
    ProjectSettingsSerializer,
    ProjectUserSettingsSerializer,
    SiteSettingsSerializer,
    UserSettingsSerializer,
)
from vf_settings.settings_api import SettingsAPI


class TestSiteSettingsSerializer(TestCase):
    """Test the SiteSettingsSerializer."""

    def setUp(self):
        super().setUp()
        self.settings_api = SettingsAPI()

    def test_serialize_existing(self):
        expected = asdict(self.settings_api.get_scope_settings())
        serializer = SiteSettingsSerializer(expected)
        self.assertDictEqual(serializer.data, expected)


class TestProjectSettingsSerializer(TestCase):
    """Test the ProjectSettingsSerializer."""

    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.settings_api = SettingsAPI(project=self.project)

    def test_serialize_existing(self):
        expected = asdict(self.settings_api.get_scope_settings())
        serializer = ProjectSettingsSerializer(expected)
        self.assertDictEqual(serializer.data, expected)


class TestProjectUserSettingsSerializer(TestCase):
    """Test the ProjectUserSettingsSerializer."""

    def setUp(self):
        super().setUp()
        self.user = self.make_user("testuser")
        self.project = ProjectFactory()
        self.settings_api = SettingsAPI(project=self.project, user=self.user)

    def test_serialize_existing(self):
        expected = asdict(self.settings_api.get_scope_settings())
        serializer = ProjectUserSettingsSerializer(expected)
        self.assertDictEqual(serializer.data, expected)


class TestUserSettingsSerializer(TestCase):
    """Test the UserSettingsSerializer."""

    def setUp(self):
        super().setUp()
        self.user = self.make_user("testuser")
        self.settings_api = SettingsAPI(user=self.user)

    def test_serialize_existing(self):
        expected = asdict(self.settings_api.get_scope_settings())
        serializer = UserSettingsSerializer(expected)
        self.assertDictEqual(serializer.data, expected)


class TestAllSettingsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.user = self.make_user("testuser")
        self.project = ProjectFactory()

    def test_serialize_existing(self):
        settings_api_site = SettingsAPI()
        settings_api_project = SettingsAPI(project=self.project)
        settings_api_project_user = SettingsAPI(project=self.project, user=self.user)
        settings_api_user = SettingsAPI(user=self.user)

        expected = {
            **asdict(settings_api_site.get_scope_settings()),
            **asdict(settings_api_project.get_scope_settings()),
            **asdict(settings_api_project_user.get_scope_settings()),
            **asdict(settings_api_user.get_scope_settings()),
        }

        serializer = AllSettingsSerializer(expected)
        self.assertDictEqual(serializer.data, expected)
