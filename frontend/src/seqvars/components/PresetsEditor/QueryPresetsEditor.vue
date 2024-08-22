<script setup lang="ts">
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import CategoryPresetsClinvarEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsClinvarEditor.vue'
import CategoryPresetsColumnsEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsColumnsEditor.vue'
import CategoryPresetsConsequenceEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsConsequenceEditor.vue'
import CategoryPresetsFrequencyEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsFrequencyEditor.vue'
import CategoryPresetsLocusEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsLocusEditor.vue'
import CategoryPresetsPhenotypePrioEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsPhenotypePrioEditor.vue'
import CategoryPresetsPredefinedQueriesEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsPredefinedQueriesEditor.vue'
import CategoryPresetsQualityEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsQualityEditor.vue'
import CategoryPresetsVariantPrioEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsVariantPrioEditor.vue'
import PresetsList from '@/seqvars/components/PresetsEditor/PresetsList.vue'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { EditableState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { PresetsCategory, PresetsCategoryInfo } from './lib'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current preset set version. */
  presetSetVersion?: string
}>()

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/* The currently selected preset set version (details, contains preset set info). */
const selectedPresetSetVersion = computed<
  SeqvarsQueryPresetsSetVersionDetails | undefined
>(() => {
  if (props.presetSetVersion) {
    return seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion)
  } else {
    return undefined
  }
})

/** Category information/definition. */
const categories = computed<PresetsCategoryInfo[]>(() => {
  return [
    {
      label: 'Quality',
      category: PresetsCategory.QUALITY,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsquality_set ?? [],
    },
    {
      label: 'Frequency',
      category: PresetsCategory.FREQUENCY,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsfrequency_set ?? [],
    },
    {
      label: 'Consequence',
      category: PresetsCategory.CONSEQUENCE,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsconsequence_set ??
        [],
    },
    {
      label: 'Locus',
      category: PresetsCategory.LOCUS,
      items: selectedPresetSetVersion.value?.seqvarsquerypresetslocus_set ?? [],
    },
    {
      label: 'Phenotype Prioritization',
      category: PresetsCategory.PHENOTYPE_PRIO,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsphenotypeprio_set ??
        [],
    },
    {
      label: 'Variant Prioritization',
      category: PresetsCategory.VARIANT_PRIO,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsvariantprio_set ??
        [],
    },
    {
      label: 'ClinVar',
      category: PresetsCategory.CLINVAR,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsclinvar_set ?? [],
    },
    {
      label: 'Columns',
      category: PresetsCategory.COLUMNS,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetscolumns_set ?? [],
    },
    {
      label: 'Predefined Queries',
      category: PresetsCategory.PREDEFINED_QUERIES,
      items: selectedPresetSetVersion.value?.seqvarspredefinedquery_set ?? [],
    },
  ]
})

/** Currently selected category. */
const selectedCategory = ref<PresetsCategory>(PresetsCategory.QUALITY)

/** Selected presets in each category. */
const selectedPreset = reactive<{
  [key in PresetsCategory]: string | undefined
}>({
  [PresetsCategory.QUALITY]: undefined,
  [PresetsCategory.FREQUENCY]: undefined,
  [PresetsCategory.CONSEQUENCE]: undefined,
  [PresetsCategory.LOCUS]: undefined,
  [PresetsCategory.PHENOTYPE_PRIO]: undefined,
  [PresetsCategory.VARIANT_PRIO]: undefined,
  [PresetsCategory.CLINVAR]: undefined,
  [PresetsCategory.COLUMNS]: undefined,
  [PresetsCategory.PREDEFINED_QUERIES]: undefined,
})

/**
 * Create a new presets, emitting "message" for success/failure.
 *
 * @param category The category for which to create presets.
 * @param label The label for the new presets.
 */
const doCreatePresets = async (category: PresetsCategory, label: string) => {
  // Guard against missing preset set version.
  if (props.presetSetVersion) {
    // Category text to show in the message.
    let msgCat: string = ''
    try {
      switch (category) {
        case PresetsCategory.QUALITY:
          msgCat = 'quality'
          seqvarsPresetsStore.createQueryPresetsQuality(
            props.presetSetVersion,
            label,
          )
          break
        default:
          throw new Error(`Unknown category ${category}`)
      }
    } catch (error) {
      emit('message', {
        text: `Failed to create ${msgCat} presets: ${error}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Successfully created ${msgCat} presets "${label}"`,
      color: 'success',
    })
  }
}

/**
 * Delete a presets, emitting "message" for success/failure.
 *
 * @param category The category for which to delete presets.
 * @param uuid The UUID of the presets to delete.
 */
const doDeletePresets = async (category: PresetsCategory, uuid: string) => {
  // Guard against missing preset set version.
  if (props.presetSetVersion) {
    // Category text to show in the message.
    let msgCat: string = ''
    try {
      switch (category) {
        case PresetsCategory.QUALITY:
          msgCat = 'quality'
          seqvarsPresetsStore.deleteQueryPresetsQuality(
            props.presetSetVersion,
            uuid,
          )
          break
        default:
          throw new Error(`Unknown category ${category}`)
      }
    } catch (error) {
      emit('message', {
        text: `Failed to delete ${msgCat} presets: ${error}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Successfully deleted ${msgCat} presets`,
      color: 'success',
    })
  }
}

/** Select the first presets in each category. */
const selectFirstPresets = (options?: { onlyIfEmpty: boolean }) => {
  for (const category of categories.value) {
    if (category.items.length) {
      if (options?.onlyIfEmpty ?? false) {
        if (selectedPreset[category.category] === undefined) {
          selectedPreset[category.category] = category.items[0].sodar_uuid
        }
      } else {
        selectedPreset[category.category] = category.items[0].sodar_uuid
      }
    }
  }
}

/** Whether the currently selected presets version is readonly. */
const presetSetVersionReadonly = computed<boolean>(() => {
  return (
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.getEditableState(props.presetSetVersion) !==
      EditableState.EDITABLE
  )
})

// Select first presets when mounted.
onMounted(() => {
  selectFirstPresets()
})
// Also select first when project, preset set, or preset set version changes.
watch(
  () => [props.projectUuid, props.presetSet, props.presetSetVersion],
  () => {
    selectFirstPresets()
  },
)
// When store finished loading, only select the first presets if it is not set.
watch(
  () => [seqvarsPresetsStore.storeState.serverInteractions],
  () => {
    if (seqvarsPresetsStore.storeState.serverInteractions === 0) {
      selectFirstPresets({ onlyIfEmpty: true })
    }
  },
)
</script>

<template>
  <v-skeleton-loader
    v-if="!selectedPresetSetVersion?.presetsset"
    loading
    type="heading,paragraph"
    class="pt-3"
  />
  <div v-else class="pt-3">
    <h3 class="pb-3">
      Presets: &raquo;{{
        selectedPresetSetVersion?.presetsset.label ?? 'UNDEFINED'
      }}
      {{
        `v${selectedPresetSetVersion?.version_major ?? 'X'}` +
        `.${selectedPresetSetVersion?.version_minor ?? 'Y'}`
      }}&laquo;
    </h3>

    <v-row class="d-flex flex-nowrap">
      <v-col cols="3">
        <v-expansion-panels
          v-model="selectedCategory"
          mandatory
          :flat="false"
          density="compact"
        >
          <v-expansion-panel
            v-for="item in categories"
            :key="item.category"
            :title="item.label"
            :value="item.category"
          >
            <v-expansion-panel-text>
              <PresetsList
                v-model="selectedPreset[item.category]"
                :items="item.items"
                :readonly="presetSetVersionReadonly"
                @create="({ label }) => doCreatePresets(item.category, label)"
                @delete="(uuid) => doDeletePresets(item.category, uuid)"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
      <v-col cols="9">
        <v-sheet class="pa-3">
          <div v-if="selectedCategory === PresetsCategory.QUALITY">
            <CategoryPresetsQualityEditor
              :preset-set-version="presetSetVersion"
              :quality-presets="selectedPreset[PresetsCategory.QUALITY]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.FREQUENCY">
            <CategoryPresetsFrequencyEditor
              :preset-set-version="presetSetVersion"
              :frequency-presets="selectedPreset[PresetsCategory.FREQUENCY]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.CONSEQUENCE">
            <CategoryPresetsConsequenceEditor
              :preset-set-version="presetSetVersion"
              :consequence-presets="selectedPreset[PresetsCategory.CONSEQUENCE]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.LOCUS">
            <CategoryPresetsLocusEditor
              :preset-set-version="presetSetVersion"
              :locus-presets="selectedPreset[PresetsCategory.LOCUS]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.PHENOTYPE_PRIO">
            <CategoryPresetsPhenotypePrioEditor
              :preset-set-version="presetSetVersion"
              :phenotype-prio-presets="
                selectedPreset[PresetsCategory.PHENOTYPE_PRIO]
              "
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.VARIANT_PRIO">
            <CategoryPresetsVariantPrioEditor
              :preset-set-version="presetSetVersion"
              :variant-prio-presets="
                selectedPreset[PresetsCategory.VARIANT_PRIO]
              "
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.CLINVAR">
            <CategoryPresetsClinvarEditor
              :preset-set-version="presetSetVersion"
              :clinvar-presets="selectedPreset[PresetsCategory.CLINVAR]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.COLUMNS">
            <CategoryPresetsColumnsEditor
              :preset-set-version="presetSetVersion"
              :columns-presets="selectedPreset[PresetsCategory.COLUMNS]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div
            v-else-if="selectedCategory === PresetsCategory.PREDEFINED_QUERIES"
          >
            <CategoryPresetsPredefinedQueriesEditor
              :preset-set-version="presetSetVersion"
              :predefined-queries-presets="
                selectedPreset[PresetsCategory.PREDEFINED_QUERIES]
              "
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <v-alert
            v-else
            :title="`Invalid category ${selectedCategory}`"
            color="error"
          />
        </v-sheet>
      </v-col>
    </v-row>
  </div>
</template>
