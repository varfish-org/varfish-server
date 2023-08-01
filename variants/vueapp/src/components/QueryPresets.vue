<script setup>
/** This component shows the list of query preset sets.
 *
 * Editing is allowed for using a child `QueryPresetsEditor` component.
 */

import { computed, onBeforeMount, ref } from 'vue'
import { useRouter } from 'vue-router'
import { minLength, required } from '@vuelidate/validators'

import { StoreState, useQueryPresetsStore } from '@variants/stores/queryPresets'
import { useCasesStore } from '@cases/stores/cases'

import QueryPresetsSetEditor from '@variants/components/QueryPresetsSetEditor.vue'
import Overlay from '@varfish/components/Overlay.vue'
import ModalInput from '@varfish/components/ModalInput.vue'
import ModalConfirm from '@varfish/components/ModalConfirm.vue'
import Toast from '@varfish/components/Toast.vue'

/** Reuseable definition for the labels. */
const labelRules = Object.freeze([required, minLength(5)])

/** Define the props. */
const props = defineProps({
  presetSet: String,
})

/** Access store with case list. */
const casesStore = useCasesStore()
/** Access store with query presets. */
const queryPresetsStore = useQueryPresetsStore()
/** Access the router. */
const router = useRouter()

/** Ref to the input modal. */
const modalInputRef = ref(null)
/** Ref to the confirmation modal. */
const modalConfirmRef = ref(null)
/** Ref to the toast. */
const toastRef = ref(null)

/** Event handler for clicks on the "delete preset set" button.
 *
 * This will first show a confirmation dialogue.  On confirmation, the preset set will be
 * deleted via a call to the API and the UI is updated accordingly.
 */
const handleDeleteClicked = async () => {
  await modalConfirmRef.value.show({
    title: 'Please Confirm Deletion',
    isDanger: true,
    extraData: { presetSetUuid: presetSetModel.value },
  })

  try {
    presetSetModel.value = 'factory-defaults'
    await queryPresetsStore.destroyPresetSet(presetSetModel.value)
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: 'The preset set was successfully deleted.',
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: 'There was a problem deleting the preset set.',
    })
  }
}

/** Helper to get next free label for cloning. */
const _proposeCloneLabel = () => {
  function isLabelKnown(label) {
    const equalLabels = Object.values(queryPresetsStore.presetSets)
      .map((p) => p.label)
      .filter((l) => l === label)
    return equalLabels.length > 0
  }

  let proposedLabelBase
  if (presetSetModel.value === 'factory-defaults') {
    proposedLabelBase = 'Copy of Factory Presets'
  } else {
    proposedLabelBase = queryPresetsStore.presetSets[presetSetModel.value].label
  }
  let proposedLabel = proposedLabelBase
  for (let i = 1; isLabelKnown(proposedLabel); i++) {
    proposedLabel = `${proposedLabelBase} (${i})`
  }

  return proposedLabel
}

/** Event handler for the "clone preset set" button.
 *
 * This will first show an input dialogue to ask for the input of the preset set's label.  On
 * confirmation, the currently selected preset set (maybe factory presets) will be cloned via
 * the API and the UI will be adjusted appropriately.
 */
const handleCloneClicked = async () => {
  // prompt user for label to use
  const label = await modalInputRef.value.show({
    title: 'Please enter preset set label',
    label: 'Label for Clone',
    helpText:
      'The label will be used for informative purposes (display to users) only.',
    defaultValue: _proposeCloneLabel(),
    rules: labelRules,
    placeholderValue: 'PresetSet Label',
  })

  // clone preset set via API
  try {
    let clonedPresetSet
    if (presetSetModel.value === 'factory-defaults') {
      clonedPresetSet = await queryPresetsStore.cloneFactoryPresetSet(label)
    } else {
      clonedPresetSet = await queryPresetsStore.cloneOtherPresetSet(
        presetSetModel.value,
        label,
      )
    }
    presetSetModel.value = clonedPresetSet.sodar_uuid
    toastRef.value.show({
      title: 'Success!',
      level: 'success',
      body: 'The preset set has been cloned successfully.',
      autohide: true,
      delay: 10000,
    })
  } catch (error) {
    console.error(error)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: 'There was a problem deleting the preset set.',
      autohide: true,
      delay: 10000,
    })
  }
}

/** Event handler for the "edit preset set" button.
 *
 *
 * This will first show an input dialogue to ask for the input of the preset set's label.  On
 * confirmation, the currently selected preset set will be renamed.
 */
const handleEditClicked = async () => {
  // prompt user for label to use
  const label = await modalInputRef.value.show({
    title: 'Please enter preset set label',
    label: 'Updated Label',
    helpText:
      'The label will be used for informative purposes (display to users) only.',
    defaultValue: queryPresetsStore.presetSets[presetSetModel.value].label,
    rules: labelRules,
    placeholderValue: 'PresetSet Label',
  })

  // handle update via API
  try {
    await queryPresetsStore.updatePresetSet(presetSetModel.value, label)
    toastRef.value.show({
      title: 'Success!',
      level: 'success',
      body: 'The preset set has been updated successfully!',
    })
  } catch (error) {
    console.error(error)
    toastRef.value.show({
      title: 'Error!',
      level: 'error',
      body: 'The preset set could not be updated!',
    })
  }
}

/** Whether to show overlay (state is inializing or has active server interactions. */
const showOverlay = computed(
  () =>
    queryPresetsStore.storeState !== StoreState.active ||
    queryPresetsStore.serverInteractions > 0,
)

/** Initialize store on first mount. */
onBeforeMount(() => {
  casesStore.initializeRes.then(() => {
    queryPresetsStore.initialize(
      casesStore.appContext.csrf_token,
      casesStore.appContext.project.sodar_uuid,
    )
  })
})

/** Return list of presets sets in a null/undefined safe manner. */
const presetSets = computed(() => {
  if (queryPresetsStore.presetSets) {
    return Object.values(queryPresetsStore.presetSets)
  } else {
    return []
  }
})

/** Computed property to trigger router update when selected preset set changes. */
const presetSetModel = computed({
  get() {
    return props.presetSet
  },
  set(newValue, oldValue) {
    if (newValue !== oldValue) {
      if (newValue === 'factory-defaults') {
        router.push({
          name: 'case-list-query-presets',
        })
      } else {
        router.push({
          name: 'case-list-query-presets-non-factory',
          params: {
            presetSet: newValue,
          },
        })
      }
    }
  },
})
</script>

<template>
  <div>
    <div>
      <div class="row form-row align-items-center pt-3 ml-2 mr-2">
        <div class="col-6">
          <div class="input-group">
            <div class="input-group-prepend">
              <span class="input-group-text"> Preset Set </span>
            </div>
            <select
              id="select-preset"
              class="custom-select"
              v-model="presetSetModel"
            >
              <option value="factory-defaults">
                factory defaults (read-only)
              </option>
              <option
                v-for="presetSet in presetSets"
                :value="presetSet.sodar_uuid"
              >
                {{ presetSet.label }}
              </option>
            </select>
            <div class="input-group-append">
              <a class="btn btn-outline-primary" @click="handleCloneClicked()">
                <i-mdi-content-copy />
                Clone
              </a>
              <a
                class="btn btn-outline-primary"
                :class="{ disabled: presetSetModel === 'factory-defaults' }"
                @click="handleEditClicked()"
              >
                <i-mdi-file-document-edit />
                Rename
              </a>
              <a
                class="btn btn-outline-danger"
                :class="{ disabled: presetSetModel === 'factory-defaults' }"
                @click="handleDeleteClicked()"
              >
                <i-mdi-delete-forever />
                Delete
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="row pt-3 pb-3 border-top mt-3">
      <div class="col">
        <QueryPresetsSetEditor :preset-set-uuid="presetSet" />
      </div>
    </div>
    <ModalInput ref="modalInputRef" />
    <ModalConfirm ref="modalConfirmRef" />
    <Toast ref="toastRef" :autohide="false" />
    <Overlay
      v-if="showOverlay"
      :message="queryPresetsStore.storeStateMessage"
    />
  </div>
</template>
