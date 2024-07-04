<script setup lang="ts">
import type { CSSProperties } from 'vue'

const props = defineProps<{ style?: CSSProperties; type?: 'text' | 'number' }>()
const model = defineModel<string | number>()
</script>

<template>
  <div class="root" :style="props.style">
    <input v-model="model" :type="props.type ?? 'text'" />
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
