<template>
  <div class="btn-group float-right">
    <button
      ref="buttonCancel"
      type="button"
      class="btn btn-secondary"
      @click="$emit('cancel-clicked')"
    >
      <span class="iconify" data-icon="mdi:close" data-inline="false"></span>
      Cancel
    </button>
    <button
      ref="buttonSave"
      type="button"
      class="btn btn-success"
      @click="$emit('save-clicked')"
    >
      <span
        class="iconify"
        data-icon="mdi:check-bold"
        data-inline="false"
      ></span>
      Save
    </button>

    <button
      v-if="wizardState === 'submissionSet'"
      ref="buttonVariants"
      type="button"
      class="btn btn-primary"
      @click="$emit('goto-submissions-clicked')"
    >
      <i class="iconify" data-icon="mdi:arrow-right-circle"></i>
      Variants
    </button>
    <button
      v-if="wizardState === 'submissions'"
      ref="buttonSubmission"
      type="button"
      class="btn btn-primary"
      @click="$emit('goto-submission-set-clicked')"
    >
      <i class="iconify" data-icon="mdi:arrow-left-circle"></i>
      Submission
    </button>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  computed: {
    ...mapState({
      wizardState: (state) => state.clinvarExport.wizardState,
    }),
  },
}
</script>

<style scoped></style>
