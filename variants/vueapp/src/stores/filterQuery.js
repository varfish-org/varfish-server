import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
  QueryStates,
} from '@variants/enums'
import { defineStore } from 'pinia'

import { copy } from '../helpers'

// Glue code to convert old query settings (read from API) to new ones (written to API).
function previousQueryDetailsToQuerySettings(caseObj, previousQueryDetails) {
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
      `${name}_gt`
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

  result.genotype = genotype
  result.quality = quality

  return result
}

export const useFilterQueryStore = defineStore({
  id: 'filterQuery',
  state: () => ({
    showFiltrationInlineHelp: false,
    filtrationComplexityMode: null,
    csrfToken: null,
    caseUuid: null,
    case: null,
    querySettingsPresets: null,
    querySettings: null,
    umdPredictorApiToken: null,
    hgmdProEnabled: null,
    hgmdProPrefix: null,
    ga4ghBeaconNetworkWidgetEnabled: null,
    exomiserEnabled: null,
    caddEnabled: null,
    previousQueryDetails: null,
    queryUuid: null,
    queryResults: null,
    queryInterval: null,
    queryState: QueryStates.Initial.value,
    queryLogs: null,
    queryLogsVisible: false,
    queryHpoTerms: null,
    displayDetails: DisplayDetails.Coordinates.value,
    displayFrequency: DisplayFrequencies.GnomadExomes.value,
    displayConstraint: DisplayConstraints.GnomadPli.value,
    displayColumns: [DisplayColumns.Effect.value],
    quickPresets: null,
    categoryPresets: {
      inheritance: null,
      frequency: null,
      impact: null,
      quality: null,
      chromosomes: null,
      flags_etc: null,
    },
  }),
  getters: {
    setQueryStatusInterval() {
      // Otherwise we have to wait for 5 seconds
      this.fetchQueryStatus()
      this.queryInterval = setInterval(this.fetchQueryStatus, 5000)
    },
    unsetQueryStatusInterval() {
      clearInterval(this.queryInterval)
      this.queryInterval = null
    },
  },
  actions: {
    fetchPresets() {
      Promise.all(
        [
          fetch('/variants/api/query-case/quick-presets/')
            .then((response) => response.json())
            .then((data) => {
              this.quickPresets = data
            }),
          fetch(
            `/variants/api/query-case/inheritance-presets/${this.caseUuid}/`
          )
            .then((response) => response.json())
            .then((data) => {
              this.categoryPresets.inheritance = data
            }),
        ] +
          ['frequency', 'impact', 'quality', 'chromosomes', 'flags_etc'].map(
            (category) =>
              fetch(`/variants/api/query-case/category-presets/${category}/`)
                .then((response) => response.json())
                .then((data) => {
                  this.categoryPresets[category] = data
                })
          )
      )
    },
    async fetchCase() {
      const res = await fetch(`/variants/ajax/case/retrieve/${this.caseUuid}/`)
      if (res.ok) {
        this.case = await res.json()
      }
    },
    async fetchDefaultSettings() {
      const res = await fetch(
        `/variants/ajax/query-case/query-settings-shortcut/${this.caseUuid}/`
      )
      if (res.ok) {
        const resJson = await res.json()
        this.querySettingsPresets = resJson.presets
        this.querySettings = resJson.query_settings
        if (this.querySettings.prio_enabled === undefined) {
          this.querySettings.prio_enabled = false
        }
        if (this.querySettings.prio_algorithm === undefined) {
          this.querySettings.prio_algorithm = 'hiphive-human'
        }
        if (this.querySettings.prio_hpo_terms === undefined) {
          this.querySettings.prio_hpo_terms = []
        }
        if (this.querySettings.patho_enabled === undefined) {
          this.querySettings.patho_enabled = false
        }
        if (this.querySettings.patho_score === undefined) {
          this.querySettings.patho_score = 'mutationtaster'
        }
        if (this.querySettings.prio_enabled === undefined) {
          this.querySettings.prio_enabled = false
        }
      }
    },
    async submitQuery() {
      const payload = {
        form_id: 'variants.small_variant_filter_form',
        form_version: 1,
        query_settings: copy(this.querySettings),
      }
      // Handle recessive-index and recessive-parent values (must be removed).
      for (const [key, value] of Object.entries(
        payload.query_settings.genotype
      )) {
        if (value.startsWith('recessive-') || value.startsWith('comphet-')) {
          payload.query_settings.genotype[key] = null
        }
      }
      const res = await fetch(
        `/variants/ajax/query-case/create/${this.caseUuid}/`,
        {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            // Accept: "application/json",
            'Content-Type': 'application/json',
            'X-CSRFToken': this.csrfToken,
          },
          body: JSON.stringify(payload),
        }
      )
      if (res.ok) {
        const resJson = await res.json()
        this.queryUuid = resJson.sodar_uuid
      }
    },
    async fetchQueryDetails() {
      const res = await fetch(
        `/variants/ajax/query-case/retrieve/${this.queryUuid}`
      )
      if (res.ok) {
        this.previousQueryDetails = await res.json()
        this.querySettings = previousQueryDetailsToQuerySettings(
          this.case,
          this.previousQueryDetails
        )
      }
    },
    async fetchQueryResults() {
      this.queryState = QueryStates.Fetching.value
      const res = await fetch(
        `/variants/ajax/query-case/results-extended/${this.queryUuid}/`
      )
      if (res.ok) {
        this.queryResults = await res.json()
        this.queryState = QueryStates.Fetched.value
      } else {
        if (res.status !== 503) {
          throw new Error(`An error has occurred: ${res.status}`)
        }
      }
    },
    async fetchQueryStatus() {
      const res = await fetch(
        `/variants/ajax/query-case/status/${this.queryUuid}`
      )
      if (res.ok) {
        const resJson = await res.json()
        this.queryLogs = resJson.logs
        if (resJson.status === 'initial') {
          this.queryState = QueryStates.Initial.value
        } else if (resJson.status === 'running') {
          this.queryState = QueryStates.Running.value
        } else if (resJson.status === 'done') {
          this.queryState = QueryStates.Finished.value
        } else {
          this.queryState = QueryStates.Error.value
        }
      }
    },
    async fetchPreviousQueryUuid() {
      const res = await fetch(
        `/variants/ajax/query-case/list/${this.caseUuid}/`
      )
      if (res.ok) {
        const resJson = await res.json()
        if (resJson.length) {
          this.queryUuid = resJson[0].sodar_uuid
        }
      }
    },
    async fetchHpoTerms() {
      const res = await fetch(
        `/variants/ajax/query-case/hpo-terms/${this.queryUuid}/`
      )
      if (res.ok) {
        this.queryHpoTerms = await res.json()['hpoterms']
      }
    },
    getAcmgBadge(acmgClass) {
      return acmgClass == null
        ? 'badge-outline-secondary text-muted'
        : acmgClass > 3
        ? 'badge-danger text-white'
        : acmgClass === 3
        ? 'badge-warning text-black'
        : 'badge-success text-white'
    },
    getClinvarSignificanceBadge(patho) {
      if (patho === 'pathogenic') {
        return 'badge-danger'
      } else if (patho === 'likely_pathogenic') {
        return 'badge-warning'
      } else if (patho === 'uncertain_significance') {
        return 'badge-info'
      } else if (patho === 'likely_benign') {
        return 'badge-secondary'
      } else if (patho === 'benign') {
        return 'badge-secondary'
      }
      return 'badge-secondary'
    },
  },
})
