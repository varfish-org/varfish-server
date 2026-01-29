from django.forms import model_to_dict
from test_plus.test import TestCase

from variants.tests.factories import (
    ChromosomePresetsFactory,
    FlagsEtcPresetsFactory,
    FrequencyPresetsFactory,
    ImpactPresetsFactory,
    PresetSetFactory,
    ProjectFactory,
    QualityPresetsFactory,
    QuickPresetsFactory,
)

from ..models import (
    ChromosomePresets,
    FlagsEtcPresets,
    FrequencyPresets,
    ImpactPresets,
    PresetSet,
    QualityPresets,
    QuickPresets,
)


class TestPresetSet(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        PresetSetFactory()
        self.assertEqual(PresetSet.objects.count(), 1)

    def test_create_as_copy_of_factory_preset_set(self):
        project = ProjectFactory()
        PresetSet.objects.create_as_copy_of_factory_preset_set(
            project=project,
            label="my presets",
        )
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(FrequencyPresets.objects.count(), 6)
        self.assertEqual(ImpactPresets.objects.count(), 5)
        self.assertEqual(QualityPresets.objects.count(), 4)
        self.assertEqual(ChromosomePresets.objects.count(), 5)
        self.assertEqual(FlagsEtcPresets.objects.count(), 3)
        self.assertEqual(QuickPresets.objects.count(), 10)

    def test_create_as_copy_of_other_preset(self):
        project = ProjectFactory()
        presetset = PresetSet.objects.create_as_copy_of_factory_preset_set(
            project=project,
            label="my presets",
        )
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(FrequencyPresets.objects.count(), 6)
        self.assertEqual(ImpactPresets.objects.count(), 5)
        self.assertEqual(QualityPresets.objects.count(), 4)
        self.assertEqual(ChromosomePresets.objects.count(), 5)
        self.assertEqual(FlagsEtcPresets.objects.count(), 3)
        self.assertEqual(QuickPresets.objects.count(), 10)

        PresetSet.objects.create_as_copy_of_other_preset_set(presetset)

        self.assertEqual(PresetSet.objects.count(), 2)
        self.assertEqual(FrequencyPresets.objects.count(), 12)
        self.assertEqual(ImpactPresets.objects.count(), 10)
        self.assertEqual(QualityPresets.objects.count(), 8)
        self.assertEqual(ChromosomePresets.objects.count(), 10)
        self.assertEqual(FlagsEtcPresets.objects.count(), 6)
        self.assertEqual(QuickPresets.objects.count(), 20)

    def test_clone_does_not_copy_default_presetset(self):
        """Test that cloning a preset set with default_presetset=True creates a copy with default_presetset=False."""
        project = ProjectFactory()
        # Create a preset set and mark it as default
        original_presetset = PresetSet.objects.create_as_copy_of_factory_preset_set(
            project=project,
            label="original presets",
        )
        original_presetset.default_presetset = True
        original_presetset.save()

        # Clone the preset set
        cloned_presetset = PresetSet.objects.create_as_copy_of_other_preset_set(original_presetset)

        # Verify original still has default_presetset=True
        original_presetset.refresh_from_db()
        self.assertTrue(original_presetset.default_presetset)

        # Verify clone has default_presetset=False
        self.assertFalse(cloned_presetset.default_presetset)

    def test_clone_preserves_other_fields(self):
        """Test that cloning preserves all other fields except excluded ones."""
        project = ProjectFactory()
        original_presetset = PresetSet.objects.create_as_copy_of_factory_preset_set(
            project=project,
            label="original presets",
        )
        original_presetset.default_presetset = True
        original_presetset.database = "refseq"
        original_presetset.save()

        # Clone the preset set
        cloned_presetset = PresetSet.objects.create_as_copy_of_other_preset_set(original_presetset)

        # Verify database field is preserved
        self.assertEqual(cloned_presetset.database, "refseq")
        # Verify project is preserved
        self.assertEqual(cloned_presetset.project, project)
        # Verify default_presetset is NOT preserved
        self.assertFalse(cloned_presetset.default_presetset)
        # Verify sodar_uuid is different
        self.assertNotEqual(cloned_presetset.sodar_uuid, original_presetset.sodar_uuid)


class TestFrequencyPresets(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(FrequencyPresets.objects.count(), 0)
        FrequencyPresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(FrequencyPresets.objects.count(), 1)

    def test_create_as_copy_of_factory_preset(self):
        presetset = PresetSetFactory()
        result = FrequencyPresets.objects.create_as_copy_of_factory_preset(
            "any", "new-any", presetset
        )
        result = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            "label": "new-any",
            "thousand_genomes_enabled": False,
            "thousand_genomes_homozygous": None,
            "thousand_genomes_heterozygous": None,
            "thousand_genomes_hemizygous": None,
            "thousand_genomes_frequency": None,
            "exac_enabled": False,
            "exac_homozygous": None,
            "exac_heterozygous": None,
            "exac_hemizygous": None,
            "exac_frequency": None,
            "gnomad_exomes_enabled": False,
            "gnomad_exomes_homozygous": None,
            "gnomad_exomes_heterozygous": None,
            "gnomad_exomes_hemizygous": None,
            "gnomad_exomes_frequency": None,
            "gnomad_genomes_enabled": False,
            "gnomad_genomes_homozygous": None,
            "gnomad_genomes_heterozygous": None,
            "gnomad_genomes_hemizygous": None,
            "gnomad_genomes_frequency": None,
            "inhouse_enabled": False,
            "inhouse_homozygous": None,
            "inhouse_heterozygous": None,
            "inhouse_hemizygous": None,
            "inhouse_carriers": None,
            "mtdb_enabled": False,
            "mtdb_count": None,
            "mtdb_frequency": None,
            "helixmtdb_enabled": False,
            "helixmtdb_het_count": None,
            "helixmtdb_hom_count": None,
            "helixmtdb_frequency": None,
            "mitomap_enabled": False,
            "mitomap_count": None,
            "mitomap_frequency": None,
        }
        self.assertDictEqual(result, expected)

    def test_create_as_copy_of_other_preset(self):
        presetset_0 = PresetSetFactory()
        presetset_1 = PresetSetFactory()
        freq_presets = FrequencyPresetsFactory(presetset=presetset_0)
        result = FrequencyPresets.objects.create_as_copy_of_other_preset(
            freq_presets, presetset_1, label="mycopy"
        )
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, presetset_1.pk)


class TestImpactPresetsFactory(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(ImpactPresets.objects.count(), 0)
        ImpactPresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(ImpactPresets.objects.count(), 1)

    def test_create_as_copy_of_factory_preset(self):
        self.maxDiff = None
        presetset = PresetSetFactory()
        result = ImpactPresets.objects.create_as_copy_of_factory_preset(
            "null_variant", "new-null_variant", presetset
        )
        result = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            "label": "new-null_variant",
            "var_type_snv": True,
            "var_type_mnv": True,
            "var_type_indel": True,
            "transcripts_coding": True,
            "transcripts_noncoding": False,
            "max_exon_dist": None,
            "effects": [
                "exon_loss_variant",
                "feature_elongation",
                "feature_truncation",
                "frameshift_elongation",
                "frameshift_truncation",
                "frameshift_variant",
                "internal_feature_elongation",
                "splice_acceptor_variant",
                "splice_donor_variant",
                "start_lost",
                "stop_gained",
                "stop_lost",
                "structural_variant",
                "transcript_ablation",
                "transcript_amplification",
            ],
        }
        self.assertDictEqual(result, expected)

    def test_create_as_copy_of_other_preset(self):
        presetset_0 = PresetSetFactory()
        presetset_1 = PresetSetFactory()
        impact_presets = ImpactPresetsFactory(presetset=presetset_0)
        result = ImpactPresets.objects.create_as_copy_of_other_preset(
            impact_presets, presetset_1, label="mycopy"
        )
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, presetset_1.pk)


class TestQualityPresetsFactory(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(QualityPresets.objects.count(), 0)
        QualityPresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(QualityPresets.objects.count(), 1)

    def test_create_as_copy_of_factory_preset(self):
        presetset = PresetSetFactory()
        result = QualityPresets.objects.create_as_copy_of_factory_preset(
            "super_strict", "new-super_strict", presetset
        )
        result = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            "label": "new-super_strict",
            "dp_het": 10,
            "dp_hom": 5,
            "ab": 0.3,
            "gq": 30,
            "ad": 3,
            "ad_max": None,
            "fail": "drop-variant",
        }
        self.assertDictEqual(result, expected)

    def test_create_as_copy_of_other_preset(self):
        presetset_0 = PresetSetFactory()
        presetset_1 = PresetSetFactory()
        quality_presets = QualityPresetsFactory(presetset=presetset_0)
        result = QualityPresets.objects.create_as_copy_of_other_preset(
            quality_presets, presetset_1, label="mycopy"
        )
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, presetset_1.pk)


class TestChromosomePresets(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(ChromosomePresets.objects.count(), 0)
        ChromosomePresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(ChromosomePresets.objects.count(), 1)

    def test_create_as_copy_of_factory_preset(self):
        presetset = PresetSetFactory()
        result = ChromosomePresets.objects.create_as_copy_of_factory_preset(
            "whole_genome", "new-whole_genome", presetset
        )
        result = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            "label": "new-whole_genome",
            "genomic_region": [],
            "gene_allowlist": [],
            "gene_blocklist": [],
        }
        self.assertDictEqual(result, expected)

    def test_create_as_copy_of_other_preset(self):
        presetset_0 = PresetSetFactory()
        presetset_1 = PresetSetFactory()
        chromosome_presets = ChromosomePresetsFactory(presetset=presetset_0)
        result = ChromosomePresets.objects.create_as_copy_of_other_preset(
            chromosome_presets, presetset_1, label="mycopy"
        )
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, presetset_1.pk)


class TestFlagsEtcPresetsFactory(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(FlagsEtcPresets.objects.count(), 0)
        FlagsEtcPresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)

    def test_create_as_copy_of_factory_preset(self):
        presetset = PresetSetFactory()
        result = FlagsEtcPresets.objects.create_as_copy_of_factory_preset(
            "defaults", "new-defaults", presetset
        )
        result = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            "label": "new-defaults",
            "clinvar_include_benign": False,
            "clinvar_include_likely_benign": False,
            "clinvar_include_likely_pathogenic": True,
            "clinvar_include_pathogenic": True,
            "clinvar_include_uncertain_significance": False,
            "clinvar_exclude_conflicting": False,
            "flag_bookmarked": True,
            "flag_incidental": True,
            "flag_candidate": True,
            "flag_doesnt_segregate": True,
            "flag_final_causative": True,
            "flag_for_validation": True,
            "flag_no_disease_association": True,
            "flag_molecular_empty": True,
            "flag_molecular_negative": True,
            "flag_molecular_positive": True,
            "flag_molecular_uncertain": True,
            "flag_phenotype_match_empty": True,
            "flag_phenotype_match_negative": True,
            "flag_phenotype_match_positive": True,
            "flag_phenotype_match_uncertain": True,
            "flag_segregates": True,
            "flag_simple_empty": True,
            "flag_summary_empty": True,
            "flag_summary_negative": True,
            "flag_summary_positive": True,
            "flag_summary_uncertain": True,
            "flag_validation_empty": True,
            "flag_validation_negative": True,
            "flag_validation_positive": True,
            "flag_validation_uncertain": True,
            "flag_visual_empty": True,
            "flag_visual_negative": True,
            "flag_visual_positive": True,
            "flag_visual_uncertain": True,
            "require_in_clinvar": False,
            "clinvar_paranoid_mode": False,
        }
        self.assertDictEqual(result, expected)

    def test_create_as_copy_of_other_preset(self):
        presetset_0 = PresetSetFactory()
        presetset_1 = PresetSetFactory()
        flags_presets = QualityPresetsFactory(presetset=presetset_0)
        result = FlagsEtcPresets.objects.create_as_copy_of_other_preset(
            flags_presets, presetset_1, label="mycopy"
        )
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, presetset_1.pk)


class TestQuickPresets(TestCase):
    def test_instantiate_smoke_test(self):
        self.assertEqual(PresetSet.objects.count(), 0)
        self.assertEqual(FrequencyPresets.objects.count(), 0)
        self.assertEqual(ImpactPresets.objects.count(), 0)
        self.assertEqual(QualityPresets.objects.count(), 0)
        self.assertEqual(ChromosomePresets.objects.count(), 0)
        self.assertEqual(FlagsEtcPresets.objects.count(), 0)
        self.assertEqual(QuickPresets.objects.count(), 0)
        QuickPresetsFactory()
        self.assertEqual(PresetSet.objects.count(), 1)
        self.assertEqual(FrequencyPresets.objects.count(), 1)
        self.assertEqual(ImpactPresets.objects.count(), 1)
        self.assertEqual(QualityPresets.objects.count(), 1)
        self.assertEqual(ChromosomePresets.objects.count(), 1)
        self.assertEqual(FlagsEtcPresets.objects.count(), 1)
        self.assertEqual(QuickPresets.objects.count(), 1)

    def test_create_as_copy_of_other_preset(self):
        quick_presets = QuickPresetsFactory()
        result = QuickPresets.objects.create_as_copy_of_other_preset(quick_presets, label="mycopy")
        result_dict = model_to_dict(
            result, exclude=("id", "sodar_uuid", "date_created", "date_modified", "presetset")
        )
        expected = {
            **result_dict,
            "label": "mycopy",
        }
        self.assertDictEqual(result_dict, expected)
        self.assertEqual(result.presetset.pk, quick_presets.presetset.pk)
