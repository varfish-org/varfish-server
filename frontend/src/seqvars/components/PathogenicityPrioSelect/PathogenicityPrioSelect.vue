<script setup lang="ts">
import { copy } from '@/varfish/helpers'
import { SeqvarsQueryPresetsVariantPrio } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
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

const setToPreset = (preset: SeqvarsQueryPresetsVariantPrio) => {
  model.value.variantpriopresets = preset.sodar_uuid
  model.value.variantprio = copy(preset)
}
</script>

<template>
  <CollapsibleGroup title="Phenotype Priorization">
    <div>
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="preset in presets"
          :key="preset.sodar_uuid"
          :selected="preset.sodar_uuid === model.variantpriopresets"
          :modified="!matchesPathogenicityPrioPreset(model.variantprio, preset)"
          @click="() => setToPreset(preset)"
          @revert="() => setToPreset(preset)"
        >
          {{ preset.label }}
        </Item>
      </div>

      <Hr />
    </div>

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
