<script setup lang="ts">
import VResizeDrawer from '@wdns/vuetify-resize-drawer'
import { ref } from 'vue'

/** Model with boolean that defines visibility. */
const showSheet = defineModel('showSheet', {
  type: Boolean,
  default: false,
})

/** Whether the drawer is pinned (otherwise, will close when outside is clicked); component state. */
const pinned = ref<boolean>(false)
</script>

<template>
  <v-resize-drawer
    v-model="showSheet"
    location="right"
    temporary
    :scrim="!pinned"
    resizable
    save-width
    touchless
    min-width="200px"
    max-width="80%"
    width-snapback
    handle-icon="mdi-drag"
    handle-position="bottom"
    storage-name="seqvars-details-drawer"
  >
    <template #prepend>
      <div class="text-right">
        <v-btn icon="" size="small" @click="pinned = !pinned">
          <v-icon
            :icon="pinned ? 'mdi-pin' : 'mdi-pin-outline'"
            :class="{ 'pin-icon-rotate': !pinned }"
          />
        </v-btn>
        <v-btn icon="" size="small" @click="showSheet = false">
          <v-icon icon="mdi-close" />
        </v-btn>
      </div>
    </template>

    <v-divider></v-divider>
  </v-resize-drawer>
</template>

<style scoped>
.pin-icon-rotate {
  transform: rotate(45deg);
}
</style>
