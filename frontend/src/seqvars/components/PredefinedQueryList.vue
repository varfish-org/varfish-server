<script setup lang="ts">
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import { Query } from '@/seqvars/types'
import { matchesPredefinedQuery } from './utils'

const { presets, query } = defineProps<{
  presets: SeqvarsQueryPresetsSetVersionDetails
  query: Query | null
}>()
const selectedId = defineModel<string | undefined>('selectedId', {
  required: true,
})

defineEmits<{ addQuery: [preset: SeqvarsPredefinedQuery] }>()
</script>

<template>
  <CollapsibleGroup title="Presets">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="pq in presets.seqvarspredefinedquery_set"
        :key="pq.sodar_uuid"
        :selected="pq.sodar_uuid === selectedId"
        :modified="!!query && !matchesPredefinedQuery(presets, query, pq)"
        @click="selectedId = pq.sodar_uuid"
        @revert="selectedId = pq.sodar_uuid"
      >
        <template #default>{{ pq.label }}</template>
        <template #extra
          ><ItemButton @click="$emit('addQuery', pq)"
            ><i-bi-filter style="font-size: 0.9em" /></ItemButton
        ></template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
