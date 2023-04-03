<script setup>
import { ref } from 'vue'
import { validConfirmed } from '@clinvarexport/helpers'
import {
  useClinvarExportStore,
  WizardState,
} from '@clinvarexport/stores/clinvar-export'

import SubmissionList from './SubmissionList.vue'
import SubmissionSetEditor from './SubmissionSetEditor.vue'
import SubmissionSetWizardFooter from './SubmissionSetWizardFooter.vue'

const components = {
  SubmissionSetEditor,
  SubmissionList,
  SubmissionSetWizardFooter,
}

const store = useClinvarExportStore()

const submissionSetEditorRef = ref(null)
const submissionListRef = ref(null)

/**
 * @returns {boolean} whether or not the currently displayed form is valid.
 */
const isValid = () => {
  if (submissionSetEditorRef.value) {
    return submissionSetEditorRef.value.isValid()
  } else if (submissionListRef.value) {
    return submissionListRef.value.isValid()
  } else {
    return true
  }
}

/**
 * Event handler called when user clicks 'save'.
 */
const onSaveClicked = () => {
  validConfirmed(isValid, store.wizardSave)
}

/**
 * Event handler when user clicks 'remove submission set'.
 */
const onRemoveClicked = () => {
  if (confirm('Really delete submission set?')) {
    store.wizardRemove()
  }
}

/**
 * Event handler called when user clicks 'cancel'.
 */
const onCancelClicked = () => {
  if (confirm('Really discard all changes?')) {
    store.wizardCancel()
  }
}

/**
 * Event handler called when user clicks 'forward to submissions'.
 */
const onGotoSubmissionsClicked = () => {
  validConfirmed(isValid, () => {
    store.wizardState = WizardState.submissions
  })
}

/**
 * Event handler called when user clicks 'back to variant list'.
 */
const onGotoSubmissionSetClicked = () => {
  validConfirmed(isValid, () => {
    store.wizardState = WizardState.submissionSet
  })
}

/**
 * @returns {String} the CSS class for the notification.
 */
const getNotificationHtmlClass = () => {
  return 'badge badge-' + (store.notification.status || 'success')
}

// Define the exposed functions
defineExpose({
  isValid,
})
</script>

<template>
  <div id="submission-set-wizard">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">
          <i-mdi-note-text />
          Edit Submission Set

          <transition name="fade">
            <div v-if="store.notification" class="float-right">
              <span :class="getNotificationHtmlClass()">
                {{ store.notification.text }}
              </span>
            </div>
          </transition>

          <button
            type="button"
            class="btn btn-sm btn-danger float-right"
            @click="onRemoveClicked"
          >
            <i-mdi-close />
            remove submission set
          </button>
        </h4>
      </div>

      <submission-set-editor
        v-if="store.wizardState === 'submissionSet'"
        ref="submissionSetEditorRef"
      ></submission-set-editor>
      <submission-list
        v-if="store.wizardState === 'submissions'"
        ref="submissionListRef"
      ></submission-list>

      <div class="card-footer">
        <submission-set-wizard-footer
          @save-clicked="onSaveClicked"
          @cancel-clicked="onCancelClicked"
          @goto-submissions-clicked="onGotoSubmissionsClicked"
          @goto-submission-set-clicked="onGotoSubmissionSetClicked"
        ></submission-set-wizard-footer>
      </div>
    </div>
  </div>
</template>
