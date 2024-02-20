<script setup lang="ts">
import { computed } from 'vue'
import { Seqvar, SeqvarImpl } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import UiToggleMaxButton from '@varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

/** The component's props. */
const props = defineProps<{
  /** The seqvar to display for. */
  seqvar?: Seqvar,
  /** Payload from row in seqvar result store. */
  // TODO: use proper type here
  resultRowPayload?: any
}>()

/** HGsVS description of SeqVar from result row. */
const seqvarHgvs = computed<string | undefined>(() => {
  if (!props.resultRowPayload) {
    return undefined
  } else {
    const arr = [props.resultRowPayload?.transcript_id]
    if (props.resultRowPayload?.symbol?.length) {
      arr.push(...['(', props.resultRowPayload?.symbol, ')'])
    }
    if (props.resultRowPayload?.hgvs_p?.length) {
      arr.push(
        ...[
          ':',
          props.resultRowPayload?.hgvs_p,
          ' (',
          props.resultRowPayload?.hgvs_c,
          ')',
        ],
      )
    } else {
      arr.push(...[':', props.resultRowPayload?.hgvs_c])
    }
    return arr.join('')
  }
})
</script>

<template>
  <v-row no-gutters class="flex-nowrap">
    <v-col cols="11" class="text-h4 flex-grow-0">
      Variant Details
      <template v-if="seqvarHgvs">
        <small class="font-italic">
          {{ seqvarHgvs }}
          [{{ seqvar?.userRepr }}]
        </small>
      </template>
      <template v-else>
        <small class="font-italic">
          {{ seqvar?.userRepr }}
        </small>
      </template>
    </v-col>
    <v-col cols="1" class="flex-shrink-0 text-right">
      <UiToggleMaxButton />
    </v-col>
  </v-row>
</template>
