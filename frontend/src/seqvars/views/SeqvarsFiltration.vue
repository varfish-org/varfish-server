<script setup>
import GenotypeSelect from '@/seqvars/components/GenotypeSelect/GenotypeSelect.vue'
import {
  Affected,
  SexAssignedAtBirth,
} from '@/seqvars/components/GenotypeSelect/types'
import QueryList from '@/seqvars/components/QueryList/QueryList.vue'
import QuickPresetsList from '@/seqvars/components/QuickPresetsList/QuickPresetsList.vue'
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
        <QueryList :queries="[{ label: 'de novo' }, { label: 'dominant' }]" />

        <QuickPresetsList
          :presets="[
            { label: 'de-novo' },
            { label: 'dominant' },
            { label: 'homozygous recessive' },
            { label: 'compound recessive' },
          ]"
        />

        <GenotypeSelect
          :pedigree-members="[
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
          ]"
        />
      </div>
    </div>
    <div>TODO</div>
  </div>
</template>
