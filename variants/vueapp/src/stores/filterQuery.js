import {
  DisplayColumns,
  DisplayConstraints,
  DisplayDetails,
  DisplayFrequencies,
  QueryStates,
} from '@variants/enums'
import { defineStore } from 'pinia'

export const useFilterQueryStore = defineStore({
  id: 'useFilterQueryStore',
  state: () => ({
    csrfToken: null,
    caseUuid: null,
    case: null,
    querySettingsPresets: null,
    querySettings: null,
    umdPredictorApiToken: null,
    hgmdProEnabled: null,
    hgmdProPrefix: null,
    ga4ghBeaconNetworkWidgetEnabled: null,
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
  }),
  getters: {
    getRole() {
      if (this.case.pedigree) {
        const index = this.case.index
        const pedigree = this.case.pedigree
        let roles = {}
        let mother = ''
        let father = ''
        // Prepare role assignment
        for (let i = 0; i < pedigree.length; ++i) {
          if (pedigree[i].name === index) {
            father = pedigree[i].father
            mother = pedigree[i].mother
          }
        }
        // Add roles
        for (const member of pedigree) {
          const name = member.name
          if (name === index) {
            roles[name] = 'index'
          } else if (name === father) {
            roles[name] = 'father'
          } else if (name === mother) {
            roles[name] = 'mother'
          } else {
            roles[name] = 'N/A'
          }
        }
        return (name) => {
          return roles[name]
        }
      }
    },
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
      }
    },
    async submitQuery() {
      const payload = {
        form_id: 'variants.small_variant_filter_form',
        form_version: 1,
        query_settings: this.querySettings,
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
