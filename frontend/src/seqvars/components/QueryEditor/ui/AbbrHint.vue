<script setup lang="ts">
/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
    /** The hint, if any. */
    hint?: string
  }>(),
  {
    hintsEnabled: false,
  },
)
</script>

<template>
  <template v-if="hintsEnabled && !!hint">
    <abbr class="abbr-hint" :title="hint">
      <slot></slot>
    </abbr>
  </template>
  <template v-else>
    <slot></slot>
  </template>
</template>

<style scope>
.abbr-hint {
  text-decoration: underline dotted blue !important;
}
</style>
