<template>
  <b-card no-body title-tag="title" footer-tag="footer">
    <template #header>
      <h4 class="mb-0">
        <i class="iconify" data-icon="fa-regular:folder"></i>
        Submission Set List {{ submissionSetList.length }}

        <transition name="fade">
          <div v-if="notification" class="float-right">
            <span :class="getNotificationHtmlClass()">{{
              notification.text
            }}</span>
          </div>
        </transition>
      </h4>
    </template>

    <b-table
      ref="submissionSetTable"
      striped
      hover
      show-empty
      :fields="fields"
      :items="submissionSetList"
    >
      <template #cell(title)="row">
        {{ row.item.title }}
      </template>
      <template #cell(last_change)="row">
        {{ row.item.date_modified }}
        <b-button-group class="float-right mr-1">
          <b-button
            class="submission-set-table-button-edit"
            size="sm"
            variant="primary"
            @click="editSubmissionSet(row.item.sodar_uuid)"
          >
            <i class="iconify" data-icon="mdi:pencil"></i>
            Edit
          </b-button>
          <b-button
            class="submission-set-table-button-clinvar-xml"
            size="sm"
            variant="secondary"
            @click="onXmlPreviewClicked(row.item.sodar_uuid)"
          >
            <i class="iconify" data-icon="fa-solid:code"></i>
            ClinVar XML
          </b-button>
        </b-button-group>
      </template>
    </b-table>

    <template #footer>
      <b-button
        ref="buttonCreateNew"
        variant="primary"
        size="sm"
        class="float-right"
        @click="createNewSubmissionSet()"
      >
        <span
          class="iconify"
          data-icon="mdi:plus-circle"
          data-inline="false"
        ></span>
        Create Set
      </b-button>
    </template>

    <b-modal
      id="modal-xml-preview"
      ref="modalXmlPreview"
      size="lg"
      scrollable
      title="ClinVar Submission XML Preview"
    >
      <p>
        VarFish allows for the export of ClinVar submission sets to XML. These
        XML files can be uploaded to ClinVar using the ClinVar web user
        interface (there is no API yet).
      </p>

      <div v-if="xmlPreviewState == 'loading'">
        <div class="text-center">
          <i
            class="iconify spin text-muted mt-5"
            data-icon="fa-solid:circle-notch"
          ></i>
          <br />
          <br />
          <span class="text-muted font-italic">Loading...</span>
        </div>
      </div>
      <div v-if="xmlPreviewState == 'loaded'">
        <pre
          class="border rounded p-2"
          style="overflow-y: auto; max-height: 400px"
        ><code>{{ xmlPreviewData }}</code></pre>
      </div>
      <div v-if="xmlValidationState == 'invalid'" class="row">
        <div class="px-0 col-12">
          <strong> Validation Details: </strong>
          <span v-if="!xmlValidationDetails" class="text-muted"
            >none provided</span
          >
          <span v-if="xmlValidationDetails">
            {{ xmlValidationDetails }}
          </span>
        </div>
      </div>
      <template #modal-footer>
        <div class="w-100">
          <div class="float-left">
            <div v-if="xmlValidationState == 'initial'" class="text-muted">
              <i class="iconify" data-icon="fa-solid:question"></i>
              XSD check: waiting for XML
            </div>
            <div v-if="xmlValidationState == 'loading'" class="text-muted">
              <i
                class="iconify spin text-muted"
                data-icon="fa-solid:circle-notch"
              ></i>
              XSD check: running
            </div>
            <div v-if="xmlValidationState == 'valid'" class="text-success">
              <span
                class="iconify"
                data-icon="mdi:check-bold"
                data-inline="false"
              ></span>
              XSD check: valid
            </div>
            <div v-if="xmlValidationState == 'invalid'" class="text-danger">
              <span
                class="iconify"
                data-icon="mdi:close"
                data-inline="false"
              ></span>
              XSD check: invalid
            </div>
          </div>

          <b-button-group class="float-right">
            <b-button
              ref="buttonDownloadXml"
              variant="primary"
              size="sm"
              @click.prevent="onDownloadXmlClicked()"
              @active="isDownloadXmlActive()"
            >
              <i class="fa fa-cloud-download"></i>
              Download
            </b-button>
            <b-button
              ref="buttonClose"
              variant="secondary"
              size="sm"
              @click="onXmlHideClicked()"
            >
              <span
                class="iconify"
                data-icon="mdi:close"
                data-inline="false"
              ></span>
              Close
            </b-button>
          </b-button-group>
        </div>
      </template>
    </b-modal>
  </b-card>
</template>

<script>
import { mapActions, mapState } from 'vuex'

import clinvarExport from '@/api/clinvarExport'

export default {
  data: function () {
    return {
      fields: ['title', 'last_change'],
      submissionSetUuid: null,
      xmlPreviewData: null,
      xmlPreviewState: 'loading',
      xmlValidationState: 'initial',
    }
  },
  computed: mapState({
    appContext: (state) => state.clinvarExport.appContext,
    notification: (state) => state.clinvarExport.notification,
    submissionSetList: (state) => state.clinvarExport.submissionSetList,
  }),
  methods: {
    ...mapActions('clinvarExport', [
      'createNewSubmissionSet',
      'editSubmissionSet',
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
      clinvarExport
        .getSubmissionSetXml(this.appContext, submissionSetUuid)
        .then((response) => {
          response.text().then((text) => {
            this.xmlPreviewData = text
            this.xmlPreviewState = 'loaded'
            this.xmlValidationState = 'loading'
            clinvarExport
              .getSubmissionSetValid(this.appContext, submissionSetUuid)
              .then((response) => {
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
      link.setAttribute('href', URL.createObjectURL(blob))
      link.setAttribute('download', `clinvar-${this.submissionSetUuid}.xml`)
      link.click()
      link.remove()
    },
    isDownloadXmlActive: function () {
      return this.xmlPreviewState === 'loaded'
    },
  },
}
</script>

<style scoped>
.modal-lg {
  max-width: 1140px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
