<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import FrequencySelect from '@/seqvars/components/FrequencySelect/FrequencySelect.vue'
import GenotypeSelect from '@/seqvars/components/GenotypeSelect/GenotypeSelect.vue'
import PhenotypePrioSelect from '@/seqvars/components/PhenotypePrioSelect/PhenotypePrioSelect.vue'
import PredefinedQueryList from '@/seqvars/components/PredefinedQueryList.vue'
import QueryList from '@/seqvars/components/QueryList.vue'
import { Query } from '@/seqvars/types'
import { copy } from '@/varfish/helpers'
import { getGenotypeSettingsFromPreset } from '../components/GenotypeSelect/utils'
import Patho from '@/svs/components/SvFilterForm/Patho.vue'
import PathogenicityPrioSelect from '../components/PathogenicityPrioSelect/PathogenicityPrioSelect.vue'

const { presets } = defineProps<{
  presets: SeqvarsQueryPresetsSetVersionDetails
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

const createQuery = (pq: SeqvarsPredefinedQuery): Query => {
  return copy({
    predefinedquery: pq.sodar_uuid,

    genotype: getGenotypeSettingsFromPreset(pq.genotype?.choice ?? 'any'),
    genotypepresets: pq.genotype,

    frequency: presets.seqvarsquerypresetsfrequency_set.find(
      (f) => f.sodar_uuid === pq.frequency,
    )!,
    frequencypresets: pq.frequency,

    phenotypeprio: presets.seqvarsquerypresetsphenotypeprio_set.find(
      (f) => f.sodar_uuid === pq.phenotypeprio,
    )!,
    phenotypepriopresets: pq.phenotypeprio,

    variantprio: presets.seqvarsquerypresetsvariantprio_set.find(
      (f) => f.sodar_uuid === pq.variantprio,
    )!,
    variantpriopresets: pq.variantprio,
  })
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
          :presets="presets"
          :queries="queries"
          @update:selected-index="(index) => (selectedQueryIndex = index)"
          @remove="(index) => queries.splice(index, 1)"
          @revert="
            () => {
              const preset = presets.seqvarspredefinedquery_set.find(
                (p) => p.sodar_uuid === selectedQuery?.predefinedquery,
              )
              if (preset) {
                selectedQuery = createQuery(preset)
              }
            }
          "
        />

        <PredefinedQueryList
          :presets="presets"
          :selected-id="selectedQuery?.predefinedquery"
          :query="selectedQuery"
          @update:selected-id="
            (id) => {
              const preset = presets.seqvarspredefinedquery_set.find(
                (p) => p.sodar_uuid === id,
              )
              if (preset) {
                selectedQuery = createQuery(preset)
              }
            }
          "
          @add-query="
            (preset) => {
              queries.push(createQuery(preset))
              selectedQueryIndex = queries.length - 1
            }
          "
        />

        <template v-if="selectedQuery">
          <GenotypeSelect v-model="selectedQuery" />
          <FrequencySelect
            v-model="selectedQuery"
            :presets="presets.seqvarsquerypresetsfrequency_set"
          />
          <PhenotypePrioSelect
            v-model="selectedQuery"
            :presets="presets.seqvarsquerypresetsphenotypeprio_set"
          />
          <PathogenicityPrioSelect
            v-model="selectedQuery"
            :presets="presets.seqvarsquerypresetsvariantprio_set"
          />
        </template>
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
