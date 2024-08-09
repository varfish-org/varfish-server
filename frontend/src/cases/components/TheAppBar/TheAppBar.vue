<script setup lang="ts">
import { Icon } from '@iconify/vue'
import VarFishLogo from '@/varfish/components/VarFishLogo.vue'

/** The props used in this component. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to show the left panel button. */
    showLeftPanelButton?: boolean
    /** Whether to show the right panel button. */
    showRightPanelButton?: boolean
    /** The string to display as the title. */
    title?: string
    /** Whether to display the loading indicator. */
    loading?: boolean
  }>(),
  { title: 'VarFish', loading: false },
)

/** Whether to show the left panel button. */
const showLeftPanel = defineModel('showLeftPanel', {
  type: Boolean,
  default: true,
})

/** Whether to show the right panel button. */
const showRightPanel = defineModel('showRightPanel', {
  type: Boolean,
  default: true,
})
</script>

<template>
  <v-app-bar color="primary" density="compact">
    <template v-if="showLeftPanelButton" #prepend>
      <v-btn
        rounded="xl"
        icon
        :title="`${showLeftPanel ? 'Hide' : 'Show'} the left panel.`"
        @click="showLeftPanel = !showLeftPanel"
      >
        <Icon
          :icon="`material-symbols:left-panel-${showLeftPanel ? 'close' : 'open'}`"
          style="font-size: 24px"
        ></Icon>
      </v-btn>
    </template>

    <v-app-bar-title>
      <slot name="title">
        <div class="d-flex">
          <template v-if="loading">
            <v-progress-circular
              indeterminate
              color="white"
            ></v-progress-circular>
          </template>
          <template v-else>
            <VarFishLogo />
          </template>
          <div class="pl-2">{{ title }}</div>
        </div>
      </slot>
    </v-app-bar-title>

    <template v-if="showRightPanelButton" #append>
      <slot name="append"> </slot>
      <v-btn
        rounded="xl"
        icon
        :title="`${showRightPanel ? 'Hide' : 'Show'} the right panel.`"
        @click="showRightPanel = !showRightPanel"
      >
        <Icon
          :icon="`material-symbols:right-panel-${showRightPanel ? 'close' : 'open'}`"
          style="font-size: 24px"
        ></Icon>
      </v-btn>
    </template>
  </v-app-bar>
</template>
