<script setup lang="ts">
import { computed } from 'vue'

import CheckButton from './CheckButton.vue'
import { InheritanceMode, InheritanceModeSet } from './types'

const ANY_ITEMS_WITH_LABELS = [
  [InheritanceMode.WILD_TYPE, '0/0'],
  [InheritanceMode.HET_ALT, '1/0'],
  [InheritanceMode.HOM_ALT, '1/1'],
] satisfies [InheritanceMode, string][]

const emit = defineEmits(['update:modelValue'])
const model = defineModel<InheritanceModeSet>({ default: new Set() })

const isAnySelected = computed(() =>
  ANY_ITEMS_WITH_LABELS.every(([item]) => model.value.has(item)),
)

const toggleModel = (key: InheritanceMode) => {
  const newModel = new Set(model.value)
  if (model.value.has(key)) {
    newModel.delete(key)
  } else {
    newModel.add(key)
  }
  emit('update:modelValue', newModel)
}
</script>

<template>
  <div style="display: flex; gap: 8px">
    <div style="display: flex; gap: 4px">
      <CheckButton
        :model-value="isAnySelected"
        @update:model-value="
          $emit(
            'update:modelValue',
            new Set(
              isAnySelected
                ? [...model].filter(
                    (i) => !ANY_ITEMS_WITH_LABELS.some(([item]) => item === i),
                  )
                : [...model, ...ANY_ITEMS_WITH_LABELS.map(([item]) => item)],
            ),
          )
        "
        >any</CheckButton
      >

      <CheckButton
        v-for="[key, label] in ANY_ITEMS_WITH_LABELS"
        :key="key"
        :model-value="model.has(key)"
        @update:model-value="toggleModel(key)"
        >{{ label }}</CheckButton
      >
    </div>

    <CheckButton
      :model-value="model.has(InheritanceMode.NO_CALL)"
      @update:model-value="toggleModel(InheritanceMode.NO_CALL)"
      >no call</CheckButton
    >
  </div>
</template>
