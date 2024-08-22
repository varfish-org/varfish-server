<script setup lang="ts">
import SeqvarDetailsInner from './SeqvarDetailsInner.vue'

/** This component's  */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** Project UUID. */
  projectUuid: string
  /** UUID of the result row to display. */
  resultRowUuid: string
  /** Identifier of the selected section. */
  selectedSection?: string
  /** Hide back button */
  hideBackButton?: boolean
}>()
</script>

<template>
  <v-app>
    <v-main>
      <v-container fluid class="pa-0">
        <SeqvarDetailsInner
          :project-uuid="projectUuid"
          :result-row-uuid="resultRowUuid"
          :selected-section="selectedSection"
          :hide-back-button="hideBackButton"
        />
      </v-container>
    </v-main>
  </v-app>
</template>
