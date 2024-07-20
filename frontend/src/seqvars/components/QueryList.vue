<script setup lang="ts">
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import { Query } from '@/seqvars/types'

import { matchesPredefinedQuery } from './utils'

const selectedIndex = defineModel<number | null>('selectedIndex', {
  required: true,
})
const { presets, queries } = defineProps<{
  presets: SeqvarsQueryPresetsSetVersionDetails
  queries: Query[]
}>()
defineEmits<{ remove: [index: number]; revert: [] }>()

let count: number
</script>

<template>
  <CollapsibleGroup title="Results">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="(query, index) in queries"
        :key="index"
        :selected="index === selectedIndex"
        :modified="
          !!query &&
          !matchesPredefinedQuery(
            presets,
            query,
            presets.seqvarspredefinedquery_set.find(
              (pq) => pq.sodar_uuid === query.predefinedquery,
            )!,
          )
        "
        @click="selectedIndex = index"
        @revert="$emit('revert')"
      >
        <template #default>
          #{{ index + 1 }}
          {{
            presets.seqvarspredefinedquery_set.find(
              (pq) => pq.sodar_uuid === query.predefinedquery,
            )?.label
          }}
          <span
            :set="
              (count = queries
                .slice(0, index)
                .filter(
                  (q) => q.predefinedquery === query.predefinedquery,
                ).length)
            "
            >{{ count > 0 ? ` (${count})` : '' }}</span
          >
        </template>
        <template #extra>
          <ItemButton @click="$emit('remove', index)"
            ><i-mdi-close-box-outline
          /></ItemButton>
        </template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
