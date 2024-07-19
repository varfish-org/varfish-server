<script setup lang="ts">
import type { CSSProperties } from 'vue'
const { style } = defineProps<{ style?: CSSProperties }>()
</script>
<template>
  <span
    :style="{
      'font-size': '12px',
      color: 'rgb(var(--v-theme-ui-aux-text))',
      ...style,
    }"
    ><slot></slot
  ></span>
</template>
