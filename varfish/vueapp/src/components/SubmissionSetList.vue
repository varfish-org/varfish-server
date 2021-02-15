<template>
  <b-card no-body title-tag="title" footer-tag="footer">
    <template #header>
      <h4 class="mb-0">
        <i class="fa fa-folder-o"></i>
        Submission Set List

        <transition name="fade">
          <div v-if="notification" class="float-right">
            <span :class="getNotificationHtmlClass()">{{ notification.text }}</span>
          </div>
        </transition>
      </h4>
    </template>

    <b-table striped hover show-empty :fields="fields" :items="submissionSetList">
      <template #cell(title)="row">
        {{ row.item.title }}
      </template>
      <template #cell(last_change)="row">
        {{ row.item.date_modified }}
        <b-button-group class="float-right mr-1">
          <b-button size="sm" variant="primary" @click="editSubmissionSet(row.item.sodar_uuid)">
            <i class="fa fa-pencil"></i>
            Edit
          </b-button>
          <b-button size="sm" variant="secondary" @click="onXmlPreviewClicked(row.item.sodar_uuid)">
            <i class="fa fa-code"></i>
            ClinVar XML
          </b-button>
        </b-button-group>
      </template>
    </b-table>

    <template #footer>
      <b-button variant="primary" size="sm" class="float-right" @click="createNewSubmissionSet()">
        <i class="fa fa-plus"></i>
        Create Set
      </b-button>
    </template>

    <b-modal id="modal-xml-preview" size="lg" scrollable title="ClinVar Submission XML Preview">
      <p>
        VarFish allows for the export of ClinVar submission sets to XML.
        These XML files can be uploaded to ClinVar using the ClinVar web user interface (there is no API yet).
      </p>

      <div v-if="xmlPreviewState == 'loading'">
        <div class="text-center">
          <i class="fa fa-4x fa-spin fa-circle-o-notch text-muted mt-5"></i>
          <br />
          <br />
          <span class="text-muted font-italic">Loading...</span>
        </div>
      </div>
      <div v-if="xmlPreviewState == 'loaded'">
        <pre class="border rounded p-2" style="overflow-y: auto; max-height: 400px;"><code>{{ xmlPreviewData }}</code></pre>
      </div>
      <div v-if="xmlValidationState == 'invalid'" class="row">
        <div class="px-0 col-12">
          <strong>
            Validation Details:
          </strong>
          <span v-if="!xmlValidationDetails" class="text-muted">none provided</span>
          <span v-if="xmlValidationDetails">
            {{ xmlValidationDetails }}
          </span>
        </div>
      </div>
      <template #modal-footer>
        <div class="w-100">
          <div class="float-left">
            <div v-if="xmlValidationState == 'initial'" class="text-muted">
              <i class="fa fa-question"></i>
              XSD check: waiting for XML
            </div>
            <div v-if="xmlValidationState == 'loading'" class="text-muted">
              <i class="fa fa-spin fa-circle-o-notch text-muted"></i>
              XSD check: running
            </div>
            <div v-if="xmlValidationState == 'valid'" class="text-success">
              <i class="fa fa-check"></i>
              XSD check: valid
            </div>
            <div v-if="xmlValidationState == 'invalid'" class="text-danger">
              <i class="fa fa-times"></i>
              XSD check: invalid
            </div>
          </div>

          <b-button-group class="float-right">
            <b-button variant="primary" size="sm" @click.prevent="onDownloadXmlClicked()" @active="isDownloadXmlActive()">
              <i class="fa fa-cloud-download"></i>
              Download
            </b-button>
            <b-button variant="secondary" size="sm" @click="onXmlHideClicked()">
              <i class="fa fa-times"></i>
              Close
            </b-button>
          </b-button-group>
        </div>
      </template>
    </b-modal>
  </b-card>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import clinvarExport from '@/api/clinvarExport'

export default {
  computed: mapState({
    appContext: state => state.clinvarExport.appContext,
    notification: state => state.clinvarExport.notification,
    submissionSetList: state => state.clinvarExport.submissionSetList
  }),
  methods: {
    ...mapActions('clinvarExport', [
      'createNewSubmissionSet',
      'editSubmissionSet'
    ]),
    getNotificationHtmlClass: function () {
      return 'small badge badge-' + (this.notification.status || 'success')
    },
    onXmlPreviewClicked: function (submissionSetUuid) {
      this.submissionSetUuid = submissionSetUuid
      this.xmlValidationState = 'initial'
      this.xmlValidationDetails = null
      this.xmlPreviewData = ''
      this.xmlPreviewState = 'loading'
      this.$bvModal.show('modal-xml-preview')
      clinvarExport.getSubmissionSetXml(this.appContext, submissionSetUuid).then((response) => {
        response.text().then((text) => {
          this.xmlPreviewData = text
          this.xmlPreviewState = 'loaded'
          this.xmlValidationState = 'loading'
          clinvarExport.getSubmissionSetValid(this.appContext, submissionSetUuid).then((response) => {
            response.json().then((result) => {
              this.xmlValidationState = result.valid ? 'valid' : 'invalid'
              this.xmlValidationDetails = result.details
            })
          })
        })
      })
    },
    onXmlHideClicked: function () {
      this.$bvModal.hide('modal-xml-preview')
    },
    onDownloadXmlClicked: function () {
      const blob = new Blob([this.xmlPreviewData], { type: 'application/xml' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `clinvar-${this.submissionSetUuid}.xml`
      link.click()
    },
    isDownloadXmlActive: function () {
      return this.xmlPreviewState === 'loaded'
    }
  },
  data: function () {
    return {
      fields: ['title', 'last_change'],
      submissionSetUuid: null,
      xmlPreviewData: null,
      xmlPreviewState: 'loading',
      xmlValidationState: 'initial'
    }
  }
}
</script>

<style scoped>
.modal-lg {
  max-width: 1140px;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
