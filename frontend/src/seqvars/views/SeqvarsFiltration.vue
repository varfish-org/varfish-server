<script setup lang="ts">
import { computed, ref } from 'vue'

import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import FrequencySelect from '@/seqvars/components/FrequencySelect/FrequencySelect.vue'
// import GenotypeSelect from '@/seqvars/components/GenotypeSelect/GenotypeSelect.vue'
import {
  Affected,
  PedigreeMember,
  SexAssignedAtBirth,
} from '@/seqvars/components/GenotypeSelect/constants'
// import { getGenotypeValueFromPreset } from '@/seqvars/components/GenotypeSelect/utils'
import PredefinedQueryList from '@/seqvars/components/PredefinedQueryList.vue'
import QueryList from '@/seqvars/components/QueryList.vue'
import { Query } from '@/seqvars/types'

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

const pedigreeMembers = ref<PedigreeMember[]>([
  {
    name: 'index',
    affected: Affected.AFFECTED,
    sexAssignedAtBirth: SexAssignedAtBirth.UNDEFINED,
  },
  {
    name: 'father',
    affected: Affected.UNDEFINED,
    sexAssignedAtBirth: SexAssignedAtBirth.MALE,
  },
  {
    name: 'mother',
    affected: Affected.AFFECTED,
    sexAssignedAtBirth: SexAssignedAtBirth.FEMALE,
  },
])

const createQuery = (pq: SeqvarsPredefinedQuery): Query => {
  return {
    predefinedquery: pq.sodar_uuid,
    frequency: presets.seqvarsquerypresetsfrequency_set.find(
      (f) => f.sodar_uuid === pq.frequency,
    )!,
    frequencypresets: pq.frequency,
  }
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
          v-model="selectedQueryIndex"
          :predefined-queries="presets.seqvarspredefinedquery_set"
          :queries="queries"
          @remove-query="(index) => queries.splice(index, 1)"
        />

        <PredefinedQueryList
          :presets="presets.seqvarspredefinedquery_set"
          :model-value="selectedQuery?.predefinedquery"
          @update:model-value="
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
          <!-- <GenotypeSelect
            v-model="selectedQuery.value.genotype"
            :pedigree-members="pedigreeMembers"
          /> -->

          <FrequencySelect
            v-model="selectedQuery"
            :presets="presets.seqvarsquerypresetsfrequency_set"
          />
        </template>
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
