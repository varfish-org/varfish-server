<script setup>
import { useRoute } from 'vue-router'
import { computed, ref, watch } from 'vue'
import queryPresetsApi from '@variants/api/queryPresets.js'
import { useCasesStore } from '@cases/stores/cases.js'
import { useCaseDetailsStore } from '@cases/stores/case-details'

import ModalSelect from '@varfish/components/ModalSelect.vue'
import ModalInput from '@varfish/components/ModalInput.vue'
import ModalConfirm from '@varfish/components/ModalConfirm.vue'
import Toast from '@varfish/components/Toast.vue'

import CaseDetailHeader from './CaseDetailHeader.vue'
import CaseDetailContent from './CaseDetailContent.vue'
import ModalPedigreeEditor from './ModalPedigreeEditor.vue'
import ModalTermsEditor from './ModalTermsEditor.vue'
import Overlay from './Overlay.vue'
import { connectTopRowControls } from '../common'

const casesStore = useCasesStore()
const caseDetailsStore = useCaseDetailsStore()

/** Whether to show the overlay. */
const overlayShow = computed(() => casesStore.serverInteractions > 0)

/** The currently used route. */
const route = useRoute()

/** The currently displayed case's UUID, updated from route. */
const caseUuidRef = ref(route.params.case)

connectTopRowControls()

// We can only finish initialization once the caseDetailsStore has completed loading as we need to initialize
// some stores needed for the details view(s).  We finish by watching the route to update the case.
casesStore.initializeRes.then(() => {
  Promise.all([
    caseDetailsStore.initialize(casesStore.cases[caseUuidRef.value]),
  ])
    .then(() => {
      watch(
        () => route.params,
        (newParams, oldParams) => {
          // reload variant annotation store if necessary
          if (newParams.case && newParams.case !== oldParams.case) {
            caseDetailsStore.initialize(casesStore.cases[caseUuidRef.value])
          }
        }
      )
    })
    .catch((err) => {
      console.error('Problem while initializing case details store', err)
    })
})

/** Ref to the select modal. */
const modalSelectRef = ref(null)
/** Ref to the input modal. */
const modalInputRef = ref(null)
/** Ref to the pedigree editor modal. */
const modalPedigreeEditorRef = ref(null)
/** Ref to the phenotype terms editor modal. */
const modalTermsEditorRef = ref(null)
/** Ref to the confirm modal. */
const modalConfirmRef = ref(null)
/** Ref to the toast. */
const toastRef = ref(null)

/** Handle clicks on "edit query presets" button.
 *
 * Show a modal dialog to select the user-defined query presets or factory defaults.
 */
const handleEditQueryPresetsClicked = async () => {
  const csrfToken = casesStore.appContext.csrf_token
  const allPresets = await queryPresetsApi.listPresetSetAll(csrfToken)
  const options = [{ value: null, label: 'Factory Presets' }].concat(
    allPresets.map((p) => ({
      value: p.sodar_uuid,
      label: p.label,
    }))
  )

  try {
    const presetSetUuid = await modalSelectRef.value.show({
      title: 'Select Query Presets',
      label: `Query Presets`,
      helpText:
        'The selected presets will apply to future queries of this case by all users.',
      defaultValue: caseDetailsStore.caseObj.presetset ?? null,
      options,
    })

    await caseDetailsStore.updateCase({ presetset: presetSetUuid })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case was updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the case.`,
    })
  }
}

/** Handle clicks on "add case comment".
 *
 * Display a modal input for the comment and then add via API.
 */
const handleAddCaseCommentClicked = async () => {
  try {
    const comment = await modalInputRef.value.show({
      title: 'Enter your comment',
      label: 'Comment Text',
      widget: 'textarea',
      modalClass: 'modal-xl',
    })

    await caseDetailsStore.createCaseComment({ comment })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case comment was created successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem creating the case comment.`,
    })
  }
}

/** Handle clicks on "edit comment".
 *
 * Display a modal prefilled with the current comments and save via API.
 */
const handleUpdateCaseCommentClicked = async (caseCommentUuid) => {
  try {
    const caseComment = caseDetailsStore.getCaseComment(caseCommentUuid)
    if (caseComment === null) {
      throw new Error(`Could not find comment UUID ${caseCommentUuid}`)
    }

    const comment = await modalInputRef.value.show({
      title: 'Update the comment text',
      label: 'Comment Text',
      defaultValue: caseComment.comment,
      widget: 'textarea',
      modalClass: 'modal-xl',
    })

    await caseDetailsStore.updateCaseComment(caseCommentUuid, { comment })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case comment was updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the case comment.`,
    })
  }
}

/** Handle clicks on "delete comment".
 *
 * Display a modal that asks for confirmation.
 */
const handleDeleteCaseCommentClicked = async (caseCommentUuid) => {
  await modalConfirmRef.value.show({
    title: 'Please Confirm Deletion',
    isDanger: true,
  })

  try {
    await caseDetailsStore.destroyCaseComment(caseCommentUuid)
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case comment was successfully deleted.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem deleting the case comment.`,
    })
  }
}

/** Handle clicks on "edit case status".
 *
 * Display a modal select for the input and save via API.
 */
const handleEditCaseStatusClicked = async () => {
  const options = [
    { value: 'initial', label: 'initial' },
    { value: 'active', label: 'active' },
    { value: 'closed-unsolved', label: 'closed as unsolved' },
    { value: 'closed-uncertain', label: 'closed as uncertain' },
    { value: 'closed-solved', label: 'closed as solved' },
  ]

  try {
    const status = await modalSelectRef.value.show({
      title: `Update Case Status`,
      label: `Case Status`,
      defaultValue: caseDetailsStore.caseObj?.status ?? null,
      options,
    })

    await caseDetailsStore.updateCase({ status })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case was updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the case.`,
    })
  }
}

/** Handle clicks on "add case comment".
 *
 * Display a modal for editing the comment and save via API.
 */
const handleEditCaseNotesClicked = async () => {
  try {
    const notes = await modalInputRef.value.show({
      title: `Update Case Notess`,
      label: `Case Notes`,
      defaultValue: caseDetailsStore.caseObj?.notes ?? '',
      widget: 'textarea',
      modalClass: 'modal-xl',
    })

    await caseDetailsStore.updateCase({ notes })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case was updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the case.`,
    })
  }
}

/** Handle clicks on "edit pedigree". */
const handleEditPedigreeClicked = async () => {
  try {
    const pedigree = await modalPedigreeEditorRef.value.show({
      title: 'Update Pedigree',
      modelValue: caseDetailsStore.caseObj?.pedigree ?? [],
    })

    await caseDetailsStore.updateCase({ pedigree })

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The pedigree was updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the pedigree.`,
    })
  }
}

/** Handle click on editing the phenotype terms of a case. */
const handleUpdateCasePhenotypeTermsClicked = async ({
  casePhenotypeTermsUuid,
  individual,
}) => {
  try {
    let origTerms = []
    if (casePhenotypeTermsUuid) {
      const casePhenotypeTerms = caseDetailsStore.getCasePhenotypeTerms(
        casePhenotypeTermsUuid
      )
      if (!casePhenotypeTerms) {
        throw new Error(
          `Could not fetch case phenotype terms ${casePhenotypeTermsUuid}`
        )
      }
      origTerms = casePhenotypeTerms.terms
    }
    const terms = await modalTermsEditorRef.value.show({
      title: 'Update Phenotype Terms',
      label: 'Phenotype Terms',
      defaultValue: origTerms,
    })

    if (casePhenotypeTermsUuid) {
      await caseDetailsStore.updateCasePhenotypeTerms(casePhenotypeTermsUuid, {
        terms,
      })
    } else {
      await caseDetailsStore.createCasePhenotypeTerms(
        caseDetailsStore.caseObj.sodar_uuid,
        {
          individual,
          terms,
        }
      )
    }

    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case phenotype terms were updated successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem updating the phenotype terms.`,
    })
  }
}
</script>

<template>
  <div class="d-flex flex-column h-100">
    <CaseDetailHeader
      :case-obj="caseDetailsStore.caseObj"
      @edit-query-presets-click="handleEditQueryPresetsClicked"
      @add-case-comment-click="handleAddCaseCommentClicked"
      @edit-case-status-click="handleEditCaseStatusClicked"
      @edit-case-notes-click="handleEditCaseNotesClicked"
      @edit-pedigree-click="handleEditPedigreeClicked"
    />
    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <CaseDetailContent
        @edit-case-status-click="handleEditCaseStatusClicked"
        @edit-case-notes-click="handleEditCaseNotesClicked"
        @edit-query-presets-click="handleEditQueryPresetsClicked"
        @add-case-comment-click="handleAddCaseCommentClicked"
        @update-case-comment-click="handleUpdateCaseCommentClicked"
        @delete-case-comment-click="handleDeleteCaseCommentClicked"
        @edit-pedigree-click="handleEditPedigreeClicked"
        @update-case-phenotype-terms-click="
          handleUpdateCasePhenotypeTermsClicked
        "
      />
      <Overlay v-if="overlayShow" />
    </div>
    <ModalInput ref="modalInputRef" />
    <ModalSelect ref="modalSelectRef" />
    <ModalPedigreeEditor ref="modalPedigreeEditorRef" />
    <ModalTermsEditor ref="modalTermsEditorRef" />
    <ModalConfirm ref="modalConfirmRef" />
    <Toast ref="toastRef" :autohide="false" />
  </div>
</template>
