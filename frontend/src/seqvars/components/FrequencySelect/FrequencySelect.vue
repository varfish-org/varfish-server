<script setup lang="ts">
import CollapsibleGroup from '@/seqvars/components/CollapsibleGroup.vue'
import Hr from '@/seqvars/components/Hr.vue'
import Item from '@/seqvars/components/Item.vue'
import FrequencyControls from './FrequencyControls.vue'
import {
  FREQUENCY_PRESETS,
  FrequencyModel,
  FrequencyPresetKey,
} from './constants'
import { getFrequencyValueFromPreset } from './utils'

const model = defineModel<FrequencyModel>({ required: true })
</script>

<template>
  <CollapsibleGroup title="Frequency">
    <div style="width: 100%; display: flex; flex-direction: column; gap: 4px">
      <div
        role="listbox"
        style="width: 100%; display: flex; flex-direction: column"
      >
        <Item
          v-for="key in Object.keys(FREQUENCY_PRESETS)"
          :key="key"
          :selected="key === model.preset"
          @click="
            () =>
              (model = getFrequencyValueFromPreset(key as FrequencyPresetKey))
          "
          >{{ key }}</Item
        >
      </div>

      <Hr />

      <FrequencyControls v-model="model.values" />
    </div>
  </CollapsibleGroup>
</template>
