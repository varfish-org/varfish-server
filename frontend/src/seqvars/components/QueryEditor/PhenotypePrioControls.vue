<script setup lang="ts">
/**
 * This component allows to edit the phenotype-based priorization settings.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 */
import {
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsPhenotypePrioRequest,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import { queryHpoAndOmimTerms } from '../utils'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import SelectBox from './ui/SelectBox.vue'
import { type ItemData } from './ui/lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue: SeqvarsQueryDetails
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Mapping from prioritzer algorithm to label. */
const ALGOS = {
  // 'exomiser.phenix': 'Phenix',  // deprecated
  // 'exomiser.phive': 'Phive',  // deprecated
  'exomiser.hiphive_human': 'HiPhive (human only)',
  'exomiser.hiphive_humanmouse': 'HiPhive (human+mouse)',
  'exomiser.hiphive_humanmousefishppi': 'HiPhive (human, mouse, fish, PPI)',
}

/** Simplified access to the currently selected algorithm item. */
const selectedAlgo = computed<string | undefined>(() => {
  const [[_, value]] = Object.entries(ALGOS).filter(
    ([key, _]) =>
      key === props.modelValue.settings.phenotypeprio?.phenotype_prio_algorithm,
  )
  return value
})

/** Whether or not the details are open. */
const detailsOpen = ref<boolean>(false)

/** Selected terms from HPO. */
// TODO: migrate to proper common type
const items = ref<ItemData[]>([])

/** Handler for executing the search. */
const onSearch = async (query: string) => {
  items.value = (await queryHpoAndOmimTerms(query)).map((i) => ({
    id: i.term_id,
    label: i.label,
    sublabel: i.term_id,
  }))
}

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.modelValue`. */
const applyMutation = async (
  phenotypeprio: SeqvarsQuerySettingsPhenotypePrioRequest,
) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      phenotypeprio: {
        ...props.modelValue.settings.phenotypeprio,
        ...phenotypeprio,
      },
    },
  }

  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body: newData,
    path: {
      session: props.modelValue.session,
      query: props.modelValue.sodar_uuid,
    },
  })
}

/** Whether the recessive mode collapsible group is opend. */
const collapsibleGroupOpen = ref<boolean>(true)
</script>

<template>
  <v-checkbox
    :model-value="modelValue.settings.phenotypeprio.phenotype_prio_enabled"
    density="compact"
    label="Enable phenotype-based priorization"
    color="primary"
    hide-details
    class="my-2"
    @update:model-value="
      async () =>
        await applyMutation({
          phenotype_prio_enabled:
            !modelValue.settings.phenotypeprio.phenotype_prio_enabled,
        })
    "
  />

  <CollapsibleGroup
    v-model:is-open="detailsOpen"
    v-model="collapsibleGroupOpen"
    title="Phenotype similarity algorithm"
    storage-name="phenotype-similarity-algorithm"
  >
    <template #summary>
      {{ selectedAlgo }}
    </template>
    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
        <div
          role="listbox"
          style="width: 100%; display: flex; flex-direction: column"
        >
          <Item
            v-for="(label, key) in ALGOS"
            :key="key"
            :selected="
              modelValue.settings.phenotypeprio.phenotype_prio_algorithm == key
            "
            @click="
              async () => await applyMutation({ phenotype_prio_algorithm: key })
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
      (modelValue.settings.phenotypeprio.terms ?? []).map((t) => ({
        id: t.term.term_id,
        label: t.term.label,
        sublabel: t.term.term_id,
      }))
    "
    label="Type to search HPO terms"
    @update:search="onSearch"
    @update:model-value="
      async (items: ItemData[]) => {
        await applyMutation({
          terms: items.map((i) => ({
            term: { label: i.label, term_id: i.id },
          })),
        })
      }
    "
  />
</template>
