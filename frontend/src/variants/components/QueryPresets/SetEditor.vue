<script setup>
// eslint-disable
/** Component for editing a single preset set.
 *
 * Displays the list of preset category entries on the left as an accordion.
 *
 * The individual preset categories are editable via child components.
 */
import { computed, onMounted, ref, watch } from 'vue'
import { minLength, required } from '@vuelidate/validators'

import Sortable from 'sortablejs'

import { useCaseListStore } from '@/cases/stores/caseList'
import { useCtxStore } from '@/varfish/stores/ctx'
import { useQueryPresetsStore } from '@/variants/stores/queryPresets'

import ModalConfirm from '@/varfish/components/ModalConfirm.vue'
import ModalInput from '@/varfish/components/ModalInput.vue'
import Toast from '@/varfish/components/Toast.vue'
import FilterFormFrequencyPane from '@/variants/components/FilterForm/FrequencyPane.vue'
import FilterFormGenesRegionsPane from '@/variants/components/FilterForm/GenesRegionsPane.vue'
import FilterFormEffectPane from '@/variants/components/FilterForm/EffectPane.vue'
import FilterFormFlagsPane from '@/variants/components/FilterForm/FlagsPane.vue'
import FilterFormClinvarPane from '@/variants/components/FilterForm/ClinvarPane.vue'
import QueryPresetsSetProperties from '@/variants/components/QueryPresets/SetProperties.vue'
import QueryPresetsSetQuickPresets from '@/variants/components/QueryPresets/SetQuickPresets.vue'
import QueryPresetsQualityPane from '@/variants/components/QueryPresets/QualityPane.vue'

/** Reuseable definition for the labels. */
const labelRules = Object.freeze([required, minLength(5)])

/** Helper constant value table. */
const Category = Object.freeze({
  quickpresets: {
    name: 'quickpresets',
    title: 'Quick Presets',
  },
  frequencypresets: {
    name: 'frequencypresets',
    title: 'Frequency Presets',
  },
  impactpresets: {
    name: 'impactpresets',
    title: 'Variant Effect Presets',
  },
  chromosomepresets: {
    name: 'chromosomepresets',
    title: 'Genes & Regions Presets',
  },
  qualitypresets: {
    name: 'qualitypresets',
    title: 'Quality Presets',
  },
  flagsetcpresets: {
    name: 'flagsetcpresets',
    title: 'Flags etc. / ClinVar Presets',
  },
})

/** Define the props. */
const props = defineProps({
  projectUuid: String,
  presetSetUuid: String,
})

/** Access to application context. */
const ctxStore = useCtxStore()
/** Access store with cases. */
const caseListStore = useCaseListStore()
/** Access store with query presets. */
const queryPresetsStore = useQueryPresetsStore()

/** Computed access to the current PresetSet object in an undefined-safe manner. */
const presetSet = computed(() => {
  if (
    props.presetSetUuid &&
    queryPresetsStore.presetSets &&
    props.presetSetUuid in queryPresetsStore.presetSets
  ) {
    return queryPresetsStore.presetSets[props.presetSetUuid]
  }
})

/** The currently shown card / presets category. */
const selectedCategory = ref('presetset')
/** The currently shown presets category title. */
const selectedCategoryTitle = computed(() => {
  if (selectedCategory.value === 'presetset') {
    return 'PresetSet Properties'
  }
  if (selectedCategory.value) {
    return Category[selectedCategory.value].title
  } else {
    return 'UNDEFINED'
  }
})

/** The currently selected presets UUID or null. */
const selectedPresetsUuid = ref(null)
/** The currently selected presets object. */
const selectedPresets = computed(() => {
  if (
    !selectedCategory.value ||
    !presetSet.value ||
    selectedCategory.value == 'presetset'
  ) {
    return null
  }
  for (const presets of presetSet.value[`${selectedCategory.value}_set`]) {
    if (presets.sodar_uuid === selectedPresetsUuid.value) {
      return presets
    }
  }
  return null
})

/** Helper function to return category entries for current preset set. */
const getPresetSetEntries = (key) => {
  if (presetSet.value) {
    return presetSet.value[`${key}_set`]
  } else {
    return []
  }
}

/** Ref to the confirm modal. */
const modalConfirmRef = ref(null)
/** Ref to the input modal. */
const modalInputRef = ref(null)
/** Ref to the toast. */
const toastRef = ref(null)

/** Handle click on a presets category, will select first entry unless editing presets set properties. */
const handleCategoryClicked = async (category) => {
  queryPresetsStore.initialize(caseListStore.projectUuid, true)
  if (presetSet.value) {
    selectedCategory.value = category
    if (
      category !== 'presetset' &&
      presetSet.value[`${category}_set`].length > 0
    ) {
      selectedPresetsUuid.value =
        presetSet.value[`${category}_set`][0].sodar_uuid
    }
  }
}

/** Handle selection of a particular presets entry. */
const handlePresetsClicked = async (category, presetUuid) => {
  selectedCategory.value = category
  selectedPresetsUuid.value = presetUuid
}

/** Event handler for reverting current pane. */
const handleRevertClicked = async (category, presetsUuid) => {
  const entity =
    category === 'presetset' ? 'Preset Set' : Category[category].title
  const entityLower = entity.toLowerCase()
  await modalConfirmRef.value.show({
    noHeader: true,
    text: 'Please Confirm Reverting',
  })

  try {
    if (category === 'presetset') {
      await queryPresetsStore.revertPresetSet(props.presetSetUuid, presetsUuid)
    } else {
      await queryPresetsStore.revertPresets(
        category,
        props.presetSetUuid,
        presetsUuid,
      )
    }
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} was successfully reverted.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem reverting the ${entityLower}.`,
    })
  }
}

/** Event handler for saving current pane. */
const handleSaveClicked = async (category, presetsUuid) => {
  const entity =
    category === 'presetset' ? 'Preset Set' : Category[category].title
  const entityLower = entity.toLowerCase()

  try {
    if (category === 'presetset') {
      await queryPresetsStore.updatePresetSet(
        props.presetSetUuid,
        presetSet.value.label,
        presetSet.value.default_presetset,
      )
    } else {
      await queryPresetsStore.updatePresets(
        category,
        props.presetSetUuid,
        presetsUuid,
        selectedPresets.value,
      )
    }
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} was successfully saved.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem saving the ${entityLower}.`,
    })
  }
}

/** Event handler for adding a new preset in the given category. */
const handleAddClicked = async (category) => {
  const entity =
    category === 'presetset' ? 'Preset Set' : Category[category].title
  const entityLower = entity.toLowerCase()
  // prompt user for label to use
  const label = await modalInputRef.value.show({
    title: `Please enter new ${entity} label`,
    label: `Label for ${entity}`,
    helpText:
      'The label will be used for informative purposes (display to users) only.',
    defaultValue: `New ${entity}`,
    rules: labelRules,
    placeholderValue: `${entity} Label`,
  })

  try {
    let payload = { label }
    if (category === 'frequencypresets' || category === 'quickpresets') {
      payload = {
        label,
        frequency: null,
        impact: null,
        quality: null,
        chromosome: null,
        flagsetc: null,
      }
    } else if (category === 'qualitypresets') {
      payload = {
        label,
        fail: 'ignore',
      }
    }

    await queryPresetsStore.createPresets(
      category,
      props.presetSetUuid,
      payload,
    )
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} was successfully added.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem adding the ${entityLower}.`,
    })
  }
}

/** Event handler for renaming an existing preset in the given category. */
const handleRenameClicked = async (category, presetsUuid) => {
  const entity = Category[category].title
  const entityLower = entity.toLowerCase()
  // prompt user for label to use
  const label = await modalInputRef.value.show({
    title: `Please enter new ${entity} label`,
    label: `Label for ${entity}`,
    helpText:
      'The label will be used for informative purposes (display to users) only.',
    defaultValue: selectedPresets.value.label,
    rules: labelRules,
    placeholderValue: `${entity} Label`,
  })

  try {
    await queryPresetsStore.updatePresets(
      category,
      props.presetSetUuid,
      presetsUuid,
      { label },
    )
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} was successfully updated.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem saving the ${entityLower}.`,
    })
  }
}

/** Helper to get next free entity label for cloning. */
const _proposeCloneLabel = (category, presetsUuid) => {
  function isLabelKnown(label) {
    const equalLabels = presetSet.value[`${category}_set`]
      .map((p) => p.label)
      .filter((l) => l === label)
    return equalLabels.length > 0
  }

  let proposedLabelBase = 'Just a copy'
  for (const presets of presetSet.value[`${category}_set`]) {
    if (presets.sodar_uuid === presetsUuid) {
      proposedLabelBase = `Copy of ${presets.label}`
    }
  }
  let proposedLabel = proposedLabelBase
  for (let i = 1; isLabelKnown(proposedLabel); i++) {
    proposedLabel = `${proposedLabelBase} (${i})`
  }

  return proposedLabel
}

/** Event handler for cloning an existing preset in the given category. */
const handleCloneClicked = async (category, presetsUuid) => {
  const entity = Category[category].title
  const entityLower = entity.toLowerCase()
  // prompt user for label to use
  const label = await modalInputRef.value.show({
    title: `Please enter ${entity} label`,
    label: `Label for ${entity} Clone`,
    helpText:
      'The label will be used for informative purposes (display to users) only.',
    defaultValue: _proposeCloneLabel(category, presetsUuid),
    rules: labelRules,
    placeholderValue: `${entity} Label`,
  })

  try {
    await queryPresetsStore.clonePresets(
      category,
      props.presetSetUuid,
      presetsUuid,
      label,
    )
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} were successfully cloned.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem cloning the ${entityLower}.`,
    })
  }
}

/** Event handler for deleting an existing prest in the given category. */
const handleDeleteClicked = async (category, presetsUuid) => {
  const entity = Category[category].title
  const entityLower = entity.toLowerCase()
  await modalConfirmRef.value.show({
    title: 'Please Confirm Deletion',
    isDanger: true,
  })

  selectedPresetsUuid.value = null

  try {
    await queryPresetsStore.destroyPresets(
      category,
      props.presetSetUuid,
      presetsUuid,
    )
    toastRef.value.show({
      level: 'success',
      title: 'Success!',
      text: `The ${entityLower} were successfully deleted.`,
    })
  } catch (err) {
    console.error(err)
    toastRef.value.show({
      level: 'error',
      title: 'Error!',
      text: `There was a problem deleting the ${entityLower}.`,
    })
  }
}

const setUpQuickPresetSortable = () => {
  var el = document.getElementById('quickpresets')
  var sortable = Sortable.create(el, {
    dataIdAttr: 'id',
    draggable: '.drag-item',
    store: {
      /**
       * Save the order of elements. Called onEnd (when the item is dropped).
       * @param {Sortable}  sortable
       */
      set: async (sortable) => {
        var uuids = sortable.toArray()
        var uuidsToPresets = {}
        for (const presets of presetSet.value[
          `${selectedCategory.value}_set`
        ]) {
          uuidsToPresets[presets.sodar_uuid] = presets
        }
        uuids.forEach(async (presetsUuid, i) => {
          if (presetsUuid in uuidsToPresets) {
            uuidsToPresets[presetsUuid].position = i
            await queryPresetsStore.updatePresets(
              'quickpresets',
              props.presetSetUuid,
              presetsUuid,
              uuidsToPresets[presetsUuid],
            )
          }
        })
      },
    },
  })
}

/** When mounted, start out with frequency presets. Initialize store if necessary. */
onMounted(async () => {
  await caseListStore.initialize(props.projectUuid)
  await queryPresetsStore.initialize(caseListStore.projectUuid)
  handleCategoryClicked('presetset')
  if (getPresetSetEntries('quickpresets').length > 0) {
    setUpQuickPresetSortable()
  }
})

/** Handle change of presetSetUuid. */
watch(
  () => props.presetSetUuid,
  (newValue) => {
    handleCategoryClicked('presetset')
  },
)

// eslint-enable
</script>

<template>
  <!-- eslint-disable -->
  <div>
    <div v-if="!presetSetUuid" class="text-muted text-center font-italic">
      No query preset selected.
    </div>
    <div
      v-else-if="presetSetUuid === 'factory-defaults'"
      class="text-muted text-center font-italic"
    >
      Cannot display factory defaults (yet). Why don't you just clone them and
      inspect your copy?
    </div>
    <div v-else>
      <div class="row pt-1">
        <div class="col-3 pl-0">
          <div class="accordion">
            <div class="card mb-0">
              <div
                class="card-header pl-1 pr-1 pt-1 pb-1"
                :class="{ 'bg-secondary': selectedCategory === 'presetset' }"
              >
                <h2 class="mb-0">
                  <button
                    class="btn btn-block text-left shadow-none"
                    :class="{
                      'text-white': selectedCategory === 'presetset',
                      'text-dark': selectedCategory !== 'presetset',
                    }"
                    type="button"
                    @click="handleCategoryClicked('presetset')"
                  >
                    Preset Set Properties
                  </button>
                </h2>
              </div>
            </div>
            <div v-for="category in Object.values(Category)" class="card mb-0">
              <div
                class="card-header pl-1 pr-1 pt-1 pb-1"
                :class="{ 'bg-secondary': selectedCategory === category.name }"
              >
                <h2 class="mb-0">
                  <button
                    class="btn btn-block text-left shadow-none"
                    :class="{
                      'text-white': selectedCategory === category.name,
                      'text-dark': selectedCategory !== category.name,
                    }"
                    type="button"
                    @click="handleCategoryClicked(category.name)"
                  >
                    {{ category.title }}
                  </button>
                </h2>
              </div>

              <div
                class="collapse"
                :class="{ show: selectedCategory === category.name }"
              >
                <div class="card-body" :id="category.name">
                  <template
                    v-if="getPresetSetEntries(category.name).length > 0"
                  >
                    <div
                      v-for="entry in getPresetSetEntries(category.name)"
                      class="drag-item nav nav-pills flex-column"
                      :id="entry.sodar_uuid"
                    >
                      <a
                        class="nav-link"
                        :class="{
                          active: entry.sodar_uuid === selectedPresetsUuid,
                        }"
                        style="cursor: pointer"
                        @click="
                          handlePresetsClicked(category.name, entry.sodar_uuid)
                        "
                      >
                        <i-mdi-reorder-horizontal
                          v-if="category.name === 'quickpresets'"
                        />
                        {{ entry.label }}
                      </a>
                    </div>
                  </template>
                  <div v-else class="nav nav-pills flex-column">
                    <span class="nav-link text-muted text-center font-italic"
                      >No presets yet.</span
                    >
                  </div>
                  <div class="nav nav-pills flex-column pt-3 pb-3">
                    <a
                      href="#"
                      class="btn btn-sm btn-light"
                      @click.prevent="handleAddClicked(category.name)"
                    >
                      <i-mdi-plus-circle />
                      Add New
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="col-9 pl-0 pr-0">
          <div class="border-bottom d-flex flex-row pb-2 mb-3">
            <h5 class="flex-grow-1">
              {{ selectedCategoryTitle }}
              <small class="text-muted">
                {{ selectedPresets?.label }}
              </small>
            </h5>
            <div class="btn-group">
              <a
                class="btn btn-sm btn-success"
                @click="
                  handleSaveClicked(selectedCategory, selectedPresetsUuid)
                "
              >
                <i-mdi-check />
                Save
              </a>
              <a
                class="btn btn-sm btn-secondary"
                @click="
                  handleRevertClicked(selectedCategory, selectedPresetsUuid)
                "
              >
                <i-mdi-undo-variant />
                Revert
              </a>
              <a
                v-if="selectedCategory !== 'presetset'"
                class="btn btn-sm btn-primary"
                @click="
                  handleCloneClicked(selectedCategory, selectedPresetsUuid)
                "
              >
                <i-mdi-content-copy />
                Clone
              </a>
              <a
                v-if="selectedCategory !== 'presetset'"
                class="btn btn-sm btn-primary"
                :class="{ disabled: presetSetUuid === 'factory-defaults' }"
                @click="
                  handleRenameClicked(selectedCategory, selectedPresetsUuid)
                "
              >
                <i-mdi-file-document-edit />
                Rename
              </a>
              <a
                v-if="selectedCategory !== 'presetset'"
                class="btn btn-sm btn-danger"
                :class="{ disabled: presetSetUuid === 'factory-defaults' }"
                @click="
                  handleDeleteClicked(selectedCategory, selectedPresetsUuid)
                "
              >
                <i-mdi-delete-forever />
                Delete
              </a>
            </div>
          </div>
          <!-- PresetSet Properties -->
          <div v-if="selectedCategory === 'presetset' && presetSet">
            <QueryPresetsSetProperties
              v-model:label="presetSet.label"
              v-model:defaultPresetSet="presetSet.default_presetset"
              :currentDefaultPresetSet="
                queryPresetsStore.getDefaultPresetSetName()
              "
            />
          </div>
          <!-- Quick Presets -->
          <div
            v-else-if="
              selectedCategory === 'quickpresets' && selectedPresetsUuid
            "
          >
            <QueryPresetsSetQuickPresets
              :preset-set="presetSet"
              :query-settings="selectedPresets"
            />
          </div>
          <!-- Frequency -->
          <div
            v-else-if="
              selectedCategory === 'frequencypresets' && selectedPresetsUuid
            "
          >
            <FilterFormFrequencyPane
              filtration-complexity-mode="advanced"
              :case="{ release: 'GRCh37' }"
              :query-settings="selectedPresets"
            />
          </div>
          <!-- Variants & Effects -->
          <div
            v-else-if="
              selectedCategory === 'impactpresets' && selectedPresetsUuid
            "
          >
            <FilterFormEffectPane
              filtration-complexity-mode="advanced"
              :query-settings="selectedPresets"
            />
          </div>
          <!-- Genes & Regions -->
          <div
            v-else-if="
              selectedCategory === 'chromosomepresets' && selectedPresetsUuid
            "
          >
            <FilterFormGenesRegionsPane
              filtration-complexity-mode="advanced"
              :query-settings="selectedPresets"
            />
          </div>
          <!-- Quality -->
          <div
            v-else-if="
              selectedCategory === 'qualitypresets' && selectedPresetsUuid
            "
          >
            <QueryPresetsQualityPane :query-settings="selectedPresets" />
          </div>
          <!-- Flags etc. / ClinVar -->
          <div
            v-else-if="
              selectedCategory === 'flagsetcpresets' && selectedPresetsUuid
            "
          >
            <h6>ClinVar</h6>
            <FilterFormFlagsPane
              filtration-complexity-mode="advanced"
              :query-settings="selectedPresets"
            />
            <h6>ClinVar</h6>
            <FilterFormClinvarPane
              filtration-complexity-mode="advanced"
              :query-settings="selectedPresets"
            />
          </div>
          <!-- Nothing Selected -->
          <div v-else class="text-center text-muted font-italic">
            Please select a presets entry on the left to edit.
          </div>
        </div>
      </div>
    </div>
    <ModalConfirm ref="modalConfirmRef" />
    <ModalInput ref="modalInputRef" />
    <Toast ref="toastRef" :autohide="false" />
  </div>
  <!-- eslint-enable -->
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
