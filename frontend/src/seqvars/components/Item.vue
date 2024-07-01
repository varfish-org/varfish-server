<script setup lang="ts">
const props = withDefaults(defineProps<{ selected?: boolean }>(), {
  selected: false,
})
</script>

<template>
  <div class="root">
    <button type="button" class="item" :aria-selected="props.selected">
      <slot />
    </button>
    <div>
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
  padding-top: 2px;
  padding-bottom: 6px;
  padding-left: 4px;
  padding-right: 4px;
  width: 100%;
  box-sizing: border-box;

  text-align: start;

  &:not(:focus-visible) {
    outline: none;
  }
}
</style>
