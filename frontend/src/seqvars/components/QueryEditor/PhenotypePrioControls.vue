<script setup lang="ts">
import { SeqvarsQueryDetails } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { queryHPO_Terms } from '../utils'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import SelectBox from './ui/SelectBox.vue'
import { type ItemData } from './ui/lib'

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
    ([key, _]) =>
      key === model.value.settings.phenotypeprio?.phenotype_prio_algorithm,
  )
  return value
})

const model = defineModel<SeqvarsQueryDetails>({ required: true })

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
  <v-checkbox
    v-model="model.settings.phenotypeprio.phenotype_prio_enabled"
    density="compact"
    label="Enable phenotype-based priorization"
    color="primary"
    hide-details
    class="my-2"
  />

  <CollapsibleGroup
    v-model:is-open="detailsOpen"
    title="Phenotype similarity algorithm"
  >
    <template #summary>
      {{ selectedItem }}
    </template>
    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
        <div
          role="listbox"
          style="width: 100%; display: flex; flex-direction: column"
        >
          <Item
            v-for="(label, key) in ITEMS"
            :key="key"
            :selected="
              model.settings.phenotypeprio.phenotype_prio_algorithm == key
            "
            @click="
              () =>
                (model.settings.phenotypeprio.phenotype_prio_algorithm = key)
            "
          >
            {{ label }}
          </Item>
        </div>
      </div>
    </template>
  </CollapsibleGroup>

  <SelectBox
    :items="items"
    :model-value="
      (model.settings.phenotypeprio.terms ?? []).map((t) => ({
        id: t.term.term_id,
        label: t.term.label,
        sublabel: t.term.term_id,
      }))
    "
    label="Type to search HPO terms"
    @update:search="onSearch"
    @update:model-value="
      (items: ItemData[]) => {
        model.settings.phenotypeprio.terms = items.map((i) => ({
          term: { label: i.label, term_id: i.id },
        }))
      }
    "
  />
</template>
