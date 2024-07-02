<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import { doesValueMatchGenotypePreset } from '@/seqvars/components/GenotypeSelect/utils'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import ModifiedIcon from '@/seqvars/components/ModifiedIcon.vue'
import type { Query } from './types'

const { queries, selectedIndex } = defineProps<{
  queries: Query[]
  selectedIndex: number | null
}>()
defineEmits(['select', 'removeQuery'])

let count: number
</script>

<template>
  <CollapsibleGroup title="Results">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="({ preset, value }, index) in queries"
        :key="index"
        :selected="index === selectedIndex"
        @click="$emit('select', index)"
      >
        <template #default>
          {{ preset.label }}
          <span
            :set="
              (count = queries
                .slice(0, index)
                .filter((q) => q.preset.label === preset.label).length)
            "
            >{{ count > 0 ? ` (${count})` : '' }}</span
          >
        </template>
        <template #extra>
          <ModifiedIcon
            v-if="
              !doesValueMatchGenotypePreset(value.genotype, preset.genotype)
            "
          />
          <ItemButton @click="$emit('removeQuery', index)"
            ><i-mdi-close-box-outline
          /></ItemButton>
        </template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
