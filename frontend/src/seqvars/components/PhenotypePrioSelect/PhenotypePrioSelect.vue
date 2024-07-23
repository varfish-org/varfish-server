<script setup lang="ts">
import { ref } from 'vue'

import { SeqvarsQueryPresetsPhenotypePrio } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '../ui/CollapsibleGroup.vue'
import Item from '../ui/Item.vue'
import PresetSelect from '../ui/PresetSelect.vue'
import { Query } from '@/seqvars/types'

import TermItem from './TermItem.vue'
import { fetchHPO, matchesPhenotypePrioPreset } from './utils'

const ITEMS = {
  phenix: 'Phenix',
  phive: 'Phive',
  'exomiser.hiphive_human': 'HiPhive (human only)',
  'exomiser.hiphive_humanmouse': 'HiPhive (human+mouse)',
  'exomiser.hiphive_humanmousefishppi': 'HiPhive (human, mouse, fish, PPI)',
}

const model = defineModel<Query>({ required: true })

const { presets } = defineProps<{
  presets: SeqvarsQueryPresetsPhenotypePrio[]
}>()

const items = ref<Record<'title' | 'value', string>[]>([])

async function onSearch(query: string) {
  items.value = (await fetchHPO(query)).map((i) => ({
    title: i.label,
    value: i.term_id,
  }))
}
</script>

<template>
  <CollapsibleGroup title="Phenotype Priorization">
    <PresetSelect
      v-model="model"
      :presets="presets"
      preset-id-field="phenotypepriopresets"
      settings-field="phenotypeprio"
      :matcher="matchesPhenotypePrioPreset"
    />

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

    <div
      style="
        margin-top: 4px;
        border: 1px solid #0003;
        padding: 4px 8px;
        display: flex;
        flex-direction: column;
        gap: 4px;
      "
    >
      <div
        v-for="({ term }, index) in model.phenotypeprio.terms"
        style="
          padding: 2px 6px;
          display: flex;
          flex-direction: row;
          justify-content: space-between;
          align-items: center;
          color: #595959;
          background: #f5f5f5;
        "
      >
        <TermItem :label="term.label" :term-id="term.term_id" />
        <button
          type="button"
          style="height: fit-content; padding: 4px"
          @click="model.phenotypeprio.terms?.splice(index, 1)"
        >
          <i-mdi-close />
        </button>
      </div>
      <v-autocomplete
        :items="items"
        :model-value="
          model.phenotypeprio.terms?.map(({ term }) => term.term_id)
        "
        label="Type to search HPO terms"
        density="compact"
        no-filter
        multiple
        hide-details
        hide-selected
        @update:model-value="
          (ids: string[]) => {
            model.phenotypeprio.terms = ids.map((id) => ({
              term: {
                term_id: id,
                label: items.find((i) => i.value == id)?.title ?? null,
              },
            }))
          }
        "
        @update:search="onSearch"
        ><template #selection="" />
        <template #item="{ item, props }"
          ><v-list-item v-bind="props" title="">
            <TermItem
              :label="item.title"
              :term-id="item.value"
              style="padding: 4px 16px; cursor: pointer"
            />
          </v-list-item>
        </template>
      </v-autocomplete>
    </div>
  </CollapsibleGroup>
</template>
