<script setup lang="ts">
import { Query } from '@/seqvars/types'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'

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
</script>

<template>
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
</template>
