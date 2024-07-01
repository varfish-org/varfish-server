<script setup lang="ts">
import { ref } from 'vue'

import GenotypeSelect from '@/seqvars/components/GenotypeSelect/GenotypeSelect.vue'
import {
  Affected,
  SexAssignedAtBirth,
} from '@/seqvars/components/GenotypeSelect/types'
import QueryList from '@/seqvars/components/QueryList/QueryList.vue'
import { Query } from '@/seqvars/components/QueryList/types'
import QuickPresetsList from '@/seqvars/components/QuickPresetsList/QuickPresetsList.vue'

const queries = ref<Query[]>([])

const pedigreeMembers = ref([
  {
    name: 'index II',
    affected: Affected.AFFECTED,
    sexAssignedAtBirth: SexAssignedAtBirth.UNDEFINED,
  },
  {
    name: 'father I',
    affected: Affected.UNDEFINED,
    sexAssignedAtBirth: SexAssignedAtBirth.MALE,
  },
  {
    name: 'mother I',
    affected: Affected.AFFECTED,
    sexAssignedAtBirth: SexAssignedAtBirth.FEMALE,
  },
  {
    name: 'sibling',
    affected: Affected.UNAFFECTED,
    sexAssignedAtBirth: SexAssignedAtBirth.FEMALE,
  },
])
</script>

<template>
  <div style="height: 100vh; display: flex" class="bg-bg">
    <div style="width: 100%; max-width: 370px; height: 100%; overflow-y: auto">
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
        style="
          border-right: 1px solid #e9e9e9;
          height: 100%;
          display: flex;
          flex-direction: column;
          gap: 16px;
        "
      >
        <QueryList
          v-if="queries.length > 0"
          :queries="
            queries.map((query, i) => {
              const sameLabelQueriesBefore = queries
                .slice(0, i)
                .filter((q) => q.label === query.label).length
              return {
                ...query,
                label:
                  query.label +
                  (sameLabelQueriesBefore == 0
                    ? ''
                    : ` (${sameLabelQueriesBefore})`),
              }
            })
          "
          @remove-query="(index) => (queries = queries.toSpliced(index, 1))"
        />

        <QuickPresetsList
          :presets="[
            { label: 'de-novo' },
            { label: 'dominant' },
            { label: 'homozygous recessive' },
            { label: 'compound recessive' },
          ]"
          @add-query="
            (label) =>
              (queries = [
                ...queries,
                { label, isRunning: false, isModified: false },
              ])
          "
        />

        <GenotypeSelect :pedigree-members="pedigreeMembers" />
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
