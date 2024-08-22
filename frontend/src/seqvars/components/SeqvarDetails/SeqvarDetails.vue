<script setup lang="ts">
import VResizeDrawer from '@wdns/vuetify-resize-drawer'

import SeqvarDetails from '@/variants/views/SeqvarDetails/SeqvarDetails.vue'

/** Model with boolean that defines visibility. */
const showSheet = defineModel('showSheet', {
  type: Boolean,
  default: false,
})

const props = defineProps<{
  /** The project UUID. */
  projectUuid: string
  resultRowUuid: string
  selectedSection?: string
}>()
</script>

<template>
  <v-resize-drawer
    v-model="showSheet"
    location="right"
    temporary
    :scrim="false"
    :resizable="true"
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
        <!-- TODO: model not updated if closed via scrim click (bug in VNavigationDrawer)-->
        <!-- <v-btn icon="" size="small" @click="pinned = !pinned">
          <v-icon
            :icon="pinned ? 'mdi-pin' : 'mdi-pin-outline'"
            :class="{ 'pin-icon-rotate': !pinned }"
          />
        </v-btn> -->
        <v-btn icon="mdi-close" size="small" @click="showSheet = false" />
      </div>
    </template>
    <v-divider></v-divider>
    <SeqvarDetails
      :project-uuid="props.projectUuid"
      :result-row-uuid="props.resultRowUuid"
      :selected-section="props.selectedSection"
      :hide-back-button="true"
    />
  </v-resize-drawer>
</template>

<style scoped>
.pin-icon-rotate {
  transform: rotate(45deg);
}
</style>
