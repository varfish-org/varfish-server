<template>
  <div id="submission-set-wizard">
    <div class="card">
      <div class="card-header">
        <h4 class="mb-0">
          <i class="iconify" data-icon="mdi:note-text"></i>
          Edit Submission Set

          <transition name="fade">
            <div v-if="notification" class="float-right">
              <span :class="getNotificationHtmlClass()">
                {{ notification.text }}
              </span>
            </div>
          </transition>

          <button
            type="button"
            class="btn btn-sm btn-danger float-right"
            @click="onRemoveClicked"
          >
            <span
              class="iconify"
              data-icon="mdi:close"
              data-inline="false"
            ></span>
            remove submission set
          </button>
        </h4>
      </div>

      <submission-set-editor
        v-if="wizardState === 'submissionSet'"
        ref="submissionSetList"
      ></submission-set-editor>
      <submission-list
        v-if="wizardState === 'submissions'"
        ref="submissionList"
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

<script>
import { mapActions, mapState } from 'vuex'

import { validConfirmed } from '@/helpers'
import { WizardState } from '@/store/modules/clinvarExport'

import SubmissionList from './SubmissionList'
import SubmissionSetEditor from './SubmissionSetEditor'
import SubmissionSetWizardFooter from './SubmissionSetWizardFooter'

export default {
  components: {
    SubmissionSetEditor,
    SubmissionList,
    SubmissionSetWizardFooter,
  },
  computed: mapState({
    wizardState: (state) => state.clinvarExport.wizardState,
    notification: (state) => state.clinvarExport.notification,
    currentSubmissionSet: (state) => state.clinvarExport.currentSubmissionSet,
  }),
  methods: {
    ...mapActions('clinvarExport', [
      'setWizardState',
      'wizardSave',
      'wizardRemove',
      'wizardCancel',
    ]),
    validConfirmed,
    /**
     * Event handler called when user clicks 'save'.
     */
    onSaveClicked() {
      this.validConfirmed(this.wizardSave)
    },
    /**
     * Event handler when user clicks 'remove submission set'.
     */
    onRemoveClicked() {
      if (confirm('Really delete submission set?')) {
        this.wizardRemove()
      }
    },
    /**
     * Event handler called when user clicks 'cancel'.
     */
    onCancelClicked() {
      if (confirm('Really discard all changes?')) {
        this.wizardCancel()
      }
    },
    /**
     * Event handler called when user clicks 'forward to submissions'.
     */
    onGotoSubmissionsClicked() {
      this.validConfirmed(() => {
        this.setWizardState(WizardState.submissions)
      })
    },
    /**
     * Event handler called when user clicks 'back to variant list'.
     */
    onGotoSubmissionSetClicked() {
      this.validConfirmed(() => {
        this.setWizardState(WizardState.submissionSet)
      })
    },
    /**
     * @returns {String} the CSS class for the notification.
     */
    getNotificationHtmlClass() {
      return 'badge badge-' + (this.notification.status || 'success')
    },
    /**
     * @returns {boolean} whether or not the currently displayed form is valid.
     */
    isValid() {
      if (this.$refs.submissionSetList !== undefined) {
        return this.$refs.submissionSetList.isValid()
      } else if (this.$refs.submissionList !== undefined) {
        return this.$refs.submissionList.isValid()
      } else {
        return true
      }
    },
  },
}
</script>

<style scoped></style>
