<script setup>
import { ref, computed } from 'vue'
import { useClinvarExportStore } from '@/stores/clinvar-export'

import SubmissionCaseListEntry from './SubmissionCaseListEntry.vue'

const components = { SubmissionCaseListEntry }

// References
const modalAddCaseRef = ref(null)

// Define Pinia store
const store = useClinvarExportStore()

const caseCount = computed(() => {
  return store.currentSubmission.submission_individuals.length
})

/**
 * Build wrapped case individiuals for the current submission.
 *
 * We must return them in a wrapper object as we cannot iterate and use it as models directory,
 * cf. https://stackoverflow.com/q/57974480
 */
const caseSubmissionIndividuals = computed(() => {
  const result = store.currentSubmission.submission_individuals.map((uuid) => ({
    wrapped: store.submissionIndividuals[uuid],
  }))
  result.sort((a, b) => a.sort_order - b.sort_order)
  return result
})

/**
 * Get individuals to display in the modal.
 *
 * @returns list of individuals from the store that are not already in the current submission
 */
const getModalIndividualList = () => {
  const blockedIndividualUuids = new Set(
    store.currentSubmission.submission_individuals.map(
      (uuid) => store.submissionIndividuals[uuid].individual
    )
  )
  const result = Object.values(store.individuals).filter(
    (obj) => !blockedIndividualUuids.has(obj.sodar_uuid)
  )
  return result
}

/**
 * Get phenotypes to display for the given Individual.
 *
 * @param individual to retrieve phenotype list display for
 * @return String with the phenotypes to display.
 */
const getPhenotypeDisplay = (individual) => {
  return (individual.phenotype_terms || [])
    .map((t) => `(${t.term_id}) ${t.term_name}`)
    .join(', ')
}

const addIndividualToCurrentSubmission = (individual) => {
  $(modalAddCaseRef.value).modal('hide')
  store.addIndividualToCurrentSubmission(individual)
}

/**
 * Show the modal for adding a case to the submission.
 */
const showModalAddCase = () => {
  $(modalAddCaseRef.value).modal('show')
}

// Define the exposed functions
defineExpose({})
</script>

<template>
  <div class="border-top">
    <h3 class="border-bottom pt-3 pb-1 mb-3">
      Individuals
      <span class="badge badge-secondary">{{ caseCount }}</span>

      <button
        type="button"
        class="btn btn-sm btn-primary float-right"
        @click="showModalAddCase()"
      >
        <span
          class="iconify"
          data-icon="mdi:plus-circle"
          data-inline="false"
        ></span>
        add individual to submission
      </button>
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

    <div ref="modalAddCaseRef" class="modal fade">
      <div class="modal-dialog modal-dialog-scrollable" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Add Case to Submission</h5>
          </div>
          <div class="modal-body">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
