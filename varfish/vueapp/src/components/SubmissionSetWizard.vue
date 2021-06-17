<template>
  <div id="submission-set-wizard">
    <b-breadcrumb :items="breadcrumbItems()"></b-breadcrumb>

    <b-card no-body title-tag="title" footer-tag="footer">
      <template #header>
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

          <b-button class="float-right" size="sm" variant="danger" @click="onRemoveClicked">
            <span class="iconify" data-icon="mdi:close" data-inline="false"></span>
            remove submission set
          </b-button>
        </h4>
      </template>

      <submission-set-editor
        v-if="wizardState === 'submissionSet'"
        ref="submissionSetCard"
      ></submission-set-editor>
      <submission-set-variant-list
        v-if="wizardState === 'submissions'"
        ref="submissionsCard"
      ></submission-set-variant-list>

      <template #footer>
        <submission-set-wizard-footer
          @save-clicked="onSaveClicked"
          @cancel-clicked="onCancelClicked"
          @goto-submissions-clicked="onGotoSubmissionsClicked"
          @goto-submission-set-clicked="onGotoSubmissionSetClicked"
        ></submission-set-wizard-footer>
      </template>
    </b-card>
  </div>
</template>

<script>
import { mapActions, mapState } from 'vuex'
import SubmissionSetEditor from './SubmissionSetEditor'
import SubmissionSetVariantList from './SubmissionList'
import SubmissionSetWizardFooter from './SubmissionSetWizardFooter'
import { WizardState } from '@/store/modules/clinvarExport'
import { validConfirmed } from '@/helpers'

export default {
  components: { SubmissionSetEditor, SubmissionSetVariantList, SubmissionSetWizardFooter },
  computed: mapState({
    wizardState: state => state.clinvarExport.wizardState,
    notification: state => state.clinvarExport.notification,
    currentSubmissionSet: state => state.clinvarExport.currentSubmissionSet
  }),
  methods: {
    ...mapActions('clinvarExport', [
      'setWizardState',
      'wizardSave',
      'wizardRemove',
      'wizardCancel'
    ]),
    validConfirmed,
    /**
     * @returns {list} with breadcrumb display
     */
    breadcrumbItems () {
      const tpl = [
        {
          text: 'Submission Set',
          href: '#',
          active: this.wizardState === WizardState.submissionSet
        },
        {
          text: 'Submissions',
          href: '#',
          active: this.wizardState === WizardState.submissions
        }
      ]

      let result = tpl
      switch (this.wizardState) {
        case 'submission':
          result = [...tpl].slice(0, 1)
          break
      }

      return result
    },
    /**
     * Event handler called when user clicks 'save'.
     */
    onSaveClicked () {
      this.validConfirmed(this.wizardSave)
    },
    /**
     * Event handler when user clicks 'remove submission set'.
     */
    onRemoveClicked () {
      this.$bvModal.msgBoxConfirm('Really delete submission set?', {
        okTitle: 'Yes',
        cancelTitle: 'No'
      }).then(value => {
        if (value) {
          this.wizardRemove()
        }
      })
    },
    /**
     * Event handler called when user clicks 'cancel'.
     */
    onCancelClicked () {
      this.$bvModal.msgBoxConfirm('Really discard any change?', {
        okTitle: 'Yes',
        cancelTitle: 'No'
      }).then(value => {
        if (value) {
          this.wizardCancel()
        }
      })
    },
    /**
     * Event handler called when user clicks 'forward to submissions'.
     */
    onGotoSubmissionsClicked () {
      this.validConfirmed(() => { this.setWizardState(WizardState.submissions) })
    },
    /**
     * Event handler called when user clicks 'back to variant list'.
     */
    onGotoSubmissionSetClicked () {
      this.validConfirmed(() => { this.setWizardState(WizardState.submissionSet) })
    },
    /**
     * @returns {String} the CSS class for the notification.
     */
    getNotificationHtmlClass () {
      return 'badge badge-' + (this.notification.status || 'success')
    },
    /**
     * @returns {boolean} whether or not the currently displayed form is valid.
     */
    isValid () {
      if (this.$refs.submissionSetCard !== undefined) {
        return this.$refs.submissionSetCard.isValid()
      } else if (this.$refs.submissionsCard !== undefined) {
        return this.$refs.submissionsCard.isValid()
      } else {
        return true
      }
    }
  }
}
</script>

<style scoped>

</style>
