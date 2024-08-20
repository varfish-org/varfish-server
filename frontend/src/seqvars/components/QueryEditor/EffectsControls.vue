<script setup lang="ts">
import {
  SeqvarsTranscriptTypeChoiceList,
  SeqvarsVariantConsequenceChoiceList,
  SeqvarsVariantTypeChoiceList,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { Query } from '@/seqvars/types'

import { toggleArrayElement } from '../utils'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const VARIANT_TYPES = {
  snv: 'SNV',
  indel: 'indel',
  mnv: 'MNV',
  complex_substitution: 'complex substitution',
} satisfies Record<SeqvarsVariantTypeChoiceList[number], string>

const TRANSCRIPT_TYPES = {
  coding: 'coding',
  non_coding: 'non-coding',
} satisfies Record<SeqvarsTranscriptTypeChoiceList[number], string>

const CUSTOMIZATION = {
  Coding: {
    transcript_ablation: 'transcript ablation',
    transcript_amplification: 'transcript amplification',
    exon_loss_variant: 'exon loss',
    frameshift_variant: 'frameshift',
    start_lost: 'start lost',
    stop_gained: 'stop gained',
    stop_lost: 'stop lost',
    disruptive_inframe_insertion: 'disruptive inframe insertion',
    disruptive_inframe_deletion: 'disruptive inframe deletion',
    conservative_inframe_insertion: 'conservative inframe insertion',
    conservative_inframe_deletion: 'conservative inframe deletion',
    inframe_indel: 'in-frame indel',
    missense_variant: 'missense',
    start_retained_variant: 'start retained',
    stop_retained_variant: 'stop retained',
    synonymous_variant: 'synonymous',
    coding_sequence_variant: 'coding',
  },
  'Off-Exome': {
    upstream_gene_variant: 'upstream',
    downstream_gene_variant: 'downstream',
    intron_variant: 'intronic',
    intergenic_variant: 'intergenic',
  },
  'Non-coding': {
    '5_prime_UTR_exon_variant': "5' UTR exon",
    '5_prime_UTR_intron_variant': "5' UTR intron",
    '3_prime_UTR_exon_variant': "3' UTR exon",
    '3_prime_UTR_intron_variant': "3' UTR intronic",
    non_coding_transcript_exon_variant: 'non-coding exonic',
    non_coding_transcript_intron_variant: 'non-coding intronic',
  },
  Splicing: {
    splice_acceptor_variant: 'splice acceptor (-1, -2)',
    splice_donor_variant: 'splice donor (+1, +2)',
    splice_donor_5th_base_variant: 'splice donor 5th-base',
    splice_region_variant: 'splice region (-3, +3, ..., +8)',
    splice_donor_region_variant: 'splice donor region',
    splice_polypyrimidine_tract_variant: 'splice polypyrimidine tract',
  },
} satisfies Record<
  string,
  Partial<Record<SeqvarsVariantConsequenceChoiceList[number], string>>
>

const model = defineModel<Query>({ required: true })

const detailsOpen = ref<boolean>(false)

const maxExonDistance = computed<number | null | undefined>({
  get: () => model.value.consequence.max_distance_to_exon,
  set(value: string | number | null | undefined) {
    if (value === null || value === undefined || value === '') {
      model.value.consequence.max_distance_to_exon = null
    } else {
      model.value.consequence.max_distance_to_exon = parseInt(`${value}`)
    }
  },
})
</script>

<template>
  <div class="d-flex flex-column ga-2">
    <div class="mt-2">
      <div class="text-body-2">Max distance to next exon</div>
      <v-row class="align-center" justify="start" no-gutters>
        <!-- Button Group -->
        <v-col cols="auto" class="pt-0">
          <v-btn-group density="compact" color="primary" divided>
            <v-btn
              class="px-0"
              :variant="maxExonDistance === null ? 'flat' : 'outlined'"
              @click="maxExonDistance = null"
            >
              any
            </v-btn>
            <v-btn
              class="px-0"
              :variant="maxExonDistance == 20 ? 'flat' : 'outlined'"
              @click="maxExonDistance = 20"
            >
              20
            </v-btn>
            <v-btn
              class="px-0"
              :variant="maxExonDistance == 100 ? 'flat' : 'outlined'"
              @click="maxExonDistance = 100"
            >
              100
            </v-btn>
          </v-btn-group>
        </v-col>

        <!-- Text Field -->
        <v-col cols="auto" class="pl-3 pt-0">
          <v-text-field
            v-model="maxExonDistance"
            density="compact"
            variant="outlined"
            hide-details
            class="exon-distance-text-field"
          />
        </v-col>
      </v-row>
    </div>

    <div>
      <div class="text-body-2">Variant Type</div>
      <v-checkbox
        v-for="(label, key) in VARIANT_TYPES"
        :key="key"
        :label="label"
        :hide-details="true"
        color="primary"
        density="compact"
        :model-value="model.consequence.variant_types?.includes(key)"
        @update:model-value="
          toggleArrayElement(model.consequence.variant_types, key)
        "
      />
    </div>

    <div>
      <div class="text-body-2">Transcript Type</div>
      <v-checkbox
        v-for="(label, key) in TRANSCRIPT_TYPES"
        :key="key"
        :label="label"
        :hide-details="true"
        color="primary"
        density="compact"
        :model-value="model.consequence.transcript_types?.includes(key)"
        @update:model-value="
          toggleArrayElement(model.consequence.transcript_types, key)
        "
      />
    </div>

    <CollapsibleGroup v-model:is-open="detailsOpen" title="Customize effects">
      <div style="display: flex; flex-direction: column; gap: 8px">
        <div v-for="(fields, title) in CUSTOMIZATION">
          <div class="text-body-2">{{ title }}</div>

          <v-checkbox
            v-for="(label, key) in fields"
            :key="key"
            :label="label"
            color="primary"
            :hide-details="true"
            density="compact"
            :model-value="model.consequence.variant_consequences?.includes(key)"
            @update:model-value="
              toggleArrayElement(model.consequence.variant_consequences, key)
            "
          />
        </div>
      </div>
    </CollapsibleGroup>
  </div>
</template>

<style>
.exon-distance-text-field .v-field__input {
  min-height: 24px !important;
  padding-block-start: 6px !important;
  padding-block-end: 6px !important;
  padding-bottom: 6px !important;
  padding-top: 6px !important;
  padding-left: 6px !important;
  padding-right: 6px !important;
  max-width: 60px;
}
</style>
