from django.conf import settings
from django.forms import model_to_dict
from test_plus import TestCase

from variants.models.presets import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    QualityPresets,
)
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
    ChromosomePresetsFactory,
    FlagsEtcPresetsFactory,
    FrequencyPresetsFactory,
    ImpactPresetsFactory,
    PresetSetFactory,
    QualityPresetsFactory,
    QuickPresetsFactory,
)

TIMEF = settings.REST_FRAMEWORK["DATETIME_FORMAT"]


class TestFrequencyPresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory()

    def _model_to_dict_frequencypresets(self, frequencypresets, **kwargs):
        expected = model_to_dict(frequencypresets, exclude=("id",))
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["presetset"] = frequencypresets.presetset.sodar_uuid
        expected["date_created"] = frequencypresets.date_created.strftime(TIMEF)
        expected["date_modified"] = frequencypresets.date_modified.strftime(TIMEF)
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = FrequencyPresetsSerializer(self.frequencypresets)
        expected = self._model_to_dict_frequencypresets(self.frequencypresets)
        self.maxDiff = None
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_frequencypresets(self.frequencypresets),
            "label": "my new preset",
        }
        serializer = FrequencyPresetsSerializer(
            data=data, context={"presetset": self.frequencypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_frequencypresets(result)
        expected = self._model_to_dict_frequencypresets(
            self.frequencypresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_frequencypresets = FrequencyPresetsFactory(presetset=self.frequencypresets.presetset)
        data = {
            **self._model_to_dict_frequencypresets(other_frequencypresets),
            "label": "my new preset",
        }
        serializer = FrequencyPresetsSerializer(
            data=data, context={"presetset": self.frequencypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_frequencypresets(result)
        expected = self._model_to_dict_frequencypresets(
            other_frequencypresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)


class TestImpactPresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.impactpresets = ImpactPresetsFactory()

    def _model_to_dict_impactpresets(self, impactpresets, **kwargs):
        expected = model_to_dict(impactpresets, exclude=("id",))
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["presetset"] = impactpresets.presetset.sodar_uuid
        expected["date_created"] = impactpresets.date_created.strftime(TIMEF)
        expected["date_modified"] = impactpresets.date_modified.strftime(TIMEF)
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = ImpactPresetsSerializer(self.impactpresets)
        expected = self._model_to_dict_impactpresets(self.impactpresets)
        self.maxDiff = None
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_impactpresets(self.impactpresets),
            "label": "my new preset",
        }
        serializer = ImpactPresetsSerializer(
            data=data, context={"presetset": self.impactpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_impactpresets(result)
        expected = self._model_to_dict_impactpresets(
            self.impactpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_impactpresets = ImpactPresetsFactory(presetset=self.impactpresets.presetset)
        data = {
            **self._model_to_dict_impactpresets(other_impactpresets),
            "label": "my new preset",
        }
        serializer = ImpactPresetsSerializer(
            data=data, context={"presetset": self.impactpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_impactpresets(result)
        expected = self._model_to_dict_impactpresets(
            other_impactpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)


class TestQualityPresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.qualitypresets = QualityPresetsFactory()

    def _model_to_dict_qualitypresets(self, qualitypresets, **kwargs):
        expected = model_to_dict(qualitypresets, exclude=("id",))
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["presetset"] = qualitypresets.presetset.sodar_uuid
        expected["date_created"] = qualitypresets.date_created.strftime(TIMEF)
        expected["date_modified"] = qualitypresets.date_modified.strftime(TIMEF)
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = QualityPresetsSerializer(self.qualitypresets)
        expected = self._model_to_dict_qualitypresets(self.qualitypresets)
        self.maxDiff = None
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_qualitypresets(self.qualitypresets),
            "label": "my new preset",
        }
        serializer = QualityPresetsSerializer(
            data=data, context={"presetset": self.qualitypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_qualitypresets(result)
        expected = self._model_to_dict_qualitypresets(
            self.qualitypresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_qualitypresets = QualityPresetsFactory(presetset=self.qualitypresets.presetset)
        data = {
            **self._model_to_dict_qualitypresets(other_qualitypresets),
            "label": "my new preset",
        }
        serializer = QualityPresetsSerializer(
            data=data, context={"presetset": self.qualitypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_qualitypresets(result)
        expected = self._model_to_dict_qualitypresets(
            other_qualitypresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)


class TestChromosomePresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.chromosomepresets = ChromosomePresetsFactory()

    def _model_to_dict_chromosomepresets(self, chromosomepresets, **kwargs):
        expected = model_to_dict(chromosomepresets, exclude=("id",))
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["presetset"] = chromosomepresets.presetset.sodar_uuid
        expected["date_created"] = chromosomepresets.date_created.strftime(TIMEF)
        expected["date_modified"] = chromosomepresets.date_modified.strftime(TIMEF)
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = ChromosomePresetsSerializer(self.chromosomepresets)
        expected = self._model_to_dict_chromosomepresets(self.chromosomepresets)
        self.maxDiff = None
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_chromosomepresets(self.chromosomepresets),
            "label": "my new preset",
        }
        serializer = ChromosomePresetsSerializer(
            data=data, context={"presetset": self.chromosomepresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_chromosomepresets(result)
        expected = self._model_to_dict_chromosomepresets(
            self.chromosomepresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_chromosomepresets = ChromosomePresetsFactory(
            presetset=self.chromosomepresets.presetset
        )
        data = {
            **self._model_to_dict_chromosomepresets(other_chromosomepresets),
            "label": "my new preset",
        }
        serializer = ChromosomePresetsSerializer(
            data=data, context={"presetset": self.chromosomepresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_chromosomepresets(result)
        expected = self._model_to_dict_chromosomepresets(
            other_chromosomepresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)


class TestFlagsEtcPresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.flagsetcpresets = FlagsEtcPresetsFactory()

    def _model_to_dict_flagsetcpresets(self, flagsetcpresets, **kwargs):
        expected = model_to_dict(flagsetcpresets, exclude=("id",))
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["presetset"] = flagsetcpresets.presetset.sodar_uuid
        expected["date_created"] = flagsetcpresets.date_created.strftime(TIMEF)
        expected["date_modified"] = flagsetcpresets.date_modified.strftime(TIMEF)
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = FlagsEtcPresetsSerializer(self.flagsetcpresets)
        expected = self._model_to_dict_flagsetcpresets(self.flagsetcpresets)
        self.maxDiff = None
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_flagsetcpresets(self.flagsetcpresets),
            "label": "my new preset",
        }
        serializer = FlagsEtcPresetsSerializer(
            data=data, context={"presetset": self.flagsetcpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_flagsetcpresets(result)
        expected = self._model_to_dict_flagsetcpresets(
            self.flagsetcpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_flagsetcpresets = FlagsEtcPresetsFactory(presetset=self.flagsetcpresets.presetset)
        data = {
            **self._model_to_dict_flagsetcpresets(other_flagsetcpresets),
            "label": "my new preset",
        }
        serializer = FlagsEtcPresetsSerializer(
            data=data, context={"presetset": self.flagsetcpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_flagsetcpresets(result)
        expected = self._model_to_dict_flagsetcpresets(
            other_flagsetcpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)


class TestQuickPresetsSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.quickpresets = QuickPresetsFactory()

    def _model_to_dict_quickpreset(self, quickpresets, **kwargs):
        expected = model_to_dict(quickpresets, exclude=("id",))
        expected["presetset"] = quickpresets.presetset.sodar_uuid
        expected["date_created"] = quickpresets.date_created.strftime(TIMEF)
        expected["date_modified"] = quickpresets.date_modified.strftime(TIMEF)
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        expected["frequency"] = FrequencyPresets.objects.get(pk=expected["frequency"]).sodar_uuid
        expected["impact"] = ImpactPresets.objects.get(pk=expected["impact"]).sodar_uuid
        expected["quality"] = QualityPresets.objects.get(pk=expected["quality"]).sodar_uuid
        expected["chromosome"] = ChromosomePresets.objects.get(pk=expected["chromosome"]).sodar_uuid
        expected["flagsetc"] = FlagsEtcPresets.objects.get(pk=expected["flagsetc"]).sodar_uuid
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = QuickPresetsSerializer(self.quickpresets)
        expected = self._model_to_dict_quickpreset(self.quickpresets)
        self.assertDictEqual(serializer.data, expected)

    def test_create(self):
        data = {
            "label": "my new preset",
            "inheritance": self.quickpresets.inheritance,
            "frequency": self.quickpresets.frequency.sodar_uuid,
            "impact": self.quickpresets.impact.sodar_uuid,
            "quality": self.quickpresets.quality.sodar_uuid,
            "chromosome": self.quickpresets.chromosome.sodar_uuid,
            "flagsetc": self.quickpresets.flagsetc.sodar_uuid,
        }
        serializer = QuickPresetsSerializer(
            data=data, context={"presetset": self.quickpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_quickpreset(result)
        expected = self._model_to_dict_quickpreset(
            self.quickpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        other_presetset = PresetSetFactory()
        other_quickpresets = QuickPresetsFactory(presetset=self.quickpresets.presetset)
        data = {
            "label": "my new preset",
            "presetset": other_presetset.sodar_uuid,
            "inheritance": self.quickpresets.inheritance,
            "frequency": self.quickpresets.frequency.sodar_uuid,
            "impact": self.quickpresets.impact.sodar_uuid,
            "quality": self.quickpresets.quality.sodar_uuid,
            "chromosome": self.quickpresets.chromosome.sodar_uuid,
            "flagsetc": self.quickpresets.flagsetc.sodar_uuid,
        }
        serializer = QuickPresetsSerializer(
            data=data, context={"presetset": other_quickpresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_quickpreset(result)
        expected = self._model_to_dict_quickpreset(
            self.quickpresets,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update_fail_validation(self):
        other_presetset = PresetSetFactory()
        data = {
            "label": "my new preset",
            "inheritance": self.quickpresets.inheritance,
            "frequency": self.quickpresets.frequency.sodar_uuid,
            "impact": self.quickpresets.impact.sodar_uuid,
            "quality": self.quickpresets.quality.sodar_uuid,
            "chromosome": self.quickpresets.chromosome.sodar_uuid,
            "flagsetc": self.quickpresets.flagsetc.sodar_uuid,
        }
        serializer = QuickPresetsSerializer(data=data, context={"presetset": other_presetset})
        self.assertFalse(serializer.is_valid())
        self.assertTrue("non_field_errors" in serializer.errors)


class TestPresetSetSerializer(TestCase):
    def setUp(self):
        super().setUp()
        self.presetset = PresetSetFactory()

    def _model_to_dict_presetset(self, presetset, **kwargs):
        expected = model_to_dict(
            presetset, exclude=("id", "state", "version_major", "version_minor", "signed_off_by")
        )
        expected["project"] = presetset.project.sodar_uuid
        expected["date_created"] = presetset.date_created.strftime(TIMEF)
        expected["date_modified"] = presetset.date_modified.strftime(TIMEF)
        expected["sodar_uuid"] = str(expected["sodar_uuid"])
        return {**expected, **kwargs}

    def test_serialize_existing(self):
        serializer = PresetSetSerializer(self.presetset)
        expected = self._model_to_dict_presetset(self.presetset)
        actual = dict(**serializer.data)
        for field in list(actual.keys()):
            if field.endswith("_set"):
                actual.pop(field)
        self.assertDictEqual(actual, expected)

    def test_create(self):
        data = {
            **self._model_to_dict_presetset(self.presetset),
            "label": "my new preset set",
        }
        serializer = PresetSetSerializer(data=data, context={"project": self.presetset.project})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_presetset(result)
        expected = self._model_to_dict_presetset(
            self.presetset,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset set",
        )
        self.assertDictEqual(result_dict, expected)

    def test_update(self):
        data = {
            "label": "my new preset set",
            "database": "refseq",
        }
        serializer = PresetSetSerializer(data=data, context={"project": self.presetset.project})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()
        result_dict = self._model_to_dict_presetset(result)
        expected = self._model_to_dict_presetset(
            self.presetset,
            date_created=result.date_created.strftime(TIMEF),
            date_modified=result.date_modified.strftime(TIMEF),
            sodar_uuid=str(result.sodar_uuid),
            label="my new preset set",
            database="refseq",
        )
        self.assertDictEqual(result_dict, expected)


class TestFrequencyPresetsEmptyStringHandling(TestCase):
    """Test that FrequencyPresetsSerializer handles empty strings correctly."""

    def setUp(self):
        super().setUp()
        self.frequencypresets = FrequencyPresetsFactory()

    def test_empty_string_converts_to_none(self):
        """Test that empty strings in integer fields are converted to None."""
        data = model_to_dict(self.frequencypresets, exclude=("id",))
        data["sodar_uuid"] = str(data["sodar_uuid"])
        data["presetset"] = self.frequencypresets.presetset.sodar_uuid
        data["date_created"] = self.frequencypresets.date_created.strftime(TIMEF)
        data["date_modified"] = self.frequencypresets.date_modified.strftime(TIMEF)
        data["label"] = "test empty strings"
        # Set frequency fields to empty strings
        data["thousand_genomes_homozygous"] = ""
        data["thousand_genomes_heterozygous"] = ""
        data["exac_frequency"] = ""

        serializer = FrequencyPresetsSerializer(
            data=data, context={"presetset": self.frequencypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()

        # Verify empty strings were converted to None
        self.assertIsNone(result.thousand_genomes_homozygous)
        self.assertIsNone(result.thousand_genomes_heterozygous)
        self.assertIsNone(result.exac_frequency)

    def test_invalid_string_raises_validation_error(self):
        """Test that non-empty invalid strings raise validation errors."""
        data = model_to_dict(self.frequencypresets, exclude=("id",))
        data["sodar_uuid"] = str(data["sodar_uuid"])
        data["presetset"] = self.frequencypresets.presetset.sodar_uuid
        data["date_created"] = self.frequencypresets.date_created.strftime(TIMEF)
        data["date_modified"] = self.frequencypresets.date_modified.strftime(TIMEF)
        data["label"] = "test invalid strings"
        # Set frequency fields to invalid strings
        data["thousand_genomes_homozygous"] = "not-a-number"

        serializer = FrequencyPresetsSerializer(
            data=data, context={"presetset": self.frequencypresets.presetset}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("thousand_genomes_homozygous", serializer.errors)

    def test_valid_integer_string_converts_correctly(self):
        """Test that valid integer strings are converted to integers."""
        data = model_to_dict(self.frequencypresets, exclude=("id",))
        data["sodar_uuid"] = str(data["sodar_uuid"])
        data["presetset"] = self.frequencypresets.presetset.sodar_uuid
        data["date_created"] = self.frequencypresets.date_created.strftime(TIMEF)
        data["date_modified"] = self.frequencypresets.date_modified.strftime(TIMEF)
        data["label"] = "test valid strings"
        # Set frequency fields to valid string representations
        data["thousand_genomes_homozygous"] = "10"
        data["exac_frequency"] = "0.05"

        serializer = FrequencyPresetsSerializer(
            data=data, context={"presetset": self.frequencypresets.presetset}
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        result = serializer.save()

        # Verify strings were converted to proper types
        self.assertEqual(result.thousand_genomes_homozygous, 10)
        self.assertEqual(result.exac_frequency, 0.05)
