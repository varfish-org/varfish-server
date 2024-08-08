<script setup lang="ts">
import VResizeDrawer from '@wdns/vuetify-resize-drawer'

/** Whether to show the drawer on the left side. */
const drawerShown = defineModel<boolean>('drawerShown', {
  default: true,
})
</script>

<template>
  <v-resize-drawer
    v-model="drawerShown"
    location="left"
    resizable
    save-width
    touchless
    min-width="200px"
    max-width="50%"
    width-snapback
    handle-icon="mdi-drag"
    handle-position="bottom"
    storage-name="seqvars-query-editor-drawer"
  >
    <slot></slot>
  </v-resize-drawer>
</template>
