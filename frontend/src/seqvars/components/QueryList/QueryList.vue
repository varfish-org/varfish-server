<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import type { Query } from './types'

const { queries } = defineProps<{ queries: Query[] }>()
</script>

<template>
  <CollapsibleGroup title="Results">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item v-for="query in queries" :key="query.label">{{ query.label }}</Item>
    </div>
  </CollapsibleGroup>
</template>
