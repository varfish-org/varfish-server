<script setup lang="ts">
/** Whether to show the drawer on the left side. */
const drawerShown = defineModel<boolean>('drawerShown', {
  default: true,
})
</script>

<template>
  <v-navigation-drawer
    :rail="!drawerShown"
    location="left"
    touchless
    color="grey-lighten-3"
    width="350"
  >
    <slot></slot>
  </v-navigation-drawer>
</template>
