<script setup lang="ts">
import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryDetails,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { diff } from 'deep-object-diff'
import isEqual from 'fast-deep-equal/es6'
import { debounce } from 'lodash'
import { computed, ref, toRaw, watch } from 'vue'

import { PedigreeObj, useCaseDetailsStore } from '@/cases/stores/caseDetails'
import GenotypeControls from '@/seqvars/components/QueryEditor/GenotypeControls.vue'
import PredefinedQueryList from '@/seqvars/components/QueryEditor/PredefinedQueryList.vue'
import PresetSummaryItem from '@/seqvars/components/QueryEditor/PresetSummaryItem.vue'
import QueryList from '@/seqvars/components/QueryEditor/QueryList.vue'
import {
  FilterGroup,
  GROUPS,
  createGenotypeFromPreset,
  createQualityFromPreset,
  matchesGenotypePreset,
  matchesQualityPreset,
} from '@/seqvars/components/QueryEditor/groups'
import {
  GENOTYPE_PRESET_TO_RECESSIVE_MODE,
  QUERY_DEBOUNCE_WAIT,
} from '@/seqvars/components/QueryEditor/lib/constants'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'
import { SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS } from '@/seqvars/lib/constants'
import { useSeqvarsQueryStore } from '@/seqvars/stores/query'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { copy } from '@/varfish/helpers'

import { AnyObject, deepCopyAndOmit } from './lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** Whether the containing VNavigationDrawer has been collapsed. */
    collapsed: boolean
    /** The presets version to use. */
    presetsDetails: SeqvarsQueryPresetsSetVersionDetails
    /** Where to teleport the queries to when collapsed. */
    teleportToWhenCollapsed?: string
    /** Whether to show labels in teleported queries. */
    teleportedQueriesLabels?: boolean
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
  }>(),
  {
    collapsed: false,
    teleportedQueriesLabels: false,
    hintsEnabled: false,
  },
)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Emitted to display a message in the VSnakbarQueue (e.g., on errors). */
  message: [message: SnackbarMessage]
}>()

/** The case detail store to use; assumed to be initialized on the outside. */
const caseDetailStore = useCaseDetailsStore()
/** The seqvars query store to use; assumed to be initialized on the ouside. */
const seqvarsQueryStore = useSeqvarsQueryStore()

/** Provide the `PedigreeObj` from the `caseDetailStore`. */
const pedigree = computed<PedigreeObj | undefined | null>(
  () => caseDetailStore.caseObj?.pedigree_obj as PedigreeObj,
)

/** The UUID of the currently selected query; component state. */
const selectedQueryUuid = ref<string | undefined>(undefined)
/** Whether to show the query update dialog; component state. */
const showUpdateDialog = ref<boolean>(false)
/** The query title in update dialog; component state. */
const updateDialogTitle = ref<string>('')

/** The currently selected query; manages `selectedQueryUuid`. */
const selectedQuery = computed<SeqvarsQueryDetails | undefined>({
  get() {
    return seqvarsQueryStore.seqvarQueries.get(selectedQueryUuid.value ?? '')
  },
  set(newValue) {
    selectedQueryUuid.value = newValue?.sodar_uuid
  },
})

/**
 * The original predefined query that the currently selected query is based on.
 */
// TODO: here we don't know why its not set...
const baselinePredefinedQuery = computed<SeqvarsPredefinedQuery | undefined>(
  () =>
    props.presetsDetails.seqvarspredefinedquery_set.find(
      (pq) => pq.sodar_uuid === selectedQuery.value?.settings.predefinedquery,
    ),
)

/**
 * Create a new query based on the given predefined query.
 */
const createQuery = async (pq: SeqvarsPredefinedQuery) => {
  let label = pq.label
  const queryLabels = Array.from(seqvarsQueryStore.seqvarQueries.values()).map(
    (q) => q.label,
  )
  let i = 2 // sic, need to place outside loop in `<template>`
  for (; queryLabels.includes(label); i++) {
    label = `${pq.label} (${i})`
  }

  try {
    selectedQueryUuid.value =
      await seqvarsQueryStore.copySeqvarsQueryFromPreset(pq.sodar_uuid, label)
    emit('message', {
      text: `Created new query: ${selectedQuery.value?.label}`,
      color: 'success',
    })
  } catch (e) {
    emit('message', {
      text: `Failed to create new query: ${e}`,
      color: 'error',
    })
  }
}

/**
 * Update the query's label.
 *
 * @param label The new label to set.
 * @returns Whether the update was successful.
 * @throws Error if the query could not be updated.
 */
const updateQueryLabel = async (label: string): Promise<boolean> => {
  if (!!selectedQuery.value) {
    selectedQuery.value.label = label
    try {
      await seqvarsQueryStore.updateSeqvarsQuery(selectedQuery.value)
      emit('message', {
        text: 'Query updated successfully.',
        color: 'success',
      })
      return true
    } catch (e) {
      emit('message', {
        text: `Failed to update query: ${e}`,
        color: 'error',
      })
    }
  }
  return false
}

/**
 * Revert the currently selected query's genotype.
 */
const revertGenotypeToPresets = async () => {
  if (
    !!selectedQuery.value?.settings.genotypepresets?.choice &&
    !!baselinePredefinedQuery.value?.genotype?.choice
  ) {
    selectedQuery.value.settings.genotypepresets.choice =
      baselinePredefinedQuery.value.genotype.choice
    updateGenotypeToPresets(selectedQuery.value.settings.genotypepresets.choice)
  }
}

/**
 * Revert the currently selected query's settings in a group/category
 * to its original presets'
 */
const revertGroupToPresets = async (group: (typeof GROUPS)[number]) => {
  const preset = props.presetsDetails[group.presetSetKey].find(
    (p) => p.sodar_uuid === baselinePredefinedQuery.value?.[group.id],
  )
  if (!!pedigree.value && !!preset) {
    revertCategoryToPresets(pedigree.value, group, preset)
  }
}

/**
 * Reverts the currently selected query's settings to its original presets'
 * value.
 */
const revertQueryToPresets = async () => {
  if (!!selectedQuery.value?.settings?.genotypepresets?.choice) {
    revertGenotypeToPresets()
  }
  for (const group of Object.values(GROUPS)) {
    revertGroupToPresets(group)
  }
}

/**
 * Set the genotype according to the given preset choice.
 *
 * Used both for setting the genotype from a preset and for reverting the
 * genotype to the preset.
 */
const updateGenotypeToPresets = (choice: SeqvarsGenotypePresetChoice) => {
  if (!selectedQuery.value || !pedigree.value) {
    return
  }
  selectedQuery.value.settings.genotype = {
    ...selectedQuery.value.settings.genotype,
    ...copy(createGenotypeFromPreset(pedigree.value, choice)),
  }
  selectedQuery.value.settings.genotypepresets = { choice }
}

/**
 * Updates the selected query UUID.
 *
 * When undefined or cannot be found in store's seqvar queries then update to
 * the first one.
 */
const updateSelectedQueryUuid = () => {
  if (
    !selectedQueryUuid.value ||
    !seqvarsQueryStore.seqvarQueries.has(selectedQueryUuid.value)
  ) {
    selectedQueryUuid.value = seqvarsQueryStore.seqvarQueries
      .values()
      .next()?.value?.sodar_uuid
  }
}

/**
 * Revert the given preset category/group to the given preset.
 */
const revertCategoryToPresets = <G extends (typeof GROUPS)[number]>(
  pedigree: PedigreeObj,
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value.settings[`${group.id}presets`] = preset.sodar_uuid
  const value =
    group.id == 'quality'
      ? createQualityFromPreset(pedigree, preset as SeqvarsQueryPresetsQuality)
      : preset
  selectedQuery.value.settings[group.id] = {
    ...selectedQuery.value.settings[group.id],
    ...copy(value),
  }
}

/** The last state of selected query that has been seen. */
const selectedQueryPrev = ref<SeqvarsQueryDetails | undefined>(undefined)

/**
 * Update the currently selected query if set and different from `selectedQueryPrev`.
 */
const updateSelectedQuery = async () => {
  /**
   * Helper that strips irrelevant keys from the objects.
   */
  const strip = (obj: AnyObject) =>
    deepCopyAndOmit(obj, [
      // dates can change on updates / recreation
      'date_created',
      'date_modified',
      // recreated on updates in the library for nested updates we use
      'sodar_uuid',
      'querysettings',
    ])

  if (!selectedQuery.value) {
    // Guard against no selected query.
    return
  } else if (
    !selectedQueryPrev.value ||
    selectedQuery.value!.sodar_uuid !== selectedQueryPrev.value.sodar_uuid
  ) {
    // Guard against no previous query or query identity/UUID change.
    selectedQueryPrev.value = structuredClone(toRaw(selectedQuery.value))
    return
  }

  // Passed all guard statements, check if the contents actually changed.
  if (!isEqual(strip(selectedQuery.value), strip(selectedQueryPrev.value))) {
    selectedQueryPrev.value = structuredClone(toRaw(selectedQuery.value))
    await seqvarsQueryStore.updateSeqvarsQuery(selectedQuery.value!)
  }
}

/**
 * Update the currently selected query in the store -- debounced.
 *
 * Used for updating settings so that the UI does not lag.
 */
const updateSelectedQueryDebounced = debounce(
  updateSelectedQuery,
  QUERY_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Observe changes in the queries and update the selected query UUID accordingly.
watch(
  () => [seqvarsQueryStore.seqvarQueries.values()],
  () => updateSelectedQueryUuid(),
)

// Observe changes in the currently selected query (deeply) and update the query
// on the server accordingly.
watch(
  () => selectedQuery,
  () => updateSelectedQueryDebounced(),
  { deep: true },
)
</script>

<template>
  <div v-if="pedigree" class="h-100 overflow-y-auto overflow-x-hidden pr-2">
    <QueryList
      v-if="!!pedigree && seqvarsQueryStore.seqvarQueries.size > 0"
      :selected-query-uuid="selectedQueryUuid"
      :presets-details="presetsDetails"
      :queries="seqvarsQueryStore.seqvarQueries"
      :query-executions="seqvarsQueryStore.seqvarsQueryExecutions"
      :pedigree="pedigree"
      :hints-enabled="hintsEnabled"
      @update:selected-query-uuid="
        (queryUuid: string) => {
          selectedQueryUuid = queryUuid
        }
      "
      @remove="
        async (queryUuid: string) => {
          const seqvarsQuery = seqvarsQueryStore.seqvarQueries.get(queryUuid)
          if (!seqvarsQuery) {
            console.error('Query not found:', queryUuid)
            return
          }
          try {
            await seqvarsQueryStore.deleteSeqvarsQuery(queryUuid)
            emit('message', {
              text: `Deleted query: ${seqvarsQuery.label}`,
              color: 'success',
            })
          } catch (e) {
            emit('message', {
              text: `Failed to delete query: ${e}`,
              color: 'error',
            })
          }
        }
      "
      @revert="revertQueryToPresets"
      @update-query="
        (queryUuid: string) => {
          selectedQueryUuid = queryUuid
          updateDialogTitle =
            seqvarsQueryStore.seqvarQueries.get(queryUuid)?.label ?? ''
          showUpdateDialog = true
        }
      "
    />

    <!-- Teleport out the query list when hidden. -->
    <Teleport
      v-if="
        collapsed &&
        teleportToWhenCollapsed &&
        seqvarsQueryStore.seqvarQueries.size > 0
      "
      :to="teleportToWhenCollapsed"
    >
      <v-list-subheader v-if="teleportedQueriesLabels" class="text-uppercase">
        Queries / Results
      </v-list-subheader>
      <v-divider v-else class="mt-1 mb-1"></v-divider>

      <v-list-item
        v-for="(query, index) in seqvarsQueryStore.seqvarQueries.values()"
        :key="query.sodar_uuid"
        :variant="
          !!selectedQuery && selectedQueryUuid === query.sodar_uuid
            ? 'tonal'
            : undefined
        "
        :title="query.label"
        :prepend-icon="'mdi-numeric-' + (index + 1) + '-box-outline'"
        @click="selectedQueryUuid = query.sodar_uuid"
      />
    </Teleport>

    <PredefinedQueryList
      :hints-enabled="hintsEnabled"
      :presets="presetsDetails"
      :selected-id="selectedQuery?.settings.predefinedquery"
      :query="selectedQuery"
      :pedigree="pedigree"
      @revert="revertQueryToPresets"
      @add-query="createQuery"
    />

    <v-divider class="my-3" />

    <template v-if="selectedQuery">
      <CollapsibleGroup
        title="Genotype"
        :hints-enabled="hintsEnabled"
        hint="For the genotype, you first select whether you want to enable filtering for any of the recessive variant modes.  For the recessive mode, you have to chose the index and parent roles in the pedigree.  If you disable the recessive mode then you can set a filter on the genotypes for each individual."
        :modified="
          !!baselinePredefinedQuery?.genotype?.choice &&
          !!selectedQuery?.settings.genotypepresets?.choice &&
          selectedQuery?.settings.genotypepresets?.choice !==
            baselinePredefinedQuery?.genotype?.choice
        "
        :summary="
          selectedQuery.settings.genotypepresets?.choice
            ? SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[
                selectedQuery.settings.genotypepresets?.choice
              ]
            : ''
        "
        @revert="revertGenotypeToPresets"
      >
        <template
          v-if="selectedQuery.settings.genotypepresets?.choice"
          #summary
        >
          <Item
            :modified="
              !!baselinePredefinedQuery &&
              !matchesGenotypePreset(
                pedigree,
                selectedQuery.settings.genotypepresets?.choice,
                selectedQuery.settings,
              )
            "
            @revert="
              () =>
                updateGenotypeToPresets(
                  selectedQuery!.settings.genotypepresets?.choice!,
                )
            "
          >
            {{
              SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[
                (pedigree, selectedQuery.settings.genotypepresets?.choice)
              ]
            }}
          </Item>
        </template>

        <template #default>
          <div
            role="listbox"
            style="width: 100%; display: flex; flex-direction: column"
          >
            <Item
              v-for="key in Object.keys(
                GENOTYPE_PRESET_TO_RECESSIVE_MODE,
              ) as SeqvarsGenotypePresetChoice[]"
              :key="key"
              :selected="selectedQuery.settings.genotypepresets?.choice === key"
              :modified="
                !!pedigree &&
                selectedQuery.settings.genotypepresets?.choice === key &&
                baselinePredefinedQuery &&
                !matchesGenotypePreset(
                  pedigree,
                  selectedQuery.settings.genotypepresets?.choice,
                  selectedQuery.settings,
                )
              "
              @click="() => updateGenotypeToPresets(key)"
              @revert="() => updateGenotypeToPresets(key)"
            >
              {{ SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[key] }}
            </Item>
          </div>
          <v-divider class="my-2" />
          <GenotypeControls
            v-model="selectedQuery"
            :pedigree="pedigree"
            :hints-enabled="hintsEnabled"
          />
        </template>
      </CollapsibleGroup>

      <CollapsibleGroup
        v-for="group in GROUPS"
        :key="group.id"
        :title="group.title"
        :hint="group.hint"
        :hints-enabled="hintsEnabled"
        :summary="
          presetsDetails[group.presetSetKey].find(
            (p) =>
              p.sodar_uuid === selectedQuery?.settings[group.queryPresetKey],
          )?.label
        "
        :modified="
          !!baselinePredefinedQuery?.[group.id] &&
          presetsDetails[group.presetSetKey].find(
            (p) =>
              p.sodar_uuid === selectedQuery?.settings[group.queryPresetKey],
          )?.sodar_uuid !== baselinePredefinedQuery?.[group.id]
        "
        @revert="() => revertGroupToPresets(group)"
      >
        <template #summary>
          <PresetSummaryItem
            :pedigree="pedigree"
            :presets-details="presetsDetails"
            :query="selectedQuery"
            :group="group"
            :preset="
              presetsDetails[group.presetSetKey].find(
                (p) =>
                  p.sodar_uuid ===
                  selectedQuery?.settings[group.queryPresetKey],
              )
            "
            @revert="
              (preset: any) => {
                if (!!pedigree) {
                  revertCategoryToPresets(pedigree, group, preset)
                }
              }
            "
          />
        </template>
        <template #default>
          <div
            role="listbox"
            style="width: 100%; display: flex; flex-direction: column"
          >
            <Item
              v-for="preset in presetsDetails[group.presetSetKey]"
              :key="preset.sodar_uuid"
              :selected="
                preset.sodar_uuid ==
                selectedQuery.settings[group.queryPresetKey]
              "
              :modified="
                preset.sodar_uuid ==
                  selectedQuery.settings[group.queryPresetKey] &&
                !(
                  !!pedigree &&
                  baselinePredefinedQuery &&
                  (group.id == 'quality'
                    ? matchesQualityPreset(
                        pedigree,
                        presetsDetails,
                        selectedQuery.settings,
                      )
                    : group.matchesPreset(
                        presetsDetails,
                        selectedQuery.settings,
                      ))
                )
              "
              @click="
                () => {
                  if (pedigree) {
                    revertCategoryToPresets(pedigree, group, preset)
                  }
                }
              "
              @revert="
                () => {
                  if (pedigree) {
                    revertCategoryToPresets(pedigree, group, preset)
                  }
                }
              "
            >
              {{ preset.label }}
            </Item>
          </div>

          <v-divider class="my-2" />

          <component
            :is="group.Component"
            v-model="selectedQuery"
            :hints-enabled="hintsEnabled"
          />
        </template>
      </CollapsibleGroup>
    </template>
  </div>

  <!-- Dialog to update query. -->
  <v-dialog v-model="showUpdateDialog" max-width="600">
    <template #default>
      <v-card>
        <v-card-title class="d-flex justify-space-between align-center">
          <div class="text-h5 text-medium-emphasis ps-2">
            Update Query Title
          </div>

          <v-btn
            icon="mdi-close"
            variant="text"
            @click="showUpdateDialog = false"
          ></v-btn>
        </v-card-title>
        <v-divider class="mb-4"></v-divider>

        <v-card-text>
          <v-text-field
            v-model="updateDialogTitle"
            variant="outlined"
            label="Query title"
          />
        </v-card-text>

        <v-divider class="mt-2"></v-divider>
        <v-card-actions class="my-2 d-flex justify-end">
          <v-btn
            class="text-none"
            rounded="xl"
            text="Cancel"
            @click="showUpdateDialog = false"
          ></v-btn>

          <v-btn
            class="text-none"
            color="primary"
            rounded="xl"
            text="Save"
            variant="flat"
            @click="
              async () => {
                if (await updateQueryLabel(updateDialogTitle)) {
                  showUpdateDialog = false
                }
              }
            "
          ></v-btn>
        </v-card-actions>
      </v-card>
    </template>
  </v-dialog>
</template>
