<script setup lang="ts">
/**
 * This component allows to edit the phenotype-based priorization settings.
 *
 * The component is passed the current seqvar query for editing and updates
 * it via TanStack Query.
 */
import {
  SeqvarsQueryDetails,
  SeqvarsQuerySettingsVariantPrioRequest,
} from '@varfish-org/varfish-api/lib'
import { ref } from 'vue'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'

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

/** Variant priorization services. */
const SERVICES = [
  {
    name: 'cadd',
    version: '1.6',
  },
  {
    name: 'mutationtaster',
    version: '2021',
  },
]

/** Whether or not the details are open. */
const detailsOpen = ref<boolean>(false)

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.modelValue`. */
const applyMutation = async (
  variantprio: SeqvarsQuerySettingsVariantPrioRequest,
) => {
  const newData = {
    ...props.modelValue,
    settings: {
      ...props.modelValue.settings,
      variantprio: {
        ...props.modelValue.settings.variantprio,
        ...variantprio,
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
    :model-value="modelValue.settings.variantprio.variant_prio_enabled"
    density="compact"
    label="Enable pathogenicity-based priorization"
    color="primary"
    hide-details
    class="my-2"
    @update:model-value="
      async () =>
        await applyMutation({
          variant_prio_enabled:
            !modelValue.settings.variantprio.variant_prio_enabled,
        })
    "
  />

  <CollapsibleGroup
    v-model:is-open="detailsOpen"
    v-model="collapsibleGroupOpen"
    title="Pathogenicity scores priorization"
    storage-name="pathogenicity-scores"
  >
    <template #summary>
      {{ modelValue.settings.variantprio.services?.[0]?.name }}
    </template>

    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
        <div
          role="listbox"
          style="width: 100%; display: flex; flex-direction: column"
        >
          <Item
            v-for="item in SERVICES"
            :key="item.name"
            :selected="
              modelValue.settings.variantprio.services?.some(
                (s) => s.name == item.name,
              )
            "
            @click="async () => await applyMutation({ services: [item] })"
          >
            {{ item.name }}
          </Item>
        </div>
      </div>
    </template>
  </CollapsibleGroup>
</template>
