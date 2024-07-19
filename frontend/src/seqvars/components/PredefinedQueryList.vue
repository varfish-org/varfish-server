<script setup lang="ts">
import { SeqvarsPredefinedQuery } from '@varfish-org/varfish-api/lib'

import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Item from '@/seqvars/components/Item.vue'
import ItemButton from '@/seqvars/components/ItemButton.vue'

const { presets } = defineProps<{ presets: SeqvarsPredefinedQuery[] }>()
const selectedId = defineModel<string | undefined>({ required: true })

defineEmits<{ addQuery: [preset: SeqvarsPredefinedQuery] }>()
</script>

<template>
  <CollapsibleGroup title="Presets">
    <div style="width: 100%; display: flex; flex-direction: column">
      <Item
        v-for="preset in presets"
        :key="preset.sodar_uuid"
        :selected="preset.sodar_uuid === selectedId"
        @click="selectedId = preset.sodar_uuid"
      >
        <template #default>{{ preset.label }}</template>
        <template #extra
          ><ItemButton @click="$emit('addQuery', preset)"
            ><i-bi-filter style="font-size: 0.9em" /></ItemButton
        ></template>
      </Item>
    </div>
  </CollapsibleGroup>
</template>
