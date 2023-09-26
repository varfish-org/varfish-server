# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["TestEnumChromosomes::testToSettingsAutosomes 1"] = {
    "gene_allowlist": None,
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
}

snapshots["TestEnumChromosomes::testToSettingsMtChromosome 1"] = {
    "gene_allowlist": [],
    "genomic_region": ["MT"],
}

snapshots["TestEnumChromosomes::testToSettingsXChromosome 1"] = {
    "gene_allowlist": [],
    "genomic_region": ["X"],
}

snapshots["TestEnumChromosomes::testToSettingsYChromosome 1"] = {
    "gene_allowlist": [],
    "genomic_region": ["Y"],
}

snapshots["TestEnumFrequency::testToSettingsAny 1"] = {
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
}

snapshots["TestEnumFrequency::testToSettingsRelaxed 1"] = {
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
}

snapshots["TestEnumFrequency::testToSettingsStrict 1"] = {
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
}

snapshots["TestEnumImpact::testToSettingsAny 1"] = {
    "tx_effects": [
        "transcript_variant",
        "exon_variant",
        "splice_region_variant",
        "intron_variant",
        "upstream_variant",
        "downstream_variant",
        "intergenic_variant",
    ]
}

snapshots["TestEnumImpact::testToSettingsExonic 1"] = {
    "tx_effects": ["transcript_variant", "exon_variant", "splice_region_variant"]
}

snapshots["TestEnumImpact::testToSettingsNearGene 1"] = {
    "tx_effects": [
        "transcript_variant",
        "exon_variant",
        "splice_region_variant",
        "intron_variant",
        "upstream_variant",
        "downstream_variant",
    ]
}

snapshots["TestEnumRegulatory::testToSettingsDefault 1"] = {
    "regulatory_custom_configs": [],
    "regulatory_ensembl_features": None,
    "regulatory_overlap": 100,
    "regulatory_vista_validation": None,
}

snapshots["TestEnumSvtype::testToSettingsAny 1"] = {
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
}

snapshots["TestEnumSvtype::testToSettingsCnvsExtraLarge 1"] = {
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
}

snapshots["TestEnumSvtype::testToSettingsCnvsLarge 1"] = {
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
}

snapshots["TestQuickPresets::testToSettingsDefaults 1"] = {
    "clinvar_sv_min_overlap": 0.75,
    "clinvar_sv_min_pathogenicity": "likely-pathogenic",
    "database": "refseq",
    "gene_allowlist": [],
    "genomic_region": [],
    "genotype": {"father": "any", "index": "any", "mother": "any"},
    "genotype_criteria": [
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.REF: 'ref'>, select_sv_sub_type=['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU', 'DUP', 'DUP:TANDEM', 'CNV'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/0', '0|0', '0', './0', '0/.', '0|.', '.|0'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=None, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=None, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=None, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=None, max_srpr_var=1, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=None, max_srpr_ab=None, min_rd_dev=None, max_rd_dev=0.2, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Wild-type genotype with high-confidence filter (CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.REF: 'ref'>, select_sv_sub_type=['INV', 'INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU', 'BND'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/0', '0|0', '0', './0', '0/.', '0|.', '.|0'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=None, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=None, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=None, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=None, max_srpr_var=1, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=None, max_srpr_ab=None, min_rd_dev=None, max_rd_dev=0.2, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Wild-type genotype with high-confidence filter (non-CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.HET: 'het'>, select_sv_sub_type=['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU', 'DUP', 'DUP:TANDEM', 'CNV'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/1', '1/0', '0|1', '1|0', './1', '1/.', '.|1', '1|.'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=2, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.1, max_srpr_ab=None, min_rd_dev=0.2, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Heterozygous genotype with high-confidence filter (CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.HET: 'het'>, select_sv_sub_type=['INV', 'INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU', 'BND'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/1', '1/0', '0|1', '1|0', './1', '1/.', '.|1', '1|.'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=10, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.1, max_srpr_ab=None, min_rd_dev=0.2, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Heterozygous genotype with high-confidence filter (non-CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.HOM: 'hom'>, select_sv_sub_type=['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU', 'DUP', 'DUP:TANDEM', 'CNV'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['1/1', '1|1', '1'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=2, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.8, max_srpr_ab=None, min_rd_dev=0.5, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Homozygous genotype with high-confidence filter (CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.HOM: 'hom'>, select_sv_sub_type=['INV', 'INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU', 'BND'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['1/1', '1|1', '1'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=10, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.8, max_srpr_ab=None, min_rd_dev=0.5, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Homozygous genotype with high-confidence filter (non-CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.NON_VARIANT: 'non-variant'>, select_sv_sub_type=['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU', 'DUP', 'DUP:TANDEM', 'CNV'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/0', '0|0', '0', './0', '0/.'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=None, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=None, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=None, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=None, max_srpr_var=1, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=None, max_srpr_ab=None, min_rd_dev=None, max_rd_dev=0.2, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Non-variant genotype with high-confidence filter (CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.NON_VARIANT: 'non-variant'>, select_sv_sub_type=['INV', 'INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU', 'BND'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/0', '0|0', '0', './0', '0/.'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=None, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=None, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=None, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=None, max_srpr_var=1, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=None, max_srpr_ab=None, min_rd_dev=None, max_rd_dev=0.2, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Non-variant genotype with high-confidence filter (non-CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.VARIANT: 'variant'>, select_sv_sub_type=['DEL', 'DEL:ME', 'DEL:ME:SVA', 'DEL:ME:L1', 'DEL:ME:ALU', 'DUP', 'DUP:TANDEM', 'CNV'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/1', '1/0', '0|1', '1|0', './1', '1/.', '.|1', '1|.', '1/1', '1|1', '1'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=2, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.1, max_srpr_ab=None, min_rd_dev=0.2, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Variant genotype with high-confidence filter (CNV)')"
        ),
        GenericRepr(
            "GenotypeCriteria(genotype=<GenotypeChoice.VARIANT: 'variant'>, select_sv_sub_type=['INV', 'INS', 'INS:ME', 'INS:ME:SVA', 'INS:ME:L1', 'INS:ME:ALU', 'BND'], select_sv_min_size=None, select_sv_max_size=None, gt_one_of=['0/1', '1/0', '0|1', '1|0', './1', '1/.', '.|1', '1|.', '1/1', '1|1', '1'], max_brk_segdup=None, max_brk_repeat=None, max_brk_segduprepeat=None, min_gq=50, min_pr_cov=None, max_pr_cov=None, min_pr_ref=None, max_pr_ref=None, min_pr_var=1, max_pr_var=None, min_sr_cov=None, max_sr_cov=None, min_sr_ref=None, max_sr_ref=None, min_sr_var=1, max_sr_var=None, min_srpr_cov=None, max_srpr_cov=None, min_srpr_ref=None, max_srpr_ref=None, min_srpr_var=10, max_srpr_var=None, min_sr_ab=None, max_sr_ab=None, min_pr_ab=None, max_pr_ab=None, min_srpr_ab=0.1, max_srpr_ab=None, min_rd_dev=0.2, max_rd_dev=None, min_amq=None, max_amq=None, missing_gt_ok=True, missing_gq_ok=True, missing_pr_ok=True, missing_sr_ok=True, missing_srpr_ok=True, missing_rd_dev_ok=True, missing_amq_ok=True, comment='Variant genotype with high-confidence filter (non-CNV)')"
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
}

snapshots["TestQuickPresets::testValueClinvarPathogenic 1"] = GenericRepr(
    "QuickPresets(label='defaults', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueDeNovo 1"] = GenericRepr(
    "QuickPresets(label='de novo', inheritance=<Inheritance.DE_NOVO: 'de_novo'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.NEAR_GENE: 'near_gene'>, sv_type=<SvType.CNVS_LARGE: 'cnvs_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueDefaults 1"] = GenericRepr(
    "QuickPresets(label='defaults', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueDominant 1"] = GenericRepr(
    "QuickPresets(label='dominant', inheritance=<Inheritance.DOMINANT: 'dominant'>, frequency=<Frequency.STRICT: 'strict'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueHeterozygousRecessive 1"] = GenericRepr(
    "QuickPresets(label='compound heterozygous', inheritance=<Inheritance.COMPOUND_HETEROZYGOUS: 'compound_heterozygous'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueHomozygousRecessive 1"] = GenericRepr(
    "QuickPresets(label='homozygous recessive', inheritance=<Inheritance.HOMOZYGOUS_RECESSIVE: 'homozygous_recessive'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueMitochondrial 1"] = GenericRepr(
    "QuickPresets(label='mitochondrial', inheritance=<Inheritance.AFFECTED_CARRIERS: 'affected_carriers'>, frequency=<Frequency.ANY: 'any'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.MT_CHROMOSOME: 'mt_chromosome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueWholeGenome 1"] = GenericRepr(
    "QuickPresets(label='whole genome', inheritance=<Inheritance.ANY: 'any'>, frequency=<Frequency.ANY: 'any'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)

snapshots["TestQuickPresets::testValueXRecessive 1"] = GenericRepr(
    "QuickPresets(label='X-recessive', inheritance=<Inheritance.X_RECESSIVE: 'x_recessive'>, frequency=<Frequency.RELAXED: 'relaxed'>, impact=<Impact.EXONIC: 'exonic'>, sv_type=<SvType.CNVS_EXTRA_LARGE: 'cnvs_extra_large'>, chromosomes=<Chromosomes.WHOLE_GENOME: 'whole_genome'>, regulatory=<Regulatory.DEFAULT: 'default'>, tad=<Tad.DEFAULT: 'default'>, known_patho=<KnownPatho.DEFAULT: 'default'>, genotype_criteria=<GenotypeCriteriaDefinitions.SVISH_HIGH: 'svish_high'>, database=<Database.REFSEQ: 'refseq'>)"
)
