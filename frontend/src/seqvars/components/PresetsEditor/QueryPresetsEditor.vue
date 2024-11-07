<script setup lang="ts">
import { useIsFetching, useQueryClient } from '@tanstack/vue-query'
import { ComputedRef, computed, onMounted, reactive, ref, watch } from 'vue'

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
  useSeqvarsQueryPresetsClinvarCreateMutation,
  useSeqvarsQueryPresetsClinvarDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsClinvar'
import {
  useSeqvarsQueryPresetsColumnsCreateMutation,
  useSeqvarsQueryPresetsColumnsDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsColumns'
import {
  useSeqvarsQueryPresetsConsequenceCreateMutation,
  useSeqvarsQueryPresetsConsequenceDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsConsequence'
import {
  useSeqvarsQueryPresetsFrequencyCreateMutation,
  useSeqvarsQueryPresetsFrequencyDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsFrequency'
import {
  useSeqvarsQueryPresetsLocusCreateMutation,
  useSeqvarsQueryPresetsLocusDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsLocus'
import {
  useSeqvarsQueryPresetsPhenotypePrioCreateMutation,
  useSeqvarsQueryPresetsPhenotypePrioDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsPhenotypePrio'
import {
  useSeqvarsPredefinedQueryCreateMutation,
  useSeqvarsPredefinedQueryDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsPredefinedQuery'
import {
  useSeqvarsQueryPresetsQualityCreateMutation,
  useSeqvarsQueryPresetsQualityDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsQuality'
import {
  useSeqvarsQueryPresetsVariantPrioCreateMutation,
  useSeqvarsQueryPresetsVariantPrioDestroyMutation,
} from '@/seqvars/queries/seqvarQueryPresetsVariantPrio'
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

/** Mutation for creating a new frequency preset. */
const frequencyPresetsCreate = useSeqvarsQueryPresetsFrequencyCreateMutation()
/** Mutation for deleting a frequency preset. */
const frequencyPresetsDestroy = useSeqvarsQueryPresetsFrequencyDestroyMutation()

/** Mutation for creating a new consequence preset. */
const consequencePresetsCreate =
  useSeqvarsQueryPresetsConsequenceCreateMutation()
/** Mutation for deleting a consequence preset. */
const consequencePresetsDestroy =
  useSeqvarsQueryPresetsConsequenceDestroyMutation()

/** Mutation for creating a new locus preset. */
const locusPresetsCreate = useSeqvarsQueryPresetsLocusCreateMutation()
/** Mutation for deleting a locus preset. */
const locusPresetsDestroy = useSeqvarsQueryPresetsLocusDestroyMutation()

/** Mutation for creating a new phenotype prio preset. */
const phenotypePrioPresetsCreate =
  useSeqvarsQueryPresetsPhenotypePrioCreateMutation()
/** Mutation for deleting a phenotypep rio preset. */
const phenotypePrioPresetsDestroy =
  useSeqvarsQueryPresetsPhenotypePrioDestroyMutation()

/** Mutation for creating a new variant prio preset. */
const variantPrioPresetsCreate =
  useSeqvarsQueryPresetsVariantPrioCreateMutation()
/** Mutation for deleting a variant prio preset. */
const variantPrioPresetsDestroy =
  useSeqvarsQueryPresetsVariantPrioDestroyMutation()

/** Mutation for creating a new clinvar preset. */
const clinvarPresetsCreate = useSeqvarsQueryPresetsClinvarCreateMutation()
/** Mutation for deleting a clinvar preset. */
const clinvarPresetsDestroy = useSeqvarsQueryPresetsClinvarDestroyMutation()

/** Mutation for creating a new columns preset. */
const columnsPresetsCreate = useSeqvarsQueryPresetsColumnsCreateMutation()
/** Mutation for deleting a columns preset. */
const columnsPresetsDestroy = useSeqvarsQueryPresetsColumnsDestroyMutation()

/** Mutation for creating a new predefined query. */
const predefinedQueryCreate = useSeqvarsPredefinedQueryCreateMutation()
/** Mutation for deleting a predefinedQuery. */
const predefinedQueryDestroy = useSeqvarsPredefinedQueryDestroyMutation()

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

/** Store category UUID together with preset set and version. */
interface SelectedPreset {
  uuid?: string
  presetSet?: string
  presetSetVersion?: string
}

/** Selected presets in each category. */
const selectedPresetRef = ref<{
  [key in PresetsCategory]: SelectedPreset
}>({
  [PresetsCategory.QUALITY]: {},
  [PresetsCategory.FREQUENCY]: {},
  [PresetsCategory.CONSEQUENCE]: {},
  [PresetsCategory.LOCUS]: {},
  [PresetsCategory.PHENOTYPE_PRIO]: {},
  [PresetsCategory.VARIANT_PRIO]: {},
  [PresetsCategory.CLINVAR]: {},
  [PresetsCategory.COLUMNS]: {},
  [PresetsCategory.PREDEFINED_QUERIES]: {},
})

/** Currently selected category. */
const selectedCategory = ref<PresetsCategory>(PresetsCategory.QUALITY)

/** Helper to create entries in `selectedPreset`. */
const createSelectedPreset = (category: PresetsCategory) => {
  return computed({
    get: () => {
      const value = selectedPresetRef.value[category]
      if (
        props.presetSet === undefined ||
        props.presetSetVersion === undefined ||
        value.presetSet !== props.presetSet ||
        value.presetSetVersion !== props.presetSetVersion
      ) {
        // Guard against change in preset set and version.
        return undefined
      } else {
        return selectedPresetRef.value[category].uuid
      }
    },
    set: (value: string | undefined) => {
      selectedPresetRef.value[category] = {
        uuid: value,
        presetSet: props.presetSet,
        presetSetVersion: props.presetSetVersion,
      }
    },
  })
}

/** Selected presets in each category */
const selectedPreset = reactive<{
  [key in PresetsCategory]: ComputedRef<string | undefined>
}>({
  [PresetsCategory.QUALITY]: createSelectedPreset(PresetsCategory.QUALITY),
  [PresetsCategory.FREQUENCY]: createSelectedPreset(PresetsCategory.FREQUENCY),
  [PresetsCategory.CONSEQUENCE]: createSelectedPreset(
    PresetsCategory.CONSEQUENCE,
  ),
  [PresetsCategory.LOCUS]: createSelectedPreset(PresetsCategory.LOCUS),
  [PresetsCategory.PHENOTYPE_PRIO]: createSelectedPreset(
    PresetsCategory.PHENOTYPE_PRIO,
  ),
  [PresetsCategory.VARIANT_PRIO]: createSelectedPreset(
    PresetsCategory.VARIANT_PRIO,
  ),
  [PresetsCategory.CLINVAR]: createSelectedPreset(PresetsCategory.CLINVAR),
  [PresetsCategory.COLUMNS]: createSelectedPreset(PresetsCategory.COLUMNS),
  [PresetsCategory.PREDEFINED_QUERIES]: createSelectedPreset(
    PresetsCategory.PREDEFINED_QUERIES,
  ),
})

/** Category labels. */
const CAT_LABELS = {
  [PresetsCategory.QUALITY]: 'quality',
  [PresetsCategory.FREQUENCY]: 'frequency',
  [PresetsCategory.CONSEQUENCE]: 'consequence',
  [PresetsCategory.LOCUS]: 'locus',
  [PresetsCategory.PHENOTYPE_PRIO]: 'phenotype priority',
  [PresetsCategory.VARIANT_PRIO]: 'variant priority',
  [PresetsCategory.CLINVAR]: 'clinvar',
  [PresetsCategory.COLUMNS]: 'columns',
  [PresetsCategory.PREDEFINED_QUERIES]: 'predefined queries',
} as const

/**
 * Create a new presets, emitting "message" for success/failure.
 *
 * @param category The category for which to create presets.
 * @param label The label for the new presets.
 */
const doCreatePresets = async (category: PresetsCategory, label: string) => {
  // Category text to show in the message.
  const msgCat: string = CAT_LABELS[category]

  // Guard against missing preset set/version.
  if (!!props.presetSet && !!props.presetSetVersion) {
    // Arguments to pass to the mutation's `mutateAsync()` method.
    const createMutateArgs = (length?: number) => ({
      path: {
        querypresetssetversion: props.presetSetVersion!,
      },
      body: {
        label,
        rank: (length ?? 0) + 1,
      },
    })

    try {
      const value = selectedPresetsSetVersion.data.value
      switch (category) {
        case PresetsCategory.QUALITY:
          await qualityPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetsquality_set.length),
          )
          break
        case PresetsCategory.FREQUENCY:
          await frequencyPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetsfrequency_set.length),
          )
          break
        case PresetsCategory.CONSEQUENCE:
          await consequencePresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetsconsequence_set.length),
          )
          break
        case PresetsCategory.LOCUS:
          await locusPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetslocus_set.length),
          )
          break
        case PresetsCategory.PHENOTYPE_PRIO:
          await phenotypePrioPresetsCreate.mutateAsync(
            createMutateArgs(
              value?.seqvarsquerypresetsphenotypeprio_set.length,
            ),
          )
          break
        case PresetsCategory.VARIANT_PRIO:
          await variantPrioPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetsvariantprio_set.length),
          )
          break
        case PresetsCategory.CLINVAR:
          await clinvarPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetsclinvar_set.length),
          )
          break
        case PresetsCategory.COLUMNS:
          await columnsPresetsCreate.mutateAsync(
            createMutateArgs(value?.seqvarsquerypresetscolumns_set.length),
          )
          break
        case PresetsCategory.PREDEFINED_QUERIES:
          await predefinedQueryCreate.mutateAsync(
            createMutateArgs(value?.seqvarspredefinedquery_set.length),
          )
          break
        default:
          throw new Error(`Unknown category ${category}`)
      }
      // Note: we currently have to invalidate the presets version sets here
      // because of limitations with hey-api.
      invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
        querypresetsset: props.presetSet,
        querypresetssetversion: props.presetSetVersion,
      })
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
  // Category text to show in the message.
  const msgCat: string = CAT_LABELS[category]

  // Guard against missing preset set/version.
  if (!!props.presetSet && !!props.presetSetVersion) {
    try {
      switch (category) {
        case PresetsCategory.QUALITY:
          await qualityPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsquality: uuid,
            },
          })
          break
        case PresetsCategory.FREQUENCY:
          await frequencyPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsfrequency: uuid,
            },
          })
          break
        case PresetsCategory.CONSEQUENCE:
          await consequencePresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsconsequence: uuid,
            },
          })
          break
        case PresetsCategory.LOCUS:
          await locusPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetslocus: uuid,
            },
          })
          break
        case PresetsCategory.PHENOTYPE_PRIO:
          await phenotypePrioPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsphenotypeprio: uuid,
            },
          })
          break
        case PresetsCategory.VARIANT_PRIO:
          await variantPrioPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsvariantprio: uuid,
            },
          })
          break
        case PresetsCategory.CLINVAR:
          await clinvarPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsclinvar: uuid,
            },
          })
          break
        case PresetsCategory.COLUMNS:
          await columnsPresetsDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetscolumns: uuid,
            },
          })
          break
        case PresetsCategory.PREDEFINED_QUERIES:
          await predefinedQueryDestroy.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              predefinedquery: uuid,
            },
          })
          break
          break
        default:
          throw new Error(`Unknown category ${category}`)
      }
      // Note: we currently have to invalidate the presets version sets here
      // because of limitations with hey-api.
      invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
        querypresetsset: props.presetSet,
        querypresetssetversion: props.presetSetVersion,
      })
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
          <div v-else-if="selectedCategory === PresetsCategory.FREQUENCY">
            <CategoryPresetsFrequencyEditor
              :preset-set="presetSet"
              :preset-set-version="presetSetVersion"
              :frequency-presets="selectedPreset[PresetsCategory.FREQUENCY]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.CONSEQUENCE">
            <CategoryPresetsConsequenceEditor
              :preset-set="presetSet"
              :preset-set-version="presetSetVersion"
              :consequence-presets="selectedPreset[PresetsCategory.CONSEQUENCE]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.LOCUS">
            <CategoryPresetsLocusEditor
              :preset-set="presetSet"
              :preset-set-version="presetSetVersion"
              :locus-presets="selectedPreset[PresetsCategory.LOCUS]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.PHENOTYPE_PRIO">
            <CategoryPresetsPhenotypePrioEditor
              :preset-set="presetSet"
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
              :preset-set="presetSet"
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
              :preset-set="presetSet"
              :preset-set-version="presetSetVersion"
              :clinvar-presets="selectedPreset[PresetsCategory.CLINVAR]"
              :readonly="presetSetVersionReadonly"
              @message="(event) => emit('message', event)"
            />
          </div>
          <div v-else-if="selectedCategory === PresetsCategory.COLUMNS">
            <CategoryPresetsColumnsEditor
              :preset-set="presetSet"
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
              :preset-set="presetSet"
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
