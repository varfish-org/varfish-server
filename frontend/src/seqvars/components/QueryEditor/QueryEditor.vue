<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryExecution,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import { GENOTYPE_PRESET_TO_RECESSIVE_MODE } from '@/seqvars/components/QueryEditor/lib/constants'
import { SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS } from '@/seqvars/lib/constants'
import GenotypeControls from '@/seqvars/components/QueryEditor/GenotypeControls.vue'
import {
  createGenotypeFromPreset,
  createQualityFromPreset,
  FilterGroup,
  GROUPS,
  matchesGenotypePreset,
  matchesQualityPreset,
} from '@/seqvars/components/QueryEditor/groups'
import PredefinedQueryList from '@/seqvars/components/QueryEditor/PredefinedQueryList.vue'
import PresetSummaryItem from '@/seqvars/components/QueryEditor/PresetSummaryItem.vue'
import QueryList from '@/seqvars/components/QueryEditor/QueryList.vue'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'
import { Query } from '@/seqvars/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
import { PedigreeObj, useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { copy } from '@/varfish/helpers'

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

// The case detail store to use; assumed to be initialized on the outside.
const caseDetailStore = useCaseDetailsStore()

/** Provide the `PedigreeObj` from the `caseDetailStore`. */
const pedigree = computed<PedigreeObj | undefined | null>(
  () => caseDetailStore.caseObj?.pedigree_obj as PedigreeObj,
)

/** The list of queries; component state. */
const queries = ref<Query[]>([])
/** The list of query executions; component state. */
const queryExecutions = ref<SeqvarsQueryExecution[]>([])
/** The index of the currently selected query; component state. */
const selectedQueryIndex = ref<number | null>(null)

/** Whether to show the query update dialog. */
const showUpdateDialog = ref<boolean>(false)
/** The query title in update dialog. */
const updateDialogTitle = ref<string>('')

/** The currently selected query; manages `selectedQueryIndex`. */
const selectedQuery = computed<Query | null>({
  get() {
    return selectedQueryIndex.value == null
      ? null
      : queries.value.at(selectedQueryIndex.value) ?? null
  },
  set(newValue) {
    if (selectedQueryIndex.value == null || newValue == null) {
      return
    }
    queries.value[selectedQueryIndex.value] = newValue
  },
})

/**
 * The currently selected predefined query.  This is used to compute differences
 * and revert back to.
 */
const selectedPredefinedQuery = computed(() =>
  props.presetsDetails.seqvarspredefinedquery_set.find(
    (pq) => pq.sodar_uuid === selectedQuery.value?.predefinedquery,
  ),
)

/**
 * Create a new `Query` object based on the given `SeqvarsPredefinedQuery`.
 *
 * This happens on the client side only.
 *
 * @throws Error if there was a problem with creating the query.
 */
const createQuery = (
  pq: SeqvarsPredefinedQuery,
  options?: { label?: string },
): Query => {
  if (!pedigree.value) {
    throw new Error('Pedigree not available')
  }

  const presetFields = Object.fromEntries(
    GROUPS.flatMap((group) => {
      const preset = props.presetsDetails[group.presetSetKey].find(
        (p) => p.sodar_uuid === pq[group.id],
      )
      return [
        [group.queryPresetKey, pq[group.id]],
        [
          group.id,
          group.id == 'quality'
            ? createQualityFromPreset(
                pedigree.value!,
                preset as SeqvarsQueryPresetsQuality,
              )
            : preset,
        ],
      ]
    }),
  ) as Pick<Query, (typeof GROUPS)[number]['id']> & Partial<Query>
  const choice = pq.genotype?.choice

  let label
  if (options?.label) {
    label = options.label
  } else {
    label = pq.label
    const queryLabels = queries.value.map((q) => q.label)
    for (let i = 2; ; i++) {
      if (queryLabels.includes(label)) {
        label = `${pq.label} (${i})`
      } else {
        break
      }
    }
  }

  return copy({
    ...presetFields,
    label,
    predefinedquery: pq.sodar_uuid,
    genotype: createGenotypeFromPreset(pedigree.value, choice),
    genotypepresets: { choice },
  })
}

/**
 * Revert the given preset group to the given preset.
 */
const revertToPresets = <G extends (typeof GROUPS)[number]>(
  pedigree: PedigreeObj,
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value[`${group.id}presets`] = preset.sodar_uuid
  const value =
    group.id == 'quality'
      ? createQualityFromPreset(pedigree, preset as SeqvarsQueryPresetsQuality)
      : preset
  selectedQuery.value[group.id] = copy(value)
}

/**
 * Revert the genotype to the given preset choice.
 */
const revertGenotypeToPresets = (choice: SeqvarsGenotypePresetChoice) => {
  if (!selectedQuery.value || !pedigree.value) {
    return
  }
  selectedQuery.value.genotype = copy(
    createGenotypeFromPreset(pedigree.value, choice),
  )
  selectedQuery.value.genotypepresets = { choice }
}

/** Reverts the currently selected query to the given preset. */
const revertQueryToPresets = async () => {
  // try {
  const pq = props.presetsDetails.seqvarspredefinedquery_set.find(
    (p) => p.sodar_uuid === selectedQuery?.value?.predefinedquery,
  )!
  selectedQuery.value = createQuery(pq, { label: pq.label })
  // } catch (e) {
  //   console.error(e)
  //   emit('message', {
  //     text: 'Failed to revert query to presets.',
  //     color: 'error',
  //   })
  // }
}
</script>

<template>
  <div v-if="pedigree" class="h-100 overflow-y-auto overflow-x-hidden pr-2">
    <QueryList
      v-if="!!pedigree && queries.length > 0"
      :selected-index="selectedQueryIndex"
      :presets-details="presetsDetails"
      :queries="queries"
      :query-executions="queryExecutions"
      :pedigree="pedigree"
      :hints-enabled="hintsEnabled"
      @update:selected-index="
        (index: number | null) => (selectedQueryIndex = index)
      "
      @remove="(index: number) => queries.splice(index, 1)"
      @revert="revertQueryToPresets"
      @update-query="
        (index: number) => {
          updateDialogTitle = queries.at(index)?.label ?? ''
          showUpdateDialog = true
        }
      "
    />

    <!-- Teleport out the query list when hidden. -->
    <Teleport
      v-if="collapsed && teleportToWhenCollapsed && queries.length > 0"
      :to="teleportToWhenCollapsed"
    >
      <v-list-subheader v-if="teleportedQueriesLabels" class="text-uppercase">
        Queries / Results
      </v-list-subheader>
      <v-divider v-else class="mt-1 mb-1"></v-divider>

      <v-list-item
        v-for="(_query, index) in queries"
        :key="index"
        :variant="selectedQueryIndex === index ? 'tonal' : undefined"
        :title="queries[index].label"
        :prepend-icon="'mdi-numeric-' + (index + 1) + '-box-outline'"
        @click="selectedQueryIndex = index"
      />
    </Teleport>

    <PredefinedQueryList
      :hints-enabled="hintsEnabled"
      :presets="presetsDetails"
      :selected-id="selectedQuery?.predefinedquery"
      :query="selectedQuery"
      :pedigree="pedigree"
      @update:selected-id="
        () => {}
        // (id?: string) => {
        //   // try {
        //   const pq = presetsDetails.seqvarspredefinedquery_set.find(
        //     (p) => p.sodar_uuid === id,
        //   )!
        //   selectedQuery = createQuery(pq)
        //   // } catch (e) {
        //   //   console.error(e)
        //   //   emit('message', {
        //   //     text: 'Failed to update query to presets.',
        //   //     color: 'error',
        //   //   })
        //   // }
        // }
      "
      @revert="revertQueryToPresets"
      @add-query="
        (pq: SeqvarsPredefinedQuery) => {
          // try {
          const query = createQuery(pq)
          queries.push(query)
          queryExecutions.push({
            sodar_uuid: '',
            date_created: '',
            date_modified: '',
            state: 'running',
            complete_percent: null,
            start_time: null,
            end_time: null,
            elapsed_seconds: null,
            query: '',
            querysettings: '',
          })
          selectedQueryIndex = queries.length - 1
          // } catch (e) {
          //   console.error(e)
          //   emit('message', {
          //     text: 'Failed to add query from presets.',
          //     color: 'error',
          //   })
          // }
        }
      "
    />

    <v-divider class="my-3" />

    <template v-if="selectedQuery">
      <CollapsibleGroup
        title="Genotype"
        :hints-enabled="hintsEnabled"
        hint="For the genotype, you first select whether you want to enable filtering for any of the recessive variant modes.  For the recessive mode, you have to chose the index and parent roles in the pedigree.  If you disable the recessive mode then you can set a filter on the genotypes for each individual."
        :modified="
          !!selectedPredefinedQuery?.genotype?.choice &&
          !!selectedQuery?.genotypepresets?.choice &&
          selectedQuery?.genotypepresets?.choice !=
            selectedPredefinedQuery?.genotype?.choice
        "
        :summary="
          selectedQuery.genotypepresets?.choice
            ? SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[
                selectedQuery.genotypepresets?.choice
              ]
            : ''
        "
        @revert="
          () => {
            if (
              !!selectedQuery?.genotypepresets?.choice &&
              !!selectedPredefinedQuery?.genotype?.choice
            ) {
              selectedQuery.genotypepresets.choice =
                selectedPredefinedQuery.genotype.choice
              revertGenotypeToPresets(selectedQuery.genotypepresets.choice)
            }
          }
        "
      >
        <template v-if="selectedQuery.genotypepresets?.choice" #summary>
          <Item
            :modified="
              !!selectedPredefinedQuery &&
              !matchesGenotypePreset(
                pedigree,
                selectedQuery.genotypepresets?.choice,
                selectedQuery,
              )
            "
            @revert="
              () =>
                revertGenotypeToPresets(selectedQuery!.genotypepresets?.choice!)
            "
          >
            {{
              SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[
                (pedigree, selectedQuery.genotypepresets?.choice)
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
              :selected="selectedQuery.genotypepresets?.choice === key"
              :modified="
                !!pedigree &&
                selectedQuery.genotypepresets?.choice === key &&
                selectedPredefinedQuery &&
                !matchesGenotypePreset(
                  pedigree,
                  selectedQuery.genotypepresets?.choice,
                  selectedQuery,
                )
              "
              @click="() => revertGenotypeToPresets(key)"
              @revert="() => revertGenotypeToPresets(key)"
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
            (p) => p.sodar_uuid === selectedQuery?.[group.queryPresetKey],
          )?.label
        "
        :modified="
          !!selectedPredefinedQuery?.[group.id] &&
          presetsDetails[group.presetSetKey].find(
            (p) => p.sodar_uuid === selectedQuery?.[group.queryPresetKey],
          )?.sodar_uuid !== selectedPredefinedQuery?.[group.id]
        "
        @revert="
          () => {
            const preset = presetsDetails[group.presetSetKey].find(
              (p) => p.sodar_uuid === selectedPredefinedQuery?.[group.id],
            )
            if (!!pedigree && !!preset) {
              revertToPresets(pedigree, group, preset)
            }
          }
        "
      >
        <template #summary>
          <PresetSummaryItem
            :pedigree="pedigree"
            :presets-details="presetsDetails"
            :query="selectedQuery"
            :group="group"
            :preset="
              presetsDetails[group.presetSetKey].find(
                (p) => p.sodar_uuid === selectedQuery?.[group.queryPresetKey],
              )
            "
            @revert="
              (preset: any) => {
                if (!!pedigree) {
                  revertToPresets(pedigree, group, preset)
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
                preset.sodar_uuid == selectedQuery[group.queryPresetKey]
              "
              :modified="
                preset.sodar_uuid == selectedQuery[group.queryPresetKey] &&
                !(
                  !!pedigree &&
                  selectedPredefinedQuery &&
                  (group.id == 'quality'
                    ? matchesQualityPreset(
                        pedigree,
                        presetsDetails,
                        selectedQuery,
                      )
                    : group.matchesPreset(presetsDetails, selectedQuery))
                )
              "
              @click="
                () => {
                  if (pedigree) {
                    revertToPresets(pedigree, group, preset)
                  }
                }
              "
              @revert="
                () => {
                  if (pedigree) {
                    revertToPresets(pedigree, group, preset)
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
            text="Send"
            variant="flat"
            @click="
              () => {
                if (selectedQuery !== null) {
                  selectedQuery.label = updateDialogTitle
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
