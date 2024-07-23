<script setup lang="ts">
const model = defineModel<boolean>({ default: false })
</script>

<template>
  <v-btn
    class="root ui-control-text"
    variant="outlined"
    rounded="sm"
    :aria-checked="model"
    @click="model = !model"
  >
    <slot />
  </v-btn>
</template>

<style scoped>
.root {
  padding: 2px 4px;
  height: fit-content;
  min-width: auto;
  color: black !important;
  text-transform: none;
  cursor: pointer;

  &:focus {
    outline: none;
  }

  &[aria-checked='true'] {
    border-color: #0f6cbd;
    color: white !important;

    &,
    &:hover {
      background: #0f6cbd;
    }
  }

  &:hover {
    background: rgb(var(--v-theme-hover-bg));
  }
}
</style>
