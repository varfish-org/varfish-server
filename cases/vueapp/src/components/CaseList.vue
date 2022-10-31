<script setup>
import {
  overlayShow,
  overlayMessage,
  connectTopRowControls,
} from '../common.js'
import CaseListHeader from './CaseListHeader.vue'
import CaseListContent from './CaseListContent.vue'
import Overlay from './Overlay.vue'

const props = defineProps({
  currentTab: String,
  presetSet: String, // if (currentTab === "query-presets")
})

connectTopRowControls()
</script>

<template>
  <div class="d-flex flex-column h-100">
    <CaseListHeader />

    <div
      class="varfish-overlay-wrap position-relative flex-grow-1 d-flex flex-column"
    >
      <CaseListContent
        :current-tab="props.currentTab"
        :preset-set="props.presetSet"
      />
      <Overlay v-if="overlayShow" :message="overlayMessage" />
    </div>
  </div>
</template>
