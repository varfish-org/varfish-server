import clinvarExportApi from '@clinvarexport/api/clinvarExport'
import {
  getVariantId,
  HPO_INHERITANCE_MODE,
  isDiseaseTerm,
  uuidv4,
} from '@clinvarexport/helpers'
import { sodarObjectListToObject } from '@varfish/api-utils'
import { defineStore } from 'pinia'

/**
 * Enum for the valid clinvar export application states.
 */
export const AppState = Object.freeze({
  initializing: 'initializing',
  list: 'list',
  edit: 'edit',
  add: 'add',
})

/**
 * Enum for the valid submission set wizard this.
 */
export const WizardState = Object.freeze({
  submissionSet: 'submissionSet',
  submissions: 'submissions',
})

/**
 * List of model keys.
 */
export const MODEL_KEYS = Object.freeze([
  'organisations',
  'families',
  'individuals',
  'assertionMethods',
  'submitters',
  'submissionSets',
  'submissions',
  'submissionIndividuals',
  'submittingOrgs',
])

export const SUBMISSION_SET_STATE_CHOICES = Object.freeze([
  'draft',
  'discontinued',
  'pending',
  'submitted',
  'released',
  'rejected',
])

export const VARIANT_ZYGOSITY_OPTIONS = Object.freeze([
  'Homozygote',
  'Single heterozygote',
  'Compound heterozygote',
  'Hemizygote',
  'not provided',
])
export const VARIANT_ORIGIN_OPTIONS = Object.freeze([
  'not provided',
  'germline',
  'somatic',
  'de novo',
  'unknown',
  'inherited',
  'maternal',
  'paternal',
  'uniparental',
  'biparental',
  'not-reported',
  'tested-inconclusive',
  'not applicable',
  'experimentally generated',
])
export const SAMPLE_SOURCE_OPTIONS = Object.freeze([
  'curation',
  'literature only',
  'provider interpretation',
  'phenotyping only',
  'case-control',
  'clinical testing',
  'in vitro',
  'in vivo',
  'research',
  'not provided',
])

export const RECORD_STATUS_OPTIONS = Object.freeze([
  'novel',
  'update',
  'delete',
])
export const RELEASE_STATUS_OPTIONS = Object.freeze([
  'public',
  'hold until published',
])
export const SIGNIFICANCE_STATUS_OPTIONS = Object.freeze([
  'no assertion provided',
  'no assertion criteria provided',
  'criteria provided, single submitter',
  'criteria provided, multiple submitters, no conflicts',
  'criteria provided, conflicting interpretations',
  'reviewed by expert panel',
  'practice guideline',
])
export const SIGNIFICANCE_DESCRIPTION_OPTIONS = Object.freeze([
  '',
  'Benign',
  'Likely benign',
  'Uncertain significance',
  'Likely pathogenic',
  'Pathogenic',
])
export const VARIANT_ASSEMBLY_OPTIONS = Object.freeze(['GRCh37', 'GRCh38'])
export const MODE_OF_INHERITANCE_OPTIONS = Object.freeze([
  '',
  'Other',
  'Autosomal dominant contiguous gene syndrome',
  'Autosomal dominant germline de novo mutation',
  'Autosomal dominant inheritance',
  'Autosomal dominant inheritance with maternal imprinting',
  'Autosomal dominant inheritance with paternal imprinting',
  'Autosomal dominant somatic cell mutation',
  'Autosomal recessive inheritance',
  'Contiguous gene syndrome',
  'Digenic inheritance',
  'Genetic anticipation',
  'Genetic anticipation with paternal anticipation bias',
  'Gonosomal inheritance',
  'Heterogeneous',
  'Male-limited autosomal dominant',
  'Mitochondrial inheritance',
  'Multifactorial inheritance',
  'Oligogenic inheritance',
  'Polygenic inheritance',
  'Semidominant mode of inheritance',
  'Sex-limited autosomal dominant',
  'Sex-limited autosomal recessive inheritance',
  'Somatic mosaicism',
  'Somatic mutation',
  'Sporadic',
  'Uniparental disomy',
  'Uniparental heterodisomy',
  'Uniparental isodisomy',
  'X-linked dominant inheritance',
  'X-linked inheritance',
  'X-linked recessive inheritance',
])
export const AGE_OF_ONSET_OPTIONS = Object.freeze([
  '',
  'Antenatal',
  'Embryonal',
  'Fetal',
  'Pediatric',
  'Infantile',
  'Childhood',
  'Juvenile',
  'Adult',
  'Neonatal',
  'Young adult',
  'Middle age',
  'Late',
  'Congenital',
])
export const VARIANT_TYPE = Object.freeze([
  'Variation',
  'Deletion',
  'Duplication',
])

/**
 * Extract variant zygosity information from this for the given smallVariant.
 */
export function extractVariantZygosity(
  smallVariant,
  individualUuids,
  individuals,
) {
  function getVariantZygosity(variantAlleleCount, isRecessive) {
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
  if (smallVariant !== null && smallVariant !== undefined) {
    let individual = null
    for (const individualUuid of individualUuids) {
      const currIndividual = individuals[individualUuid]
      if (individual === null) {
        individual = currIndividual
      }
      if (
        variantAlleleCount === null &&
        individual.name in smallVariant.genotype
      ) {
        variantAlleleCount = (
          (smallVariant.genotype[individual.name].gt || '').match(/1/g) || []
        ).length
      }
      if (individual !== null) {
        // eslint-disable-next-line camelcase
        for (const { term_id } of individual.phenotype_terms || []) {
          anyRecessive =
            anyRecessive ||
            (HPO_INHERITANCE_MODE.get(term_id) || '').includes('recessive')
        }
      }
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
  if (variantAlleleCount === null) {
    variantAlleleCount = 0
  }
  if (variantZygosity === null) {
    variantZygosity = 'not provided'
  }
  return { variantAlleleCount, variantZygosity }
}

export const useClinvarExportStore = defineStore('clinvarExport', {
  state: () => ({
    // application / client this
    appContext: null,
    appState: AppState.initializing,
    serverInteraction: false,
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
    submissionSetList: [],
  }),
  getters: {},
  actions: {
    /**
     * Initialize the store from the remote URL.
     */
    initialize: async function (appContext) {
      this.appContext = appContext
      this.appState = AppState.initializing

      return Promise.all([
        clinvarExportApi.getOrganisations(this.appContext).then((res) => {
          this.organisations = sodarObjectListToObject(res)
        }),
        clinvarExportApi
          .getSubmitters(this.appContext)
          .then((res) => (this.submitters = sodarObjectListToObject(res))),
        clinvarExportApi
          .getAssertionMethods(this.appContext)
          .then(
            (res) => (this.assertionMethods = sodarObjectListToObject(res)),
          ),
        clinvarExportApi
          .getSubmissionSets(this.appContext)
          .then((res) => this.setSubmissionSets(res)),
        clinvarExportApi
          .getSubmissions(this.appContext)
          .then((res) => (this.submissions = sodarObjectListToObject(res))),
        clinvarExportApi
          .getIndividuals(this.appContext)
          .then((res) => (this.individuals = sodarObjectListToObject(res))),
        clinvarExportApi
          .getSubmissionIndividuals(this.appContext)
          .then(
            (res) =>
              (this.submissionIndividuals = sodarObjectListToObject(res)),
          ),
        clinvarExportApi
          .getFamilies(this.appContext)
          .then((res) => (this.families = sodarObjectListToObject(res))),
        clinvarExportApi
          .getSubmittingOrgs(this.appContext)
          .then((res) => (this.submittingOrgs = sodarObjectListToObject(res))),
      ]).then(
        (_response) => {
          for (const submissionSet of Object.values(this.submissionSets)) {
            submissionSet.organisations = submissionSet.submitting_orgs.map(
              (subOrgUuid) => this.submittingOrgs[subOrgUuid].organisation,
            )
          }
          this.saveOldModel()
          this.appState = AppState.list
        },
        (error) => {
          /* istanbul ignore next */
          throw new Error(
            `Problem loading application this from API: ${error}\n\n${error.stack}`,
          )
        },
      )
    },
    /**
     * Make clinvar export editor edit the submission with the given ID.
     */
    editSubmissionSet(submissionSetUuid) {
      this.setCurrentSubmissionSet(submissionSetUuid)
      this.appState = AppState.edit
    },
    /**
     * Make clinvar export editor create a new submission (without committing through API) and edit it.
     *
     * Changes will be committed through `wizardSave`.
     */
    createNewSubmissionSet() {
      const titles = Object.values(this.submissionSets).map(
        (submissionSet) => submissionSet.title,
      )
      let title = 'New Submission Set'
      let i = 2
      while (titles.includes(title)) {
        title = 'New Submission Set #' + i
        i += 1
      }
      const submissionSet = {
        sodar_uuid: uuidv4(),
        date_modified: new Date().toLocaleString(),
        title,
        state: 'draft',
        sort_order: Object.keys(this.submissionSets).length,
        submitter: null,
        organisations: [],
        submitting_orgs: [],
        submissions: [],
      }

      this.addSubmissionSet(submissionSet)
      this.setCurrentSubmissionSet(submissionSet.sodar_uuid)
      this.wizardState = WizardState.submissionSet
      this.appState = AppState.add
    },
    /**
     * Update the `wizardState`.
     */
    setWizardState(value) {
      this.wizardState = value
    },

    /**
     * Save submission set currently open in wizard through API.
     */
    async wizardSave() {
      this.serverInteraction = true
      const _wizardSaveSubmissionSet = async (submissionSetExists) => {
        if (submissionSetExists) {
          const res = await clinvarExportApi.updateSubmissionSet(
            this.currentSubmissionSet,
            this.appContext,
          )
          return res
        } else {
          const apiSet = await clinvarExportApi.createSubmissionSet(
            this.currentSubmissionSet,
            this.appContext,
          )
          // Add submission set from API.  Then change the list to first remove the just added apiSet and replace the
          // old one with the one from the API.
          this.addSubmissionSet(apiSet)
          this.submissionSetList = this.submissionSetList
            .filter((ss) => ss.sodar_uuid !== apiSet.sodar_uuid)
            .map((ss) =>
              ss.sodar_uuid === this.currentSubmissionSet.sodar_uuid
                ? apiSet
                : ss,
            )
          return apiSet
        }
      }

      const _wizardSaveApplySubmittingOrgs = async (apiSet) => {
        // Remove existing submitting orgs that are not present in the old store.
        if (apiSet.sodar_uuid in this.oldModel.submissionSets) {
          const oldSubmissionSet =
            this.oldModel.submissionSets[apiSet.sodar_uuid]
          for (let i = 0; i < oldSubmissionSet.submitting_orgs.length; i++) {
            const localSubmittingOrgUuid = oldSubmissionSet.submitting_orgs[i]
            if (!(localSubmittingOrgUuid in this.submittingOrgs)) {
              await clinvarExportApi.deleteSubmittingOrg(
                this.oldModel.submittingOrgs[localSubmittingOrgUuid],
                this.appContext,
              )
            }
          }
        }
        // Create and update appropriate submitting orgs with API.
        const submitting_orgs = Array.from(
          this.currentSubmissionSet.submitting_orgs,
        )
        this.currentSubmissionSet.submitting_orgs = []
        for (let i = 0; i < submitting_orgs.length; i++) {
          const localUuid = submitting_orgs[i]
          if (localUuid in this.oldModel.submittingOrgs) {
            await clinvarExportApi.updateSubmittingOrg(
              {
                ...JSON.parse(JSON.stringify(this.submittingOrgs[localUuid])),
                sort_order: i,
              },
              this.appContext,
            )
            this.currentSubmissionSet.submitting_orgs.push(submitting_orgs[i])
          } else {
            const apiSubmittingOrg = await clinvarExportApi.createSubmittingOrg(
              {
                ...JSON.parse(JSON.stringify(this.submittingOrgs[localUuid])),
                sort_order: i,
                submission_set: apiSet.sodar_uuid,
              },
              this.appContext,
            )
            this.submittingOrgs[apiSubmittingOrg.sodar_uuid] = apiSubmittingOrg
            this.submissionSets[apiSet.sodar_uuid].submitting_orgs.push(
              apiSubmittingOrg.sodar_uuid,
            )
            delete this.submittingOrgs[localUuid]
          }
        }
      }

      const _wizardSaveSubmission = async (
        apiSet,
        sortOrder,
        localSubmissionUuid,
      ) => {
        const submissionExists =
          localSubmissionUuid in this.oldModel.submissions
        const localSubmission = this.submissions[localSubmissionUuid]
        let apiSubmission = null
        if (submissionExists) {
          apiSubmission = await clinvarExportApi.updateSubmission(
            {
              ...JSON.parse(JSON.stringify(localSubmission)),
              sort_order: sortOrder,
            },
            this.appContext,
          )
        } else {
          apiSubmission = await clinvarExportApi.createSubmission(
            {
              ...JSON.parse(JSON.stringify(localSubmission)),
              sort_order: sortOrder,
              submission_set: apiSet.sodar_uuid,
            },
            this.appContext,
          )
          // Register submission from API.
          this.submissions[apiSubmission.sodar_uuid] = apiSubmission
          this.submissionSets[apiSet.sodar_uuid].submissions.push(
            apiSubmission.sodar_uuid,
          )
        }

        // Delete submission individuals from old data that are not in current data.
        if (submissionExists) {
          const oldSubmission =
            this.oldModel.submissions[localSubmission.sodar_uuid]
          for (
            let i = 0;
            i < oldSubmission.submission_individuals.length;
            i++
          ) {
            const localIndividualUuid = oldSubmission.submission_individuals[i]
            if (
              !localSubmission.submission_individuals.includes(
                localIndividualUuid,
              )
            ) {
              await clinvarExportApi.deleteSubmissionIndividual(
                this.oldModel.submissionIndividuals[localIndividualUuid],
                this.appContext,
              )
            }
          }
        }

        // Copy over submission individuals and delete local ones.
        const keys = Array.from(localSubmission.submission_individuals)
        for (let i = 0; i < keys.length; i++) {
          const localIndividualUuid = keys[i]
          const localSI = this.submissionIndividuals[localIndividualUuid]
          const localSubmissionIndividualExists =
            localSI.sodar_uuid in this.oldModel.submissionIndividuals
          let apiSubmissionIndividual = null
          if (localSubmissionIndividualExists) {
            apiSubmissionIndividual =
              await clinvarExportApi.updateSubmissionIndividual(
                {
                  ...JSON.parse(JSON.stringify(localSI)),
                  sort_order: i,
                },
                this.appContext,
              )
          } else {
            apiSubmissionIndividual =
              await clinvarExportApi.createSubmissionIndividual(
                {
                  ...JSON.parse(JSON.stringify(localSI)),
                  sort_order: i,
                  submission: apiSubmission.sodar_uuid,
                },
                this.appContext,
              )

            // Register submission individual from API.
            if (!localSubmissionIndividualExists) {
              this.submissionIndividuals[apiSubmissionIndividual.sodar_uuid] =
                apiSubmissionIndividual
              this.submissions[
                apiSubmission.sodar_uuid
              ].submission_individuals.push(apiSubmissionIndividual.sodar_uuid)
              // Delete local submission individual if necessary.
              this.deleteSubmissionIndividual(localIndividualUuid)
            }
          }
        }

        // Delete local submission.
        if (!submissionExists) {
          this.deleteSubmission(localSubmissionUuid)
        }
      }

      // Save submission set and submitting orgs.
      const submissionSetExists =
        this.currentSubmissionSet.sodar_uuid in this.oldModel.submissionSets
      const apiSet = await _wizardSaveSubmissionSet(submissionSetExists)
      await _wizardSaveApplySubmittingOrgs(apiSet)

      // Create appropriate submissions with API, copy over individuals and remove local submissions and submission
      // individuals.
      const submissionUuids = this.currentSubmissionSet.submissions.slice()
      for (let i = 0; i < submissionUuids.length; i++) {
        await _wizardSaveSubmission(apiSet, i, submissionUuids[i])
      }
      // Remove submissions from old model data that are not present in the current submission set any more.
      if (submissionSetExists) {
        const oldSubmissionSet =
          this.oldModel.submissionSets[this.currentSubmissionSet.sodar_uuid]
        for (const oldSubmissionUuid of oldSubmissionSet.submissions) {
          if (!(oldSubmissionUuid in this.submissions)) {
            const oldSubmission = this.oldModel.submissions[oldSubmissionUuid]
            for (const oldSubmissionIndividualUuid of oldSubmission.submission_individuals) {
              await clinvarExportApi.deleteSubmissionIndividual(
                this.oldModel.submissionIndividuals[
                  oldSubmissionIndividualUuid
                ],
                this.appContext,
              )
              this.deleteSubmissionIndividual(oldSubmissionIndividualUuid)
            }
            await clinvarExportApi.deleteSubmission(
              oldSubmission,
              this.appContext,
            )
            this.deleteSubmission(oldSubmissionUuid)
          }
        }
      }

      // Finalization, remove old this.currentSubmissionSet if necessary, save old model data.
      if (!submissionSetExists) {
        // Delete old local/temporary submission set if necessary.
        this.deleteSubmissionSet(this.currentSubmissionSet.sodar_uuid)
      }

      this.setCurrentSubmissionSet(null)
      this.setCurrentSubmission(null)

      this.saveOldModel()
      this.appState = AppState.list
      this.serverInteraction = false
    },
    /**
     * Remove submission set currently open in wizard through API.
     */
    async wizardRemove() {
      this.serverInteraction = true
      this.appState = AppState.list

      for (const submittingOrgUuid of this.currentSubmissionSet
        .submitting_orgs) {
        if (submittingOrgUuid in this.oldModel.submittingOrgs) {
          await clinvarExportApi.deleteSubmittingOrg(
            this.submittingOrgs[submittingOrgUuid],
            this.appContext,
          )
        }
        delete this.submittingOrgs[submittingOrgUuid]
      }

      const submissionUuids = Array.from(this.currentSubmissionSet.submissions)
      for (const submissionUuid of submissionUuids) {
        const submissionInvidualUuids = Array.from(
          this.submissions[submissionUuid].submission_individuals,
        )
        for (const submissionInvidualUuid of submissionInvidualUuids) {
          if (submissionInvidualUuid in this.oldModel.submissionIndividuals) {
            await clinvarExportApi.deleteSubmissionIndividual(
              this.submissionIndividuals[submissionInvidualUuid],
              this.appContext,
            )
          }
          this.deleteSubmissionIndividual(submissionInvidualUuid)
        }
        if (submissionUuid in this.oldModel.submissions) {
          await clinvarExportApi.deleteSubmission(
            this.submissions[submissionUuid],
            this.appContext,
          )
        }
        this.deleteSubmission(submissionUuid)
      }

      if (
        this.currentSubmissionSet.sodar_uuid in this.oldModel.submissionSets
      ) {
        await clinvarExportApi.deleteSubmissionSet(
          this.submissionSets[this.currentSubmissionSet.sodar_uuid],
          this.appContext,
        )
      }
      this.deleteSubmissionSet(this.currentSubmissionSet.sodar_uuid)

      this.setCurrentSubmissionSet(null)
      this.setCurrentSubmission(null)

      this.saveOldModel()
      this.serverInteraction = false
    },
    /**
     * Cancel submission editing currently open in wizard.
     */
    wizardCancel() {
      this.appState = AppState.list
      this.setCurrentSubmission(null)
      this.setCurrentSubmissionSet(null)
      this.restoreOldModel()
    },
    /**
     * Select a certain submission in the current submission set.
     */
    selectCurrentSubmission(submissionUuid) {
      this.setCurrentSubmission(submissionUuid)
    },
    /**
     * Set property of `currentSubmission`.
     */
    updateCurrentSubmission({ key, value }) {
      this.currentSubmission[key] = value
    },
    /**
     * Move current submission up or down using the sort order.
     */
    moveCurrentSubmission(up) {
      const c = this.currentSubmission.sort_order
      const next = (acc, loc) =>
        loc.sort_order > c && loc.sort_order < acc.sort_order ? loc : acc
      const prev = (acc, loc) =>
        loc.sort_order < c && loc.sort_order > acc.sort_order ? loc : acc
      const other = this.currentSubmissionSet.submissions
        .map((k) => this.submissions[k])
        .filter((o) => o.sort_order !== c)
        .reduce(up ? next : prev)
      if (other) {
        const c2 = other.sort_order
        if (other) {
          this.updateCurrentSubmission({ key: 'sort_order', value: c2 })
          other.sort_order = c
        }
      }
    },
    /**
     * Apply sort order of submission list.
     */
    applySubmissionListSortOrder(lst) {
      const updateArr = lst.map((s, i) => [s.sodar_uuid, i])
      updateArr.sort((a, b) => a[1] - b[1])
      const updateMap = Object.fromEntries(updateArr)
      for (const [uuid, sortOrder] of Object.entries(updateMap)) {
        this.submissions[uuid].sort_order = sortOrder
      }
    },
    /**
     * Delete the current submission.
     */
    deleteCurrentSubmission() {
      const submissionInvidualUuids = Array.from(
        this.currentSubmission.submission_individuals,
      )
      for (const submissionInvidualUuid of submissionInvidualUuids) {
        this.deleteSubmissionIndividual(submissionInvidualUuid)
      }
      this.deleteSubmission(this.currentSubmission.sodar_uuid)
      this.setCurrentSubmission(null)
    },
    /**
     * Add the given individual to the current submission.
     */
    async addIndividualToCurrentSubmission(individual) {
      this.serverInteraction = true
      const res = await clinvarExportApi.getUserAnnotations(
        this.appContext,
        individual.family,
      )
      const smallVariants = Object.fromEntries(
        res.small_variants.map((v) => [getVariantId(v), v]),
      )
      this.addIndividualToCurrentSubmissionImpl({
        individual,
        smallVariants,
      })
      this.serverInteraction = false
    },
    /**
     * Update the given submission individual.
     */
    updateSubmissionIndividual({ submissionIndividual, key, value }) {
      console.assert(
        submissionIndividual.sodar_uuid in this.submissionIndividuals,
        this.submissionIndividuals,
        submissionIndividual.sodar_uuid,
      )
      const obj = this.submissionIndividuals[submissionIndividual.sodar_uuid]
      obj[key] = value
    },
    /**
     * Move submission individual up/down.
     */
    moveSubmissionIndividual({ submissionIndividual, up }) {
      const c = submissionIndividual.sort_order
      const next = (acc, loc) =>
        loc.sort_order > c && loc.sort_order < acc.sort_order ? loc : acc
      const prev = (acc, loc) =>
        loc.sort_order < c && loc.sort_order > acc.sort_order ? loc : acc
      const other = this.currentSubmission.submission_individuals
        .map((k) => this.submissionIndividuals[k])
        .filter((o) => o.sort_order !== c)
        .reduce(up ? next : prev)
      if (other) {
        const c2 = other.sort_order
        if (other) {
          submissionIndividual.sort_order = c2
          other.sort_order = c
        }
      }
    },
    /**
     * Remove submission individual from current submission.
     */
    removeSubmissionIndividualFromCurrentSubmission(submissionIndividual) {
      this.currentSubmission.submission_individuals =
        this.currentSubmission.submission_individuals.filter(
          (uuid) => uuid !== submissionIndividual.sodar_uuid,
        )
    },
    setCurrentSubmissionSet(submissionSetUuid) {
      console.assert(
        submissionSetUuid === null || submissionSetUuid in this.submissionSets,
        submissionSetUuid,
        this.submissionSets,
      )
      if (submissionSetUuid === null) {
        this.currentSubmissionSet = null
      } else {
        this.currentSubmissionSet = this.submissionSets[submissionSetUuid]
      }
    },
    /**
     * Store current model this into `this.oldModel`.
     */
    saveOldModel() {
      this.oldModel = JSON.parse(
        JSON.stringify(Object.fromEntries(MODEL_KEYS.map((k) => [k, this[k]]))),
      )
    },
    /**
     * Restore current model this from `this.oldModel`.
     */
    restoreOldModel() {
      for (const key of MODEL_KEYS) {
        this[key] = this.oldModel[key]
      }
      this.submissionSetList = Object.values(this.submissionSets)
    },
    /**
     * Add a freshly created `submissionSet` into the store.
     */
    addSubmissionSet(submissionSet) {
      this.submissionSetList.push(submissionSet)
      this.submissionSets[submissionSet.sodar_uuid] = submissionSet
    },
    setSubmissionSets(submissionSetList) {
      this.submissionSets = sodarObjectListToObject(submissionSetList)
      this.submissionSetList = Object.values(this.submissionSets)
    },

    deleteSubmissionIndividual(submissionInvidualUuid) {
      for (const submission of Object.values(this.submissions)) {
        if (
          submission.submission_individuals.includes(submissionInvidualUuid)
        ) {
          submission.submission_individuals =
            submission.submission_individuals.filter(
              (uuid) => uuid !== submissionInvidualUuid,
            )
        }
      }
      delete this.submissionIndividuals[submissionInvidualUuid]
    },
    deleteSubmission(submissionUuid) {
      for (const submissionSet of Object.values(this.submissionSets)) {
        submissionSet.submissions = submissionSet.submissions.filter(
          (o) => o !== submissionUuid,
        )
      }
      if (
        this.currentSubmission &&
        this.currentSubmission.sodar_uuid === submissionUuid
      ) {
        this.currentSubmission = null
      }
      delete this.submissions[submissionUuid]
    },
    deleteSubmissionSet(submissionSetUuid) {
      if (
        this.currentSubmissionSet &&
        this.currentSubmissionSet.sodar_uuid === submissionSetUuid
      ) {
        this.currentSubmissionSet = null
      }
      delete this.submissionSets[submissionSetUuid]
      this.submissionSetList = this.submissionSetList.filter(
        (ss) => ss.sodar_uuid !== submissionSetUuid,
      )
    },
    setCurrentSubmission(submissionUuid) {
      if (
        submissionUuid === null ||
        (this.currentSubmission &&
          this.currentSubmission.sodar_uuid === submissionUuid)
      ) {
        this.currentSubmission = null
      } else {
        this.currentSubmission = this.submissions[submissionUuid]
      }
    },

    createSubmissionInCurrentSubmissionSet({
      smallVariant,
      submission,
      individualUuids,
    }) {
      // Create new submission from the given data with a new UUID.  Note well that this UUID will be overwritten
      // when sent to the UUID so it must be then updated locally.
      const newSubmission = {
        ...submission,
        _isInvalid: false,
        sodar_uuid: uuidv4(),
        sort_order: Object.keys(this.submissions).length,
        submission_individuals: [],
      }
      const { variantAlleleCount, variantZygosity } = extractVariantZygosity(
        smallVariant,
        individualUuids,
        this.individuals,
      )

      for (const individualUuid of individualUuids) {
        const individual = this.individuals[individualUuid]
        const phenotypes = JSON.parse(
          JSON.stringify(individual.phenotype_terms || []),
        ).filter(
          (term) =>
            !HPO_INHERITANCE_MODE.has(term.term_id) &&
            !isDiseaseTerm(term.term_id),
        )
        const newSubmissionIndividual = {
          sodar_uuid: uuidv4(),
          individual: individualUuid,
          submission: newSubmission.sodar_uuid,
          phenotypes,
          variant_allele_count: variantAlleleCount,
          variant_zygosity: variantZygosity,
          variant_origin: 'germline',
          source: 'clinical testing',
          tissue: 'Blood',
          citations: [],
        }
        this.submissionIndividuals[newSubmissionIndividual.sodar_uuid] =
          newSubmissionIndividual
        newSubmission.submission_individuals.push(
          newSubmissionIndividual.sodar_uuid,
        )
      }

      this.submissions[newSubmission.sodar_uuid] = newSubmission
      this.currentSubmission = newSubmission
      this.currentSubmissionSet.submissions.push(newSubmission.sodar_uuid)
    },
    updateCurrentSubmissionSetOrganisations(shouldUuids) {
      // Build symmetric difference in terms of organisation UUIDs.
      const currUuids = new Set(this.currentSubmissionSet.organisations)
      const removeUuids = new Set(
        Array.from(currUuids).filter((uuid) => !shouldUuids.includes(uuid)),
      )
      const addUuids = new Set(
        Array.from(shouldUuids).filter((uuid) => !currUuids.has(uuid)),
      )

      // Remove submitting orgs as needed.
      const removeSOUuids = new Set(
        this.currentSubmissionSet.submitting_orgs.filter((soUuid) =>
          removeUuids.has(this.submittingOrgs[soUuid].organisation),
        ),
      )
      for (const uuid of removeSOUuids) {
        delete this.submittingOrgs[uuid]
      }
      this.currentSubmissionSet.submitting_orgs =
        this.currentSubmissionSet.submitting_orgs.filter(
          (soUuid) => !removeSOUuids.has(soUuid),
        )

      // Add submitting orgs as needed.
      for (const orgUuid of addUuids) {
        const newSubmittingOrg = {
          sodar_uuid: uuidv4(),
          organisation: orgUuid,
          submission_set: this.currentSubmissionSet.sodar_uuid,
          sort_order: 0,
        }
        this.submittingOrgs[newSubmittingOrg.sodar_uuid] = newSubmittingOrg
        this.currentSubmissionSet.submitting_orgs.push(
          newSubmittingOrg.sodar_uuid,
        )
      }

      // Update the current submission set properties.
      this.currentSubmissionSet.organisations = shouldUuids
      // Adjust the sort order.
      const orgUuidToSortOrder = Object.fromEntries(
        shouldUuids.map((orgUuid, i) => [orgUuid, i]),
      )
      for (const soUuid of this.currentSubmissionSet.submitting_orgs) {
        this.submittingOrgs[soUuid].sort_order =
          orgUuidToSortOrder[this.submittingOrgs[soUuid].organisation]
      }
      this.currentSubmissionSet.submitting_orgs.sort((a, b) => {
        return (
          this.submittingOrgs[a].sort_order - this.submittingOrgs[b].sort_order
        )
      })
    },
    addIndividualToCurrentSubmissionImpl({ individual, smallVariants }) {
      const variantKey = getVariantId(this.currentSubmission, 'variant_')
      const smallVariant = smallVariants[variantKey]
      const { variantAlleleCount, variantZygosity } = extractVariantZygosity(
        smallVariant,
        [individual.sodar_uuid],
        this.individuals,
      )

      const newUuid = uuidv4()
      this.submissionIndividuals[newUuid] = {
        sodar_uuid: newUuid,
        sort_order: Object.keys(this.currentSubmission.submission_individuals)
          .length,
        individual: individual.sodar_uuid,
        submission: this.currentSubmission.sodar_uuid,
        phenotypes: JSON.parse(
          JSON.stringify(
            this.individuals[individual.sodar_uuid].phenotype_terms,
          ),
        ),
        variant_zygosity: variantZygosity,
        variant_allele_count: variantAlleleCount,
        variant_origin: 'germline',
        source: 'clinical testing',
        tissue: 'Blood',
        citations: [],
      }
      this.currentSubmission.submission_individuals.push(newUuid)
    },
  },
})
