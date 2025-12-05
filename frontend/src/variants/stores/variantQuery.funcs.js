import { copy } from '@/variants/helpers'

// Glue code to convert old query settings (read from API) to new ones (written to API).
//
// This function can be removed once support for the fold forms is removed.
export function previousQueryDetailsToQuerySettings(
  caseObj,
  previousQueryDetails,
) {
  const freqKeys = [
    'exac_enabled',
    'exac_frequency',
    'exac_hemizygous',
    'exac_heterozygous',
    'exac_homozygous',
    'gnomad_exomes_enabled',
    'gnomad_exomes_frequency',
    'gnomad_exomes_hemizygous',
    'gnomad_exomes_heterozygous',
    'gnomad_exomes_homozygous',
    'gnomad_genomes_enabled',
    'gnomad_genomes_frequency',
    'gnomad_genomes_hemizygous',
    'gnomad_genomes_heterozygous',
    'gnomad_genomes_homozygous',
    'helixmtdb_enabled',
    'helixmtdb_frequency',
    'helixmtdb_het_count',
    'helixmtdb_hom_count',
    'inhouse_carriers',
    'inhouse_enabled',
    'inhouse_hemizygous',
    'inhouse_heterozygous',
    'inhouse_homozygous',
    'mitomap_count',
    'mitomap_enabled',
    'mitomap_frequency',
    'mtdb_count',
    'mtdb_enabled',
    'mtdb_frequency',
    'thousand_genomes_enabled',
    'thousand_genomes_frequency',
    'thousand_genomes_hemizygous',
    'thousand_genomes_heterozygous',
    'thousand_genomes_homozygous',
  ]

  const result = copy(previousQueryDetails.query_settings)
  const keysToDel = [
    'export_flags',
    'prio_hpo_terms_curated',
    'result_rows_limit',
    'database_select',
    'submit',
    'training_mode',
    'file_type',
    'export_comments',
    'recessive_indices',
    'compound_recessive_indices',
  ]
  const genotype = {}
  const quality = {}

  for (const { name } of caseObj.pedigree) {
    quality[name] = {
      ab: result[`${name}_ab`],
      ad: result[`${name}_ad`],
      ad_max: result[`${name}_ad_max`],
      dp_het: result[`${name}_dp_het`],
      dp_hom: result[`${name}_dp_hom`],
      gq: result[`${name}_gq`],
      fail: result[`${name}_fail`],
    }
    genotype[name] = result[`${name}_gt`]
    keysToDel.push(
      `${name}_ab`,
      `${name}_ad`,
      `${name}_ad_max`,
      `${name}_dp_het`,
      `${name}_dp_hom`,
      `${name}_gq`,
      `${name}_fail`,
      `${name}_gt`,
    )
  }

  result.recessive_index = null
  result.recessive_mode = null
  if (caseObj.name in result.recessive_indices) {
    result.recessive_index = result.recessive_indices[caseObj.name]
    result.recessive_mode = 'recessive'
  }
  if (caseObj.name in result.compound_recessive_indices) {
    result.recessive_index = result.compound_recessive_indices[caseObj.name]
    result.recessive_mode = 'compound-recessive'
  }

  for (const key of Object.keys(result)) {
    if (key.startsWith('effect_')) {
      keysToDel.push(key)
    }
    if (
      key.startsWith('flag_phenotype_') &&
      !key.startsWith('flag_phenotype_match_')
    ) {
      keysToDel.push(key)
      result[key.replace('_phenotype_', '_phenotype_match_')] = result[key]
    }
    if (key.endsWith('_export')) {
      keysToDel.push(key)
    }
  }

  result.database = result.database_select

  const flagsKeys = [
    'clinvar_include_pathogenic',
    'clinvar_include_likely_pathogenic',
    'clinvar_include_uncertain_significance',
    'clinvar_include_likely_benign',
    'clinvar_include_benign',
    'clinvar_include_conflicting',
    'clinvar_paranoid_mode',
    'require_in_clinvar',
  ]
  for (const key of flagsKeys) {
    if (!result[key]) {
      result[key] = false
    }
  }

  for (const key of freqKeys) {
    if (!(key in result)) {
      result[key] = null
    }
  }

  for (const key of keysToDel) {
    delete result[key]
  }

  if (result.max_exon_dist === '') {
    result.max_exon_dist = null
  } else if (
    result.max_exon_dist !== null &&
    result.max_exon_dist !== undefined
  ) {
    result.max_exon_dist = Number(result.max_exon_dist)
  }

  result.genotype = genotype
  result.quality = quality

  result.genomic_region = result.genomic_region.map((region) => {
    // Handle both string format and tuple format
    if (typeof region === 'string') {
      // Already a string, return as-is
      return region
    }
    // Legacy tuple format: [chromosome, start, end]
    let range = ''
    if (region[1] !== null && region[2] !== null) {
      range =
        ':' + region[1].toLocaleString() + '-' + region[2].toLocaleString()
    }
    return 'chr' + region[0] + range
  })

  return result
}
