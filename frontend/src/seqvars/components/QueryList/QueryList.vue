<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import type { Query } from './types'

const { queries } = defineProps<{ queries: Query[] }>()
defineEmits(['removeQuery'])
</script>

<template>
  <CollapsibleGroup title="Results">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item v-for="(query, index) in queries" :key="query.label">
        <template #default>
          {{ query.label }}
        </template>
        <template #extra>
          <ItemButton @click="$emit('removeQuery', index)"
            ><i-mdi-close-box-outline
          /></ItemButton>
        </template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
