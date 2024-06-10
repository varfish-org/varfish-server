from unittest.mock import MagicMock, patch

from django.conf import settings
from django.urls import reverse
from projectroles.tests.test_permissions_api import TestProjectAPIPermissionBase

from variants.models import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
    QuickPresets,
)
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


class ApiViewTestBase(TestProjectAPIPermissionBase):
    media_type = settings.SODAR_API_MEDIA_TYPE
    api_version = settings.SODAR_API_DEFAULT_VERSION

    def setUp(self):
        super().setUp()

        self.knox_token = self.get_token(self.superuser)


class TestFrequencyPresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory(presetset__project=self.project)
        self.presetset = self.frequencypresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-frequencypresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(FrequencyPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.frequencypresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-frequencypresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(FrequencyPresets.objects.count(), 2)


class TestFrequencyPresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory(presetset__project=self.project)
        self.presetset = self.frequencypresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-frequencypresets-retrieveupdatedestroy",
                    kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.frequencypresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(FrequencyPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.frequencypresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-frequencypresets-retrieveupdatedestroy",
                    kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(FrequencyPresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(FrequencyPresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-frequencypresets-retrieveupdatedestroy",
                    kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(FrequencyPresets.objects.count(), 0)


class TestFrequencyPresetsCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"presetset": self.presetset.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.FrequencyPresetsManager.create_as_copy_of_factory_preset",
            MagicMock(return_value=FrequencyPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-frequencypresets-clonefactorypresets",
                        kwargs={"name": "the-name"},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with("the-name", data["label"], self.presetset)


class TestFrequencyPresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.frequencypresets = FrequencyPresetsFactory(presetset=self.presetset)

    def test_post(self):
        data = {
            "frequencypresets": self.frequencypresets.sodar_uuid,
            "presetset": self.presetset.sodar_uuid,
            "label": "my label",
        }
        with patch(
            "variants.models.presets.FrequencyPresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=FrequencyPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-frequencypresets-cloneother",
                        kwargs={"frequencypresets": self.frequencypresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(
            self.frequencypresets, presetset=self.presetset, label=data["label"]
        )


class TestImpactPresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.impactpresets = ImpactPresetsFactory(presetset__project=self.project)
        self.presetset = self.impactpresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-impactpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(ImpactPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.impactpresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-impactpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(ImpactPresets.objects.count(), 2)


class TestImpactPresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.impactpresets = ImpactPresetsFactory(presetset__project=self.project)
        self.presetset = self.impactpresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-impactpresets-retrieveupdatedestroy",
                    kwargs={"impactpresets": self.impactpresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.impactpresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(ImpactPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.impactpresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-impactpresets-retrieveupdatedestroy",
                    kwargs={"impactpresets": self.impactpresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(ImpactPresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(ImpactPresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-impactpresets-retrieveupdatedestroy",
                    kwargs={"impactpresets": self.impactpresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ImpactPresets.objects.count(), 0)


class TestImpactPresetsCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"presetset": self.presetset.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.ImpactPresetsManager.create_as_copy_of_factory_preset",
            MagicMock(return_value=ImpactPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-impactpresets-clonefactorypresets",
                        kwargs={"name": "the-name"},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with("the-name", data["label"], self.presetset)


class TestImpactPresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.impactpresets = ImpactPresetsFactory(presetset=self.presetset)

    def test_post(self):
        data = {
            "impactpresets": self.impactpresets.sodar_uuid,
            "presetset": self.presetset.sodar_uuid,
            "label": "my label",
        }
        with patch(
            "variants.models.presets.ImpactPresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=ImpactPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-impactpresets-cloneother",
                        kwargs={"impactpresets": self.impactpresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(
            self.impactpresets, presetset=self.presetset, label=data["label"]
        )


class TestQualityPresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.qualitypresets = QualityPresetsFactory(presetset__project=self.project)
        self.presetset = self.qualitypresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-qualitypresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(QualityPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.qualitypresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-qualitypresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(QualityPresets.objects.count(), 2)


class TestQualityPresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.qualitypresets = QualityPresetsFactory(presetset__project=self.project)
        self.presetset = self.qualitypresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-qualitypresets-retrieveupdatedestroy",
                    kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.qualitypresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(QualityPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.qualitypresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-qualitypresets-retrieveupdatedestroy",
                    kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(QualityPresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(QualityPresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-qualitypresets-retrieveupdatedestroy",
                    kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(QualityPresets.objects.count(), 0)


class TestQualityPresetsCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"presetset": self.presetset.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.QualityPresetsManager.create_as_copy_of_factory_preset",
            MagicMock(return_value=QualityPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-qualitypresets-clonefactorypresets",
                        kwargs={"name": "the-name"},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with("the-name", data["label"], self.presetset)


class TestQualityPresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.qualitypresets = QualityPresetsFactory(presetset=self.presetset)

    def test_post(self):
        data = {
            "qualitypresets": self.qualitypresets.sodar_uuid,
            "presetset": self.presetset.sodar_uuid,
            "label": "my label",
        }
        with patch(
            "variants.models.presets.QualityPresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=QualityPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-qualitypresets-cloneother",
                        kwargs={"qualitypresets": self.qualitypresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(
            self.qualitypresets, presetset=self.presetset, label=data["label"]
        )


class TestChromosomePresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.chromosomepresets = ChromosomePresetsFactory(presetset__project=self.project)
        self.presetset = self.chromosomepresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-chromosomepresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(ChromosomePresets.objects.count(), 1)
        data = model_to_dict_for_api(self.chromosomepresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-chromosomepresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(ChromosomePresets.objects.count(), 2)


class TestChromosomePresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.chromosomepresets = ChromosomePresetsFactory(presetset__project=self.project)
        self.presetset = self.chromosomepresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-chromosomepresets-retrieveupdatedestroy",
                    kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.chromosomepresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(ChromosomePresets.objects.count(), 1)
        data = model_to_dict_for_api(self.chromosomepresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-chromosomepresets-retrieveupdatedestroy",
                    kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(ChromosomePresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(ChromosomePresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-chromosomepresets-retrieveupdatedestroy",
                    kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(ChromosomePresets.objects.count(), 0)


class TestChromosomePresetsCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"presetset": self.presetset.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.ChromosomePresetsManager.create_as_copy_of_factory_preset",
            MagicMock(return_value=ChromosomePresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-chromosomepresets-clonefactorypresets",
                        kwargs={"name": "the-name"},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with("the-name", data["label"], self.presetset)


class TestChromosomePresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.chromosomepresets = ChromosomePresetsFactory(presetset=self.presetset)

    def test_post(self):
        data = {
            "chromosomepresets": self.chromosomepresets.sodar_uuid,
            "presetset": self.presetset.sodar_uuid,
            "label": "my label",
        }
        with patch(
            "variants.models.presets.ChromosomePresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=ChromosomePresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-chromosomepresets-cloneother",
                        kwargs={"chromosomepresets": self.chromosomepresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(
            self.chromosomepresets, presetset=self.presetset, label=data["label"]
        )


class TestFlagsEtcPresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.flagsetcpresets = FlagsEtcPresetsFactory(presetset__project=self.project)
        self.presetset = self.flagsetcpresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-flagsetcpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.flagsetcpresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-flagsetcpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(FlagsEtcPresets.objects.count(), 2)


class TestFlagsEtcPresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.flagsetcpresets = FlagsEtcPresetsFactory(presetset__project=self.project)
        self.presetset = self.flagsetcpresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
                    kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.flagsetcpresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.flagsetcpresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
                    kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-flagsetcpresets-retrieveupdatedestroy",
                    kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(FlagsEtcPresets.objects.count(), 0)


class TestFlagsEtcPresetsCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"presetset": self.presetset.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.FlagsEtcPresetsManager.create_as_copy_of_factory_preset",
            MagicMock(return_value=FlagsEtcPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-flagsetcpresets-clonefactorypresets",
                        kwargs={"name": "the-name"},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with("the-name", data["label"], self.presetset)


class TestFlagsEtcPresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)
        self.flagsetcpresets = FlagsEtcPresetsFactory(presetset=self.presetset)

    def test_post(self):
        data = {
            "flagsetcpresets": self.flagsetcpresets.sodar_uuid,
            "presetset": self.presetset.sodar_uuid,
            "label": "my label",
        }
        with patch(
            "variants.models.presets.FlagsEtcPresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=FlagsEtcPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-flagsetcpresets-cloneother",
                        kwargs={"flagsetcpresets": self.flagsetcpresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(
            self.flagsetcpresets, presetset=self.presetset, label=data["label"]
        )


class TestQuickPresetsListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)
        self.presetset = self.quickpresets.presetset

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-quickpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["presetset"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(QuickPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.quickpresets)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-quickpresets-listcreate",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(QuickPresets.objects.count(), 2)


class TestQuickPresetsRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)
        self.presetset = self.quickpresets.presetset

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-quickpresets-retrieveupdatedestroy",
                    kwargs={"quickpresets": self.quickpresets.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.quickpresets.sodar_uuid))

    def test_update(self):
        self.assertEqual(QuickPresets.objects.count(), 1)
        data = model_to_dict_for_api(self.quickpresets)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-quickpresets-retrieveupdatedestroy",
                    kwargs={"quickpresets": self.quickpresets.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["presetset"], str(self.presetset.sodar_uuid))
        self.assertEqual(QuickPresets.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(QuickPresets.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-quickpresets-retrieveupdatedestroy",
                    kwargs={"quickpresets": self.quickpresets.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(QuickPresets.objects.count(), 0)


class TestQuickPresetsCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory(presetset__project=self.project)

    def test_post(self):
        data = {"label": "my label"}
        with patch(
            "variants.models.presets.QuickPresetsManager.create_as_copy_of_other_preset",
            MagicMock(return_value=QuickPresetsFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-quickpresets-cloneother",
                        kwargs={"quickpresets": self.quickpresets.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(self.quickpresets, label=data["label"])


class TestPresetSetListCreateAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_list(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-presetset-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["sodar_uuid"], str(self.presetset.sodar_uuid))

    def test_create(self):
        self.assertEqual(PresetSet.objects.count(), 1)
        data = model_to_dict_for_api(self.presetset)
        with self.login(self.superuser):
            response = self.client.post(
                reverse(
                    "variants:ajax-presetset-listcreate",
                    kwargs={"project": self.project.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(PresetSet.objects.count(), 2)


class TestPresetSetListAllAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_listall(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-presetset-listall",
                )
            )
        self.assertEqual(response.status_code, 200)
        self.maxDiff = None
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["sodar_uuid"], str(self.presetset.sodar_uuid))


class TestPresetSetRetrieveUpdateDestroyAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_retrieve(self):
        with self.login(self.superuser):
            response = self.client.get(
                reverse(
                    "variants:ajax-presetset-retrieveupdatedestroy",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                )
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["sodar_uuid"], str(self.presetset.sodar_uuid))

    def test_update(self):
        self.assertEqual(PresetSet.objects.count(), 1)
        data = model_to_dict_for_api(self.presetset)
        with self.login(self.superuser):
            response = self.client.patch(
                reverse(
                    "variants:ajax-presetset-retrieveupdatedestroy",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
                data=data,
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project"], str(self.project.sodar_uuid))
        self.assertEqual(PresetSet.objects.count(), 1)

    def test_delete(self):
        self.assertEqual(PresetSet.objects.count(), 1)
        with self.login(self.superuser):
            response = self.client.delete(
                reverse(
                    "variants:ajax-presetset-retrieveupdatedestroy",
                    kwargs={"presetset": self.presetset.sodar_uuid},
                ),
            )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(PresetSet.objects.count(), 0)


class TestPresetSetCloneFactoryPresetsAjaxView(ApiViewTestBase):
    def test_post(self):
        data = {"project": self.project.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.PresetSetManager.create_as_copy_of_factory_preset_set",
            MagicMock(return_value=PresetSetFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-presetset-clonefactorypresets",
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(project=self.project, label=data["label"])


class TestPresetSetCloneOtherAjaxView(ApiViewTestBase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory(project=self.project)

    def test_post(self):
        data = {"project": self.project.sodar_uuid, "label": "my label"}
        with patch(
            "variants.models.presets.PresetSetManager.create_as_copy_of_other_preset_set",
            MagicMock(return_value=PresetSetFactory.build()),
        ) as mock_create:
            with self.login(self.superuser):
                response = self.client.post(
                    reverse(
                        "variants:ajax-presetset-cloneother",
                        kwargs={"presetset": self.presetset.sodar_uuid},
                    ),
                    data=data,
                )
        self.assertEqual(response.status_code, 201)
        mock_create.assert_called_with(self.presetset, project=self.project, label=data["label"])
