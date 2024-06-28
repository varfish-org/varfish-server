<script setup lang="ts">
const model = defineModel<boolean>({ default: false })
</script>

<template>
  <v-btn
    class="root ui-control-text"
    variant="outlined"
    rounded="sm"
    :aria-selected="model"
    @click="model = !model"
  >
    <slot />
  </v-btn>
</template>

<style scoped>
.root {
  padding: 5px 12px;
  height: fit-content;
  min-width: auto;
  color: black !important;
  text-transform: none;
  cursor: pointer;

  &:focus {
    outline: none;
  }

  &[aria-selected='true'] {
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
