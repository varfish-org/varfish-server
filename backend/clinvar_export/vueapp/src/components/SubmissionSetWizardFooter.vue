<script setup>
import { computed } from 'vue'

import { useClinvarExportStore } from '@clinvarexport/stores/clinvar-export'

const store = useClinvarExportStore()

const wizardState = computed(() => store.wizardState)
</script>

<template>
  <div class="btn-group float-right">
    <!-- eslint-disable vue/require-explicit-emits -->
    <button
      ref="buttonCancel"
      type="button"
      class="btn btn-secondary"
      @click="$emit('cancel-clicked')"
    >
      <i-mdi-close />
      Cancel
    </button>
    <button
      ref="buttonSave"
      type="button"
      class="btn btn-success"
      @click="$emit('save-clicked')"
    >
      <i-mdi-check-bold />
      Save
    </button>

    <button
      v-if="wizardState === 'submissionSet'"
      ref="buttonVariants"
      type="button"
      class="btn btn-primary"
      @click="$emit('goto-submissions-clicked')"
    >
      <i-mdi-arrow-right-circle />
      Variants
    </button>
    <button
      v-if="wizardState === 'submissions'"
      ref="buttonSubmission"
      type="button"
      class="btn btn-primary"
      @click="$emit('goto-submission-set-clicked')"
    >
      <i-mdi-arrow-left-circle />
      Submission
    </button>
    <!-- eslint-enable -->
  </div>
</template>
