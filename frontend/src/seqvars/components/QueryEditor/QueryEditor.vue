<script setup lang="ts">
import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryDetails,
  SeqvarsQueryDetailsRequest,
  SeqvarsQueryExecution,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsQuerySettingsDetails,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

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
import { GENOTYPE_PRESET_TO_RECESSIVE_MODE } from '@/seqvars/components/QueryEditor/lib/constants'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'
import { SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS } from '@/seqvars/lib/constants'
import { useSeqvarsQueryStore } from '@/seqvars/stores/query'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'
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
 * The currently selected predefined query.  This is used to compute differences
 * and revert back to.
 */
const selectedPredefinedQuery = computed(() =>
  props.presetsDetails.seqvarspredefinedquery_set.find(
    (pq) => pq.sodar_uuid === selectedQuery.value?.settings.predefinedquery,
  ),
)

/**
 * Create a new `Query` object based on the given `SeqvarsPredefinedQuery`.
 *
 * The function first creates a `SeqvarsQueryDetails` on the client side.  This
 * is then saved to the server using the `seqvarsQueryStore`.
 *
 * @throws Error if there was a problem with creating the query.
 */
const createQuery = async (
  pq: SeqvarsPredefinedQuery,
  options?: { label?: string },
) => {
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
  ) as Pick<SeqvarsQuerySettingsDetails, (typeof GROUPS)[number]['id']> & Partial<SeqvarsQuerySettingsDetails>
  const choice = pq.genotype?.choice

  // Pick unique label.
  let label
  if (options?.label) {
    label = options.label
  } else {
    label = pq.label
    const queryLabels = Array.from(seqvarsQueryStore.seqvarQueries.values()).map((q) => q.label)
    for (let i = 2; ; i++) {
      if (queryLabels.includes(label)) {
        label = `${pq.label} (${i})`
      } else {
        break
      }
    }
  }
  // Pick a next rank.
  let rank = Math.max(1, ...Array.from(seqvarsQueryStore.seqvarQueries.values()).map((q) => q.rank ?? 0))
  let result: SeqvarsQueryDetailsRequest = {
    rank,
    label,
    settings: {
      genotypepresets: undefined,
      qualitypresets: undefined,
      consequencepresets: undefined,
      locuspresets: undefined,
      frequencypresets: undefined,
      phenotypepriopresets: undefined,
      variantpriopresets: undefined,
      clinvarpresets: undefined,
      genotype: {
        recessive_mode: undefined,
        sample_genotype_choices: undefined
      },
      quality: {
        sample_quality_filters: undefined
      },
      consequence: {
        variant_types: undefined,
        transcript_types: undefined,
        variant_consequences: undefined,
        max_distance_to_exon: undefined
      },
      locus: {
        genes: undefined,
        gene_panels: undefined,
        genome_regions: undefined
      },
      frequency: {
        gnomad_exomes: undefined,
        gnomad_genomes: undefined,
        gnomad_mitochondrial: undefined,
        helixmtdb: undefined,
        inhouse: undefined
      },
      phenotypeprio: {
        phenotype_prio_enabled: undefined,
        phenotype_prio_algorithm: undefined,
        terms: undefined
      },
      variantprio: {
        variant_prio_enabled: undefined,
        services: undefined
      },
      clinvar: {
        clinvar_presence_required: undefined,
        clinvar_germline_aggregate_description: undefined,
        allow_conflicting_interpretations: undefined
      }
    },
    columnsconfig: {
      column_settings: []
    }
  }
  return result

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
      :selected-query-uuid="selectedQueryUuid"
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
      :selected-id="selectedQuery?.settings.predefinedquery"
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
          !!selectedQuery?.settings.genotypepresets?.choice &&
          selectedQuery?.settings.genotypepresets?.choice !=
            selectedPredefinedQuery?.genotype?.choice
        "
        :summary="
          selectedQuery.settings.genotypepresets?.choice
            ? SEQVARS_GENOTYPE_PRESET_CHOICES_LABELS[
                selectedQuery.settings.genotypepresets?.choice
              ]
            : ''
        "
        @revert="
          () => {
            if (
              !!selectedQuery?.settings.genotypepresets?.choice &&
              !!selectedPredefinedQuery?.genotype?.choice
            ) {
              selectedQuery.settings.genotypepresets.choice =
                selectedPredefinedQuery.genotype.choice
              revertGenotypeToPresets(
                selectedQuery.settings.genotypepresets.choice,
              )
            }
          }
        "
      >
        <template
          v-if="selectedQuery.settings.genotypepresets?.choice"
          #summary
        >
          <Item
            :modified="
              !!selectedPredefinedQuery &&
              !matchesGenotypePreset(
                pedigree,
                selectedQuery.settings.genotypepresets?.choice,
                selectedQuery.settings,
              )
            "
            @revert="
              () =>
                revertGenotypeToPresets(
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
                selectedPredefinedQuery &&
                !matchesGenotypePreset(
                  pedigree,
                  selectedQuery.settings.genotypepresets?.choice,
                  selectedQuery.settings,
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
            (p) =>
              p.sodar_uuid === selectedQuery?.settings[group.queryPresetKey],
          )?.label
        "
        :modified="
          !!selectedPredefinedQuery?.[group.id] &&
          presetsDetails[group.presetSetKey].find(
            (p) =>
              p.sodar_uuid === selectedQuery?.settings[group.queryPresetKey],
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
                (p) =>
                  p.sodar_uuid ===
                  selectedQuery?.settings[group.queryPresetKey],
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
                preset.sodar_uuid ==
                selectedQuery.settings[group.queryPresetKey]
              "
              :modified="
                preset.sodar_uuid ==
                  selectedQuery.settings[group.queryPresetKey] &&
                !(
                  !!pedigree &&
                  selectedPredefinedQuery &&
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
