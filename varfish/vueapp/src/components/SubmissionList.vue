<template>
  <div class="row">
    <div class="col-2 px-0">
      <div>
        <b-list-group flush>
          <b-list-group-item class="font-weight-bold" variant="secondary" inactive>
            <h5>
              Submissions
              <b-button size="sm" variant="primary" class="float-right" @click="onAddSubmissionClicked()">
                <span class="iconify" data-icon="mdi:plus-circle" data-inline="false"></span>
                add
              </b-button>
            </h5>
          </b-list-group-item>
          <draggable v-model="submissionList">
            <b-list-group-item
                v-for="item in submissionList"
                :key="item.sodar_uuid"
                :class="{ active: (item === currentSubmission) }"
                @click="onListItemClicked(item.sodar_uuid)"
            >
              {{ getSubmissionLabel(item) }}
              <i v-if="item._isInvalid" class="iconify text-warning" data-icon="bi:exclamation-circle"></i>
              <div class="pull-right">
                <i class="fa fa-chevron-right"></i>
              </div>
            </b-list-group-item>
          </draggable>
          <b-list-group-item v-if="!submissionList.length" class="inactive text-muted font-italic text-center">
            There are no variants for this submission yet.
          </b-list-group-item>
        </b-list-group>
      </div>
    </div>
    <div class="col-10 border-left d-flex">
      <submission-editor v-if="currentSubmission"></submission-editor>
      <div v-if="currentSubmission === null" class="text-muted font-italic text-center align-self-center flex-grow-1">
        Select a variant on the left or create a new one to edit it here.
      </div>
    </div>

    <b-modal id="modal-add-submission" size="lg" scrollable title="Add Submission to Submission List" hide-footer>
      <p>
        Create a new submission by selecting one of the variants below or
        <b-button size="sm" variant="primary" @click="onCreateEmptySubmissionClicked()">
          <i class="iconify" data-icon="fa-solid:fa-asterisk"></i>
          create empty.
        </b-button>
      </p>
      <ul class="list-group mb-3">
        <li
          class="list-group-item list-group-item-action list-group-item-dark"
        >
          <b>Filters:</b>

          <span
            :class="{ 'cursor-pointer ml-2 badge badge-light': !modalIncludeAll, 'cursor-pointer ml-2 badge badge-success': modalIncludeAll }"
            @click="toggleData('modalIncludeAll')"
          >
            all: <i :class="{ 'fa fa-check-circle': modalIncludeAll, 'fa fa-times-circle': !modalIncludeAll }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeComments, 'cursor-pointer ml-1 badge badge-success': modalIncludeComments }"
            @click="toggleData('modalIncludeComments')"
          >
            comments <i :class="{ 'fa fa-check-circle': modalIncludeComments, 'fa fa-times-circle': !modalIncludeComments }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeCandidates, 'cursor-pointer ml-1 badge badge-success': modalIncludeCandidates }"
            @click="toggleData('modalIncludeCandidates')"
          >
            candidates <i :class="{ 'fa fa-check-circle': modalIncludeCandidates, 'fa fa-times-circle': !modalIncludeCandidates }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeFinalCausatives, 'cursor-pointer ml-1 badge badge-success': modalIncludeFinalCausatives }"
            @click="toggleData('modalIncludeFinalCausatives')"
          >
            causative <i :class="{ 'fa fa-check-circle': modalIncludeFinalCausatives, 'fa fa-times-circle': !modalIncludeFinalCausatives }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeAcmg3, 'cursor-pointer ml-1 badge badge-success': modalIncludeAcmg3 }"
            @click="toggleData('modalIncludeAcmg3')"
          >
            VUCS3 <i :class="{ 'fa fa-check-circle': modalIncludeAcmg3, 'fa fa-times-circle': !modalIncludeAcmg3 }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeAcmg4, 'cursor-pointer ml-1 badge badge-success': modalIncludeAcmg4 }"
            @click="toggleData('modalIncludeAcmg4')"
          >
            LP4 <i :class="{ 'fa fa-check-circle': modalIncludeAcmg4, 'fa fa-times-circle': !modalIncludeAcmg4 }"></i>
          </span>
          <span
            :class="{ 'cursor-pointer ml-1 badge badge-light': !modalIncludeAcmg5, 'cursor-pointer ml-1 badge badge-success': modalIncludeAcmg5 }"
            @click="toggleData('modalIncludeAcmg5')"
          >
            P5 <i :class="{ 'fa fa-check-circle': modalIncludeAcmg5, 'fa fa-times-circle': !modalIncludeAcmg5 }"></i>
          </span>
        </li>
        <li
          class="list-group-item list-group-item-action"
          v-for="item in modalUserAnnotations"
          :key="item.sodar_uuid"
          @click="onCreateSubmissionClicked(item)"
        >
          <h5>
            {{ getVariantLabel(item) }}
            <small v-if="getVariantExtraLabel(item)">
              {{ getVariantExtraLabel(item) }}
            </small>
          </h5>
          <small>
            <span
              :class="{
                'badge badge-light': item.comments.length === 0,
                'badge badge-dark': item.comments.length > 0
              }"
              :title="`${item.comments.length} user comments`"
            >
              <i class="fa fa-comment-o"></i> {{ item.comments.length }}
            </span>
            |
            <span
              :class="{
                'badge badge-dark': item.flags.some(x => x.flag_final_causative),
                'badge badge-light': !item.flags.some(x => x.flag_final_causative)
              }"
              :title="`${item.flags.flag_final_causative ? '': 'NOT '}flagged as final causative`"
            >
              <i class="iconify" data-icon="fa-solid:flag-checkered"></i>
            </span>
            |
            <span :class="{
              'badge badge-dark': item.flags.some(x => x.flag_candidate),
              'badge badge-light': !item.flags.some(x => x.flag_candidate)
              }"
              :title="`${item.flags.flag_final_causative ? '': 'NOT '}flagged as candidate`"
            >
              <i class="iconify" data-icon="fa-solid:heart"></i>
            </span>
          </small>
          |
          <span :class="{
            'badge badge-danger': [4, 5].includes(getAcmgRating(item)),
            'badge badge-warning': getAcmgRating(item) === 3,
            'badge badge-success': [1, 2].includes(getAcmgRating(item)),
            'badge badge-secondary': getAcmgRating(item) === 'N/A'
          }">
            ACMG: {{ getAcmgRating(item) }}
          </span>
          |
          <span>{{ item.caseNames.join(', ') }}</span>
        </li>
        <li
          class="list-group-item list-group-item-action text-muted font-italic text-center"
          v-if="modalUserAnnotations.length === 0"
        >
          There is no user annotation for variants in this project.
        </li>
      </ul>
    </b-modal>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import draggable from 'vuedraggable'
import SubmissionEditor from './SubmissionEditor'
import { getSubmissionLabel, validConfirmed } from '@/helpers'

export default {
  components: { draggable, SubmissionEditor },
  data () {
    return {
      modalIncludeAll: false,
      modalIncludeComments: false,
      modalIncludeCandidates: true,
      modalIncludeFinalCausatives: true,
      modalIncludeAcmg3: false,
      modalIncludeAcmg4: true,
      modalIncludeAcmg5: true
    }
  },
  computed: {
    ...mapState({
      individuals: state => state.clinvarExport.individuals,
      submissions: state => state.clinvarExport.submissions,
      currentSubmissionSet: state => state.clinvarExport.currentSubmissionSet,
      currentSubmission: state => state.clinvarExport.currentSubmission,
      userAnnotations: state => state.clinvarExport.userAnnotations,
      assertionMethods: state => state.clinvarExport.assertionMethods
    }),

    submissionList: {
      get () {
        const lst = this.currentSubmissionSet.submissions.map(k => this.submissions[k])
        lst.sort((lhs, rhs) => (lhs.sort_order - rhs.sort_order))
        return lst
      },
      set (value) {
        this.applySubmissionListSortOrder(value)
      }
    },

    /**
     * Return data to display in the annotated variant modal.
     */
    modalUserAnnotations () {
      const c = 300_000_000 // longer than longest chromosome
      const ua = this.userAnnotations

      const smallVariants = Object.values(ua.smallVariants)
        .map(smallVar => {
          const flags = ua.smallVariantFlags[smallVar.variantId] || []
          const rating = ua.acmgCriteriaRating[smallVar.variantId] || []
          const comments = ua.smallVariantComments[smallVar.variantId] || []
          return { ...smallVar, flags, rating, comments }
        })
        .filter(smallVar => {
          if (this.modalIncludeAll) {
            return true
          } else if (this.modalIncludeComments && smallVar.comments.length > 0) {
            return true
          } else if (this.modalIncludeCandidates && smallVar.flags.some(x => x.flag_candidate)) {
            return true
          } else if (this.modalIncludeFinalCausatives && smallVar.flags.some(x => x.flag_final_causative)) {
            return true
          } else if (this.modalIncludeAcmg3 && this.getAcmgRating(smallVar) >= 3) {
            return true
          } else if (this.modalIncludeAcmg4 && this.getAcmgRating(smallVar) >= 4) {
            return true
          } else if (this.modalIncludeAcmg5 && this.getAcmgRating(smallVar) >= 5) {
            return true
          } else {
            return false
          }
        })
      smallVariants.sort((a, b) => (a.chromosome_no * c + a.start) - (b.chromosome_no * c + b.start))
      return smallVariants
    }
  },
  methods: {
    ...mapActions('clinvarExport', [
      'selectCurrentSubmission',
      'createSubmissionInCurrentSubmissionSet',
      'applySubmissionListSortOrder'
    ]),

    toggleData (name) {
      this.$set(this, name, !this[name])
    },

    getSubmissionLabel,
    validConfirmed,

    getVariantLabel (item) {
      return `${item.refseq_gene_symbol}:${item.refseq_hgvs_p || '<none>'}`
    },
    getVariantExtraLabel (item) {
      if (!item) {
        return null
      } else {
        return `(${item.refseq_transcript_id}:${item.refseq_hgvs_c})`
      }
    },
    getAcmgRating (items) {
      const res = Math.max.apply(
        0,
        items.rating.map(x => x.class_override || x.class_auto || 0)
      )
      if (isFinite(res)) {
        return res || 'N/A'
      } else {
        return 'N/A'
      }
    },

    onListItemClicked (item) {
      this.validConfirmed(() => {
        this.selectCurrentSubmission(item)
      })
    },
    onCreateEmptySubmissionClicked () {
      this.createSubmissionInCurrentSubmissionSet({
        smallVariant: null,
        submission: this.getEmptySubmissionData(),
        individualUuids: []
      })
      this.$bvModal.hide('modal-add-submission')
    },
    /**
     * Clicked on an existing small variant with user annotation.
     */
    onCreateSubmissionClicked (smallVariant) {
      this.createSubmissionInCurrentSubmissionSet(this.getSubmissionData(smallVariant))
      this.$bvModal.hide('modal-add-submission')
    },
    onAddSubmissionClicked () {
      this.validConfirmed(() => {
        this.$bvModal.show('modal-add-submission')
      })
    },

    /**
     * @return {object} with keys submission, individualUuids (of affected carrier individuals).
     */
    getSubmissionData (smallVariant) {
      // Get individuals that carry the variants.
      const carrierNames = Object.entries(smallVariant.genotype)
        .filter(kv => {
          const value = kv[1]
          return value.gt && value.gt.includes('1')
        })
        .map(kv => kv[0])
      const individualUuids = Object.entries(this.individuals)
        .filter(kv => carrierNames.includes(kv[1].name))
        .map(kv => kv[0])
      individualUuids.sort()

      const significanceDescription = {
        1: 'Benign',
        2: 'Likely benign',
        3: 'Uncertain significance',
        4: 'Likely pathogenic',
        5: 'Pathogenic'
      }[this.getAcmgRating(smallVariant)] || null

      const variantGene = [smallVariant.refseq_gene_symbol]
      const variantHgvs = [smallVariant.refseq_hgvs_p || 'p.?']

      const submission = {
        record_status: 'novel',
        release_status: 'public',
        significance_status: 'criteria provided, single submitter',
        significance_description: significanceDescription,
        significance_last_evaluation: (new Date()).toISOString().substr(0, 10),
        assertion_method: Object.values(this.assertionMethods)[0].sodar_uuid,
        age_of_onset: '',
        inheritance: '',
        variant_type: 'Variation',
        variant_assembly: smallVariant.release,
        variant_chromosome: smallVariant.chromosome,
        variant_start: smallVariant.start,
        variant_stop: smallVariant.start + smallVariant.reference.length - 1,
        variant_reference: smallVariant.reference,
        variant_alternative: smallVariant.alternative,
        variant_gene: variantGene,
        variant_hgvs: variantHgvs
      }

      return { smallVariant, submission, individualUuids }
    },
    /**
     * @return {object} the data of an empty submission
     */
    getEmptySubmissionData () {
      return {
        record_status: 'novel',
        release_status: 'public',
        significance_status: 'criteria provided, single submitter',
        significance_description: null,
        significance_last_evaluation: (new Date()).toISOString().substr(0, 10),
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
        submission_individuals: []
      }
    },

    /**
     * @returns {boolean} whether the child component's form is valid.
     */
    isValid () {
      return !this.$children.some(c => {
        if (c.$v) {
          return c.$v.$invalid
        }
      })
    }
  }
}
</script>

<style scoped>
.modal-lg {
  max-width: 800px;
}
.cursor-pointer {
  cursor: pointer;
}
</style>
