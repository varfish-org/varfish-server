<script setup lang="ts">
import { SeqvarsPredefinedQuery } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import { matchesFrequencyPreset } from '@/seqvars/components/FrequencySelect/utils'
import { matchesGenotypePreset } from '@/seqvars/components/GenotypeSelect/utils'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import ModifiedIcon from '@/seqvars/components/ModifiedIcon.vue'
import { Query } from '@/seqvars/types'

const selectedIndex = defineModel<number | null>({ required: true })
const { predefinedQueries, queries } = defineProps<{
  predefinedQueries: SeqvarsPredefinedQuery[]
  queries: Query[]
}>()
defineEmits(['removeQuery'])

let count: number
</script>

<template>
  <CollapsibleGroup title="Results">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="(query, index) in queries"
        :key="index"
        :selected="index === selectedIndex"
        @click="selectedIndex = index"
      >
        <template #default>
          #{{ index + 1 }}
          {{
            predefinedQueries.find(
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
          <ModifiedIcon
            v-if="!matchesGenotypePreset || !matchesFrequencyPreset"
          />
          <ItemButton @click="$emit('removeQuery', index)"
            ><i-mdi-close-box-outline
          /></ItemButton>
        </template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
