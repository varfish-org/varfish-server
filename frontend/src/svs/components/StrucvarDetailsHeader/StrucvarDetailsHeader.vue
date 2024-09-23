<script setup lang="ts">
import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

import UiToggleMaxButton from '@/varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

/** The component's props. */
const props = defineProps<{
  /** The strucvr to display for. */
  strucvar?: Strucvar
  /** Payload from row in strucvar result store. */
  // TODO: use proper type here
  resultRowPayload?: any
}>()
</script>

<template>
  <v-row no-gutters class="flex-nowrap">
    <v-col cols="11" class="text-h4 flex-grow-0">
      Structural Variant Details
      <small class="font-italic">
        {{ strucvar?.userRepr }}
      </small>
    </v-col>
    <v-col cols="1" class="flex-shrink-0 text-right">
      <UiToggleMaxButton />
    </v-col>
  </v-row>
</template>
