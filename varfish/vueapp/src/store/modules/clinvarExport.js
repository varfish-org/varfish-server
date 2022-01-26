import Vue from 'vue'
import clinvarExport from '../../api/clinvarExport'
import { uuidv4, isDiseaseTerm, HPO_INHERITANCE_MODE } from '@/helpers'

/**
 * Enum for the valid clinvar export application states.
 */
export const AppState = Object.freeze({
  initializing: 'initializing',
  list: 'list',
  edit: 'edit',
  add: 'add'
})

/**
 * Enum for the valid submission set wizard state.
 */
export const WizardState = Object.freeze({
  submissionSet: 'submissionSet',
  submissions: 'submissions'
})

/**
 * List of model keys.
 */
const MODEL_KEYS = Object.freeze([
  'organisations',
  'families',
  'individuals',
  'assertionMethods',
  'submitters',
  'submissionSets',
  'submissions',
  'submissionIndividuals',
  'submittingOrgs'
])

const state = () => ({
  // application / client state
  appContext: null,
  appState: AppState.initializing,
  wizardState: WizardState.submissionSet,
  notification: null,
  currentSubmissionSet: null,
  currentSubmission: null,

  // data from server / API
  organisations: {},
  families: {},
  individuals: {},
  assertionMethods: {},
  submitters: {},
  submissionSets: {},
  submissions: {},
  submissionIndividuals: {},
  submittingOrgs: {},
  // data from server / API before any change
  oldModel: null,

  // interwoven state/data
  submissionSetList: []
})

const getters = {}

const actions = {
  /**
   * Initialize the store from the remote URL.
   */
  initialize ({ state, commit }, payload) {
    commit('SET_APP_CONTEXT', payload.appContext)
    commit('SET_APP_STATE', AppState.initializing)

    Promise.all([
      clinvarExport.getOrganisations(state.appContext).then((res) => commit('SET_ORGANISATIONS', res)),
      clinvarExport.getSubmitters(state.appContext).then((res) => commit('SET_SUBMITTERS', res)),
      clinvarExport.getAssertionMethods(state.appContext).then((res) => commit('SET_ASSERTION_METHODS', res)),
      clinvarExport.getSubmissionSets(state.appContext).then((res) => commit('SET_SUBMISSION_SETS', res)),
      clinvarExport.getSubmissions(state.appContext).then((res) => commit('SET_SUBMISSIONS', res)),
      clinvarExport.getIndividuals(state.appContext).then((res) => commit('SET_INDIVIDUALS', res)),
      clinvarExport.getSubmissionIndividuals(state.appContext).then((res) => commit('SET_SUBMISSION_INDIVIDUALS', res)),
      clinvarExport.getFamilies(state.appContext).then((res) => commit('SET_FAMILIES', res)),
      clinvarExport.getSubmittingOrgs(state.appContext).then((res) => commit('SET_SUBMITTING_ORGS', res)),
      clinvarExport.getUserAnnotations(state.appContext).then((res) => commit('SET_USER_ANNOTATIONS', res))
    ]).then(_response => {
      commit('INITIALIZE_SUBMISSION_SET_ORGANISATIONS')
      commit('SAVE_OLD_MODEL')
      commit('SET_APP_STATE', AppState.list)
    }, error => {
      throw new Error(`Problem loading application state from API: ${error}`)
    })
  },
  /**
   * Make clinvar export editor edit the submission with the given ID.
   */
  editSubmissionSet ({ state, commit }, submissionSetUuid) {
    commit('SET_CURRENT_SUBMISSION_SET', submissionSetUuid)
    commit('SET_APP_STATE', AppState.edit)
  },
  /**
   * Make clinvar export editor create a new submission (without committing through API) and edit it.
   *
   * Changes will be committed through `wizardSave`.
   */
  createNewSubmissionSet ({ state, commit }) {
    const titles = Object.values(state.submissionSets).map(submissionSet => submissionSet.title)
    let title = 'New Submission Set'
    let i = 2
    while (titles.includes(title)) {
      title = 'New Submission Set #' + i
      i += 1
    }
    const submissionSet = {
      sodar_uuid: uuidv4(),
      date_modified: new Date().toLocaleString(),
      title: title,
      state: 'draft',
      sort_order: Object.keys(state.submissionSets).length,
      submitter: null,
      organisations: [],
      submitting_orgs: [],
      submissions: []
    }

    commit('ADD_SUBMISSION_SET', submissionSet)
    commit('SET_CURRENT_SUBMISSION_SET', submissionSet.sodar_uuid)
    commit('SET_WIZARD_STATE', WizardState.submissionSet)
    commit('SET_APP_STATE', AppState.add)
  },
  /**
   * Update the `wizardState`.
   */
  setWizardState ({ commit }, value) {
    commit('SET_WIZARD_STATE', value)
  },

  /**
   * Save submission set currently open in wizard through API.
   */
  async wizardSave ({ state, commit }) {
    async function _wizardSaveSubmissionSet ({ state, commit }, submissionSetExists) {
      if (submissionSetExists) {
        const res = await clinvarExport.updateSubmissionSet(state.currentSubmissionSet, state.appContext)
        return res
      } else {
        const apiSet = await clinvarExport.createSubmissionSet(state.currentSubmissionSet, state.appContext)
        // Add submission set from API.  Then change the list to first remove the just added apiSet and replace the
        // old one with the one from the API.
        commit('ADD_SUBMISSION_SET', apiSet)
        commit(
          'SET_SUBMISSION_SET_LIST',
          state.submissionSetList
            .filter(ss => (ss.sodar_uuid !== apiSet.sodar_uuid))
            .map(ss => (ss.sodar_uuid === state.currentSubmissionSet.sodar_uuid) ? apiSet : ss)
        )
        return apiSet
      }
    }

    async function _wizardSaveApplySubmittingOrgs ({ state, commit }, apiSet) {
      // Create and update appropriate submitting orgs with API.
      for (let i = 0; i < state.currentSubmissionSet.submitting_orgs.length; i++) {
        const localUuid = state.currentSubmissionSet.submitting_orgs[i]
        if (localUuid in state.oldModel.submittingOrgs) {
          await clinvarExport.updateSubmittingOrg(
            {
              ...JSON.parse(JSON.stringify(state.submittingOrgs[localUuid])),
              sort_order: i
            },
            state.appContext
          )
        } else {
          const apiSubmittingOrg = await clinvarExport.createSubmittingOrg(
            {
              ...JSON.parse(JSON.stringify(state.submittingOrgs[localUuid])),
              sort_order: i,
              submission_set: apiSet.sodar_uuid
            },
            state.appContext
          )
          commit('ADD_SUBMITTING_ORG', apiSubmittingOrg)
          commit(
            'ADD_SUBMITTING_ORG_TO_SUBMISSION_SET',
            {
              submissionSet: apiSet.sodar_uuid,
              submittingOrg: apiSubmittingOrg.sodar_uuid
            }
          )
          commit('DELETE_SUBMITTING_ORG', localUuid)
        }
      }

      // Remove existing submitting orgs that are not present in the old state.
      if (apiSet.sodar_uuid in state.oldModel.submissionSets) {
        const oldSubmissionSet = state.oldModel.submissionSets[apiSet.sodar_uuid]
        for (let i = 0; i < oldSubmissionSet.submitting_orgs.length; i++) {
          const localSubmittingOrgUuid = oldSubmissionSet.submitting_orgs[i]
          if (!(localSubmittingOrgUuid in state.submittingOrgs)) {
            await clinvarExport.deleteSubmittingOrg(
              state.oldModel.submittingOrgs[localSubmittingOrgUuid],
              state.appContext
            )
          }
        }
      }
    }

    async function _wizardSaveSubmission ({ state, commit }, apiSet, sortOrder, localSubmissionUuid) {
      const submissionExists = (localSubmissionUuid in state.oldModel.submissions)
      const localSubmission = state.submissions[localSubmissionUuid]
      let apiSubmission = null
      if (submissionExists) {
        apiSubmission = await clinvarExport.updateSubmission(
          {
            ...JSON.parse(JSON.stringify(localSubmission)),
            sort_order: sortOrder
          },
          state.appContext
        )
      } else {
        apiSubmission = await clinvarExport.createSubmission(
          {
            ...JSON.parse(JSON.stringify(localSubmission)),
            sort_order: sortOrder,
            submission_set: apiSet.sodar_uuid
          },
          state.appContext
        )
        // Register submission from API.
        commit('ADD_SUBMISSION', apiSubmission)
        commit('ADD_SUBMISSION_TO_SUBMISSION_SET', {
          submissionSet: apiSet.sodar_uuid,
          submission: apiSubmission.sodar_uuid
        })
      }

      // Delete submission individuals from old data that are not in current data.
      if (submissionExists) {
        const oldSubmission = state.oldModel.submissions[localSubmission.sodar_uuid]
        for (let i = 0; i < oldSubmission.submission_individuals.length; i++) {
          const localIndividualUuid = oldSubmission.submission_individuals[i]
          if (!localSubmission.submission_individuals.includes(localIndividualUuid)) {
            await clinvarExport.deleteSubmissionIndividual(
              state.oldModel.submissionIndividuals[localIndividualUuid],
              state.appContext
            )
          }
        }
      }

      // Copy over submission individuals and delete local ones.
      const keys = Array.from(localSubmission.submission_individuals)
      for (let i = 0; i < keys.length; i++) {
        const localIndividualUuid = keys[i]
        const localSI = state.submissionIndividuals[localIndividualUuid]
        const localSubmissionIndividualExists = (localSI.sodar_uuid in state.oldModel.submissionIndividuals)
        let apiSubmissionIndividual = null
        if (localSubmissionIndividualExists) {
          apiSubmissionIndividual = await clinvarExport.updateSubmissionIndividual(
            {
              ...JSON.parse(JSON.stringify(localSI)),
              sort_order: i
            },
            state.appContext
          )
        } else {
          apiSubmissionIndividual = await clinvarExport.createSubmissionIndividual(
            {
              ...JSON.parse(JSON.stringify(localSI)),
              sort_order: i,
              submission: apiSubmission.sodar_uuid
            },
            state.appContext
          )

          // Register submission individual from API.
          if (!localSubmissionIndividualExists) {
            commit('ADD_SUBMISSION_INDIVIDUAL', apiSubmissionIndividual)
            commit('ADD_SUBMISSION_INDIVIDUAL_TO_SUBMISSION', {
              submission: apiSubmission.sodar_uuid,
              submissionIndividual: apiSubmissionIndividual.sodar_uuid
            })
            // Delete local submission individual if necessary.
            commit('DELETE_SUBMISSION_INDIVIDUAL', localIndividualUuid)
          }
        }
      }

      // Delete local submission.
      if (!submissionExists) {
        commit('DELETE_SUBMISSION', localSubmissionUuid)
      }
    }

    commit('SET_APP_STATE', AppState.list)

    // Save submission set and submitting orgs.
    const submissionSetExists = state.currentSubmissionSet.sodar_uuid in state.oldModel.submissionSets
    const apiSet = await _wizardSaveSubmissionSet({ state, commit }, submissionSetExists)
    await _wizardSaveApplySubmittingOrgs({ state, commit }, apiSet)

    // Create appropriate submissions with API, copy over individuals and remove local submissions and submission
    // individuals.
    const submissionUuids = state.currentSubmissionSet.submissions.slice()
    for (let i = 0; i < submissionUuids.length; i++) {
      await _wizardSaveSubmission({ state, commit }, apiSet, i, submissionUuids[i])
    }
    // Remove submissions from old model data that are not present in the current submission set any more.
    if (submissionSetExists) {
      const oldSubmissionSet = state.oldModel.submissionSets[state.currentSubmissionSet.sodar_uuid]
      for (const oldSubmissionUuid of oldSubmissionSet.submissions) {
        if (!(oldSubmissionUuid in state.submissions)) {
          const oldSubmission = state.oldModel.submissions[oldSubmissionUuid]
          for (const oldSubmissionIndividualUuid of oldSubmission.submission_individuals) {
            await clinvarExport.deleteSubmissionIndividual(
              state.oldModel.submissionIndividuals[oldSubmissionIndividualUuid],
              state.appContext
            )
            commit('DELETE_SUBMISSION_INDIVIDUAL', oldSubmissionIndividualUuid)
          }
          await clinvarExport.deleteSubmission(oldSubmission, state.appContext)
          commit('DELETE_SUBMISSION', oldSubmissionUuid)
        }
      }
    }

    // Finalization, remove old state.currentSubmissionSet if necessary, save old model data.
    if (!submissionSetExists) {
      // Delete old local/temporary submission set if necessary.
      commit('DELETE_SUBMISSION_SET', state.currentSubmissionSet.sodar_uuid)
    }

    commit('SET_CURRENT_SUBMISSION_SET', null)
    commit('SET_CURRENT_SUBMISSION', null)

    commit('SAVE_OLD_MODEL')
  },
  /**
   * Remove submission set currently open in wizard through API.
   */
  async wizardRemove ({ state, commit }) {
    commit('SET_APP_STATE', AppState.list)

    for (const submittingOrgUuid of state.currentSubmissionSet.submitting_orgs) {
      if (submittingOrgUuid in state.oldModel.submittingOrgs) {
        await clinvarExport.deleteSubmittingOrg(
          state.submittingOrgs[submittingOrgUuid],
          state.appContext
        )
      }
      commit('DELETE_SUBMITTING_ORG', submittingOrgUuid)
    }

    const submissionUuids = Array.from(state.currentSubmissionSet.submissions)
    for (const submissionUuid of submissionUuids) {
      const submissionInvidualUuids = Array.from(state.submissions[submissionUuid].submission_individuals)
      for (const submissionInvidualUuid of submissionInvidualUuids) {
        if (submissionInvidualUuid in state.oldModel.submissionIndividuals) {
          await clinvarExport.deleteSubmissionIndividual(
            state.submissionIndividuals[submissionInvidualUuid],
            state.appContext
          )
        }
        commit('DELETE_SUBMISSION_INDIVIDUAL', submissionInvidualUuid)
      }
      if (submissionUuid in state.oldModel.submissions) {
        await clinvarExport.deleteSubmission(
          state.submissions[submissionUuid],
          state.appContext
        )
      }
      commit('DELETE_SUBMISSION', submissionUuid)
    }

    if (state.currentSubmissionSet.sodar_uuid in state.oldModel.submissionSets) {
      await clinvarExport.deleteSubmissionSet(
        state.submissionSets[state.currentSubmissionSet.sodar_uuid],
        state.appContext
      )
    }
    commit('DELETE_SUBMISSION_SET', state.currentSubmissionSet.sodar_uuid)

    commit('SET_CURRENT_SUBMISSION_SET', null)
    commit('SET_CURRENT_SUBMISSION', null)

    commit('SAVE_OLD_MODEL')
  },
  /**
   * Cancel submission editing currently open in wizard.
   */
  wizardCancel ({ commit }) {
    commit('SET_APP_STATE', AppState.list)
    commit('SET_CURRENT_SUBMISSION', null)
    commit('SET_CURRENT_SUBMISSION_SET', null)
    commit('RESTORE_OLD_MODEL')
  },
  /**
   * Set property of `currentSubmissionSet`.
   */
  updateCurrentSubmissionSet ({ commit }, { key, value }) {
    commit('UPDATE_CURRENT_SUBMISSION_SET', { key, value })
  },
  /**
   * Set the organisations member of currentSubmissionSet via submitting orgs.
   */
  updateCurrentSubmissionSetOrganisations ({ state, commit }, organisations) {
    commit('UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS', organisations)
  },
  /**
   * Select a certain submission in the current submission set.
   */
  selectCurrentSubmission ({ commit }, submissionUuid) {
    commit('SET_CURRENT_SUBMISSION', submissionUuid)
  },
  /**
   * Set property of `currentSubmission`.
   */
  updateCurrentSubmission ({ commit }, { key, value }) {
    commit('UPDATE_CURRENT_SUBMISSION', { key, value })
  },
  /**
   * Create new submission with the given data and individuals in `currentSubmissionSet` and set as `currentSubmission`.
   */
  createSubmissionInCurrentSubmissionSet ({ commit }, { smallVariant, submission, individualUuids }) {
    commit('CREATE_SUBMISSION_IN_CURRENT_SUBMISSION_SET', { smallVariant, submission, individualUuids })
  },
  /**
   * Move current submission up or down using the sort order.
   */
  moveCurrentSubmission ({ state, commit }, up) {
    const c = state.currentSubmission.sort_order
    const next = (acc, loc) => (loc.sort_order > c && loc.sort_order < acc.sort_order) ? loc : acc
    const prev = (acc, loc) => (loc.sort_order < c && loc.sort_order > acc.sort_order) ? loc : acc
    const other = state
      .currentSubmissionSet
      .submissions
      .map(k => state.submissions[k])
      .filter(o => o.sort_order !== c)
      .reduce(up ? next : prev)
    if (other) {
      const c2 = other.sort_order
      if (other) {
        commit('UPDATE_CURRENT_SUBMISSION', { key: 'sort_order', value: c2 })
        commit('UPDATE_SUBMISSION', { submission: other, key: 'sort_order', value: c })
      }
    }
  },
  /**
   * Apply sort order of submission list.
   */
  applySubmissionListSortOrder ({ commit }, lst) {
    const updateArr = lst.map((s, i) => [s.sodar_uuid, i])
    updateArr.sort((a, b) => a[1] - b[1])
    const updateMap = Object.fromEntries(updateArr)
    commit('APPLY_SUBMISSION_LIST_ORDER', updateMap)
  },
  /**
   * Delete the current submission.
   */
  deleteCurrentSubmission ({ state, commit }) {
    const submissionInvidualUuids = Array.from(state.currentSubmission.submission_individuals)
    for (const submissionInvidualUuid of submissionInvidualUuids) {
      commit('DELETE_SUBMISSION_INDIVIDUAL', submissionInvidualUuid)
    }
    commit('DELETE_SUBMISSION', state.currentSubmission.sodar_uuid)
    commit('SET_CURRENT_SUBMISSION', null)
  },
  /**
   * Add the given individual to the current submission.
   */
  addIndividualToCurrentSubmission ({ commit }, individual) {
    commit('ADD_INDIVIDUAL_TO_CURRENT_SUBMISSION', individual)
  },
  /**
   * Update the given submission individual.
   */
  updateSubmissionIndividual ({ commit }, payload) {
    commit('UPDATE_SUBMISSION_INDIVIDUAL', payload)
  },
  /**
   * Move submission individual up/down.
   */
  moveSubmissionIndividual ({ state, commit }, { submissionIndividual, up }) {
    const c = submissionIndividual.sort_order
    const next = (acc, loc) => (loc.sort_order > c && loc.sort_order < acc.sort_order) ? loc : acc
    const prev = (acc, loc) => (loc.sort_order < c && loc.sort_order > acc.sort_order) ? loc : acc
    const other = state
      .currentSubmission
      .submission_individuals
      .map(k => state.submissionIndividuals[k])
      .filter(o => o.sort_order !== c)
      .reduce(up ? next : prev)
    if (other) {
      const c2 = other.sort_order
      if (other) {
        commit('UPDATE_CURRENT_SUBMISSION', { key: 'sort_order', value: c2 })
        commit('UPDATE_SUBMISSION', { submission: other, key: 'sort_order', value: c })
      }
    }
  },
  /**
   * Remove submission individual from current submission.
   */
  removeSubmissionIndividualFromCurrentSubmission ({ state, commit }, submissionIndividual) {
    commit(
      'UPDATE_CURRENT_SUBMISSION',
      {
        key: 'submission_individuals',
        value: state.currentSubmission.submission_individuals.filter(uuid => uuid !== submissionIndividual.sodar_uuid)
      }
    )
  }
}

/**
 * Convert Array of objects with `sodar_uuid` member to mapping from UUID to object.
 *
 * @param lst Array with such objects.
 * @return Object with the mapping.
 */
function sodarObjectListToObject (lst) {
  return Object.fromEntries(lst.map(o => [o.sodar_uuid, o]))
}

/**
 * Extract variant zygosity information from state for the given smallVariant.
 */
function extractVariantZygosity (smallVariant, individualUuids, state) {
  function getVariantZygosity (variantAlleleCount, isRecessive) {
    if (variantAlleleCount === 2) {
      return 'Homozygote'
    } else {
      if (isRecessive) {
        return 'Compound heterozygote'
      } else {
        return 'Single heterozygote'
      }
    }
  }

  // See whether any individual is annotated as recessive.
  let anyRecessive = false
  let variantAlleleCount = null
  let variantZygosity = null
  if (smallVariant !== null) {
    let individual = null
    for (const individualUuid of individualUuids) {
      const currIndividual = state.individuals[individualUuid]
      if (individual === null) {
        individual = currIndividual
      }
      console.log('A')
      if (variantAlleleCount === null && (individual.name in smallVariant.genotype)) {
        variantAlleleCount = ((smallVariant.genotype[individual.name].gt || '').match(/1/g) || []).length
      }
      console.log('B', individual)
      if (individual !== null) {
        // eslint-disable-next-line camelcase
        for (const { term_id } of (individual.phenotype_terms || [])) {
          anyRecessive = anyRecessive || (HPO_INHERITANCE_MODE.get(term_id) || '').includes('recessive')
        }
      }
      console.log('C')
    }
    if (variantAlleleCount === null) {
      variantAlleleCount = 0
    }
    if (individual && variantAlleleCount) {
      if (smallVariant.chromosome.includes('X')) {
        if (individual.sex === 'female') {
          variantZygosity = getVariantZygosity(variantAlleleCount, anyRecessive)
        } else {
          variantAlleleCount = 1
          variantZygosity = 'Hemizygote'
        }
      } else if (smallVariant.chromosome.includes('Y')) {
        if (individual.sex === 'female') {
          variantAlleleCount = 0
          variantZygosity = 'not provided'
        } else {
          variantAlleleCount = 1
          variantZygosity = 'Hemizygote'
        }
      } else {
        variantZygosity = getVariantZygosity(variantAlleleCount, anyRecessive)
      }
    }
  }
  return { variantAlleleCount, variantZygosity }
}

const mutations = {
  // set application state without direct correlation in API backend

  SET_APP_CONTEXT (state, appContext) {
    Vue.set(state, 'appContext', appContext)
  },

  SET_APP_STATE (state, appState) {
    Vue.set(state, 'appState', appState)
  },

  SET_CURRENT_SUBMISSION_SET (state, submissionSetUuid) {
    console.assert(
      (submissionSetUuid === null) || (submissionSetUuid in state.submissionSets),
      submissionSetUuid,
      state.submissionSets
    )
    Vue.set(state, 'currentSubmissionSet', state.submissionSets[submissionSetUuid])
  },

  INITIALIZE_SUBMISSION_SET_ORGANISATIONS (state) {
    for (const submissionSet of Object.values(state.submissionSets)) {
      submissionSet.organisations = submissionSet.submitting_orgs
        .map(subOrgUuid => state.submittingOrgs[subOrgUuid].organisation)
    }
  },

  /**
   * Store current model state into `state.oldModel`.
   */
  SAVE_OLD_MODEL (state) {
    Vue.set(state, 'oldModel', JSON.parse(JSON.stringify(Object.fromEntries(MODEL_KEYS.map(k => [k, state[k]])))))
  },

  /**
   * Restore current model state from `state.oldModel`.
   */
  RESTORE_OLD_MODEL (state) {
    for (const key of MODEL_KEYS) {
      Vue.set(state, key, state.oldModel[key])
    }
    Vue.set(state, 'submissionSetList', Object.values(state.submissionSets))
  },

  // complex actions

  /**
   * Add a freshly created `submissionSet` into the store.
   */
  ADD_SUBMISSION_SET (state, submissionSet) {
    state.submissionSetList.push(submissionSet)
    Vue.set(state.submissionSets, submissionSet.sodar_uuid, submissionSet)
  },

  // set data retrieved from API

  SET_ORGANISATIONS (state, values) {
    Vue.set(state, 'organisations', sodarObjectListToObject(values))
  },

  SET_SUBMITTERS (state, values) {
    Vue.set(state, 'submitters', sodarObjectListToObject(values))
  },

  SET_ASSERTION_METHODS (state, values) {
    Vue.set(state, 'assertionMethods', sodarObjectListToObject(values))
  },

  SET_SUBMISSION_SETS (state, values) {
    Vue.set(state, 'submissionSets', sodarObjectListToObject(values))
    Vue.set(state, 'submissionSetList', Object.values(state.submissionSets))
  },

  SET_SUBMISSION_SET_LIST (state, value) {
    Vue.set(state, 'submissionSetList', value)
  },

  ADD_SUBMITTING_ORG_TO_SUBMISSION_SET (state, { submissionSet, submittingOrg }) {
    state.submissionSets[submissionSet].submitting_orgs.push(submittingOrg)
  },

  ADD_SUBMITTING_ORG (state, submittingOrg) {
    Vue.set(state.submittingOrgs, submittingOrg.sodar_uuid, submittingOrg)
  },

  ADD_SUBMISSION (state, submission) {
    Vue.set(state.submissions, submission.sodar_uuid, submission)
  },

  ADD_SUBMISSION_TO_SUBMISSION_SET (state, { submissionSet, submission }) {
    state.submissionSets[submissionSet].submissions.push(submission)
  },

  SET_SUBMISSIONS (state, values) {
    Vue.set(state, 'submissions', sodarObjectListToObject(values))
  },

  SET_INDIVIDUALS (state, values) {
    Vue.set(state, 'individuals', sodarObjectListToObject(values))
  },

  SET_SUBMISSION_INDIVIDUALS (state, values) {
    Vue.set(state, 'submissionIndividuals', sodarObjectListToObject(values))
  },

  SET_FAMILIES (state, values) {
    Vue.set(state, 'families', sodarObjectListToObject(values))
  },

  SET_SUBMITTING_ORGS (state, values) {
    Vue.set(state, 'submittingOrgs', sodarObjectListToObject(values))
  },

  SET_USER_ANNOTATIONS (state, value) {
    const getVariantId = (obj) => {
      return `${obj.release}-${obj.chromosome}-${obj.start}-${obj.reference}-${obj.alternative}`
    }

    const collect = (arr) => {
      const result = {}
      for (const obj of arr) {
        if (getVariantId(obj) in result) {
          result[getVariantId(obj)].push(obj)
        } else {
          Vue.set(result, getVariantId(obj), [obj])
        }
      }
      for (const arr of Object.values(result)) {
        arr.sort((a, b) => (a.case_name < b.case_name) ? -1 : 1)
      }
      return result
    }

    const smallVariants = {}
    for (const smallVar of value.small_variants) {
      if (getVariantId(smallVar) in smallVariants) {
        smallVariants[getVariantId(smallVar)].caseNames.push(smallVar.case_name)
        Vue.set(
          smallVariants[getVariantId(smallVar)],
          'genotype',
          {
            ...smallVariants[getVariantId(smallVar)].genotype,
            ...smallVar.genotype
          }
        )
      } else {
        Vue.set(
          smallVariants,
          getVariantId(smallVar),
          {
            ...smallVar,
            caseNames: [smallVar.case_name],
            variantId: getVariantId(smallVar)
          }
        )
        Vue.delete(smallVariants[getVariantId(smallVar)], 'case_name')
      }
    }
    for (const arr of Object.values(smallVariants)) {
      arr.caseNames = [...new Set(arr.caseNames)]
      arr.caseNames.sort((a, b) => (a.case_name < b.case_name) ? -1 : 1)
    }

    const userAnnotations = {
      smallVariants,
      smallVariantFlags: collect(value.small_variant_flags),
      smallVariantComments: collect(value.small_variant_comments),
      acmgCriteriaRating: collect(value.acmg_criteria_rating)
    }

    Vue.set(state, 'userAnnotations', userAnnotations)
  },

  SET_WIZARD_STATE (state, value) {
    Vue.set(state, 'wizardState', value)
  },

  SET_CURRENT_SUBMISSION (state, submissionUuid) {
    // console.assert((submissionUuid === null) || state.currentSubmissionSet)
    // console.assert(
    //   (submissionUuid === null) ||
    //   (state.currentSubmissionSet && state.currentSubmissionSet.submissions.includes(submissionUuid)),
    //   submissionUuid,
    //   state.currentSubmissionSet.submissions
    // )

    if ((submissionUuid === null) ||
        (state.currentSubmission &&
          state.currentSubmission &&
          state.currentSubmission.sodar_uuid === submissionUuid)) {
      Vue.set(state, 'currentSubmission', null)
    } else {
      Vue.set(state, 'currentSubmission', state.submissions[submissionUuid])
    }
  },

  UPDATE_CURRENT_SUBMISSION_SET (state, { key, value }) {
    console.assert(state.currentSubmissionSet, state.currentSubmissionSet)
    console.assert(key in state.currentSubmissionSet, state.currentSubmissionSet, key)
    Vue.set(state.currentSubmissionSet, key, value)
  },

  UPDATE_CURRENT_SUBMISSION_SET_ORGANISATIONS (state, shouldUuids) {
    // Build symmetric difference in terms of organisation UUIDs.
    const currUuids = new Set(state.currentSubmissionSet.organisations)
    const removeUuids = new Set(Array.from(currUuids).filter(uuid => !shouldUuids.includes(uuid)))
    const addUuids = new Set(Array.from(shouldUuids).filter(uuid => !currUuids.has(uuid)))

    // Remove submitting orgs as needed.
    const removeSOUuids = new Set(
      state.currentSubmissionSet.submitting_orgs
        .filter(soUuid => removeUuids.has(state.submittingOrgs[soUuid].organisation))
    )
    for (const uuid of removeSOUuids) {
      Vue.delete(state.submittingOrgs, uuid)
    }
    Vue.set(
      state.currentSubmissionSet,
      'submitting_orgs',
      state.currentSubmissionSet.submitting_orgs.filter(soUuid => !removeSOUuids.has(soUuid))
    )

    // Add submitting orgs as needed.
    for (const orgUuid of addUuids) {
      const newSubmittingOrg = {
        sodar_uuid: uuidv4(),
        organisation: orgUuid,
        submission_set: state.currentSubmissionSet.sodar_uuid,
        sort_order: 0
      }
      Vue.set(
        state.submittingOrgs,
        newSubmittingOrg.sodar_uuid,
        newSubmittingOrg
      )
      state.currentSubmissionSet.submitting_orgs.push(newSubmittingOrg.sodar_uuid)
    }

    // Update the current submission set properties.
    Vue.set(state.currentSubmissionSet, 'organisations', shouldUuids)
    // Adjust the sort order.
    const orgUuidToSortOrder = Object.fromEntries(shouldUuids.map((orgUuid, i) => [orgUuid, i]))
    for (const soUuid of state.currentSubmissionSet.submitting_orgs) {
      state.submittingOrgs[soUuid].sort_order = orgUuidToSortOrder[state.submittingOrgs[soUuid].organisation]
    }
    state.currentSubmissionSet.submitting_orgs.sort((a, b) => {
      return state.submittingOrgs[a].sort_order - state.submittingOrgs[b].sort_order
    })
  },

  UPDATE_CURRENT_SUBMISSION (state, { key, value }) {
    console.assert(state.currentSubmission, state.currentSubmission)
    console.assert(
      key.slice(0, 1) === '_' ||
      key in state.currentSubmission,
      state.currentSubmission,
      key
    )
    Vue.set(state.currentSubmission, key, value)
  },

  UPDATE_SUBMISSION (state, { submission, key, value }) {
    console.assert(submission.sodar_uuid in state.submissions, state.submissions, submission.sodar_uuid)
    console.assert(key in state.submissions[submission.sodar_uuid], state.submissions, submission.sodar_uuid)
    Vue.set(state.submissions[submission.sodar_uuid], key, value)
  },

  APPLY_SUBMISSION_LIST_ORDER (state, updateMap) {
    for (const [uuid, sortOrder] of Object.entries(updateMap)) {
      Vue.set(state.submissions[uuid], 'sort_order', sortOrder)
    }
  },

  DELETE_SUBMISSION (state, submissionUuid) {
    for (const submissionSet of Object.values(state.submissionSets)) {
      submissionSet.submissions = submissionSet.submissions.filter(o => o !== submissionUuid)
    }
    if (state.currentSubmission && state.currentSubmission.sodar_uuid === submissionUuid) {
      state.currentSubmission = null
    }
    Vue.delete(state.submissions, submissionUuid)
  },

  DELETE_SUBMITTING_ORG (state, submittingOrgUuid) {
    Vue.delete(state.submittingOrgs, submittingOrgUuid)
  },

  DELETE_SUBMISSION_SET (state, submissionSetUuid) {
    if (state.currentSubmissionSet && state.currentSubmissionSet.sodar_uuid === submissionSetUuid) {
      state.currentSubmissionSet = null
    }
    Vue.delete(state.submissionSets, submissionSetUuid)
    Vue.set(
      state,
      'submissionSetList',
      state.submissionSetList.filter(ss => ss.sodar_uuid !== submissionSetUuid)
    )
  },

  ADD_INDIVIDUAL_TO_CURRENT_SUBMISSION (state, individual) {
    const s = state.currentSubmission
    const variantKey = `${s.variant_assembly}-${s.variant_chromosome}` +
      `-${s.variant_start}-${s.variant_reference}-${s.variant_alternative}`
    const smallVariant = state.userAnnotations.smallVariants[variantKey]
    const { variantAlleleCount, variantZygosity } = extractVariantZygosity(
      smallVariant,
      [individual.sodar_uuid],
      state
    )

    const newUuid = uuidv4()
    Vue.set(
      state.submissionIndividuals,
      newUuid,
      {
        sodar_uuid: newUuid,
        sort_order: Object.keys(state.currentSubmission.submission_individuals).length,
        individual: individual.sodar_uuid,
        submission: state.currentSubmission.sodar_uuid,
        phenotypes: JSON.parse(JSON.stringify(state.individuals[individual.sodar_uuid].phenotype_terms)),
        variant_zygosity: variantZygosity,
        variant_allele_count: variantAlleleCount,
        variant_origin: 'germline',
        source: 'clinical testing',
        tissue: 'Blood',
        citations: []
      }
    )
    state.currentSubmission.submission_individuals.push(newUuid)
  },

  CREATE_SUBMISSION_IN_CURRENT_SUBMISSION_SET (state, { smallVariant, submission, individualUuids }) {
    // Create new submission from the given data with a new UUID.  Note well that this UUID will be overwritten
    // when sent to the UUID so it must be then updated locally.
    const newSubmission = {
      ...submission,
      _isInvalid: false,
      sodar_uuid: uuidv4(),
      sort_order: Object.keys(state.submissions).length,
      submission_individuals: []
    }
    const { variantAlleleCount, variantZygosity } = extractVariantZygosity(smallVariant, individualUuids, state)

    for (const individualUuid of individualUuids) {
      const individual = state.individuals[individualUuid]
      const phenotypes = JSON.parse(JSON.stringify(individual.phenotype_terms || []))
        .filter(term => !HPO_INHERITANCE_MODE.has(term.term_id) && !isDiseaseTerm(term.term_id))
      const newSubmissionIndividual = {
        sodar_uuid: uuidv4(),
        individual: individualUuid,
        submission: newSubmission.sodar_uuid,
        phenotypes: phenotypes,
        variant_allele_count: variantAlleleCount,
        variant_zygosity: variantZygosity,
        variant_origin: 'germline',
        source: 'clinical testing',
        tissue: 'Blood',
        citations: []
      }
      Vue.set(state.submissionIndividuals, newSubmissionIndividual.sodar_uuid, newSubmissionIndividual)
      newSubmission.submission_individuals.push(newSubmissionIndividual.sodar_uuid)
    }

    Vue.set(state.submissions, newSubmission.sodar_uuid, newSubmission)
    Vue.set(state, 'currentSubmission', newSubmission)
    state.currentSubmissionSet.submissions.push(newSubmission.sodar_uuid)
  },

  UPDATE_SUBMISSION_INDIVIDUAL (state, { submissionIndividual, key, value }) {
    console.assert(
      submissionIndividual.sodar_uuid in state.submissionIndividuals,
      state.submissionIndividuals,
      submissionIndividual.sodar_uuid
    )
    const obj = state.submissionIndividuals[submissionIndividual.sodar_uuid]
    Vue.set(obj, key, value)
  },

  DELETE_SUBMISSION_INDIVIDUAL (state, submissionInvidualUuid) {
    for (const submission of Object.values(state.submissions)) {
      if (submission.submission_individuals.includes(submissionInvidualUuid)) {
        submission.submission_individuals = submission.submission_individuals
          .filter(uuid => uuid !== submissionInvidualUuid)
      }
    }
    Vue.delete(state.submissionIndividuals, submissionInvidualUuid)
  },

  ADD_SUBMISSION_INDIVIDUAL (state, submissionIndividual) {
    Vue.set(state.submissionIndividuals, submissionIndividual.sodar_uuid, submissionIndividual)
  },

  ADD_SUBMISSION_INDIVIDUAL_TO_SUBMISSION (state, { submissionIndividual, submission }) {
    state.submissions[submission].submission_individuals.push(submissionIndividual)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
