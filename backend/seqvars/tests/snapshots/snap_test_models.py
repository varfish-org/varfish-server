# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["TestSeqvarsQuerySettings::test_from_predefinedquery 1"] = {
    "clinvar": GenericRepr("UUID('96d4c341-e37f-41be-b795-f4f23da217d4')"),
    "clinvarpresets": "90282cf6-5759-4003-aae5-99c55cf39bc6",
    "consequence": GenericRepr("UUID('d0f895c7-0567-4e90-9c42-7864e4af57a7')"),
    "consequencepresets": "7a5ab3ec-3d0c-487b-ae57-4f4660f8b71f",
    "date_created": "2012-01-14T12:00:01Z",
    "date_modified": "2012-01-14T12:00:01Z",
    "frequency": GenericRepr("UUID('2049d926-e500-460a-8002-32f8295b7697')"),
    "frequencypresets": "e2a6e90f-88f6-4a3a-b78b-96e472d00bca",
    "genotype": GenericRepr("UUID('7af7005f-83a7-4f36-a563-d2edf8f47ea3')"),
    "genotypepresets": {"choice": "any"},
    "locus": GenericRepr("UUID('08c0ff39-519c-4fdd-9ea6-93239af0f8ef')"),
    "locuspresets": "0bfc5702-3833-4ccb-999f-ee55e9b3db4d",
    "phenotypeprio": GenericRepr("UUID('e2bbc543-0454-442a-b212-df664a0cd498')"),
    "phenotypepriopresets": "6ca23340-51a4-44f8-8191-52e30ad539b5",
    "predefinedquery": "eeec779a-d029-4c05-8b34-d59271c30474",
    "presetssetversion": "c64821f0-c38b-42d6-8a26-b86e72d86bcb",
    "quality": GenericRepr("UUID('a8bb0882-b543-4718-b6c0-5f503420e090')"),
    "qualitypresets": "e024db63-333f-41ee-8439-c2556c14f669",
    "session": "6e5461c6-0f16-447e-b858-3e22d68bd0ea",
    "sodar_uuid": "771cc621-5b72-42b0-b796-781a9e75ae41",
    "variantprio": GenericRepr("UUID('26b0ca5d-85c2-49c7-9b30-58664e16e71b')"),
    "variantpriopresets": "f61ee1eb-3153-42a3-8c12-4b462592ee1b",
}

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
    "frequency": None,
    "hemizygous": None,
    "heterozygous": None,
    "homozygous": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets gnomad_genomes"] = {
    "enabled": False,
    "frequency": None,
    "hemizygous": None,
    "heterozygous": None,
    "homozygous": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets gnomad_mitochondrial"] = {
    "enabled": False,
    "frequency": None,
    "heteroplasmic": None,
    "homoplasmic": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets helixmtdb"] = {
    "enabled": False,
    "frequency": None,
    "heteroplasmic": None,
    "homoplasmic": None,
}

snapshots["TestSeqvarsQuerySettingsFrequency::test_from_presets inhouse"] = {
    "carriers": None,
    "enabled": False,
    "hemizygous": None,
    "heterozygous": None,
    "homozygous": None,
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
