<script setup lang="ts">
import { SeqvarsQueryDetails } from '@varfish-org/varfish-api/lib'
import { ref } from 'vue'

import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

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

const detailsOpen = ref<boolean>(false)

const model = defineModel<SeqvarsQueryDetails>({ required: true })
</script>

<template>
  <v-checkbox
    v-model="model.settings.variantprio.variant_prio_enabled"
    density="compact"
    label="Enable pathogenicity-based priorization"
    color="primary"
    hide-details
    class="my-2"
  />

  <CollapsibleGroup
    v-model:is-open="detailsOpen"
    title="Phenotype similarity algorithm"
  >
    <template #summary>
      {{ model.settings.variantprio.services?.[0]?.name }}
    </template>

    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
        <div
          role="listbox"
          style="width: 100%; display: flex; flex-direction: column"
        >
          <Item
            v-for="item in ITEMS"
            :key="item.name"
            :selected="
              model.settings.variantprio.services?.some(
                (s) => s.name == item.name,
              )
            "
            @click="() => (model.settings.variantprio.services = [item])"
          >
            {{ item.name }}
          </Item>
        </div>
      </div>
    </template>
  </CollapsibleGroup>
</template>
