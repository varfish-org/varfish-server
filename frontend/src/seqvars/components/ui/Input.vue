<script setup lang="ts">
import type { CSSProperties } from 'vue'

const props = defineProps<{
  id?: string
  style?: CSSProperties
  type?: 'text' | 'number'
  ariaLabel?: string
}>()
const model = defineModel<string | number | null>()
</script>

<template>
  <div class="root" :style="props.style">
    <input
      :id="props.id"
      v-model="model"
      :aria-label="props.ariaLabel"
      :type="props.type ?? 'text'"
    />
    <slot name="after"></slot>
  </div>
</template>

<style scoped>
.root {
  border: 1px solid #d1d1d1;
  border-bottom-color: #616161;
  border-radius: 4px;
  padding: 2px 4px;
  display: flex;
  flex-direction: row;

  &:focus-within {
    border-bottom-color: blue;
  }
}

.root input {
  width: 100%;

  &:focus {
    outline: none;
  }
}
</style>
