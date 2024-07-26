<script lang="ts">
import {
  HpoOmim,
  HpoTerm,
  VigunoClient,
} from '@bihealth/reev-frontend-lib/api/viguno'

async function fetchHPO(query: string) {
  const vigunoClient = new VigunoClient('/proxy/varfish/viguno')
  const queryArg = encodeURIComponent(query)
  let results: (HpoTerm | HpoOmim)[]
  if (query.startsWith('HP:')) {
    results = (await vigunoClient.resolveHpoTermById(queryArg)).result
  } else if (query.startsWith('OMIM:')) {
    results = (await vigunoClient.resolveOmimTermById(queryArg)).result
  } else {
    let [{ result: hpoResults }, { result: omimResults }] = await Promise.all([
      vigunoClient.queryHpoTermsByName(queryArg),
      vigunoClient.queryOmimTermsByName(queryArg),
    ])
    if (hpoResults.length < 2 && omimResults.length > 2) {
      omimResults = omimResults.slice(0, 2 + hpoResults.length)
    } else if (omimResults.length < 2 && hpoResults.length > 2) {
      hpoResults = hpoResults.slice(0, 2 + omimResults.length)
    } else {
      hpoResults = hpoResults.slice(0, 2)
      omimResults = omimResults.slice(0, 2)
    }
    results = [...hpoResults, ...omimResults]
  }

  return results.map(({ name, ...item }) => {
    const id = 'termId' in item ? item.termId : item.omimId
    return { label: name, term_id: id }
  })
}
</script>

<script setup lang="ts">
import { ref } from 'vue'

import { Query } from '@/seqvars/types'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import SelectBox, { type ItemData } from './ui/SelectBox.vue'

const ITEMS = {
  phenix: 'Phenix',
  phive: 'Phive',
  'exomiser.hiphive_human': 'HiPhive (human only)',
  'exomiser.hiphive_humanmouse': 'HiPhive (human+mouse)',
  'exomiser.hiphive_humanmousefishppi': 'HiPhive (human, mouse, fish, PPI)',
}

const model = defineModel<Query>({ required: true })

const items = ref<ItemData[]>([])

async function onSearch(query: string) {
  items.value = (await fetchHPO(query)).map((i) => ({
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

  <CollapsibleGroup title="Phenotype similarity algorithm">
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
      (items) => {
        model.phenotypeprio.terms = items.map((i) => ({
          term: { label: i.label, term_id: i.id },
        }))
      }
    "
  />
</template>
