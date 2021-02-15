<template>
  <b-button-group class="float-right">
    <b-button
      variant="secondary"
      @click="$emit('cancel-clicked')"
    >
      <i class="fa fa-times"></i>
      Cancel
    </b-button>
    <b-button
      variant="success"
      @click="$emit('save-clicked')"
    >
      <i class="fa fa-check"></i>
      Save
    </b-button>

    <b-button
      v-if="wizardState === 'submissionSet'"
      variant="primary"
      @click="$emit('goto-submissions-clicked')"
    >
      <i class="fa fa-arrow-circle-right"></i>
      Variants
    </b-button>
    <b-button
      v-if="wizardState === 'submissions'"
      variant="primary"
      @click="$emit('goto-submission-set-clicked')"
    >
      <i class="fa fa-arrow-circle-left"></i>
      Submission
    </b-button>
  </b-button-group>
</template>

<script>
import { mapState } from 'vuex'

export default {
  computed: {
    ...mapState({
      wizardState: state => state.clinvarExport.wizardState
    })
  }
}
</script>

<style scoped>
</style>
