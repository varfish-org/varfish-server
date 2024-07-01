<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'
import { QuickPresets } from './types'

const { presets } = defineProps<{ presets: QuickPresets[] }>()
defineEmits(['addQuery'])
</script>

<template>
  <CollapsibleGroup title="Presets">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item v-for="preset in presets" :key="preset.label">
        <template #default>{{ preset.label }}</template>
        <template #extra
          ><ItemButton @click="$emit('addQuery', preset.label)"
            ><i-bi-filter style="font-size: 0.9em" /></ItemButton
        ></template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
