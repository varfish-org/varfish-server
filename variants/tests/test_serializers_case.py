from django.forms import model_to_dict
from test_plus import TestCase

from variants.models.presets import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
)
from variants.serializers import CaseSerializer
from variants.serializers.presets import (
    ChromosomePresetsSerializer,
    FlagsEtcPresetsSerializer,
    FrequencyPresetsSerializer,
    ImpactPresetsSerializer,
    PresetSetSerializer,
    QualityPresetsSerializer,
    QuickPresetsSerializer,
)
from variants.tests.factories import (
    CaseFactory,
    ChromosomePresetsFactory,
    FlagsEtcPresetsFactory,
    FrequencyPresetsFactory,
    ImpactPresetsFactory,
    PresetSetFactory,
    ProjectFactory,
    QualityPresetsFactory,
    QuickPresetsFactory,
)


def fixup_pedigree(pedigree):
    """Convert 'patient' fields back into 'name' in pedigree."""
    # TODO: can go away after renaming
    return [{{"patient": "name"}.get(k, k): v for k, v in m.items()} for m in pedigree]


class TestCaseSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.project = ProjectFactory()
        self.presetset = PresetSetFactory(project=self.project)
        self.case = CaseFactory(project=self.project, presetset=self.presetset)

    def test_create_with_empty_presetset(self):
        data = model_to_dict(CaseFactory.build(project=self.project), exclude="presetset")
        data["pedigree"] = fixup_pedigree(data["pedigree"])
        serializer = CaseSerializer(
            data=data, context={"project": self.project, "release": "GRCh37"}
        )
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.case.refresh_from_db()
        self.assertIsNone(instance.presetset)

    def test_create_with_nonempty_presetset(self):
        data = model_to_dict(CaseFactory.build(project=self.project), exclude="presetset")
        data["pedigree"] = fixup_pedigree(data["pedigree"])
        data["presetset"] = self.presetset.sodar_uuid
        serializer = CaseSerializer(
            data=data, context={"project": self.project, "release": "GRCh37"}
        )
        self.assertTrue(serializer.is_valid())
        instance = serializer.save()
        self.case.refresh_from_db()
        self.assertEquals(instance.presetset.sodar_uuid, self.presetset.sodar_uuid)

    def test_update_with_empty_presetset(self):
        serializer = CaseSerializer(self.case, data={"presetset": None}, partial=True)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.case.refresh_from_db()
        self.assertIsNone(self.case.presetset)

    def test_with_with_nonempty_presetset(self):
        presetset_other = PresetSetFactory(project=self.project)
        serializer = CaseSerializer(
            self.case, data={"presetset": str(presetset_other.sodar_uuid)}, partial=True
        )
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.case.refresh_from_db()
        self.assertEquals(self.case.presetset.sodar_uuid, presetset_other.sodar_uuid)
