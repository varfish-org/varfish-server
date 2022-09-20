<template>
  <b-button-group class="float-right">
    <b-button
      ref="buttonCancel"
      variant="secondary"
      @click="$emit('cancel-clicked')"
    >
      <span class="iconify" data-icon="mdi:close" data-inline="false"></span>
      Cancel
    </b-button>
    <b-button ref="buttonSave" variant="success" @click="$emit('save-clicked')">
      <span
        class="iconify"
        data-icon="mdi:check-bold"
        data-inline="false"
      ></span>
      Save
    </b-button>

    <b-button
      v-if="wizardState === 'submissionSet'"
      ref="buttonVariants"
      variant="primary"
      @click="$emit('goto-submissions-clicked')"
    >
      <i class="iconify" data-icon="mdi:arrow-right-circle"></i>
      Variants
    </b-button>
    <b-button
      v-if="wizardState === 'submissions'"
      ref="buttonSubmission"
      variant="primary"
      @click="$emit('goto-submission-set-clicked')"
    >
      <i class="iconify" data-icon="mdi:arrow-left-circle"></i>
      Submission
    </b-button>
  </b-button-group>
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
