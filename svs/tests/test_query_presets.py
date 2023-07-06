"""Tests for the ``svs.query_presets`` module."""

from test_plus.test import TestCase

from svs import query_presets
from svs.query_presets import (
    GT_CRITERIA_DEFAULT,
    GT_CRITERIA_HIGH,
    GT_CRITERIA_PASS,
    GenotypeCriteriaDefinitions,
)
from svs.query_schemas import GenotypeCriteria, TranscriptEffect
from variants.query_presets import GenotypeChoice
from variants.tests.test_query_presets import PedigreesMixin


class TestEnumFrequency(TestCase):
    maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.Frequency.ANY.value, "any")
        self.assertEqual(query_presets.Frequency.STRICT.value, "strict")
        self.assertEqual(query_presets.Frequency.RELAXED.value, "relaxed")
        self.assertEqual(query_presets.Frequency.CUSTOM.value, "custom")

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.Frequency.ANY.to_settings(),
            {
                "svdb_dbvar_enabled": True,
                "svdb_dbvar_max_count": None,
                "svdb_dbvar_min_overlap": 0.75,
                "svdb_dgv_enabled": True,
                "svdb_dgv_gs_enabled": True,
                "svdb_dgv_gs_max_count": None,
                "svdb_dgv_gs_min_overlap": 0.75,
                "svdb_dgv_max_count": None,
                "svdb_dgv_min_overlap": 0.75,
                "svdb_exac_enabled": True,
                "svdb_exac_max_count": None,
                "svdb_exac_min_overlap": 0.75,
                "svdb_g1k_enabled": True,
                "svdb_g1k_max_count": None,
                "svdb_g1k_min_overlap": 0.75,
                "svdb_gnomad_enabled": True,
                "svdb_gnomad_max_count": None,
                "svdb_gnomad_min_overlap": 0.75,
                "svdb_inhouse_enabled": True,
                "svdb_inhouse_max_count": None,
                "svdb_inhouse_min_overlap": 0.75,
            },
        )

    def testToSettingsStrict(self):
        self.assertEqual(
            query_presets.Frequency.STRICT.to_settings(),
            {
                "svdb_dbvar_enabled": True,
                "svdb_dbvar_max_count": None,
                "svdb_dbvar_min_overlap": 0.75,
                "svdb_dgv_enabled": True,
                "svdb_dgv_gs_enabled": True,
                "svdb_dgv_gs_max_count": None,
                "svdb_dgv_gs_min_overlap": 0.75,
                "svdb_dgv_max_count": None,
                "svdb_dgv_min_overlap": 0.75,
                "svdb_exac_enabled": True,
                "svdb_exac_max_count": None,
                "svdb_exac_min_overlap": 0.75,
                "svdb_g1k_enabled": True,
                "svdb_g1k_max_count": None,
                "svdb_g1k_min_overlap": 0.75,
                "svdb_gnomad_enabled": True,
                "svdb_gnomad_max_count": 10,
                "svdb_gnomad_min_overlap": 0.75,
                "svdb_inhouse_enabled": True,
                "svdb_inhouse_max_count": 5,
                "svdb_inhouse_min_overlap": 0.75,
            },
        )

    def testToSettingsRelaxed(self):
        self.assertEqual(
            query_presets.Frequency.RELAXED.to_settings(),
            {
                "svdb_dbvar_enabled": True,
                "svdb_dbvar_max_count": None,
                "svdb_dbvar_min_overlap": 0.75,
                "svdb_dgv_enabled": True,
                "svdb_dgv_gs_enabled": True,
                "svdb_dgv_gs_max_count": None,
                "svdb_dgv_gs_min_overlap": 0.75,
                "svdb_dgv_max_count": None,
                "svdb_dgv_min_overlap": 0.75,
                "svdb_exac_enabled": True,
                "svdb_exac_max_count": None,
                "svdb_exac_min_overlap": 0.75,
                "svdb_g1k_enabled": True,
                "svdb_g1k_max_count": None,
                "svdb_g1k_min_overlap": 0.75,
                "svdb_gnomad_enabled": True,
                "svdb_gnomad_max_count": 20,
                "svdb_gnomad_min_overlap": 0.75,
                "svdb_inhouse_enabled": True,
                "svdb_inhouse_max_count": 30,
                "svdb_inhouse_min_overlap": 0.75,
            },
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Frequency.CUSTOM.to_settings()


class TestEnumSvtype(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.SvType.ANY.value, "any")
        self.assertEqual(query_presets.SvType.CNVS_LARGE.value, "cnvs_large")
        self.assertEqual(query_presets.SvType.CNVS_EXTRA_LARGE.value, "cnvs_extra_large")

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.SvType.ANY.to_settings(),
            {
                "sv_size_max": None,
                "sv_size_min": None,
                "sv_sub_types": [
                    "DEL",
                    "DEL:ME",
                    "DEL:ME:SVA",
                    "DEL:ME:L1",
                    "DEL:ME:ALU",
                    "DUP",
                    "DUP:TANDEM",
                    "CNV",
                    "INV",
                    "INS",
                    "INS:ME",
                    "INS:ME:SVA",
                    "INS:ME:L1",
                    "INS:ME:ALU",
                    "BND",
                ],
                "sv_types": ["DEL", "DUP", "INV", "INS", "BND", "CNV"],
            },
        )

    def testToSettingsCnvsLarge(self):
        self.assertEqual(
            query_presets.SvType.CNVS_LARGE.to_settings(),
            {
                "sv_size_max": None,
                "sv_size_min": 500,
                "sv_sub_types": [
                    "DEL",
                    "DEL:ME",
                    "DEL:ME:SVA",
                    "DEL:ME:L1",
                    "DEL:ME:ALU",
                    "DUP",
                    "DUP:TANDEM",
                    "CNV",
                ],
                "sv_types": ["DEL", "DUP", "CNV"],
            },
        )

    def testToSettingsCnvsExtraLarge(self):
        self.assertEqual(
            query_presets.SvType.CNVS_EXTRA_LARGE.to_settings(),
            {
                "sv_size_max": None,
                "sv_size_min": 10000,
                "sv_sub_types": [
                    "DEL",
                    "DEL:ME",
                    "DEL:ME:SVA",
                    "DEL:ME:L1",
                    "DEL:ME:ALU",
                    "DUP",
                    "DUP:TANDEM",
                    "CNV",
                ],
                "sv_types": ["DEL", "DUP", "CNV"],
            },
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.SvType.CUSTOM.to_settings()


class TestEnumImpact(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.maxDiff = None

    def testValues(self):
        self.assertEqual(query_presets.Impact.ANY.value, "any")
        self.assertEqual(query_presets.Impact.NEAR_GENE.value, "near_gene")
        self.assertEqual(query_presets.Impact.EXONIC.value, "exonic")

    def testToSettingsAny(self):
        self.assertEqual(
            query_presets.Impact.ANY.to_settings(),
            {
                "tx_effects": [
                    "transcript_variant",
                    "exon_variant",
                    "splice_region_variant",
                    "intron_variant",
                    "upstream_variant",
                    "downstream_variant",
                    "intergenic_variant",
                ]
            },
        )

    def testToSettingsNearGene(self):
        self.assertEqual(
            query_presets.Impact.NEAR_GENE.to_settings(),
            {
                "tx_effects": [
                    "transcript_variant",
                    "exon_variant",
                    "splice_region_variant",
                    "intron_variant",
                    "upstream_variant",
                    "downstream_variant",
                ]
            },
        )

    def testToSettingsExonic(self):
        self.assertEqual(
            query_presets.Impact.EXONIC.to_settings(),
            {
                "tx_effects": [
                    "transcript_variant",
                    "exon_variant",
                    "splice_region_variant",
                ]
            },
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Impact.CUSTOM.to_settings()


class TestEnumChromosomes(TestCase):
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
        self.assertEqual(
            query_presets.Chromosomes.AUTOSOMES.to_settings(),
            {
                "genomic_region": [
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                    "13",
                    "14",
                    "15",
                    "16",
                    "17",
                    "18",
                    "19",
                    "20",
                    "21",
                    "22",
                ],
                "gene_allowlist": None,
            },
        )

    def testToSettingsXChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.X_CHROMOSOME.to_settings(),
            {"genomic_region": ["X"], "gene_allowlist": []},
        )

    def testToSettingsYChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.Y_CHROMOSOME.to_settings(),
            {"genomic_region": ["Y"], "gene_allowlist": []},
        )

    def testToSettingsMtChromosome(self):
        self.assertEqual(
            query_presets.Chromosomes.MT_CHROMOSOME.to_settings(),
            {"genomic_region": ["MT"], "gene_allowlist": []},
        )

    def testToSettingsCustom(self):
        with self.assertRaises(AttributeError):
            query_presets.Chromosomes.CUSTOM.to_settings()


class TestEnumRegulatory(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Regulatory.DEFAULT.value, "default")

    def testToSettingsDefault(self):
        self.assertEqual(
            query_presets.Regulatory.DEFAULT.to_settings(),
            {
                "regulatory_overlap": 100,
                "regulatory_ensembl_features": None,
                "regulatory_vista_validation": None,
                "regulatory_custom_configs": [],
            },
        )


class TestEnumTad(TestCase):
    def testValues(self):
        self.assertEqual(query_presets.Tad.DEFAULT.value, "default")

    def testToSettingsDefault(self):
        self.assertEqual(query_presets.Tad.DEFAULT.to_settings(), {"tad_set": "hesc"})


class TestEnumGenotypeCriteria(TestCase):
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


class TestQuickPresets(PedigreesMixin, TestCase):
    maxDiff = None

    def testValueDefaults(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.defaults),
            "QuickPresets(label='defaults', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueDeNovo(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.de_novo),
            "QuickPresets(label='de novo', inheritance=<Inheritance.DE_NOVO: 'de_novo'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.NEAR_GENE: 'near_gene'>, sv_type=<SvType.CNVS_LARGE: 'cnvs_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueDominant(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.dominant),
            "QuickPresets(label='dominant', inheritance=<Inheritance.DOMINANT: 'dominant'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueHomozygousRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.homozygous_recessive),
            "QuickPresets(label='homozygous recessive', inheritance=<Inheritance.HOMOZYGOUS_RECESSIVE: 'homozygous_recessive'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueHeterozygousRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.compound_heterozygous),
            "QuickPresets(label='compound heterozygous', inheritance=<Inheritance.COMPOUND_HETEROZYGOUS: 'compound_heterozygous'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueXRecessive(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.x_recessive),
            "QuickPresets(label='X-recessive', inheritance=<Inheritance.X_RECESSIVE: 'x_recessive'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueClinvarPathogenic(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.defaults),
            "QuickPresets(label='defaults', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueMitochondrial(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.mitochondrial),
            "QuickPresets(label='mitochondrial', inheritance=<Inheritance.AFFECTED_CARRIERS: 'affected_carriers'>, frequency=<Frequency.ANY: 'any'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.MT_CHROMOSOME: 'mt_chromosome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testValueWholeGenome(self):
        self.assertEqual(
            str(query_presets.QUICK_PRESETS.whole_genome),
            "QuickPresets(label='whole genome', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.ANY: 'any'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.DEFAULT: 'default'>, database=<Database.REFSEQ: 'refseq'>)",
        )

    def testToSettingsDefaults(self):
        # NB: we only test the full output for the defaults and otherwise just smoke test to_settings.
        self.maxDiff = None
        self.assertEqual(
            query_presets.QUICK_PRESETS.defaults.to_settings(self.trio_denovo),
            {
                "clinvar_sv_min_overlap": 0.75,
                "clinvar_sv_min_pathogenicity": "likely-pathogenic",
                "database": "refseq",
                "gene_allowlist": [],
                "genomic_region": [],
                "genotype": {"father": "any", "index": "any", "mother": "any"},
                "genotype_criteria": [
                    GenotypeCriteria(
                        genotype=GenotypeChoice.REF,
                        select_sv_sub_type=[
                            "DEL",
                            "DEL:ME",
                            "DEL:ME:SVA",
                            "DEL:ME:L1",
                            "DEL:ME:ALU",
                            "DUP",
                            "DUP:TANDEM",
                            "CNV",
                            "INV",
                            "INS",
                            "INS:ME",
                            "INS:ME:SVA",
                            "INS:ME:L1",
                            "INS:ME:ALU",
                            "BND",
                        ],
                        select_sv_min_size=None,
                        select_sv_max_size=None,
                        gt_one_of=["0/0", "0|0", "0", "./0", "0/.", "0|.", ".|0"],
                        max_brk_segdup=None,
                        max_brk_repeat=None,
                        max_brk_segduprepeat=None,
                        min_gq=None,
                        min_pr_cov=None,
                        max_pr_cov=None,
                        min_pr_ref=None,
                        max_pr_ref=None,
                        min_pr_var=None,
                        max_pr_var=None,
                        min_sr_cov=None,
                        max_sr_cov=None,
                        min_sr_ref=None,
                        max_sr_ref=None,
                        min_sr_var=None,
                        max_sr_var=None,
                        min_srpr_cov=None,
                        max_srpr_cov=None,
                        min_srpr_ref=None,
                        max_srpr_ref=None,
                        min_srpr_var=None,
                        max_srpr_var=None,
                        min_sr_ab=None,
                        max_sr_ab=None,
                        min_pr_ab=None,
                        max_pr_ab=None,
                        min_srpr_ab=None,
                        max_srpr_ab=None,
                        min_rd_dev=None,
                        max_rd_dev=None,
                        min_amq=None,
                        max_amq=None,
                        missing_gt_ok=True,
                        missing_gq_ok=True,
                        missing_pr_ok=True,
                        missing_sr_ok=True,
                        missing_srpr_ok=True,
                        missing_rd_dev_ok=True,
                        missing_amq_ok=True,
                        comment="Trust the genotype to show the wild-type/reference",
                    ),
                    GenotypeCriteria(
                        genotype=GenotypeChoice.HET,
                        select_sv_sub_type=[
                            "DEL",
                            "DEL:ME",
                            "DEL:ME:SVA",
                            "DEL:ME:L1",
                            "DEL:ME:ALU",
                            "DUP",
                            "DUP:TANDEM",
                            "CNV",
                            "INV",
                            "INS",
                            "INS:ME",
                            "INS:ME:SVA",
                            "INS:ME:L1",
                            "INS:ME:ALU",
                            "BND",
                        ],
                        select_sv_min_size=None,
                        select_sv_max_size=None,
                        gt_one_of=["0/1", "1/0", "0|1", "1|0", "./1", "1/.", ".|1", "1|."],
                        max_brk_segdup=None,
                        max_brk_repeat=None,
                        max_brk_segduprepeat=None,
                        min_gq=None,
                        min_pr_cov=None,
                        max_pr_cov=None,
                        min_pr_ref=None,
                        max_pr_ref=None,
                        min_pr_var=None,
                        max_pr_var=None,
                        min_sr_cov=None,
                        max_sr_cov=None,
                        min_sr_ref=None,
                        max_sr_ref=None,
                        min_sr_var=None,
                        max_sr_var=None,
                        min_srpr_cov=None,
                        max_srpr_cov=None,
                        min_srpr_ref=None,
                        max_srpr_ref=None,
                        min_srpr_var=None,
                        max_srpr_var=None,
                        min_sr_ab=None,
                        max_sr_ab=None,
                        min_pr_ab=None,
                        max_pr_ab=None,
                        min_srpr_ab=None,
                        max_srpr_ab=None,
                        min_rd_dev=None,
                        max_rd_dev=None,
                        min_amq=None,
                        max_amq=None,
                        missing_gt_ok=True,
                        missing_gq_ok=True,
                        missing_pr_ok=True,
                        missing_sr_ok=True,
                        missing_srpr_ok=True,
                        missing_rd_dev_ok=True,
                        missing_amq_ok=True,
                        comment="Trust the genotype to show the wild-type/reference",
                    ),
                    GenotypeCriteria(
                        genotype=GenotypeChoice.HOM,
                        select_sv_sub_type=[
                            "DEL",
                            "DEL:ME",
                            "DEL:ME:SVA",
                            "DEL:ME:L1",
                            "DEL:ME:ALU",
                            "DUP",
                            "DUP:TANDEM",
                            "CNV",
                            "INV",
                            "INS",
                            "INS:ME",
                            "INS:ME:SVA",
                            "INS:ME:L1",
                            "INS:ME:ALU",
                            "BND",
                        ],
                        select_sv_min_size=None,
                        select_sv_max_size=None,
                        gt_one_of=["1/1", "1|1", "1"],
                        max_brk_segdup=None,
                        max_brk_repeat=None,
                        max_brk_segduprepeat=None,
                        min_gq=None,
                        min_pr_cov=None,
                        max_pr_cov=None,
                        min_pr_ref=None,
                        max_pr_ref=None,
                        min_pr_var=None,
                        max_pr_var=None,
                        min_sr_cov=None,
                        max_sr_cov=None,
                        min_sr_ref=None,
                        max_sr_ref=None,
                        min_sr_var=None,
                        max_sr_var=None,
                        min_srpr_cov=None,
                        max_srpr_cov=None,
                        min_srpr_ref=None,
                        max_srpr_ref=None,
                        min_srpr_var=None,
                        max_srpr_var=None,
                        min_sr_ab=None,
                        max_sr_ab=None,
                        min_pr_ab=None,
                        max_pr_ab=None,
                        min_srpr_ab=None,
                        max_srpr_ab=None,
                        min_rd_dev=None,
                        max_rd_dev=None,
                        min_amq=None,
                        max_amq=None,
                        missing_gt_ok=True,
                        missing_gq_ok=True,
                        missing_pr_ok=True,
                        missing_sr_ok=True,
                        missing_srpr_ok=True,
                        missing_rd_dev_ok=True,
                        missing_amq_ok=True,
                        comment="Trust the genotype to show homozygous alternative genotype",
                    ),
                    GenotypeCriteria(
                        genotype=GenotypeChoice.NON_VARIANT,
                        select_sv_sub_type=[
                            "DEL",
                            "DEL:ME",
                            "DEL:ME:SVA",
                            "DEL:ME:L1",
                            "DEL:ME:ALU",
                            "DUP",
                            "DUP:TANDEM",
                            "CNV",
                            "INV",
                            "INS",
                            "INS:ME",
                            "INS:ME:SVA",
                            "INS:ME:L1",
                            "INS:ME:ALU",
                            "BND",
                        ],
                        select_sv_min_size=None,
                        select_sv_max_size=None,
                        gt_one_of=["0/0", "0|0", "0", "./0", "0/."],
                        max_brk_segdup=None,
                        max_brk_repeat=None,
                        max_brk_segduprepeat=None,
                        min_gq=None,
                        min_pr_cov=None,
                        max_pr_cov=None,
                        min_pr_ref=None,
                        max_pr_ref=None,
                        min_pr_var=None,
                        max_pr_var=None,
                        min_sr_cov=None,
                        max_sr_cov=None,
                        min_sr_ref=None,
                        max_sr_ref=None,
                        min_sr_var=None,
                        max_sr_var=None,
                        min_srpr_cov=None,
                        max_srpr_cov=None,
                        min_srpr_ref=None,
                        max_srpr_ref=None,
                        min_srpr_var=None,
                        max_srpr_var=None,
                        min_sr_ab=None,
                        max_sr_ab=None,
                        min_pr_ab=None,
                        max_pr_ab=None,
                        min_srpr_ab=None,
                        max_srpr_ab=None,
                        min_rd_dev=None,
                        max_rd_dev=None,
                        min_amq=None,
                        max_amq=None,
                        missing_gt_ok=True,
                        missing_gq_ok=True,
                        missing_pr_ok=True,
                        missing_sr_ok=True,
                        missing_srpr_ok=True,
                        missing_rd_dev_ok=True,
                        missing_amq_ok=True,
                        comment="Trust the genotype to show non-variant genotype",
                    ),
                    GenotypeCriteria(
                        genotype=GenotypeChoice.VARIANT,
                        select_sv_sub_type=[
                            "DEL",
                            "DEL:ME",
                            "DEL:ME:SVA",
                            "DEL:ME:L1",
                            "DEL:ME:ALU",
                            "DUP",
                            "DUP:TANDEM",
                            "CNV",
                            "INV",
                            "INS",
                            "INS:ME",
                            "INS:ME:SVA",
                            "INS:ME:L1",
                            "INS:ME:ALU",
                            "BND",
                        ],
                        select_sv_min_size=None,
                        select_sv_max_size=None,
                        gt_one_of=[
                            "0/1",
                            "1/0",
                            "0|1",
                            "1|0",
                            "./1",
                            "1/.",
                            ".|1",
                            "1|.",
                            "1/1",
                            "1|1",
                            "1",
                        ],
                        max_brk_segdup=None,
                        max_brk_repeat=None,
                        max_brk_segduprepeat=None,
                        min_gq=None,
                        min_pr_cov=None,
                        max_pr_cov=None,
                        min_pr_ref=None,
                        max_pr_ref=None,
                        min_pr_var=None,
                        max_pr_var=None,
                        min_sr_cov=None,
                        max_sr_cov=None,
                        min_sr_ref=None,
                        max_sr_ref=None,
                        min_sr_var=None,
                        max_sr_var=None,
                        min_srpr_cov=None,
                        max_srpr_cov=None,
                        min_srpr_ref=None,
                        max_srpr_ref=None,
                        min_srpr_var=None,
                        max_srpr_var=None,
                        min_sr_ab=None,
                        max_sr_ab=None,
                        min_pr_ab=None,
                        max_pr_ab=None,
                        min_srpr_ab=None,
                        max_srpr_ab=None,
                        min_rd_dev=None,
                        max_rd_dev=None,
                        min_amq=None,
                        max_amq=None,
                        missing_gt_ok=True,
                        missing_gq_ok=True,
                        missing_pr_ok=True,
                        missing_sr_ok=True,
                        missing_srpr_ok=True,
                        missing_rd_dev_ok=True,
                        missing_amq_ok=True,
                        comment="Trust the genotype to show variant genotype",
                    ),
                ],
                "recessive_index": None,
                "recessive_mode": None,
                "regulatory_custom_configs": [],
                "regulatory_ensembl_features": None,
                "regulatory_overlap": 100,
                "regulatory_vista_validation": None,
                "sv_size_max": None,
                "sv_size_min": 10000,
                "sv_sub_types": [
                    "DEL",
                    "DEL:ME",
                    "DEL:ME:SVA",
                    "DEL:ME:L1",
                    "DEL:ME:ALU",
                    "DUP",
                    "DUP:TANDEM",
                    "CNV",
                ],
                "sv_types": ["DEL", "DUP", "CNV"],
                "svdb_dbvar_enabled": True,
                "svdb_dbvar_max_count": None,
                "svdb_dbvar_min_overlap": 0.75,
                "svdb_dgv_enabled": True,
                "svdb_dgv_gs_enabled": True,
                "svdb_dgv_gs_max_count": None,
                "svdb_dgv_gs_min_overlap": 0.75,
                "svdb_dgv_max_count": None,
                "svdb_dgv_min_overlap": 0.75,
                "svdb_exac_enabled": True,
                "svdb_exac_max_count": None,
                "svdb_exac_min_overlap": 0.75,
                "svdb_g1k_enabled": True,
                "svdb_g1k_max_count": None,
                "svdb_g1k_min_overlap": 0.75,
                "svdb_gnomad_enabled": True,
                "svdb_gnomad_max_count": 10,
                "svdb_gnomad_min_overlap": 0.75,
                "svdb_inhouse_enabled": True,
                "svdb_inhouse_max_count": 5,
                "svdb_inhouse_min_overlap": 0.75,
                "tad_set": "hesc",
                "tx_effects": ["transcript_variant", "exon_variant", "splice_region_variant"],
            },
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
