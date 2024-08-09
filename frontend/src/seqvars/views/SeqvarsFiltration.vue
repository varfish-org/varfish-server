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
import GeneDataTable from '@/seqvars/components/GeneDataTable/GeneDataTable.vue'
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
import SidebarCollapseIcon from '@/seqvars/components/ui/SidebarCollapseIcon.vue'
import SidebarExpandIcon from '@/seqvars/components/ui/SidebarExpandIcon.vue'
import { Query } from '@/seqvars/types'

const { presetsDetails } = defineProps<{
  presetsDetails: SeqvarsQueryPresetsSetVersionDetails
}>()

const queries = ref<Query[]>([])
const selectedQueryIndex = ref<number | null>(null)
const sidebarExpanded = ref(true)
const selectedGene = ref<any | null>(null)

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
  presetsDetails.seqvarspredefinedquery_set.find(
    (pq) => pq.sodar_uuid === selectedQuery.value?.predefinedquery,
  ),
)

const getGenotypeLabel = (key: SeqvarsGenotypePresetChoice) =>
  key == 'any' ? 'any mode' : key.toLowerCase().split('_').join(' ')

const createQuery = (pq: SeqvarsPredefinedQuery): Query => {
  const presetFields = Object.fromEntries(
    GROUPS.flatMap((group) => {
      const preset = presetsDetails[group.presetSetKey].find(
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
  <div style="height: 100vh; display: flex; gap: 8px" class="bg-bg">
    <div
      :style="{
        borderRight: '1px solid #eaeaea',
        minWidth: sidebarExpanded ? '340px' : 'fit-content',
        height: '100%',
        overflowY: 'auto',
        overflowX: 'hidden',
      }"
    >
      <div
        class="text-ui-control-text"
        style="
          padding: 6px;
          font-weight: bold;
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: white !important;
          background: #1e3064;
        "
      >
        <span v-if="sidebarExpanded"> NA12878 </span>
        <button
          type="button"
          class="sidebar-toggle"
          @click="sidebarExpanded = !sidebarExpanded"
        >
          <SidebarCollapseIcon v-if="sidebarExpanded" />
          <SidebarExpandIcon v-else />
        </button>
      </div>
      <div
        v-if="sidebarExpanded"
        style="height: 100%; display: flex; flex-direction: column; gap: 8px"
      >
        <QueryList
          v-if="queries.length > 0"
          :selected-index="selectedQueryIndex"
          :presets-details="presetsDetails"
          :queries="queries"
          @update:selected-index="(index) => (selectedQueryIndex = index)"
          @remove="(index) => queries.splice(index, 1)"
          @revert="
            () => {
              const pq = presetsDetails.seqvarspredefinedquery_set.find(
                (p) => p.sodar_uuid === selectedQuery?.predefinedquery,
              )!
              selectedQuery = createQuery(pq)
            }
          "
        />
        <PredefinedQueryList
          :presets="presetsDetails"
          :selected-id="selectedQuery?.predefinedquery"
          :query="selectedQuery"
          @update:selected-id="
            (id) => {
              const pq = presetsDetails.seqvarspredefinedquery_set.find(
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
              aria-label="Genotype presets"
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
              presetsDetails[group.presetSetKey].find(
                (p) => p.sodar_uuid === selectedQuery?.[group.queryPresetKey],
              )?.label
            "
          >
            <div
              role="listbox"
              :aria-label="`${group.title} presets`"
              style="width: 100%; display: flex; flex-direction: column"
            >
              <Item
                v-for="preset in presetsDetails[group.presetSetKey]"
                :key="preset.sodar_uuid"
                :selected="
                  preset.sodar_uuid == selectedQuery[group.queryPresetKey]
                "
                :modified="
                  !(
                    selectedPredefinedQuery &&
                    (group.id == 'quality'
                      ? matchesQualityPreset(presetsDetails, selectedQuery)
                      : group.matchesPreset(presetsDetails, selectedQuery))
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
      <div v-else>
        <Item
          v-for="(_query, index) in queries"
          :key="index"
          :selected="selectedQueryIndex == index"
          style="padding: 4px"
          @click="() => (selectedQueryIndex = index)"
        >
          #{{ index + 1 }}
        </Item>
      </div>
    </div>
    <v-sheet style="height: auto; overflow: auto" :elevation="2" rounded>
      <GeneDataTable
        v-if="selectedQueryIndex != null"
        :selected-query-index="selectedQueryIndex"
        :presets-details="presetsDetails"
        :queries="queries"
        @show-details="(item) => (selectedGene = item)"
      />
    </v-sheet>

    <div v-if="selectedGene" style="border-left: 1px solid #d7d7d7">
      <button @click="selectedGene = null">close</button>
      <pre>{{ JSON.stringify(selectedGene, null, 2) }}</pre>
    </div>
  </div>
</template>

<style scoped>
.sidebar-toggle {
  padding: 4px;
  display: flex;
  &:not(:focus-visible) {
    outline: none;
  }
  &:hover {
    filter: invert(0.2);
  }
}
</style>
