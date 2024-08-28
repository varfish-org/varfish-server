<script setup>
import $ from 'jquery'
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { overlayMessage, overlayShow } from '@/cases/common'
import Content from '@/cases/components/CaseDetail/Content.vue'
import ModalPedigreeEditor from '@/cases/components/ModalPedigreeEditor.vue'
import ModalTermsEditor from '@/cases/components/ModalTermsEditor.vue'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { useCaseListStore } from '@/cases/stores/caseList'
import { useCaseQcStore } from '@/cases_qc/stores/caseQc'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { useSvFlagsStore } from '@/svs/stores/strucvarFlags'
import { useSvCommentsStore } from '@/svs/stores/svComments'
import { useSvResultSetStore } from '@/svs/stores/svResultSet'
import ModalConfirm from '@/varfish/components/ModalConfirm.vue'
import ModalInput from '@/varfish/components/ModalInput.vue'
import ModalSelect from '@/varfish/components/ModalSelect.vue'
import Overlay from '@/varfish/components/Overlay.vue'
import Toast from '@/varfish/components/Toast.vue'
import { useCtxStore } from '@/varfish/stores/ctx'
import { updateUserSetting } from '@/varfish/userSettings'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { useVariantCommentsStore } from '@/variants/stores/variantComments'
import { useVariantFlagsStore } from '@/variants/stores/variantFlags'
import { useVariantResultSetStore } from '@/variants/stores/variantResultSet'

const props = defineProps({
  /** The project UUID. */
  // eslint-disable-next-line vue/require-default-prop
  projectUuid: String,
  /** The case UUID. */
  // eslint-disable-next-line vue/require-default-prop
  caseUuid: String,
  /** The current tab. */
  // eslint-disable-next-line vue/require-default-prop
  currentTab: String,
})

const ctxStore = useCtxStore()

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

const seqvarPresetsStore = useSeqvarsPresetsStore()

// Routing-related.
const router = useRouter()

const refreshStores = async () => {
  if (
    props.projectUuid !== undefined &&
    props.projectUuid !== null &&
    props.caseUuid !== undefined &&
    props.caseUuid !== null
  ) {
    await Promise.all([
      (async () => {
        // We currently load this mostly for demonstration purposes in this place.
        // It really belongs to the seqvars query view.
        await Promise.all([seqvarPresetsStore.initialize(props.projectUuid)])
      })(),
      caseDetailsStore
        .initialize(props.projectUuid, props.caseUuid)
        .then(async () => {
          caseQcStore.initialize(
            props.projectUuid,
            caseDetailsStore.caseObj.sodar_uuid,
          )
          variantResultSetStore.initialize().then(async () => {
            await variantResultSetStore.loadResultSetViaCase(
              caseDetailsStore.caseObj.sodar_uuid,
            )
          })
          svResultSetStore.initialize().then(async () => {
            await svResultSetStore.loadResultSetViaCase(
              caseDetailsStore.caseObj.sodar_uuid,
            )
          })
          await Promise.all([
            variantFlagsStore.initialize(
              props.projectUuid,
              caseDetailsStore.caseObj.sodar_uuid,
            ),
            variantCommentsStore.initialize(
              props.projectUuid,
              caseDetailsStore.caseObj.sodar_uuid,
            ),
            variantAcmgRatingStore.initialize(
              props.projectUuid,
              caseDetailsStore.caseObj.sodar_uuid,
            ),
            svFlagsStore.initialize(
              props.projectUuid,
              caseDetailsStore.caseObj.sodar_uuid,
            ),
            svCommentsStore.initialize(
              props.projectUuid,
              caseDetailsStore.caseObj.sodar_uuid,
            ),
          ])
        }),
    ])
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
  const queryPresetsClient = new QueryPresetsClient(ctxStore.csrfToken)
  const allPresets = await queryPresetsClient.listPresetSetAll()
  const projectDefaultPresetSet =
    await queryPresetsClient.retrieveProjectDefaultPresetSet(props.projectUuid)
  caseDetailsStore.projectDefaultPresetSet = projectDefaultPresetSet
  const defaultLabel = projectDefaultPresetSet
    ? 'Project Default'
    : 'Factory Presets'
  const options = [{ value: null, label: defaultLabel }].concat(
    allPresets.map((p) => ({
      value: p.sodar_uuid,
      label:
        p.label +
        (p.sodar_uuid === projectDefaultPresetSet?.sodar_uuid ? '*' : ''),
    })),
  )

  try {
    const presetSetUuid = await modalSelectRef.value.show({
      title: 'Select Query Presets',
      label: 'Query Presets',
      helpText:
        'The selected presets will apply to future queries of this case by all users. ' +
        'A custom case preset will override the project default (*).',
      defaultValue: caseDetailsStore?.caseObj?.presetset ?? null,
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

defineExpose({
  handleEditQueryPresetsClicked,
  handleAddCaseCommentClicked,
  handleEditCaseStatusClicked,
  handleEditCaseNotesClicked,
  handleEditPedigreeClicked,
  handleDestroyCaseClicked,
  handleUpdateCaseCommentClicked,
  handleDeleteCaseCommentClicked,
  handleUpdateCasePhenotypeTermsClicked,
})

// Reflect "show inline help" and "filter complexity" setting in navbar checkbox.
watch(
  () => caseListStore.showInlineHelp,
  (newValue, oldValue) => {
    if (newValue !== undefined && newValue !== oldValue) {
      updateUserSetting(
        ctxStore.csrfToken,
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
    if (newValue !== undefined && newValue !== oldValue) {
      updateUserSetting(
        ctxStore.csrfToken,
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
  <h2>
    Case
    <small v-if="caseDetailsStore.caseObj" class="text-muted">{{
      caseDetailsStore.caseObj.name
    }}</small>
    <small v-else>NO CASE</small>
    &mdash;
    <span>
      <template v-if="currentTab == 'overview'"> Overview </template>
      <template v-else-if="currentTab == 'qc'"> Quality Control </template>
      <template v-else-if="currentTab == 'annotation'"> Annotation </template>
      <template v-else> UNKNOWN TAB </template>
    </span>
  </h2>
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
      @update-case-phenotype-terms-click="handleUpdateCasePhenotypeTermsClicked"
    />
    <Overlay v-if="overlayShow" :message="overlayMessage" />
  </div>
  <ModalInput ref="modalInputRef" />
  <ModalSelect ref="modalSelectRef" />
  <ModalPedigreeEditor ref="modalPedigreeEditorRef" />
  <ModalTermsEditor ref="modalTermsEditorRef" />
  <ModalConfirm ref="modalConfirmRef" />
  <Toast ref="toastRef" :autohide="false" />
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
