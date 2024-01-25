<script setup>
import { onMounted, nextTick, ref, watch } from 'vue'
import { QueryPresetsClient } from '@variants/api/queryPresetsClient'
import { useCaseListStore } from '@cases/stores/caseList'
import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { useCaseQcStore } from '@cases_qc/stores/caseQc'
import { useVariantFlagsStore } from '@variants/stores/variantFlags'
import { useVariantCommentsStore } from '@variants/stores/variantComments'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { useVariantResultSetStore } from '@variants/stores/variantResultSet'
import { useSvResultSetStore } from '@svs/stores/svResultSet'
import { useSvFlagsStore } from '@svs/stores/svFlags'
import { useSvCommentsStore } from '@svs/stores/svComments'
import { overlayShow, overlayMessage } from '@cases/common'
import { useRouter } from 'vue-router'

import ModalSelect from '@varfish/components/ModalSelect.vue'
import ModalInput from '@varfish/components/ModalInput.vue'
import ModalConfirm from '@varfish/components/ModalConfirm.vue'
import Overlay from '@varfish/components/Overlay.vue'
import Toast from '@varfish/components/Toast.vue'
import { updateUserSetting } from '@varfish/userSettings'

import Header from '@cases/components/CaseDetail/Header.vue'
import Content from '@cases/components/CaseDetail/Content.vue'
import ModalPedigreeEditor from '@cases/components/ModalPedigreeEditor.vue'
import ModalTermsEditor from '@cases/components/ModalTermsEditor.vue'

const props = defineProps({
  /** The case UUID. */
  caseUuid: String,
  /** The current tab. */
  currentTab: String,
})

/** Obtain global application content (as for all entry level components) */
const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)

const caseListStore = useCaseListStore()
const caseDetailsStore = useCaseDetailsStore()
const caseQcStore = useCaseQcStore()
const variantFlagsStore = useVariantFlagsStore()
const variantCommentsStore = useVariantCommentsStore()
const variantAcmgRatingStore = useVariantAcmgRatingStore()
const variantResultSetStore = useVariantResultSetStore()
const svResultSetStore = useSvResultSetStore()
const svFlagsStore = useSvFlagsStore()
const svCommentsStore = useSvCommentsStore()

// Routing-related.

const router = useRouter()

const refreshStores = async () => {
  if (
    appContext?.csrf_token &&
    appContext?.project?.sodar_uuid &&
    props?.caseUuid
  ) {
    caseDetailsStore
      .initialize(
        appContext.csrf_token,
        appContext.project.sodar_uuid,
        props.caseUuid,
      )
      .then(async () => {
        caseQcStore.initialize(
          appContext.csrf_token,
          appContext.project.sodar_uuid,
          caseDetailsStore.caseObj.sodar_uuid,
        )
        variantResultSetStore
          .initialize(appContext.csrf_token)
          .then(async () => {
            await variantResultSetStore.loadResultSetViaCase(
              caseDetailsStore.caseObj.sodar_uuid,
            )
          })
        svResultSetStore.initialize(appContext.csrf_token).then(async () => {
          await svResultSetStore.loadResultSetViaCase(
            caseDetailsStore.caseObj.sodar_uuid,
          )
        })
        await Promise.all([
          variantFlagsStore.initialize(
            appContext.csrf_token,
            appContext.project.sodar_uuid,
            caseDetailsStore.caseObj.sodar_uuid,
          ),
          variantCommentsStore.initialize(
            appContext.csrf_token,
            appContext.project.sodar_uuid,
            caseDetailsStore.caseObj.sodar_uuid,
          ),
          variantAcmgRatingStore.initialize(
            appContext.csrf_token,
            appContext.project.sodar_uuid,
            caseDetailsStore.caseObj.sodar_uuid,
          ),
          svFlagsStore.initialize(
            appContext.csrf_token,
            appContext.project?.sodar_uuid,
            caseDetailsStore.caseObj.sodar_uuid,
          ),
          svCommentsStore.initialize(
            appContext.csrf_token,
            appContext.project?.sodar_uuid,
            caseDetailsStore.caseObj.sodar_uuid,
          ),
        ])
      })
  }
}

onMounted(() => {
  refreshStores()
})

watch(
  () => props.caseUuid,
  () => refreshStores(),
)

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
  const queryPresetsClient = new QueryPresetsClient(caseListStore.csrfToken)
  const allPresets = await queryPresetsClient.listPresetSetAll()
  const options = [{ value: null, label: 'Factory Presets' }].concat(
    allPresets.map((p) => ({
      value: p.sodar_uuid,
      label: p.label,
    })),
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
      title: `Update Case Notes`,
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
        casePhenotypeTermsUuid,
      )
      if (!casePhenotypeTerms) {
        throw new Error(
          `Could not fetch case phenotype terms ${casePhenotypeTermsUuid}`,
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
        },
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

/** Handle clicks on "add case comment".
 *
 * Display a modal for editing the comment and save via API.
 */
const handleDestroyCaseClicked = async () => {
  await modalConfirmRef.value.show({
    title: 'Please Confirm Deletion',
    isDanger: true,
  })
  try {
    await caseDetailsStore.destroyCase()
    router.push({
      name: 'case-list',
    })
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The case was deleted successfully.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem deleting the case.`,
    })
  }
}

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => caseListStore.showInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== oldValue && caseListStore.csrfToken) {
      updateUserSetting(
        caseListStore.csrfToken,
        'vueapp.filtration_inline_help',
        newValue,
      )
    }
    const elem = $('#vueapp-filtration-inline-help')
    if (elem) {
      elem.prop('checked', newValue)
    }
  },
)
watch(
  () => caseListStore.complexityMode,
  (newValue, oldValue) => {
    if (newValue !== oldValue && caseListStore.csrfToken) {
      updateUserSetting(
        caseListStore.csrfToken,
        'vueapp.filtration_complexity_mode',
        newValue,
      )
    }
    const elem = $('#vueapp-filtration-complexity-mode')
    if (elem && elem.val(newValue)) {
      elem.val(newValue).change()
    }
  },
)

// Vice versa.
onMounted(() => {
  const handleUpdate = () => {
    const caseListStore = useCaseListStore()
    caseListStore.showInlineHelp = $('#vueapp-filtration-inline-help').prop(
      'checked',
    )
    caseListStore.complexityMode = $('#vueapp-filtration-complexity-mode').val()
  }
  nextTick(() => {
    handleUpdate()
    $('#vueapp-filtration-inline-help').change(handleUpdate)
    $('#vueapp-filtration-complexity-mode').change(handleUpdate)
  })
})
</script>

<template>
  <div class="d-flex flex-column h-100">
    <Header
      :case-obj="caseDetailsStore.caseObj"
      @edit-query-presets-click="handleEditQueryPresetsClicked"
      @add-case-comment-click="handleAddCaseCommentClicked"
      @edit-case-status-click="handleEditCaseStatusClicked"
      @edit-case-notes-click="handleEditCaseNotesClicked"
      @edit-pedigree-click="handleEditPedigreeClicked"
      @destroy-case-click="handleDestroyCaseClicked"
    />
    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <Content
        :case-uuid="props.caseUuid"
        :current-tab="props.currentTab"
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
      <Overlay v-if="overlayShow" :message="overlayMessage" />
    </div>
    <ModalInput ref="modalInputRef" />
    <ModalSelect ref="modalSelectRef" />
    <ModalPedigreeEditor ref="modalPedigreeEditorRef" />
    <ModalTermsEditor ref="modalTermsEditorRef" />
    <ModalConfirm ref="modalConfirmRef" />
    <Toast ref="toastRef" :autohide="false" />
  </div>
</template>
