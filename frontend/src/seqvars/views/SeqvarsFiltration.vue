<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { copy } from '@/varfish/helpers'

import { FilterGroup } from '@/seqvars/components/FilterGroup'
import { GENOTYPE_PRESETS } from '@/seqvars/components/genotype/constants'
import { genotypeFilterGroup } from '@/seqvars/components/genotype/group'
import { GROUPS } from '@/seqvars/components/groups'
import PredefinedQueryList from '@/seqvars/components/PredefinedQueryList.vue'
import QueryList from '@/seqvars/components/QueryList.vue'
import { Query } from '@/seqvars/types'
import CollapsibleGroup from '@/seqvars/components/ui/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/ui/Hr.vue'
import Item from '@/seqvars/components/ui/Item.vue'

const { presetDetails } = defineProps<{
  presetDetails: SeqvarsQueryPresetsSetVersionDetails
}>()

const queries = ref<Query[]>([])
const selectedQueryIndex = ref<number | null>(null)
const selectedQuery = computed({
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

const selectedPredefinedQuery = computed(() =>
  presetDetails.seqvarspredefinedquery_set.find(
    (pq) => pq.sodar_uuid === selectedQuery.value?.predefinedquery,
  ),
)

const getGenotypeLabel = (key: SeqvarsGenotypePresetChoice) =>
  key == 'any' ? 'any mode' : key.toLowerCase().split('_').join(' ')

const createQuery = (pq: SeqvarsPredefinedQuery): Query => {
  const presetFields = Object.fromEntries(
    GROUPS.flatMap((group) => {
      const preset = group.getPreset(presetDetails, pq)!
      return [
        [group.queryPresetKey, pq[group.id]],
        [
          group.id,
          group.createSettingsFromPreset?.(preset, pq[group.id] as never) ??
            preset,
        ],
      ]
    }),
  ) as Pick<Query, (typeof GROUPS)[number]['id']> & Partial<Query>
  return copy({ ...presetFields, predefinedquery: pq.sodar_uuid })
}

const setToPreset = <
  G extends Exclude<(typeof GROUPS)[number], { id: 'genotype' }>,
>(
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value[`${group.id}presets`] = preset.sodar_uuid
  selectedQuery.value[group.id] = copy(preset)
}

const setGenotypeToPreset = (choice: SeqvarsGenotypePresetChoice) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value.genotype = copy(
    genotypeFilterGroup.createSettingsFromPreset!(null as never, { choice }),
  )
  selectedQuery.value.genotypepresets = { choice }
}
</script>

<template>
  <div style="height: 100vh; display: flex" class="bg-bg">
    <div
      style="
        padding-right: 8px;
        min-width: 250px;
        height: 100%;
        overflow-y: auto;
      "
    >
      <div
        class="text-ui-control-text"
        style="
          padding: 6px;
          font-weight: bold;
          color: white !important;
          background: #1e3064;
        "
      >
        NA12878
      </div>
      <div
        style="height: 100%; display: flex; flex-direction: column; gap: 8px"
      >
        <QueryList
          v-if="queries.length > 0"
          :selected-index="selectedQueryIndex"
          :presets="presetDetails"
          :queries="queries"
          @update:selected-index="(index) => (selectedQueryIndex = index)"
          @remove="(index) => queries.splice(index, 1)"
          @revert="
            () => {
              const pq = presetDetails.seqvarspredefinedquery_set.find(
                (p) => p.sodar_uuid === selectedQuery?.predefinedquery,
              )!
              selectedQuery = createQuery(pq)
            }
          "
        />
        <PredefinedQueryList
          :presets="presetDetails"
          :selected-id="selectedQuery?.predefinedquery"
          :query="selectedQuery"
          @update:selected-id="
            (id) => {
              const pq = presetDetails.seqvarspredefinedquery_set.find(
                (p) => p.sodar_uuid === id,
              )!
              selectedQuery = createQuery(pq)
            }
          "
          @add-query="
            (pq) => {
              const query = createQuery(pq)
              queries.push(query)
              selectedQueryIndex = queries.length - 1
            }
          "
        />

        <template v-if="selectedQuery">
          <template v-for="group in GROUPS">
            <CollapsibleGroup
              v-if="group.id == 'genotype'"
              :key="group.id"
              :title="group.title"
              :summary="
                selectedQuery.genotypepresets?.choice
                  ? getGenotypeLabel(selectedQuery.genotypepresets?.choice)
                  : ''
              "
            >
              <div
                role="listbox"
                style="width: 100%; display: flex; flex-direction: column"
              >
                <Item
                  v-for="key in Object.keys(
                    GENOTYPE_PRESETS,
                  ) as SeqvarsGenotypePresetChoice[]"
                  :key="key"
                  :selected="selectedQuery.genotypepresets?.choice == key"
                  :modified="
                    selectedPredefinedQuery &&
                    genotypeFilterGroup.matchesPreset(
                      presetDetails,
                      selectedPredefinedQuery,
                      selectedQuery,
                    )
                  "
                  @click="() => setGenotypeToPreset(key)"
                  @revert="() => setGenotypeToPreset(key)"
                >
                  {{ getGenotypeLabel(key) }}
                </Item>
              </div>
              <Hr />
              <component :is="group.Component" v-model="selectedQuery" />
            </CollapsibleGroup>

            <CollapsibleGroup
              v-else
              :key="`else-${group.id}`"
              :title="group.title"
              :summary="
                presetDetails[group.presetSetKey].find(
                  (p) => p.sodar_uuid === selectedQuery?.[group.id],
                )?.label
              "
            >
              <div
                role="listbox"
                style="width: 100%; display: flex; flex-direction: column"
              >
                <Item
                  v-for="preset in presetDetails[group.presetSetKey]"
                  :key="preset.sodar_uuid"
                  :selected="
                    preset.sodar_uuid == selectedQuery[group.queryPresetKey]
                  "
                  :modified="
                    !(
                      selectedPredefinedQuery &&
                      group.matchesPreset(
                        presetDetails,
                        selectedPredefinedQuery,
                        selectedQuery,
                      )
                    )
                  "
                  @click="() => setToPreset(group, preset)"
                  @revert="() => setToPreset(group, preset)"
                >
                  {{ preset.label }}
                </Item>
              </div>
              <Hr />
              <component :is="group.Component" v-model="selectedQuery" />
            </CollapsibleGroup>
          </template>
        </template>
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
