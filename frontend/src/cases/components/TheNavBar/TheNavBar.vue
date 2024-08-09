<script setup lang="ts">
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether the navigation bar is hidden. */
    navbarShown: boolean
  }>(),
  {
    navbarShown: true,
  },
)
</script>

<template>
  <v-navigation-drawer permanent color="grey-lighten-3" :rail="!navbarShown">
    <v-list density="compact">
      <slot></slot>
    </v-list>
  </v-navigation-drawer>
</template>
