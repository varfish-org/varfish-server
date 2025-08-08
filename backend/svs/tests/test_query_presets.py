"""Tests for the ``svs.query_presets`` module."""

from snapshottest.unittest import TestCase as TestCaseSnapshot
from test_plus.test import TestCase

from svs import query_presets
from svs.query_presets import GT_CRITERIA_DEFAULT, GT_CRITERIA_HIGH, GT_CRITERIA_PASS
from variants.tests.test_query_presets import PedigreesMixin


class TestEnumFrequency(TestCaseSnapshot, TestCase):
    maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.Frequency.ANY.value, "any")
        self.assertEqual(query_presets.Frequency.STRICT.value, "strict")
        self.assertEqual(query_presets.Frequency.RELAXED.value, "relaxed")
        self.assertEqual(query_presets.Frequency.CUSTOM.value, "custom")

    def testToSettingsAny(self):
        self.assertMatchSnapshot(
            query_presets.Frequency.ANY.to_settings(),
        )

    def testToSettingsStrict(self):
        self.assertMatchSnapshot(
            query_presets.Frequency.STRICT.to_settings(),
        )

    def testToSettingsRelaxed(self):
        self.assertMatchSnapshot(
            query_presets.Frequency.RELAXED.to_settings(),
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Frequency.CUSTOM.to_settings()


class TestEnumSvtype(TestCaseSnapshot, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.SvType.ANY.value, "any")
        self.assertEqual(query_presets.SvType.CNVS_LARGE.value, "cnvs_large")
        self.assertEqual(query_presets.SvType.CNVS_EXTRA_LARGE.value, "cnvs_extra_large")

    def testToSettingsAny(self):
        self.assertMatchSnapshot(
            query_presets.SvType.ANY.to_settings(),
        )

    def testToSettingsCnvsLarge(self):
        self.assertMatchSnapshot(
            query_presets.SvType.CNVS_LARGE.to_settings(),
        )

    def testToSettingsCnvsExtraLarge(self):
        self.assertMatchSnapshot(
            query_presets.SvType.CNVS_EXTRA_LARGE.to_settings(),
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.SvType.CUSTOM.to_settings()


class TestEnumImpact(TestCaseSnapshot, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.Impact.ANY.value, "any")
        self.assertEqual(query_presets.Impact.NEAR_GENE.value, "near_gene")
        self.assertEqual(query_presets.Impact.EXONIC.value, "exonic")

    def testToSettingsAny(self):
        self.assertMatchSnapshot(
            query_presets.Impact.ANY.to_settings(),
        )

    def testToSettingsNearGene(self):
        self.assertMatchSnapshot(
            query_presets.Impact.NEAR_GENE.to_settings(),
        )

    def testToSettingsExonic(self):
        self.assertMatchSnapshot(
            query_presets.Impact.EXONIC.to_settings(),
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Impact.CUSTOM.to_settings()


class TestEnumChromosomes(TestCaseSnapshot, TestCase):
    maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.Chromosomes.WHOLE_GENOME.value, "whole_genome")
        self.assertEqual(query_presets.Chromosomes.AUTOSOMES.value, "autosomes")
        self.assertEqual(query_presets.Chromosomes.X_CHROMOSOME.value, "x_chromosome")
        self.assertEqual(query_presets.Chromosomes.Y_CHROMOSOME.value, "y_chromosome")
        self.assertEqual(query_presets.Chromosomes.MT_CHROMOSOME.value, "mt_chromosome")
        self.assertEqual(query_presets.Chromosomes.CUSTOM.value, "custom")

    def testToSettingsWholeGenome(self):
        self.assertEqual(
            query_presets.Chromosomes.WHOLE_GENOME.to_settings(),
            {"genomic_region": [], "gene_allowlist": []},
        )

    def testToSettingsAutosomes(self):
        self.assertMatchSnapshot(
            query_presets.Chromosomes.AUTOSOMES.to_settings(),
        )

    def testToSettingsXChromosome(self):
        self.assertMatchSnapshot(
            query_presets.Chromosomes.X_CHROMOSOME.to_settings(),
        )

    def testToSettingsYChromosome(self):
        self.assertMatchSnapshot(
            query_presets.Chromosomes.Y_CHROMOSOME.to_settings(),
        )

    def testToSettingsMtChromosome(self):
        self.assertMatchSnapshot(
            query_presets.Chromosomes.MT_CHROMOSOME.to_settings(),
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Chromosomes.CUSTOM.to_settings()


class TestEnumRegulatory(TestCaseSnapshot, TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Regulatory.DEFAULT.value, "default")

    def testToSettingsDefault(self):
        self.assertMatchSnapshot(
            query_presets.Regulatory.DEFAULT.to_settings(),
        )


class TestEnumTad(TestCaseSnapshot, TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Tad.DEFAULT.value, "default")

    def testToSettingsDefault(self):
        self.assertEqual(query_presets.Tad.DEFAULT.to_settings(), {"tad_set": "hesc"})


class TestEnumGenotypeCriteria(TestCaseSnapshot, TestCase):
    maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.GenotypeCriteriaDefinitions.SVISH_HIGH.value, "svish_high")
        self.assertEqual(query_presets.GenotypeCriteriaDefinitions.SVISH_PASS.value, "svish_pass")
        self.assertEqual(query_presets.GenotypeCriteriaDefinitions.DEFAULT.value, "default")

    def testToSettingsSvishHigh(self):
        self.assertEqual(
            query_presets.GenotypeCriteriaDefinitions.SVISH_HIGH.to_settings(),
            GT_CRITERIA_HIGH,
        )

    def testToSettingsSvishPass(self):
        self.assertEqual(
            query_presets.GenotypeCriteriaDefinitions.SVISH_PASS.to_settings(),
            GT_CRITERIA_PASS,
        )

    def testToSettingsDefault(self):
        self.assertEqual(
            query_presets.GenotypeCriteriaDefinitions.DEFAULT.to_settings(),
            GT_CRITERIA_DEFAULT,
        )


class TestQuickPresets(PedigreesMixin, TestCaseSnapshot, TestCase):
    maxDiff = None

    def testValueDefaults(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.defaults,
        )

    def testValueDeNovo(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.de_novo,
        )

    def testValueDominant(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.dominant,
        )

    def testValueHomozygousRecessive(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.homozygous_recessive,
        )

    def testValueHeterozygousRecessive(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.compound_heterozygous,
        )

    def testValueXRecessive(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.x_recessive,
        )

    def testValueClinvarPathogenic(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.defaults,
        )

    def testValueMitochondrial(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.mitochondrial,
        )

    def testValueWholeGenome(self):
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.whole_genome,
        )

    def testToSettingsDefaults(self):
        # NB: we only test the full output for the defaults and otherwise just smoke test to_settings.
        self.assertMatchSnapshot(
            query_presets.QUICK_PRESETS.defaults.to_settings(self.trio_denovo),
        )

    def testToSettingsOther(self):
        self.assertTrue(query_presets.QUICK_PRESETS.defaults.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.de_novo.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.dominant.to_settings(self.trio_denovo))
        self.assertTrue(
            query_presets.QUICK_PRESETS.homozygous_recessive.to_settings(self.trio_denovo)
        )
        self.assertTrue(
            query_presets.QUICK_PRESETS.compound_heterozygous.to_settings(self.trio_denovo)
        )
        self.assertTrue(query_presets.QUICK_PRESETS.x_recessive.to_settings(self.trio_denovo))
        self.assertTrue(
            query_presets.QUICK_PRESETS.clinvar_pathogenic.to_settings(self.trio_denovo)
        )
        self.assertTrue(query_presets.QUICK_PRESETS.mitochondrial.to_settings(self.trio_denovo))
        self.assertTrue(query_presets.QUICK_PRESETS.whole_genome.to_settings(self.trio_denovo))
