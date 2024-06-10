from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.models import QuickPresets
from variants.tests.factories import (
    ChromosomePresetsFactory,
    FlagsEtcPresetsFactory,
    FrequencyPresetsFactory,
    ImpactPresetsFactory,
    PresetSetFactory,
    QualityPresetsFactory,
    QuickPresetsFactory,
)
from variants.tests.utils import model_to_dict_for_api


class TestFrequencyPresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory(presetset__project=self.project)
        self.presetset = self.frequencypresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-frequencypresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-frequencypresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.frequencypresets)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestFrequencyPresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-frequencypresets-retrieveupdatedestroy",
            kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-frequencypresets-retrieveupdatedestroy",
            kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-frequencypresets-retrieveupdatedestroy",
            kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            frequencypresets = FrequencyPresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-frequencypresets-retrieveupdatedestroy",
                    kwargs={"frequencypresets": frequencypresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestFrequencyPresetsCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-frequencypresets-clonefactorypresets", kwargs={"name": "dominant_strict"}
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestFrequencyPresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.frequencypreset = FrequencyPresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-frequencypresets-cloneother",
            kwargs={"frequencypresets": self.frequencypreset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.frequencypreset.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestImpactPresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.impactpresets = ImpactPresetsFactory(presetset__project=self.project)
        self.presetset = self.impactpresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-impactpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-impactpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.impactpresets)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestImpactPresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.impactpresets = ImpactPresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-impactpresets-retrieveupdatedestroy",
            kwargs={"impactpresets": self.impactpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-impactpresets-retrieveupdatedestroy",
            kwargs={"impactpresets": self.impactpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-impactpresets-retrieveupdatedestroy",
            kwargs={"impactpresets": self.impactpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            impactpresets = ImpactPresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-impactpresets-retrieveupdatedestroy",
                    kwargs={"impactpresets": impactpresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestImpactPresetsCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-impactpresets-clonefactorypresets", kwargs={"name": "null_variant"}
        )
        good_users = [
            self.superuser,
            self.user_owner,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestImpactPresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.impactpreset = ImpactPresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-impactpresets-cloneother",
            kwargs={"impactpresets": self.impactpreset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.impactpreset.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestQualityPresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.qualitypresets = QualityPresetsFactory(presetset__project=self.project)
        self.presetset = self.qualitypresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-qualitypresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-qualitypresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.qualitypresets)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestQualityPresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.qualitypresets = QualityPresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-qualitypresets-retrieveupdatedestroy",
            kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-qualitypresets-retrieveupdatedestroy",
            kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-qualitypresets-retrieveupdatedestroy",
            kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            qualitypresets = QualityPresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-qualitypresets-retrieveupdatedestroy",
                    kwargs={"qualitypresets": qualitypresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestQualityPresetsCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse("variants:ajax-qualitypresets-clonefactorypresets", kwargs={"name": "strict"})
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestQualityPresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.qualitypreset = QualityPresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-qualitypresets-cloneother",
            kwargs={"qualitypresets": self.qualitypreset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.qualitypreset.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestChromosomePresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.chromosomepresets = ChromosomePresetsFactory(presetset__project=self.project)
        self.presetset = self.chromosomepresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-chromosomepresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-chromosomepresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.chromosomepresets)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestChromosomePresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.chromosomepresets = ChromosomePresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-chromosomepresets-retrieveupdatedestroy",
            kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-chromosomepresets-retrieveupdatedestroy",
            kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-chromosomepresets-retrieveupdatedestroy",
            kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            chromosomepresets = ChromosomePresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-chromosomepresets-retrieveupdatedestroy",
                    kwargs={"chromosomepresets": chromosomepresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestChromosomePresetsCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-chromosomepresets-clonefactorypresets", kwargs={"name": "whole_genome"}
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestChromosomePresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.chromosomepreset = ChromosomePresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-chromosomepresets-cloneother",
            kwargs={"chromosomepresets": self.chromosomepreset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.chromosomepreset.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestFlagsEtcPresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.flagsetcpresets = FlagsEtcPresetsFactory(presetset__project=self.project)
        self.presetset = self.flagsetcpresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.flagsetcpresets)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestFlagsEtcPresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.flagsetcpresets = FlagsEtcPresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
            kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
            kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
            kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            flagsetcpresets = FlagsEtcPresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
                    kwargs={"flagsetcpresets": flagsetcpresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestFlagsEtcPresetsCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-clonefactorypresets", kwargs={"name": "defaults"}
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestFlagsEtcPresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.flagsetcpreset = FlagsEtcPresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-flagsetcpresets-cloneother",
            kwargs={"flagsetcpresets": self.flagsetcpreset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "presetset": self.flagsetcpreset.presetset.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestQuickPresetsListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)
        self.presetset = self.quickpresets.presetset

    def test_list(self):
        url = reverse(
            "variants:ajax-quickpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-quickpresets-listcreate",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {
            "presetset": str(self.presetset.sodar_uuid),
            "label": "my quick presets",
            "inheritance": "de_novo",
            "frequency": str(self.quickpresets.frequency.sodar_uuid),
            "impact": str(self.quickpresets.impact.sodar_uuid),
            "quality": str(self.quickpresets.quality.sodar_uuid),
            "chromosome": str(self.quickpresets.chromosome.sodar_uuid),
            "flagsetc": str(self.quickpresets.flagsetc.sodar_uuid),
        }
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestQuickPresetsRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-quickpresets-retrieveupdatedestroy",
            kwargs={"quickpresets": self.quickpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-quickpresets-retrieveupdatedestroy",
            kwargs={"quickpresets": self.quickpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-quickpresets-retrieveupdatedestroy",
            kwargs={"quickpresets": self.quickpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            quickpresets = QuickPresetsFactory(presetset__project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-quickpresets-retrieveupdatedestroy",
                    kwargs={"quickpresets": quickpresets.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestQuickPresetsCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-quickpresets-cloneother",
            kwargs={"quickpresets": self.quickpresets.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets"}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)

    def get_queryset(self):
        return QuickPresets.objects.all()

    def get_project(self, *args, **kwargs):
        return QuickPresets.objects.get(sodar_uuid=self.kwargs["sodar_uuid"]).presetset.project


class TestPresetSetListCreateAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_list(self):
        url = reverse(
            "variants:ajax-presetset-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_create(self):
        url = reverse(
            "variants:ajax-presetset-listcreate",
            kwargs={"project": self.project.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = model_to_dict_for_api(self.presetset)
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestPresetSetListAllAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_listall(self):
        url = reverse(
            "variants:ajax-presetset-listall",
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
            self.user_no_roles,
        ]
        bad_users_401 = []
        bad_users_302 = [self.anonymous]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_302, 302, method="GET")


class TestPresetSetRetrieveUpdateDestroyAjaxView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_retrieve(self):
        url = reverse(
            "variants:ajax-presetset-retrieveupdatedestroy",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
            self.user_guest,
        ]
        bad_users_401 = []
        bad_users_403 = [self.anonymous, self.user_no_roles]
        self.assert_response(url, good_users, 200, method="GET")
        self.assert_response(url, bad_users_401, 401, method="GET")
        self.assert_response(url, bad_users_403, 403, method="GET")

    def test_update(self):
        url = reverse(
            "variants:ajax-presetset-retrieveupdatedestroy",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        self.assert_response(url, good_users, 200, method="PATCH")
        self.assert_response(url, bad_users_401, 401, method="PATCH")
        self.assert_response(url, bad_users_403, 403, method="PATCH")

    def test_destroy(self):
        url = reverse(
            "variants:ajax-presetset-retrieveupdatedestroy",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        for user in good_users:
            presetset = PresetSetFactory(project=self.project)
            self.assert_response(
                reverse(
                    "variants:ajax-presetset-retrieveupdatedestroy",
                    kwargs={"presetset": presetset.sodar_uuid},
                ),
                [user],
                204,
                method="DELETE",
            )
        self.assert_response(url, bad_users_401, 401, method="DELETE")
        self.assert_response(url, bad_users_403, 403, method="DELETE")


class TestPresetSetCloneFactoryDefaultsView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-presetset-clonefactorypresets",
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets", "project": self.presetset.project.sodar_uuid}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)


class TestPresetSetCloneOtherView(TestProjectAPIPermissionBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        url = reverse(
            "variants:ajax-presetset-cloneother",
            kwargs={"presetset": self.presetset.sodar_uuid},
        )
        good_users = [
            self.superuser,
            self.owner_as.user,
            self.user_delegate,
            self.user_contributor,
        ]
        bad_users_401 = []
        bad_users_403 = [
            self.anonymous,
            self.user_no_roles,
            self.user_guest,
        ]
        data = {"label": "my new presets"}
        self.assert_response(url, good_users, 201, method="POST", data=data)
        self.assert_response(url, bad_users_401, 401, method="POST", data=data)
        self.assert_response(url, bad_users_403, 403, method="POST", data=data)
