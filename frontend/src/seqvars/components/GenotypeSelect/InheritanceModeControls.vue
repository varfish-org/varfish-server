<script setup lang="ts">
import CheckButton from './CheckButton.vue'
import { InheritanceMode, InheritanceModeSet } from './types'

const items = [
  [InheritanceMode.WILD_TYPE, '0/0'],
  [InheritanceMode.HET_ALT, '1/0'],
  [InheritanceMode.HOM_ALT, '1/1'],
] satisfies [InheritanceMode, string][]

defineEmits(['update:modelValue'])
const model = defineModel<InheritanceModeSet>({ default: new Set() })
</script>

<template>
  <div style="display: flex; gap: 8px">
    <div style="display: flex; gap: 4px">
      <CheckButton
        :model-value="model.size == 3"
        @update:model-value="
          $emit('update:modelValue', new Set(model.size == 3 ? [] : items))
        "
        >any</CheckButton
      >
      <CheckButton
        v-for="[key, label] in items"
        :key="key"
        :model-value="model.has(key)"
        @update:model-value="
          $emit(
            'update:modelValue',
            new Set(
              model.has(key)
                ? [...model].filter((i) => i != key)
                : [...model, key],
            ),
          )
        "
        >{{ label }}</CheckButton
      >
    </div>
    <CheckButton
      :model-value="model.size == 0"
      @update:model-value="
        $emit('update:modelValue', new Set(model.size == 0 ? items : []))
      "
      >no call</CheckButton
    >
  </div>
</template>
