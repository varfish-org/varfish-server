<script setup lang="ts">
import { ref } from 'vue'

import { SeqvarsQueryPresetsPhenotypePrio } from '@varfish-org/varfish-api/lib'
import { copy } from '@/varfish/helpers'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
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

const setToPreset = (preset: SeqvarsQueryPresetsPhenotypePrio) => {
  model.value.phenotypepriopresets = preset.sodar_uuid
  model.value.phenotypeprio = copy(preset)
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
          :selected="preset.sodar_uuid === model.phenotypepriopresets"
          :modified="!matchesPhenotypePrioPreset(model.phenotypeprio, preset)"
          @click="() => setToPreset(preset)"
          @revert="() => setToPreset(preset)"
        >
          {{ preset.label }}
        </Item>
      </div>

      <Hr />
    </div>

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
          ><v-list-items v-bind="props">
            <TermItem
              :label="item.title"
              :term-id="item.value"
              class="term-list-item"
            />
          </v-list-items>
        </template>
      </v-autocomplete>
    </div>
  </CollapsibleGroup>
</template>

<style scoped>
.term-list-item {
  padding: 4px 16px;
  cursor: pointer;

  &:hover {
    background: #f5f5f5;
  }
}
</style>
