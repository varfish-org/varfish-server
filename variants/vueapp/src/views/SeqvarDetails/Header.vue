<script setup lang="ts">
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** Seqvar to display the header for. */
  seqvar?: Seqvar
  /** An optional HGVS string to display for the variant. */
  hgvsRepr?: string
}>()
</script>

<template>
  <div>
    <h4>
      Variant Details
    </h4>
    <div class="text-caption">
      <span v-if="seqvar === undefined">
        <v-progress-circular indeterminate size="20" />
        (Loading Variant)
      </span>
      <span v-else>
        <template v-if="hgvsRepr === undefined">
          {{ props.seqvar!.userRepr }}
        </template>
        <template v-else>
          {{ hgvsRepr }}
          <span>
            ({{ props.seqvar!.userRepr }})
          </span>
        </template>
      </span>
    </div>
  </div>
</template>
