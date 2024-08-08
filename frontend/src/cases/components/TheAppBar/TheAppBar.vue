<script setup lang="ts">
import VarFishLogo from '@/varfish/components/VarFishLogo.vue'
import { Icon } from '@iconify/vue'

/** The props used in this component. */
const props = withDefaults(
  defineProps<{
    /** Whether to show the left pane button. */
    showLeftPanelButton?: boolean
    /** Whether to show the right pane button. */
    showRightPanelButton?: boolean
  }>(),
  {
    showLeftPanelButton: true,
    showRightPanelButton: false,
  },
)

/** Model manipulated with left panel hide/show button. */
const hideLeftPanel = defineModel('hideLeftPanel', {
  type: Boolean,
  default: true,
})

/** Model manipulated with right panel hide/show button. */
const hideRightPanel = defineModel('hideRightPanel', {
  type: Boolean,
  default: true,
})
</script>

<template>
  <v-app-bar color="primary" density="compact">
    <template #prepend v-if="showLeftPanelButton">
      <v-btn
        rounded="xl"
        icon=""
        :title="`${hideLeftPanel ? 'Show' : 'Hide'} the left pane.`"
        @click="hideLeftPanel = !hideLeftPanel"
      >
        <Icon
          :icon="`material-symbols:left-panel-${hideLeftPanel ? 'open' : 'close'}`"
          style="font-size: 24px"
        ></Icon>
      </v-btn>
    </template>

    <v-app-bar-title>
      <div class="d-flex">
        <VarFishLogo />
        <div class="pl-2">VarFish</div>
      </div>
    </v-app-bar-title>

    <template #append v-if="showRightPanelButton">
      <v-btn
        rounded="xl"
        icon=""
        :title="`${hideRightPanel ? 'Show' : 'Hide'} the right pane.`"
        @click="hideRightPanel = !hideRightPanel"
      >
        <Icon
          :icon="`material-symbols:right-panel-${hideRightPanel ? 'open' : 'close'}`"
          style="font-size: 24px"
        ></Icon>
      </v-btn>
    </template>
  </v-app-bar>
</template>
