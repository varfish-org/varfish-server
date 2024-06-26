<script setup lang="ts">
import CheckButton from './CheckButton.vue'

const items = ['0/0', '1/0', '1/1'] as const
defineEmits(['update:modelValue'])
const model = defineModel<Set<(typeof items)[number]>>({ default: new Set() })
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
        v-for="item in items"
        :key="item"
        :model-value="model.has(item)"
        @update:model-value="
          $emit(
            'update:modelValue',
            new Set(
              model.has(item)
                ? [...model].filter((i) => i != item)
                : [...model, item],
            ),
          )
        "
        >{{ item }}</CheckButton
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
