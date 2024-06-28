<script setup lang="ts">
const props = withDefaults(defineProps<{ selected?: boolean }>(), {
  selected: false,
})
</script>

<template>
  <button type="button" class="root" :aria-selected="props.selected">
    <slot />
  </button>
</template>

<style scoped>
.root {
  outline: none;
  padding-top: 2px;
  padding-bottom: 6px;
  padding-left: 4px;
  padding-right: 4px;
  width: 100%;
  box-sizing: border-box;
  text-align: start;

  &[aria-selected='true'] {
    background: rgb(var(--v-theme-selected-bg));
  }

  &:hover {
    background: rgb(var(--v-theme-hover-bg));
  }
}
</style>
