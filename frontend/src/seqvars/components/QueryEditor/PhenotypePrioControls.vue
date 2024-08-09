<script setup lang="ts">
import { computed, ref } from 'vue'

import { Query } from '@/seqvars/types'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import SelectBox from './ui/SelectBox.vue'
import { type ItemData } from './ui/lib'
import { queryHPO_Terms } from '../utils'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const ITEMS = {
  phenix: 'Phenix',
  phive: 'Phive',
  'exomiser.hiphive_human': 'HiPhive (human only)',
  'exomiser.hiphive_humanmouse': 'HiPhive (human+mouse)',
  'exomiser.hiphive_humanmousefishppi': 'HiPhive (human, mouse, fish, PPI)',
}

const selectedItem = computed<string | undefined>(() => {
  const [[_, value]] = Object.entries(ITEMS).filter(
    ([key, _]) => key === model.value.phenotypeprio?.phenotype_prio_algorithm,
  )
  return value
})

const model = defineModel<Query>({ required: true })

const detailsOpen = ref<boolean>(false)

const items = ref<ItemData[]>([])

async function onSearch(query: string) {
  items.value = (await queryHPO_Terms(query)).map((i) => ({
    id: i.term_id,
    label: i.label,
    sublabel: i.term_id,
  }))
}
</script>

<template>
  <label style="display: flex; max-width: 260px">
    <v-checkbox-btn v-model="model.phenotypeprio.phenotype_prio_enabled" />
    Enable phenotype-based priorization</label
  >

  <CollapsibleGroup
    v-model:is-open="detailsOpen"
    title="Phenotype similarity algorithm"
    :summary="selectedItem"
  >
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="(label, key) in ITEMS"
          :key="key"
          :selected="model.phenotypeprio.phenotype_prio_algorithm == key"
          @click="() => (model.phenotypeprio.phenotype_prio_algorithm = key)"
        >
          {{ label }}
        </Item>
      </div>
    </div>
  </CollapsibleGroup>

  <SelectBox
    :items="items"
    :model-value="
      (model.phenotypeprio.terms ?? []).map((t) => ({
        id: t.term.term_id,
        label: t.term.label,
        sublabel: t.term.term_id,
      }))
    "
    label="Type to search HPO terms"
    @update:search="onSearch"
    @update:model-value="
      (items: ItemData[]) => {
        model.phenotypeprio.terms = items.map((i) => ({
          term: { label: i.label, term_id: i.id },
        }))
      }
    "
  />
</template>
