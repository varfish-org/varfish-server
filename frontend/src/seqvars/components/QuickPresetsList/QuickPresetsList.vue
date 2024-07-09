<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'

import { QUICK_PRESETS } from './constants'
import { QuickPreset } from './types'

const { value } = defineProps<{ value?: QuickPreset }>()

defineEmits<{
  addQuery: [preset: QuickPreset]
  'update:value': [preset: QuickPreset]
}>()
</script>

<template>
  <CollapsibleGroup title="Presets">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="preset in QUICK_PRESETS"
        :key="preset.label"
        :selected="value?.label == preset.label"
        @click="$emit('update:value', preset)"
      >
        <template #default>{{ preset.label }}</template>
        <template #extra
          ><ItemButton
            :aria-label="`Create query based on ${preset.label}`"
            @click="$emit('addQuery', preset)"
            ><i-bi-filter style="font-size: 0.9em" /></ItemButton
        ></template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
