<script>
import { mapActions, mapState } from 'pinia'

import clinvarExport from '@/api/clinvarExport'
import { useClinvarExportStore } from '@/stores/clinvar-export'

export default {
  data: function () {
    return {
      submissionSetUuid: null,
      xmlPreviewData: null,
      xmlPreviewState: 'loading',
      xmlValidationState: 'initial',
    }
  },
  computed: {
    ...mapState(useClinvarExportStore, [
      'appContext',
      'notification',
      'submissionSetList',
    ]),
  },
  methods: {
    ...mapActions(useClinvarExportStore, [
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
      $(this.$refs.modalXmlPreview).modal('show')
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
      $(this.$refs.modalXmlPreview).modal('hide')
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
    isValid: function () {
      return true
    },
  },
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="mb-0">
        <i class="iconify" data-icon="fa-regular:folder"></i>
        Submission Set List

        <transition name="fade">
          <div v-if="notification" class="float-right">
            <span :class="getNotificationHtmlClass()">{{
              notification.text
            }}</span>
          </div>
        </transition>
      </h4>
    </div>

    <table class="table table-striped table-hover">
      <thead>
        <tr>
          <th>Title</th>
          <th>Last Change</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="submissionSet in submissionSetList"
          :key="submissionSet.sodar_uuid"
        >
          <td>{{ submissionSet.title }}</td>
          <td>
            {{ submissionSet.date_modified }}
            <div class="btn-group float-right mr-1">
              <button
                type="button"
                class="btn btn-sm btn-primary submission-set-table-button-edit"
                @click="editSubmissionSet(submissionSet.sodar_uuid)"
              >
                <i class="iconify" data-icon="mdi:pencil"></i>
                Edit
              </button>
              <button
                type="button"
                class="btn btn-sm btn-secondary submission-set-table-button-edit"
                @click="onXmlPreviewClicked(submissionSet.sodar_uuid)"
              >
                <i class="iconify" data-icon="fa-solid:code"></i>
                ClinVar XML
              </button>
            </div>
          </td>
        </tr>
        <tr v-if="!submissionSetList.length">
          <td colspan="2" class="text-center font-italic text-muted">
            No submission sets yet.
          </td>
        </tr>
      </tbody>
    </table>

    <div class="card-footer">
      <button
        ref="buttonCreateNew"
        type="button"
        class="btn btn-primary float-right"
        size="sm"
        @click="createNewSubmissionSet()"
      >
        <span
          class="iconify"
          data-icon="mdi:plus-circle"
          data-inline="false"
        ></span>
        Create Set
      </button>
    </div>

    <div ref="modalXmlPreview" class="modal fade">
      <div
        class="modal-dialog modal-lg modal-dialog-scrollable"
        role="document"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">ClinVar Submission XML Preview</h5>
          </div>
          <div class="modal-body">
            <p>
              VarFish allows for the export of ClinVar submission sets to XML.
              These XML files can be uploaded to ClinVar using the ClinVar web
              user interface (there is no API yet).
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
          </div>
          <div class="modal-footer">
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

              <div class="btn-group float-right">
                <button
                  ref="buttonDownloadXml"
                  type="button"
                  class="btn btn-sm btn-primary"
                  @click.prevent="onDownloadXmlClicked()"
                  @active="isDownloadXmlActive()"
                >
                  <i class="fa fa-cloud-download"></i>
                  Download
                </button>
                <button
                  ref="buttonClose"
                  type="button"
                  class="btn btn-sm btn-secondary"
                  @click="onXmlHideClicked()"
                >
                  <span
                    class="iconify"
                    data-icon="mdi:close"
                    data-inline="false"
                  ></span>
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

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
