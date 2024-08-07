<script setup lang="ts">
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'
import { getQueryLabel } from '@/seqvars/utils'

import { matchesPredefinedQuery } from './groups'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import ItemButton from './ui/ItemButton.vue'

const selectedIndex = defineModel<number | null>('selectedIndex', {
  required: true,
})
const { presetDetails, queries } = defineProps<{
  presetDetails: SeqvarsQueryPresetsSetVersionDetails
  queries: Query[]
}>()
defineEmits<{ remove: [index: number]; revert: [] }>()
</script>

<template>
  <CollapsibleGroup
    title="Results"
    :summary="
      selectedIndex
        ? `#${selectedIndex + 1} ${getQueryLabel({ presetDetails, queries, index: selectedIndex })}`
        : undefined
    "
  >
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="(query, index) in queries"
        :key="index"
        :selected="index === selectedIndex"
        :modified="
          !!query &&
          !matchesPredefinedQuery(
            presetDetails,
            presetDetails.seqvarspredefinedquery_set.find(
              (pq) => pq.sodar_uuid === query.predefinedquery,
            )!,
            query,
          )
        "
        @click="selectedIndex = index"
        @revert="$emit('revert')"
      >
        <template #default>
          #{{ index + 1 }}
          {{ getQueryLabel({ presetDetails, queries, index }) }}
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
