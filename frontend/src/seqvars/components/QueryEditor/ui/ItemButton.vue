<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether the button is disabled. */
    disabled?: boolean
  }>(),
  { disabled: false },
)
</script>

<template>
  <button :disabled="disabled" type="button"><slot></slot></button>
</template>

<style scoped>
button {
  padding: 0 6px;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;

  &:hover {
    background: #e3e3e380;
  }

  &:not(:focus-visible) {
    outline: none;
  }
}
</style>
