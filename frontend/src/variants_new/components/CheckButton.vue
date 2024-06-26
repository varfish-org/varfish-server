<script setup lang="ts">
const model = defineModel<boolean>({ default: false })
</script>

<template>
  <button
    type="button"
    class="root ui-control-text"
    :aria-selected="JSON.stringify(model)"
    @click="model = !model"
  >
    <slot />
  </button>
</template>

<style scoped>
.root {
  border-radius: 4px;
  border: 1px solid black;
  padding: 5px 12px;
  height: fit-content;
  cursor: pointer;

  &:focus {
    outline: none;
  }

  &[aria-selected='true'] {
    border-color: #0f6cbd;
    background: #f3f9ff;
  }

  &:hover {
    background: rgb(var(--v-theme-hover-bg));
  }
}
</style>
