<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  SeqvarsGenotypePresetChoice,
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { copy } from '@/varfish/helpers'

import { GENOTYPE_PRESETS } from '@/seqvars/components/genotype/constants'
import GenotypeControls from '@/seqvars/components/genotype/GenotypeControls.vue'
import {
  createGenotypeFromPreset,
  createQualityFromPreset,
  FilterGroup,
  GROUPS,
  matchesGenotypePreset,
  matchesQualityPreset,
} from '@/seqvars/components/groups'
import PredefinedQueryList from '@/seqvars/components/PredefinedQueryList.vue'
import QueryList from '@/seqvars/components/QueryList.vue'
import CollapsibleGroup from '@/seqvars/components/ui/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/ui/Hr.vue'
import Item from '@/seqvars/components/ui/Item.vue'
import { Query } from '@/seqvars/types'

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
      const preset = presetDetails[group.presetSetKey].find(
        (p) => p.sodar_uuid === pq[group.id],
      )
      return [
        [group.queryPresetKey, pq[group.id]],
        [
          group.id,
          group.id == 'quality'
            ? createQualityFromPreset(preset as SeqvarsQueryPresetsQuality)
            : preset,
        ],
      ]
    }),
  ) as Pick<Query, (typeof GROUPS)[number]['id']> & Partial<Query>
  const choice = pq.genotype?.choice
  return copy({
    ...presetFields,
    predefinedquery: pq.sodar_uuid,
    genotype: createGenotypeFromPreset(choice),
    genotypepresets: { choice },
  })
}

const setToPreset = <G extends (typeof GROUPS)[number]>(
  group: G,
  preset: G extends FilterGroup<any, any, infer Preset> ? Preset : never,
) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value[`${group.id}presets`] = preset.sodar_uuid
  const value =
    group.id == 'quality'
      ? createQualityFromPreset(preset as SeqvarsQueryPresetsQuality)
      : preset
  selectedQuery.value[group.id] = copy(value)
}

const setGenotypeToPreset = (choice: SeqvarsGenotypePresetChoice) => {
  if (!selectedQuery.value) {
    return
  }
  selectedQuery.value.genotype = copy(createGenotypeFromPreset(choice))
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
          <CollapsibleGroup
            title="Genotype"
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
                  !matchesGenotypePreset(
                    selectedQuery.genotypepresets?.choice,
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
            <GenotypeControls v-model="selectedQuery" />
          </CollapsibleGroup>

          <CollapsibleGroup
            v-for="group in GROUPS"
            :key="group.id"
            :title="group.title"
            :summary="
              presetDetails[group.presetSetKey].find(
                (p) => p.sodar_uuid === selectedQuery?.[group.queryPresetKey],
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
                    (group.id == 'quality'
                      ? matchesQualityPreset(presetDetails, selectedQuery)
                      : group.matchesPreset(presetDetails, selectedQuery))
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
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
