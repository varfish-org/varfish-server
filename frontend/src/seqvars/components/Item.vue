<script setup lang="ts">
const props = withDefaults(defineProps<{ selected?: boolean }>(), {
  selected: false,
})
</script>

<template>
  <div class="root" :aria-selected="props.selected">
    <button type="button" class="item">
      <slot />
    </button>
    <div style="display: flex; align-items: center">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<style scoped>
.root {
  display: flex;
  justify-content: space-between;

  &[aria-selected='true'] {
    background: rgb(var(--v-theme-selected-bg));
  }

  &:hover {
    background: rgb(var(--v-theme-hover-bg));
  }
}

button.item {
  padding: 2px;
  padding-bottom: 3px;
  width: 100%;
  box-sizing: border-box;

  text-align: start;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  &:not(:focus-visible) {
    outline: none;
  }
}
</style>
