<script setup lang="ts">
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '../ui/CollapsibleGroup.vue'
import Item from '../ui/Item.vue'
import PresetSelect from '../ui/PresetSelect.vue'
import { Query } from '@/seqvars/types'

import { matchesPathogenicityPrioPreset } from './utils'

const ITEMS = [
  {
    name: 'cadd',
    version: '1.6',
  },
  {
    name: 'mutationtaster',
    version: '2021',
  },
]

const model = defineModel<Query>({ required: true })

const { presets } = defineProps<{
  presets: SeqvarsQueryPresetsVariantPrio[]
}>()
</script>

<template>
  <CollapsibleGroup title="Phenotype Priorization">
    <PresetSelect
      v-model="model"
      :presets="presets"
      preset-id-field="variantpriopresets"
      settings-field="variantprio"
      :matcher="matchesPathogenicityPrioPreset"
    />

    <label style="display: flex; max-width: 260px">
      <v-checkbox-btn v-model="model.variantprio.variant_prio_enabled" />
      Enable pathogenicity-based priorization</label
    >

    <CollapsibleGroup title="Phenotype similarity algorithm">
      <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
        <div
          role="listbox"
          style="width: 100%; display: flex; flex-direction: column"
        >
          <Item
            v-for="item in ITEMS"
            :key="item.name"
            :selected="
              model.variantprio.services?.some((s) => s.name == item.name)
            "
            @click="() => (model.variantprio.services = [item])"
          >
            {{ item.name }}
          </Item>
        </div>
      </div>
    </CollapsibleGroup>
  </CollapsibleGroup>
</template>
