"""Tests for the module ``svs.views.ajax.presets``."""

from django.urls import reverse
from projectroles.app_settings import AppSettingAPI

from variants.tests.factories import CaseFactory
from variants.tests.helpers import ApiViewTestBase


class InhouseCarriersProjectSettingsMixin:
    """Configure distinct in-house carrier thresholds per genome build for ``self.project``."""

    def set_inhouse_carriers_project_settings(self):
        app_settings = AppSettingAPI()
        for name, value in (
            ("sv_inhouse_carriers_strict_37", 1),
            ("sv_inhouse_carriers_relaxed_37", 10),
            ("sv_inhouse_carriers_strict_38", 7),
            ("sv_inhouse_carriers_relaxed_38", 70),
        ):
            app_settings.set("variants", name, value, project=self.project)


class TestSvFrequencyPresetsAjaxView(InhouseCarriersProjectSettingsMixin, ApiViewTestBase):
    def get_frequency_presets(self, case):
        url = reverse("svs:ajax-frequency-presets", kwargs={"case": case.sodar_uuid})
        with self.login(self.superuser):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_get_factory_defaults(self):
        case = CaseFactory(project=self.project, release="GRCh38")

        res_json = self.get_frequency_presets(case)

        self.assertEqual(set(res_json), {"any", "strict", "relaxed"})
        self.assertEqual(res_json["strict"]["svdb_inhouse_max_count"], 5)
        self.assertEqual(res_json["relaxed"]["svdb_inhouse_max_count"], 30)
        self.assertIsNone(res_json["any"]["svdb_inhouse_max_count"])

    def test_get_project_settings_grch37(self):
        self.set_inhouse_carriers_project_settings()
        case = CaseFactory(project=self.project, release="GRCh37")

        res_json = self.get_frequency_presets(case)

        self.assertEqual(res_json["strict"]["svdb_inhouse_max_count"], 1)
        self.assertEqual(res_json["relaxed"]["svdb_inhouse_max_count"], 10)
        self.assertIsNone(res_json["any"]["svdb_inhouse_max_count"])

    def test_get_project_settings_grch38(self):
        self.set_inhouse_carriers_project_settings()
        case = CaseFactory(project=self.project, release="GRCh38")

        res_json = self.get_frequency_presets(case)

        self.assertEqual(res_json["strict"]["svdb_inhouse_max_count"], 7)
        self.assertEqual(res_json["relaxed"]["svdb_inhouse_max_count"], 70)
        self.assertIsNone(res_json["any"]["svdb_inhouse_max_count"])


class TestSvQuerySettingsShortcutAjaxView(InhouseCarriersProjectSettingsMixin, ApiViewTestBase):
    def get_query_settings(self, case, quick_preset):
        url = reverse("svs:ajax-svquerysettings-shortcut", kwargs={"case": case.sodar_uuid})
        with self.login(self.superuser):
            response = self.client.get(url, {"quick_preset": quick_preset})
        self.assertEqual(response.status_code, 200)
        return response.json()["query_settings"]

    def test_get_factory_defaults(self):
        case = CaseFactory(project=self.project, release="GRCh38")

        query_settings = self.get_query_settings(case, "defaults")

        self.assertEqual(query_settings["svdb_inhouse_max_count"], 5)

    def test_get_project_settings_strict(self):
        self.set_inhouse_carriers_project_settings()
        case = CaseFactory(project=self.project, release="GRCh38")

        query_settings = self.get_query_settings(case, "defaults")

        self.assertEqual(query_settings["svdb_inhouse_max_count"], 7)

    def test_get_project_settings_relaxed(self):
        self.set_inhouse_carriers_project_settings()
        case = CaseFactory(project=self.project, release="GRCh37")

        query_settings = self.get_query_settings(case, "de_novo_high_quality")

        self.assertEqual(query_settings["svdb_inhouse_max_count"], 10)
