<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import { QuickPresets } from './types'

const { presets } = defineProps<{ presets: QuickPresets[] }>()
</script>

<template>
  <CollapsibleGroup title="Presets">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item v-for="preset in presets" :key="preset.label">{{
        preset.label
      }}</Item>
    </div>
  </CollapsibleGroup>
</template>
