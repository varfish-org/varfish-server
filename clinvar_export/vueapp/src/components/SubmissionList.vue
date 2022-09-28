<template>
  <div class="row">
    <div class="col-2 px-0">
      <div>
        <ul class="list-group list-group-flush">
          <li
            class="list-group-item list-group-item-secondary font-weight-bold"
          >
            <h5>
              Submissions
              <div
                ref="buttonAddSubmission"
                type="button"
                class="btn btn-primary btn-small float-right"
                @click="onAddSubmissionClicked()"
              >
                <span
                  class="iconify"
                  data-icon="mdi:plus-circle"
                  data-inline="false"
                ></span>
                add
              </div>
            </h5>
          </li>
          <draggable ref="submissionList" v-model="submissionList">
            <li
              v-for="item in submissionList"
              :key="item.sodar_uuid"
              :class="{
                'list-group-item list-group-item-action list-group-item-primary':
                  item === currentSubmission,
                'list-group-item list-group-item-action':
                  item !== currentSubmission,
              }"
              @click="onListItemClicked(item.sodar_uuid)"
            >
              {{ getSubmissionLabel(item) }}
              <span v-if="getSubmissionIndividualsCount(item) > 0" class="small"
                >({{ getSubmissionIndividualsLabel(item) }})</span
              >
              <i
                v-if="item._isInvalid"
                class="iconify text-warning"
                data-icon="bi:exclamation-circle"
              ></i>
              <div class="pull-right">
                <span class="iconify" data-icon="fa-solid:chevron-right"></span>
              </div>
            </li>
          </draggable>
          <li
            v-if="!submissionList.length"
            class="list-group-item list-group-item-light font-italic text-center"
          >
            There are no variants for this submission yet.
          </li>
        </ul>
      </div>
    </div>
    <div class="col-10 border-left d-flex">
      <submission-editor
        v-if="currentSubmission"
        ref="submissionEditor"
      ></submission-editor>
      <div
        v-if="currentSubmission === null"
        class="text-muted font-italic text-center align-self-center flex-grow-1"
      >
        Select a variant on the left or create a new one to edit it here.
      </div>
    </div>

    <div ref="modalAddSubmission" class="modal fade">
      <div
        class="modal-dialog modal-lg modal-dialog-scrollable"
        role="document"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Submissio to Submission List</h5>
          </div>
          <div class="modal-body">
            <p>
              Create new submissions by selecting from the variants below and
              clicking
              <span class="badge badge-primary"
                ><i class="iconify" data-icon="fa-solid:plus"></i></span
              >. If you select no variant, a blank submission will be created.
            </p>
            <ul ref="userAnnotationList" class="list-group mb-3">
              <li
                class="list-group-item list-group-item-action list-group-item-dark pl-2 pr-2"
              >
                <div class="form-inline">
                  <div
                    class="form-group mr-3"
                    style="width: 200px; max-width: 200px"
                  >
                    <multiselect
                      id="input-family"
                      ref="inputSelectCase"
                      v-model="familyUuid"
                      placeholder="Select Case"
                      select-label=""
                      deselect-label=""
                      :loading="loadingVariants"
                      :disabled="loadingVariants"
                      :options="familyUuids"
                      :custom-label="getFamilyLabel"
                      @input="fetchRawModalUserAnnotations()"
                    ></multiselect>
                  </div>
                  <div class="form-group">
                    <span
                      :class="{
                        'cursor-pointer ml-2 badge badge-light':
                          !modalIncludeAll,
                        'cursor-pointer ml-2 badge badge-success':
                          modalIncludeAll,
                      }"
                      @click="toggleData('modalIncludeAll')"
                    >
                      all:
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeAll,
                          'fa fa-times-circle': !modalIncludeAll,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeComments,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeComments,
                      }"
                      @click="toggleData('modalIncludeComments')"
                    >
                      <i class="iconify" data-icon="fa-solid:comment"></i
                      >&nbsp;&nbsp;
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeComments,
                          'fa fa-times-circle': !modalIncludeComments,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeCandidates,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeCandidates,
                      }"
                      @click="toggleData('modalIncludeCandidates')"
                    >
                      <i class="iconify" data-icon="fa-solid:heart"></i
                      >&nbsp;&nbsp;
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeCandidates,
                          'fa fa-times-circle': !modalIncludeCandidates,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeFinalCausatives,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeFinalCausatives,
                      }"
                      @click="toggleData('modalIncludeFinalCausatives')"
                    >
                      <i class="iconify" data-icon="fa-solid:flag-checkered"></i
                      >&nbsp;&nbsp;
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeFinalCausatives,
                          'fa fa-times-circle': !modalIncludeFinalCausatives,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeAcmg3,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeAcmg3,
                      }"
                      @click="toggleData('modalIncludeAcmg3')"
                    >
                      VUCS3
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeAcmg3,
                          'fa fa-times-circle': !modalIncludeAcmg3,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeAcmg4,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeAcmg4,
                      }"
                      @click="toggleData('modalIncludeAcmg4')"
                    >
                      LP4
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeAcmg4,
                          'fa fa-times-circle': !modalIncludeAcmg4,
                        }"
                      ></i>
                    </span>
                    <span
                      :class="{
                        'cursor-pointer ml-1 badge badge-light':
                          !modalIncludeAcmg5,
                        'cursor-pointer ml-1 badge badge-success':
                          modalIncludeAcmg5,
                      }"
                      @click="toggleData('modalIncludeAcmg5')"
                    >
                      P5
                      <i
                        :class="{
                          'fa fa-check-circle': modalIncludeAcmg5,
                          'fa fa-times-circle': !modalIncludeAcmg5,
                        }"
                      ></i>
                    </span>
                  </div>
                  <div class="form-group ml-3" style="height: 43px">
                    <div class="custom-control custom-checkbox">
                      <input
                        id="submission-set-affecteds-only"
                        v-model="onlyAddAffected"
                        type="checkbox"
                        class="custom-control-input"
                        value="true"
                      />
                      <label
                        for="submission-set-affecteds-only"
                        class="custom-control-label"
                        >affecteds only</label
                      >
                    </div>
                  </div>
                  <div class="form-group ml-auto">
                    <button
                      ref="buttonAddSelectedSubmissions"
                      type="button"
                      class="btn btn-sm btn-primary"
                      @click="onCreateSubmissionClicked()"
                    >
                      <i class="iconify" data-icon="fa-solid:plus"></i>
                    </button>
                  </div>
                </div>
              </li>
              <li
                v-for="item in modalUserAnnotations"
                :key="item.sodar_uuid"
                :class="{
                  'list-group-item x-not-active': !isVariantSelected(item),
                  'list-group-item x-active': isVariantSelected(item),
                }"
                @click="onVariantClicked(item)"
                @mousedown.prevent=""
              >
                <h5>
                  <i
                    class="iconify x-active-show text-primary"
                    data-icon="bi:check-square-fill"
                  ></i>
                  <i
                    class="iconify x-active-hide text-muted"
                    data-icon="bi:square"
                  ></i>
                  {{ getVariantLabel(item) }}
                  <small v-if="getVariantExtraLabel(item)">
                    {{ getVariantExtraLabel(item) }}
                  </small>
                </h5>
                <small>
                  <span
                    :class="{
                      'badge badge-light': item.comments.length === 0,
                      'badge badge-dark': item.comments.length > 0,
                    }"
                    :title="`${item.comments.length} user comments`"
                  >
                    <i class="iconify" data-icon="fa-regular:comment"></i>
                    {{ item.comments.length }}
                  </span>
                  |
                  <span
                    :class="{
                      'badge badge-dark': item.flags.some(
                        (x) => x.flag_final_causative
                      ),
                      'badge badge-light': !item.flags.some(
                        (x) => x.flag_final_causative
                      ),
                    }"
                    :title="`${
                      item.flags.flag_final_causative ? '' : 'NOT '
                    }flagged as final causative`"
                  >
                    <i class="iconify" data-icon="fa-solid:flag-checkered"></i>
                  </span>
                  |
                  <span
                    :class="{
                      'badge badge-dark': item.flags.some(
                        (x) => x.flag_candidate
                      ),
                      'badge badge-light': !item.flags.some(
                        (x) => x.flag_candidate
                      ),
                    }"
                    :title="`${
                      item.flags.flag_final_causative ? '' : 'NOT '
                    }flagged as candidate`"
                  >
                    <i class="iconify" data-icon="fa-solid:heart"></i>
                  </span>
                </small>
                |
                <span
                  :class="{
                    'badge badge-danger': [4, 5].includes(getAcmgRating(item)),
                    'badge badge-warning': getAcmgRating(item) === 3,
                    'badge badge-success': [1, 2].includes(getAcmgRating(item)),
                    'badge badge-secondary': getAcmgRating(item) === 'N/A',
                  }"
                >
                  ACMG: {{ getAcmgRating(item) }}
                </span>
                |
                <span>{{ item.caseNames.join(', ') }}</span>
              </li>
              <li
                v-if="modalUserAnnotations.length === 0"
                class="list-group-item list-group-item-action text-muted font-italic text-center"
              >
                <span v-if="familyUuid === ''">
                  <span>
                    Please select a case to display the variant user
                    annotations.
                  </span>
                </span>
                <span v-else-if="loadingVariants">
                  <span> Fetching variants from case from server... </span>
                </span>
                <span v-else-if="fetchError">
                  <span>
                    Ouch, an error occured while fetching the variants!
                  </span>
                </span>
                <span v-else-if="rawModalUserAnnotationsCount > 0">
                  <span>
                    None of the {{ rawModalUserAnnotationsCount }} user
                    annotations matched your selection criteria.
                  </span>
                </span>
                <span v-else>
                  <span>
                    There is no matching user annotation for variants in this
                    project.
                  </span>
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import Multiselect from 'vue-multiselect'
import draggable from 'vuedraggable'
import { mapActions, mapState } from 'vuex'

import {
  getSubmissionLabel,
  getVariantId,
  HPO_AGE_OF_ONSET,
  HPO_INHERITANCE_MODE,
  isDiseaseTerm,
  removeItemAll,
  validConfirmed,
} from '@/helpers'

import clinvarExport from '../api/clinvarExport'
import SubmissionEditor from './SubmissionEditor'

export default {
  components: { draggable, SubmissionEditor, Multiselect },
  data() {
    return {
      familyUuid: '',
      modalIncludeAll: false,
      modalIncludeComments: false,
      modalIncludeCandidates: true,
      modalIncludeFinalCausatives: true,
      modalIncludeAcmg3: false,
      modalIncludeAcmg4: true,
      modalIncludeAcmg5: true,
      individualFilter: '',
      onlyAddAffected: true,
      loadingVariants: false,
      fetchError: false,
      rawModalUserAnnotations: null,
      rawModalUserAnnotationsCount: 0,
      modalUserAnnotations: [],
      selectedSmallVariants: [],
    }
  },
  computed: {
    ...mapState({
      appContext: (state) => state.clinvarExport.appContext,
      families: (state) => state.clinvarExport.families,
      individuals: (state) => state.clinvarExport.individuals,
      submissionIndividuals: (state) =>
        state.clinvarExport.submissionIndividuals,
      submissions: (state) => state.clinvarExport.submissions,
      currentSubmissionSet: (state) => state.clinvarExport.currentSubmissionSet,
      currentSubmission: (state) => state.clinvarExport.currentSubmission,
      assertionMethods: (state) => state.clinvarExport.assertionMethods,
    }),

    familyUuids: function () {
      return Array.from(Object.values(this.families), (f) => f.sodar_uuid)
    },
    submissionList: {
      get() {
        const lst = this.currentSubmissionSet.submissions.map(
          (k) => this.submissions[k]
        )
        lst.sort((lhs, rhs) => lhs.sort_order - rhs.sort_order)
        return lst
      },
      set(value) {
        this.applySubmissionListSortOrder(value)
      },
    },
  },
  methods: {
    ...mapActions('clinvarExport', [
      'selectCurrentSubmission',
      'createSubmissionInCurrentSubmissionSet',
      'applySubmissionListSortOrder',
    ]),

    /**
     * Fetch model user annotations.
     */
    fetchRawModalUserAnnotations() {
      if (this.familyUuid) {
        Vue.set(this, 'modalUserAnnotations', [])
        this.fetchError = false
        this.loadingVariants = true
        Vue.set(this, 'rawModalUserAnnotations', null)
        Vue.set(this, 'rawModalUserAnnotationsCount', 0)

        clinvarExport
          .getUserAnnotations(this.appContext, this.familyUuid)
          .then((res) => {
            this.fetchError = false

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
                arr.sort((a, b) => (a.case_name < b.case_name ? -1 : 1))
              }
              return result
            }

            const smallVariants = {}
            for (const smallVar of res.small_variants) {
              if (getVariantId(smallVar) in smallVariants) {
                smallVariants[getVariantId(smallVar)].caseNames.push(
                  smallVar.case_name
                )
                Vue.set(smallVariants[getVariantId(smallVar)], 'genotype', {
                  ...smallVariants[getVariantId(smallVar)].genotype,
                  ...smallVar.genotype,
                })
              } else {
                Vue.set(smallVariants, getVariantId(smallVar), {
                  ...smallVar,
                  caseNames: [smallVar.case_name],
                  variantId: getVariantId(smallVar),
                })
                Vue.delete(smallVariants[getVariantId(smallVar)], 'case_name')
              }
            }
            for (const arr of Object.values(smallVariants)) {
              arr.caseNames = [...new Set(arr.caseNames)]
              arr.caseNames.sort((a, b) => (a.case_name < b.case_name ? -1 : 1))
            }

            Vue.set(this, 'rawModalUserAnnotations', {
              smallVariants,
              smallVariantFlags: collect(res.small_variant_flags),
              smallVariantComments: collect(res.small_variant_comments),
              acmgCriteriaRating: collect(res.acmg_criteria_rating),
            })
            Vue.set(
              this,
              'rawModalUserAnnotationsCount',
              Object.keys(smallVariants).length
            )
            Vue.set(
              this,
              'modalUserAnnotations',
              this._computeUserAnnotations(this.rawModalUserAnnotations)
            )
            this.loadingVariants = false
          })
          .catch((error) => {
            this.loadingVariants = false
            this.fetchError = true
            console.error(error)
          })
      }
    },

    /**
     * Return filtered data to display in the annotated variant modal.
     */
    _computeUserAnnotations(ua) {
      const c = 300000000 // longer than longest chromosome
      if (!ua) {
        return []
      }

      const smallVariants = Object.values(ua.smallVariants)
        .map((smallVar) => {
          const flags = ua.smallVariantFlags[smallVar.variantId] || []
          const rating = ua.acmgCriteriaRating[smallVar.variantId] || []
          const comments = ua.smallVariantComments[smallVar.variantId] || []
          return { ...smallVar, flags, rating, comments }
        })
        .filter((smallVar) => {
          if (this.individualFilter) {
            if (
              !smallVar.caseNames.some((s) => s.includes(this.individualFilter))
            ) {
              return false
            }
          }
          if (this.modalIncludeAll) {
            return true
          } else if (
            this.modalIncludeComments &&
            smallVar.comments.length > 0
          ) {
            return true
          } else if (
            this.modalIncludeCandidates &&
            smallVar.flags.some((x) => x.flag_candidate)
          ) {
            return true
          } else if (
            this.modalIncludeFinalCausatives &&
            smallVar.flags.some((x) => x.flag_final_causative)
          ) {
            return true
          } else if (
            this.modalIncludeAcmg3 &&
            this.getAcmgRating(smallVar) >= 3
          ) {
            return true
          } else if (
            this.modalIncludeAcmg4 &&
            this.getAcmgRating(smallVar) >= 4
          ) {
            return true
          } else if (
            this.modalIncludeAcmg5 &&
            this.getAcmgRating(smallVar) >= 5
          ) {
            return true
          } else {
            return false
          }
        })
      smallVariants.sort(
        (a, b) =>
          a.chromosome_no * c + a.start - (b.chromosome_no * c + b.start)
      )
      return smallVariants
    },

    toggleData(name) {
      this.$set(this, name, !this[name])
    },

    getSubmissionLabel,
    validConfirmed,

    getFamilyLabel(familyUuid) {
      return this.families[familyUuid].case_name
    },
    getSubmissionIndividualsCount(item) {
      return item.submission_individuals.length
    },
    getSubmissionIndividualsLabel(item) {
      let names = item.submission_individuals.map((uuid) =>
        this.individuals[
          this.submissionIndividuals[uuid].individual
        ].name.replace(/-N.-DNA.-....$/, '')
      )
      if (names.length > 2) {
        names = names.slice(0, 2) + ['...']
      }
      return names.join(', ')
    },
    isVariantSelected(item) {
      const variantDesc = this.getVariantDesc(item)
      return this.selectedSmallVariants.includes(variantDesc)
    },
    getVariantDesc(item) {
      return `${item.release}-${item.chromosome}-${item.start}-${item.reference}-${item.alternative}`
    },
    getVariantLabel(item) {
      return `${item.refseq_gene_symbol}:${item.refseq_hgvs_p || '--none--'}`
    },
    getVariantExtraLabel(item) {
      if (!item) {
        return null
      } else {
        return `(${item.refseq_transcript_id}:${item.refseq_hgvs_c})`
      }
    },
    getAcmgRating(items) {
      const res = Math.max.apply(
        0,
        items.rating.map((x) => x.class_override || x.class_auto || 0)
      )
      if (isFinite(res)) {
        return res || 'N/A'
      } else {
        return 'N/A'
      }
    },

    onListItemClicked(item) {
      this.validConfirmed(() => {
        this.selectCurrentSubmission(item)
      })
    },
    onVariantClicked(smallVariant) {
      const variantDesc = this.getVariantDesc(smallVariant)
      if (this.selectedSmallVariants.includes(variantDesc)) {
        removeItemAll(this.selectedSmallVariants, variantDesc)
      } else {
        this.selectedSmallVariants.push(variantDesc)
      }
    },
    /**
     * Clicked on an existing small variant with user annotation.
     */
    onCreateSubmissionClicked() {
      if (!this.selectedSmallVariants.length) {
        this.createSubmissionInCurrentSubmissionSet({
          smallVariant: null,
          submission: this.getEmptySubmissionData(),
          individualUuids: [],
        })
      } else {
        for (let i = 0; i < this.modalUserAnnotations.length; ++i) {
          const smallVariant = this.modalUserAnnotations[i]
          const variantDesc = this.getVariantDesc(smallVariant)
          if (this.selectedSmallVariants.includes(variantDesc)) {
            this.createSubmissionInCurrentSubmissionSet(
              this.getSubmissionData(smallVariant)
            )
          }
        }
        this.selectedSmallVariants = []
      }
      $(this.$refs.modalAddSubmission).modal('hide')
    },
    onAddSubmissionClicked() {
      this.validConfirmed(() => {
        $(this.$refs.modalAddSubmission).modal('show')
      })
    },

    /**
     * @return {object} with keys submission, individualUuids (of affected carrier individuals).
     */
    getSubmissionData(smallVariant) {
      // Get individuals that carry the variants.
      const affectedNames = Object.values(this.individuals)
        .filter((indiv) => indiv.affected === 'yes')
        .map((indiv) => indiv.name)
      const carrierNames = Object.entries(smallVariant.genotype)
        .filter((kv) => {
          const name = kv[0]
          const value = kv[1]
          return (
            value.gt &&
            value.gt.includes('1') &&
            (!this.onlyAddAffected || affectedNames.includes(name))
          )
        })
        .map((kv) => kv[0])
      const individualUuids = Object.entries(this.individuals)
        .filter((kv) => carrierNames.includes(kv[1].name))
        .map((kv) => kv[0])
      individualUuids.sort()

      const significanceDescription =
        {
          1: 'Benign',
          2: 'Likely benign',
          3: 'Uncertain significance',
          4: 'Likely pathogenic',
          5: 'Pathogenic',
        }[this.getAcmgRating(smallVariant)] || null

      const variantGene = [smallVariant.refseq_gene_symbol]
      const variantHgvs = [smallVariant.refseq_hgvs_p || 'p.?']

      let ageOfOnset = ''
      let inheritance = ''
      const diseases = []
      for (const individualUuid of individualUuids) {
        const individual = this.individuals[individualUuid]
        if (individual.phenotype_terms) {
          // eslint-disable-next-line camelcase
          for (let { term_id, term_name } of individual.phenotype_terms) {
            // eslint-disable-next-line camelcase
            term_name = term_name.split(';')[0].trim()
            inheritance = inheritance || HPO_INHERITANCE_MODE.get(term_id) || ''
            ageOfOnset = ageOfOnset || HPO_AGE_OF_ONSET.get(term_id) || ''
            // eslint-disable-next-line camelcase
            if (
              isDiseaseTerm(term_id) &&
              // eslint-disable-next-line camelcase
              !diseases.some((x) => x.term_id === term_id)
            ) {
              // eslint-disable-next-line camelcase
              diseases.push({ term_id, term_name })
            }
          }
        }
      }

      const submission = {
        record_status: 'novel',
        release_status: 'public',
        significance_status: 'criteria provided, single submitter',
        significance_description: significanceDescription,
        significance_last_evaluation: new Date().toISOString().substr(0, 10),
        assertion_method: Object.values(this.assertionMethods)[0].sodar_uuid,
        age_of_onset: ageOfOnset,
        diseases,
        inheritance,
        variant_type: 'Variation',
        variant_assembly: smallVariant.release,
        variant_chromosome: smallVariant.chromosome,
        variant_start: smallVariant.start,
        variant_stop: smallVariant.start + smallVariant.reference.length - 1,
        variant_reference: smallVariant.reference,
        variant_alternative: smallVariant.alternative,
        variant_gene: variantGene,
        variant_hgvs: variantHgvs,
      }

      return { smallVariant, submission, individualUuids }
    },
    /**
     * @return {object} the data of an empty submission
     */
    getEmptySubmissionData() {
      return {
        record_status: 'novel',
        release_status: 'public',
        significance_status: 'criteria provided, single submitter',
        significance_description: null,
        significance_last_evaluation: new Date().toISOString().substr(0, 10),
        assertion_method: Object.values(this.assertionMethods)[0].sodar_uuid,
        age_of_onset: '',
        inheritance: '',
        variant_type: 'Variation',
        variant_assembly: 'GRCh37',
        variant_chromosome: null,
        variant_start: null,
        variant_stop: null,
        variant_reference: null,
        variant_alternative: null,
        variant_gene: [],
        variant_hgvs: [],

        diseases: [],
        submission_individuals: [],
      }
    },

    /**
     * @returns {boolean} whether the child component's form is valid.
     */
    isValid() {
      if (this.$refs.submissionEditor) {
        return this.$refs.submissionEditor.isValid()
      } else {
        return true
      }
    },
  },
}
</script>

<style scoped>
.modal-lg {
  max-width: 800px;
}
.cursor-pointer {
  cursor: pointer;
}

.x-not-active .x-active-show {
  display: none;
}

.x-active .x-active-hide {
  display: none;
}
</style>
