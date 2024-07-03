<script setup lang="ts">
const props = withDefaults(defineProps<{
  /** Whether the navigation bar is hidden. */
  navbarHidden: boolean
}>(), {
  navbarHidden: false
})
</script>

<template>
  <v-navigation-drawer floating permanent color="grey-lighten-3" :rail="navbarHidden">
    <v-list density="compact">
      <slot></slot>
    </v-list>
  </v-navigation-drawer>
</template>
