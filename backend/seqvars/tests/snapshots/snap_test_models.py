# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots[
    "TestSeqvarsQuerySettingsClinvar::test_from_presets allow_conflicting_interpretations"
] = False

snapshots[
    "TestSeqvarsQuerySettingsClinvar::test_from_presets clinvar_germline_aggregate_description"
] = [
    "ClinvarGermlineAggregateDescriptionChoice.PATHOGENIC",
    "ClinvarGermlineAggregateDescriptionChoice.LIKELY_PATHOGENIC",
]

snapshots["TestSeqvarsQuerySettingsClinvar::test_from_presets clinvar_presence_required"] = False

snapshots["TestSeqvarsQuerySettingsColumns::test_from_presets column_settings"] = [
    GenericRepr(
        "SeqvarsColumnConfigPydantic(name='chromosome', label='Chromosome', description=None, width=300, visible=True)"
    )
]

snapshots["TestSeqvarsQuerySettingsConsequence::test_from_presets max_distance_to_exon"] = 50

snapshots["TestSeqvarsQuerySettingsConsequence::test_from_presets transcript_types"] = [
    "SeqvarsTranscriptTypeChoice.CODING"
]

snapshots["TestSeqvarsQuerySettingsConsequence::test_from_presets variant_consequences"] = [
    "SeqvarsVariantConsequenceChoice.MISSENSE_VARIANT"
]

snapshots["TestSeqvarsQuerySettingsConsequence::test_from_presets variant_types"] = [
    "SeqvarsVariantTypeChoice.SNV"
]

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets gnomad_exomes"] = {
    "enabled": False,
    "max_af": None,
    "max_hemi": None,
    "max_het": None,
    "max_hom": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets gnomad_genomes"] = {
    "enabled": False,
    "max_af": None,
    "max_hemi": None,
    "max_het": None,
    "max_hom": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets gnomad_mtdna"] = {
    "enabled": False,
    "max_af": None,
    "max_het": None,
    "max_hom": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets helixmtdb"] = {
    "enabled": False,
    "max_af": None,
    "max_het": None,
    "max_hom": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets inhouse"] = {
    "enabled": False,
    "max_carriers": None,
    "max_hemi": None,
    "max_het": None,
    "max_hom": None,
}

snapshots["TestSeqvarsQuerySettingsGenotype::test_from_presets_0_any sample_genotype_choices"] = [
    {"enabled": True, "genotype": "any", "include_no_call": False, "sample": "IND_0"}
]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_1_de_novo sample_genotype_choices"
] = [{"enabled": True, "genotype": "variant", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_2_dominant sample_genotype_choices"
] = [{"enabled": True, "genotype": "het", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_3_homozygous_recessive sample_genotype_choices"
] = [{"enabled": True, "genotype": "recessive_index", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_4_compound_heterozygous_recessive sample_genotype_choices"
] = [{"enabled": True, "genotype": "recessive_index", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_5_recessive sample_genotype_choices"
] = [{"enabled": True, "genotype": "recessive_index", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_6_x_recessive sample_genotype_choices"
] = [{"enabled": True, "genotype": "recessive_index", "include_no_call": False, "sample": "IND_0"}]

snapshots[
    "TestSeqvarsQuerySettingsGenotype::test_from_presets_7_affected_carriers sample_genotype_choices"
] = [{"enabled": True, "genotype": "variant", "include_no_call": False, "sample": "IND_0"}]

snapshots["TestSeqvarsQuerySettingsLocus::test_from_presets gene_panels"] = [
    {"name": "Monogenic hearing loss", "panel_id": "126", "source": "panelapp", "version": "4.39"}
]

snapshots["TestSeqvarsQuerySettingsLocus::test_from_presets genes"] = [
    {"ensembl_id": None, "entrez_id": None, "hgnc_id": "HGNC:1234", "name": None, "symbol": "GENE1"}
]

snapshots["TestSeqvarsQuerySettingsLocus::test_from_presets genome_regions"] = []

snapshots["TestSeqvarsQuerySettingsPhenotypePrio::test_from_presets phenotype_prio_algorithm"] = (
    "HiPhive"
)

snapshots["TestSeqvarsQuerySettingsPhenotypePrio::test_from_presets phenotype_prio_enabled"] = False

snapshots["TestSeqvarsQuerySettingsPhenotypePrio::test_from_presets terms"] = [
    {"excluded": False, "term": {"label": "Phenotype 1", "term_id": "HP:0000001"}}
]

snapshots["TestSeqvarsQuerySettingsQuality::test_from_presets sample_quality_filters"] = [
    {
        "filter_active": True,
        "max_ad": None,
        "min_ab_het": 0.3,
        "min_ad": 3,
        "min_dp_het": 10,
        "min_dp_hom": 5,
        "min_gq": 20,
        "sample": "IND_0",
    }
]

snapshots["TestSeqvarsQuerySettingsVariantPrio::test_from_presets services"] = [
    {"name": "MutationTaster", "version": "2021"}
]

snapshots["TestSeqvarsQuerySettingsVariantPrio::test_from_presets variant_prio_enabled"] = False
