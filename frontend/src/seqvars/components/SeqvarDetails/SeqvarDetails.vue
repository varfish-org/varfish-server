<script setup lang="ts">
import { Icon } from '@iconify/vue'
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
    location="right"
    temporary
    :scrim="!pinned"
    v-model="showSheet"
    resizable
    save-width
    touchless
    min-width="200px"
    handle-icon="mdi-drag"
    handle-position="bottom"
  >
    <template v-slot:prepend>
      <div class="text-right">
        <v-btn icon="" @click="pinned = !pinned" size="small">
          <v-icon
            :icon="pinned ? 'mdi-pin' : 'mdi-pin-outline'"
            :class="{ 'pin-icon-rotate': !pinned }"
          />
        </v-btn>
        <v-btn icon="" @click="showSheet = false" size="small">
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
