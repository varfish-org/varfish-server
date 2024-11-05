<script setup lang="ts">
import { useIsFetching, useQueryClient } from '@tanstack/vue-query'
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
import {
  getEditableState,
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsQualityCreateMutation,
  useSeqvarsQueryPresetsQualityDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsQuality'
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

/** Presets set UUID as `ComputedRef` for queries. */
const presetsSetUuid = computed<string | undefined>(() => {
  return props.presetSet
})
/** Presets set version UUID as `ComputedRef` for queries. */
const presetsSetVersionUuid = computed<string | undefined>(() => {
  return props.presetSetVersion
})

/** The `QueryClient` for explicit invalidation.*/
const queryClient = useQueryClient()
/** Query for the selected presets set version details. */
const selectedPresetsSetVersion = useSeqvarQueryPresetsSetVersionRetrieveQuery({
  presetsSetUuid,
  presetsSetVersionUuid,
})

/** Mutation for creating a new quality preset. */
const qualityPresetsCreate = useSeqvarsQueryPresetsQualityCreateMutation()
/** Mutation for deleting a quality preset. */
const qualityPresetsDestroy = useSeqvarsQueryPresetsQualityDestroyMutation()

/** Category information/definition. */
const categories = computed<PresetsCategoryInfo[]>(() => {
  return [
    {
      label: 'Quality',
      category: PresetsCategory.QUALITY,
      items:
        selectedPresetsSetVersion.data.value?.seqvarsquerypresetsquality_set ??
        [],
    },
    {
      label: 'Frequency',
      category: PresetsCategory.FREQUENCY,
      items:
        selectedPresetsSetVersion.data.value
          ?.seqvarsquerypresetsfrequency_set ?? [],
    },
    {
      label: 'Consequence',
      category: PresetsCategory.CONSEQUENCE,
      items:
        selectedPresetsSetVersion.data.value
          ?.seqvarsquerypresetsconsequence_set ?? [],
    },
    {
      label: 'Locus',
      category: PresetsCategory.LOCUS,
      items:
        selectedPresetsSetVersion.data.value?.seqvarsquerypresetslocus_set ??
        [],
    },
    {
      label: 'Phenotype Prioritization',
      category: PresetsCategory.PHENOTYPE_PRIO,
      items:
        selectedPresetsSetVersion.data.value
          ?.seqvarsquerypresetsphenotypeprio_set ?? [],
    },
    {
      label: 'Variant Prioritization',
      category: PresetsCategory.VARIANT_PRIO,
      items:
        selectedPresetsSetVersion.data.value
          ?.seqvarsquerypresetsvariantprio_set ?? [],
    },
    {
      label: 'ClinVar',
      category: PresetsCategory.CLINVAR,
      items:
        selectedPresetsSetVersion.data.value?.seqvarsquerypresetsclinvar_set ??
        [],
    },
    {
      label: 'Columns',
      category: PresetsCategory.COLUMNS,
      items:
        selectedPresetsSetVersion.data.value?.seqvarsquerypresetscolumns_set ??
        [],
    },
    {
      label: 'Predefined Queries',
      category: PresetsCategory.PREDEFINED_QUERIES,
      items:
        selectedPresetsSetVersion.data.value?.seqvarspredefinedquery_set ?? [],
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
  // Guard against missing preset set/version.
  if (!!props.presetSet && !!props.presetSetVersion) {
    // Category text to show in the message.
    let msgCat: string = ''
    try {
      switch (category) {
        case PresetsCategory.QUALITY:
          msgCat = 'quality'
          await qualityPresetsCreate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
            },
            body: {
              label,
              rank:
                (selectedPresetsSetVersion.data.value
                  ?.seqvarsquerypresetsquality_set.length ?? 0) + 1,
            },
          })
          // Note: we currently have to invalidate the presets version sets here
          // because of limitations with hey-api.
          invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
            querypresetsset: props.presetSet,
            querypresetssetversion: props.presetSetVersion,
          })
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
  // Guard against missing preset set/version.
  if (!!props.presetSet && !!props.presetSetVersion) {
    // Category text to show in the message.
    let msgCat: string = ''
    try {
      switch (category) {
        case PresetsCategory.QUALITY:
          msgCat = 'quality'
          await qualityPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsquality: uuid,
            },
          })
          // Note: we currently have to invalidate the presets version sets here
          // because of limitations with hey-api.
          invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
            querypresetsset: props.presetSet,
            querypresetssetversion: props.presetSetVersion,
          })
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
    selectedPresetsSetVersion.data.value === undefined ||
    getEditableState(selectedPresetsSetVersion.data.value) !==
      EditableState.EDITABLE
  )
})

/** Returns number of true (non-background) loads. */
const isQueryFetching = useIsFetching({
  predicate: (query) => query.state.status !== 'pending',
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
  () => [isQueryFetching.value],
  () => {
    if (isQueryFetching.value === 0) {
      selectFirstPresets({ onlyIfEmpty: true })
    }
  },
)
</script>

<template>
  <v-skeleton-loader
    v-if="!selectedPresetsSetVersion.data.value?.presetsset"
    loading
    type="heading,paragraph"
    class="mt-3 pt-3"
  />
  <div v-else class="pt-3">
    <h3 class="pb-3">
      Presets: &raquo;{{
        selectedPresetsSetVersion.data.value?.presetsset.label ?? 'UNDEFINED'
      }}
      {{
        `v${selectedPresetsSetVersion.data.value?.version_major ?? 'X'}` +
        `.${selectedPresetsSetVersion.data.value?.version_minor ?? 'Y'}`
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
              :preset-set="presetSet"
              :preset-set-version="presetSetVersion"
              :quality-presets="selectedPreset[PresetsCategory.QUALITY]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <!-- <div v-else-if="selectedCategory === PresetsCategory.FREQUENCY">
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
          /> -->
        </v-sheet>
      </v-col>
    </v-row>
  </div>
</template>
