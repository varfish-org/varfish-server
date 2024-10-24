<script setup lang="ts">
/**
 * This component provides the overall query editor.
 *
 * The `QueryEditor` is very complex.  To reduce the complexity, the
 * following measures have been taken:
 *
 * - Server state management is done via TanStack Query.
 * - The top level component only orchestrates create, update, and "revert
 *   to presets values" actions.
 * - The updates of the "deep inner" values are handled in the child
 *   components directly via TanStack Query.
 *
 * Effectively, we don't have any "models" in this component or the
 * descendants and rely on TanStack Query for state management.
 */
import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryDetails,
  SeqvarsQueryDetailsRequest,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { isDeepEqual } from 'remeda'
import { computed, ref, toRaw, watch } from 'vue'

import { useCaseRetrieveQuery } from '@/cases/queries/cases'
import { PedigreeObj } from '@/cases/stores/caseDetails'
import GenotypeControls from '@/seqvars/components/QueryEditor/GenotypeControls.vue'
import PredefinedQueryList from '@/seqvars/components/QueryEditor/PredefinedQueryList.vue'
import PresetSummaryItem from '@/seqvars/components/QueryEditor/PresetSummaryItem.vue'
import QueryList from '@/seqvars/components/QueryEditor/QueryList.vue'
import {
  FilterGroup,
  GROUPS,
  QueryKey,
  createGenotypeFromPreset,
  createQualityFromPreset,
  matchesGenotypePreset,
  matchesQualityPreset,
} from '@/seqvars/components/QueryEditor/groups'
import { GENOTYPE_PRESET_TO_RECESSIVE_MODE } from '@/seqvars/components/QueryEditor/lib/constants'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'
import { SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS } from '@/seqvars/lib/constants'
import {
  useCopySeqvarQueryFromPresetCreateMutation,
  useSeqvarQueryDestroyMutation,
  useSeqvarQueryListInfiniteQuery,
  useSeqvarQueryRetrieveQueries,
  useSeqvarQueryUpdateMutation,
} from '@/seqvars/queries/seqvarQuery'
import { useSeqvarQueryExecutionStartMutation } from '@/seqvars/queries/seqvarQueryExecution'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the case to edit queries for. */
    caseUuid: string
    /** UUID of the case analysis session to edit queries for. */
    sessionUuid: string
    /** UUIDs of the currently opened queries. */
    openQueryUuids: string[]
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
    openQueryUuids: () => [],
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

/** The UUID of the currently selected query; component state. */
const selectedQueryUuid = defineModel<string | undefined>('selectedQueryUuid')
/** Whether to show the query update dialog; component state. */
const showUpdateDialog = ref<boolean>(false)
/** The query title in update dialog; component state. */
const updateDialogTitle = ref<string>('')
/** Wraps `props.caseUuid` into a `ComputedRef` for use with queries. */
const caseUuid = computed(() => props.caseUuid)
/** Wraps `props.sessionUuid` into a `ComputedRef` for use with queries. */
const sessionUuid = computed(() => props.sessionUuid)

/** Retrieve Case through TanStack Query. */
const caseRetrieveRes = useCaseRetrieveQuery({ caseUuid })
/** List all queries for the given case in the given session. */
const seqvarQueryListRes = useSeqvarQueryListInfiniteQuery({ sessionUuid })
/** Provide the UUIDs from `seqvarsQueryListRes` as an `ComputedRef<string[]>` for use with queries. */
const seqvarQueryUuids = computed<string[] | undefined>(() => {
  const res = seqvarQueryListRes.data?.value?.pages?.reduce(
    (acc, page) => acc.concat(page.results?.map((q) => q.sodar_uuid) ?? []),
    [] as string[],
  )
  if ((res?.length ?? 0) > 0) {
    return res
  } else {
    return undefined
  }
})
/** Provide detailed seqvar queries for the `seqvarQueryListRes` via UUIDs in `sevarQueryListRes`. */
const seqvarQueryRetrieveRes = useSeqvarQueryRetrieveQueries({
  sessionUuid,
  seqvarQueryUuids,
})

/** Provide access to all queries as a `Map` by their UUID. */
const seqvarQueries = computed<Map<string, SeqvarsQueryDetails>>(() => {
  return new Map(
    // @ts-ignore // https://github.com/hey-api/openapi-ts/issues/653#issuecomment-2314847011
    seqvarQueryRetrieveRes.value.data?.map((q) => [q.sodar_uuid, q]) ?? [],
  )
})

/** Wraps the `PedigreeObj` into a `ComputedRef` for easier access. */
const pedigree = computed<PedigreeObj | undefined>(
  () =>
    (caseRetrieveRes.data?.value?.pedigree_obj ?? undefined) as
      | PedigreeObj
      | undefined,
)

/** The currently selected query; manages `selectedQueryUuid`. */
const selectedQuery = computed<SeqvarsQueryDetails | undefined>({
  get() {
    return seqvarQueries.value.get(selectedQueryUuid.value ?? '')
  },
  set(newValue) {
    selectedQueryUuid.value = newValue?.sodar_uuid
  },
})

/**
 * The original predefined query that the currently selected query is based on.
 */
const baselinePredefinedQuery = computed<SeqvarsPredefinedQuery | undefined>(
  () =>
    props.presetsDetails.seqvarspredefinedquery_set.find(
      (pq) => pq.sodar_uuid === selectedQuery.value?.settings.predefinedquery,
    ),
)

/** Mutation for creating a new query based on given predefined query. */
const seqvarQueryCreateFromPresets =
  useCopySeqvarQueryFromPresetCreateMutation()

/**
 * Create a new query based on the given predefined query.
 */
const createQuery = async (pq: SeqvarsPredefinedQuery) => {
  let label = pq.label
  const queryLabels = Array.from(seqvarQueries.value.values()).map(
    (q) => q.label,
  )
  let i = 2 // sic, need to place outside loop in `<template>`
  for (; queryLabels.includes(label); i++) {
    label = `${pq.label} (${i})`
  }

  try {
    const res = await seqvarQueryCreateFromPresets.mutateAsync({
      body: {
        predefinedquery: pq.sodar_uuid,
        label,
      },
      path: {
        session: sessionUuid.value,
      },
    })
    selectedQueryUuid.value = res.sodar_uuid
    emit('message', {
      text: `Created new query: ${res.label}`,
      color: 'success',
    })
  } catch (e) {
    emit('message', {
      text: `Failed to create new query: ${e}`,
      color: 'error',
    })
  }
}

/** Mutation for updating a seqvar query. */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/**
 * Update the query's label.
 *
 * @param label The new label to set.
 * @returns Whether the update was successful.
 * @throws Error if the query could not be updated.
 */
const updateQueryLabel = async (label: string): Promise<boolean> => {
  if (!!selectedQuery.value) {
    try {
      await seqvarQueryUpdate.mutateAsync({
        body: {
          ...selectedQuery.value,
          label,
        },
        path: {
          session: sessionUuid.value,
          query: selectedQuery.value.sodar_uuid,
        },
      })
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

/** Mutation for deleting a seqvar query. */
const seqvarQueryDestroy = useSeqvarQueryDestroyMutation()

/** Delete the query with the given UUID. */
const deleteQuery = async (queryUuid: string) => {
  const seqvarsQuery = seqvarQueries.value.get(queryUuid)
  if (!seqvarsQuery) {
    console.error('Query not found:', queryUuid)
    return
  }
  try {
    await seqvarQueryDestroy.mutateAsync({
      path: {
        session: sessionUuid.value,
        query: seqvarsQuery.sodar_uuid,
      },
    })
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

/** Mutation for creating a query execution for a query. */
const seqvarQueryExecutionStart = useSeqvarQueryExecutionStartMutation()

/** Start query with the given UUID. */
const startQuery = async (queryUuid: string) => {
  try {
    await seqvarQueryExecutionStart.mutateAsync({
      path: {
        query: queryUuid,
      },
    })
    emit('message', {
      text: `Started query: ${seqvarQueries.value.get(queryUuid)?.label}`,
      color: 'success',
    })
  } catch (e) {
    emit('message', {
      text: `Failed to start query: ${e}`,
      color: 'error',
    })
  }
}

/**
 * Revert the currently selected query's genotype.
 */
const revertGenotypeToPresets = async () => {
  if (!!baselinePredefinedQuery.value?.genotype?.choice && !!pedigree.value) {
    await updateGenotypeToPresets(
      baselinePredefinedQuery.value?.genotype?.choice,
    )
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
    await revertCategoryToPresets(pedigree.value, group, preset)
  }
}

/**
 * Update genotype to presets in a `seqvarsQuery` in a `SeqvarsQueryDetailsRequest`.
 */
const queryWithGenotypePresets = <T extends SeqvarsQueryDetailsRequest>(
  seqvarsQuery: T,
  choice: SeqvarsGenotypePresetChoice,
  pedigree: PedigreeObj,
): T => {
  if (!seqvarsQuery.settings.genotypepresets?.choice) {
    return seqvarsQuery
  } else {
    return {
      ...seqvarsQuery,
      settings: {
        ...seqvarsQuery.settings,
        genotypepresets: {
          ...seqvarsQuery.settings.genotype,
          choice,
        },
        genotype: createGenotypeFromPreset(pedigree, choice),
      },
    }
  }
}

/**
 * Update a category of the query settings to the given preset.
 */
const queryWithGroupPresets = <
  G extends (typeof GROUPS)[number],
  T extends SeqvarsQueryDetailsRequest,
>(
  seqvarsQuery: T,
  pedigree: PedigreeObj,
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
): T => {
  if (!seqvarsQuery.settings.genotypepresets?.choice) {
    return seqvarsQuery
  } else {
    const value =
      group.id === 'quality'
        ? createQualityFromPreset(
            pedigree,
            preset as SeqvarsQueryPresetsQuality,
          )
        : preset
    return {
      ...seqvarsQuery,
      settings: {
        ...seqvarsQuery.settings,
        [`${group.id}presets`]: preset.sodar_uuid,
        [group.id]: {
          ...seqvarsQuery.settings[group.id],
          ...value,
        },
      },
    }
  }
}

/**
 * Reverts the currently selected query's settings to its original presets'
 * value.
 */
const revertQueryToPresets = async () => {
  if (!selectedQuery.value) {
    // guard against no query
    return
  }
  let seqvarsQuery = selectedQuery.value

  const choice = baselinePredefinedQuery.value?.genotype?.choice
  if (!!choice) {
    seqvarsQuery = queryWithGenotypePresets(
      seqvarsQuery,
      choice,
      pedigree.value!,
    )
  }

  for (const group of Object.values(GROUPS)) {
    const preset = props.presetsDetails[group.presetSetKey].find(
      (p) => p.sodar_uuid === baselinePredefinedQuery.value?.[group.id],
    )
    if (!!seqvarsQuery && !!preset) {
      seqvarsQuery = queryWithGroupPresets(
        seqvarsQuery,
        pedigree.value!,
        group,
        preset,
      )
    }
  }

  await seqvarQueryUpdate.mutateAsync({
    body: seqvarsQuery,
    path: {
      session: sessionUuid.value,
      query: selectedQuery.value.sodar_uuid,
    },
  })
}

/**
 * Set the genotype according to the given preset choice.
 *
 * Used both for setting the genotype from a preset and for reverting the
 * genotype to the preset.
 */
const updateGenotypeToPresets = async (choice: SeqvarsGenotypePresetChoice) => {
  if (!!selectedQuery.value && !!pedigree.value) {
    await seqvarQueryUpdate.mutateAsync({
      body: queryWithGenotypePresets(
        selectedQuery.value,
        choice,
        pedigree.value,
      ),
      path: {
        session: sessionUuid.value,
        query: selectedQuery.value.sodar_uuid,
      },
    })
  }
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
    !seqvarQueries.value.has(selectedQueryUuid.value)
  ) {
    selectedQueryUuid.value = seqvarQueries.value
      .values()
      .next()?.value?.sodar_uuid
  }
}

/**
 * Revert the given preset category/group to the given preset.
 */
const revertCategoryToPresets = async <G extends (typeof GROUPS)[number]>(
  pedigree: PedigreeObj,
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
) => {
  if (!!selectedQuery.value) {
    await seqvarQueryUpdate.mutateAsync({
      body: queryWithGroupPresets(selectedQuery.value, pedigree, group, preset),
      path: {
        session: sessionUuid.value,
        query: selectedQuery.value.sodar_uuid,
      },
    })
  }
}

// Observe changes in the queries and update the selected query UUID accordingly.
watch(
  () => [seqvarQueries.value.values()],
  () => updateSelectedQueryUuid(),
)

/** Whether the recessive mode collapsible group for genotype is opend. */
const collapsibleGroupOpenGenotype = ref<boolean>(true)
/** Whether the recessive mode collapsible group for genotype is opend. */
const collapsibleGroupOpenColumns = ref<boolean>(true)
/** Whether the collapsible group for the given ID is opened. */
const collapsibleGroupOpenGeneric = ref<Record<QueryKey, boolean>>({
  frequency: true,
  sodar_uuid: true,
  date_created: true,
  date_modified: true,
  presetssetversion: true,
  genotype: true,
  quality: true,
  consequence: true,
  locus: true,
  phenotypeprio: true,
  variantprio: true,
  clinvar: true,
  columns: true,
})
</script>

<template>
  <div v-if="pedigree" class="h-100 overflow-y-auto overflow-x-hidden pr-2">
    <QueryList
      v-if="!!pedigree && seqvarQueries.size > 0"
      :selected-query-uuid="selectedQueryUuid"
      :presets-details="presetsDetails"
      :queries="seqvarQueries"
      :pedigree="pedigree"
      :hints-enabled="hintsEnabled"
      @update:selected-query-uuid="
        (queryUuid: string) => {
          selectedQueryUuid = queryUuid
        }
      "
      @remove="deleteQuery"
      @revert="revertQueryToPresets"
      @start="startQuery"
      @update-query="
        (queryUuid: string) => {
          selectedQueryUuid = queryUuid
          updateDialogTitle = seqvarQueries.get(queryUuid)?.label ?? ''
          showUpdateDialog = true
        }
      "
    />

    <!-- Teleport out the query list when hidden. -->
    <Teleport
      v-if="collapsed && teleportToWhenCollapsed && seqvarQueries.size > 0"
      :to="teleportToWhenCollapsed"
    >
      <v-list-subheader v-if="teleportedQueriesLabels" class="text-uppercase">
        Queries / Results
      </v-list-subheader>
      <v-divider v-else class="mt-1 mb-1"></v-divider>

      <v-list-item
        v-for="(query, index) in seqvarQueries.values()"
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

    <template v-if="!!selectedQuery">
      <CollapsibleGroup
        v-model="collapsibleGroupOpenGenotype"
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
        storage-name="query-editor-genotype"
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
              async () =>
                await updateGenotypeToPresets(
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
              @click="async () => await updateGenotypeToPresets(key)"
              @revert="async () => await updateGenotypeToPresets(key)"
            >
              {{ SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[key] }}
            </Item>
          </div>
          <v-divider class="my-2" />
          <GenotypeControls
            :seqvars-query="selectedQuery"
            :pedigree="pedigree"
            :hints-enabled="hintsEnabled"
          />
        </template>
      </CollapsibleGroup>

      <CollapsibleGroup
        v-for="group in GROUPS"
        :key="group.id"
        v-model="collapsibleGroupOpenGeneric[group.id]"
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
        :storage-name="`query-editor-${group.id}`"
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
              async (preset: any) => {
                if (!!pedigree) {
                  await revertCategoryToPresets(pedigree, group, preset)
                }
              }
            "
          />
        </template>
        <template #default>
          <div role="listbox" class="w-100 d-flex flex-column">
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
                async () => {
                  if (pedigree) {
                    await revertCategoryToPresets(pedigree, group, preset)
                  }
                }
              "
              @revert="
                async () => {
                  if (pedigree) {
                    await revertCategoryToPresets(pedigree, group, preset)
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
            :model-value="selectedQuery"
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
