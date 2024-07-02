<script setup lang="ts">
import { computed, ref } from 'vue'

import GenotypeSelect from '@/seqvars/components/GenotypeSelect/GenotypeSelect.vue'
import {
  Affected,
  GenotypeState,
  PedigreeMember,
  SexAssignedAtBirth,
} from '@/seqvars/components/GenotypeSelect/types'
import QueryList from '@/seqvars/components/QueryList/QueryList.vue'
import { Query } from '@/seqvars/components/QueryList/types'
import QuickPresetsList from '@/seqvars/components/QuickPresetsList/QuickPresetsList.vue'

const queries = ref<Query[]>([])
const selectedQueryIndex = ref<number | null>(null)
const selectedQuery = computed({
  get() {
    return selectedQueryIndex.value == null
      ? null
      : queries.value[selectedQueryIndex.value]
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
          :queries="queries"
          :selected-index="selectedQueryIndex"
          @select="(index) => (selectedQueryIndex = index)"
          @remove-query="(index) => queries.splice(index, 1)"
        />

        <QuickPresetsList
          :value="selectedQuery?.preset"
          @add-query="
            (preset) =>
              queries.push({
                preset,
                value: {
                  genotype: Object.fromEntries(
                    (['father', 'mother', 'index'] as const).map((name) => [
                      name,
                      { mode: preset.genotype[name], checked: true },
                    ]),
                  ) as GenotypeState,
                },
                isRunning: false,
              })
          "
          @update:value="
            (preset) => {
              if (!selectedQuery) return

              selectedQuery = {
                preset,
                value: {
                  genotype: Object.fromEntries(
                    Object.entries(preset.genotype).map(([name, mode]) => [
                      name,
                      { checked: true, mode },
                    ]),
                  ) as GenotypeState,
                },
                isRunning: false,
              }
            }
          "
        />

        <template v-if="selectedQuery">
          <GenotypeSelect
            v-model="selectedQuery.value.genotype"
            :pedigree-members="pedigreeMembers"
          />
        </template>
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
