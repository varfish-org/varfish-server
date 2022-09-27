<template>
  <div class="border-top">
    <h3 class="border-bottom pt-3 pb-1 mb-3">
      Individuals
      <span class="badge badge-secondary">{{ caseCount }}</span>

      <b-button
        v-b-modal.modal-add-case
        size="sm"
        variant="primary"
        class="float-right"
      >
        <span
          class="iconify"
          data-icon="mdi:plus-circle"
          data-inline="false"
        ></span>
        add individual to submission
      </b-button>
    </h3>
    <div v-for="item in caseSubmissionIndividuals" :key="item.sodar_uuid">
      <submission-case-list-entry
        v-model="item.wrapped"
      ></submission-case-list-entry>
    </div>
    <p
      v-if="caseSubmissionIndividuals.length === 0"
      class="text-center text-secondary font-italic"
    >
      No individuals have been added to this submission yet.
    </p>

    <b-modal
      id="modal-add-case"
      scrollable
      title="Add Case to Submission"
      hide-footer
    >
      <p>Select an individual to add for this variant.</p>
      <ul class="list-group mb-3">
        <li
          v-for="individual in getModalIndividualList()"
          :key="individual.sodar_uuid"
          class="list-group-item list-group-item-action"
          @click="addIndividualToCurrentSubmission(individual)"
        >
          <h5>
            {{ individual.name }}
          </h5>
          <small>{{ getPhenotypeDisplay(individual) }}</small>
        </li>
        <li
          v-if="getModalIndividualList().length === 0"
          class="list-group-item list-group-item-action text-muted font-italic text-center"
        >
          There is no individual (left) that can be added to this case.
        </li>
      </ul>
      <p class="mb-0">You can only add each individual once.</p>
    </b-modal>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'

import SubmissionCaseListEntry from './SubmissionCaseListEntry'

export default {
  components: { SubmissionCaseListEntry },
  computed: {
    ...mapState({
      currentSubmission: (state) => state.clinvarExport.currentSubmission,
      individuals: (state) => state.clinvarExport.individuals,
      submissionIndividuals: (state) =>
        state.clinvarExport.submissionIndividuals,
    }),

    caseCount() {
      return this.currentSubmission.submission_individuals.length
    },

    /**
     * Build wrapped case individiuals for the current submission.
     *
     * We must return them in a wrapper object as we cannot iterate and use it as models directory,
     * cf. https://stackoverflow.com/q/57974480
     */
    caseSubmissionIndividuals() {
      const result = this.currentSubmission.submission_individuals.map(
        (uuid) => ({ wrapped: this.submissionIndividuals[uuid] })
      )
      result.sort((a, b) => a.sort_order - b.sort_order)
      return result
    },
  },
  methods: {
    ...mapActions('clinvarExport', ['addIndividualToCurrentSubmission']),

    /**
     * Get individuals to display in the modal.
     *
     * @returns list of individuals from the store that are not already in the current submission
     */
    getModalIndividualList() {
      const blockedIndividualUuids = new Set(
        this.currentSubmission.submission_individuals.map(
          (uuid) => this.submissionIndividuals[uuid].individual
        )
      )
      const result = Object.values(this.individuals).filter(
        (obj) => !blockedIndividualUuids.has(obj.sodar_uuid)
      )
      return result
    },
    /**
     * Get phenotypes to display for the given Individual.
     *
     * @param individual to retrieve phenotype list display for
     * @return String with the phenotypes to display.
     */
    getPhenotypeDisplay(individual) {
      return (individual.phenotype_terms || [])
        .map((t) => `(${t.term_id}) ${t.term_name}`)
        .join(', ')
    },
  },
}
</script>

<style scoped></style>
