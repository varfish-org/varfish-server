<script setup lang="ts">
import { computed } from 'vue'

import {
  SeqvarsQueryPresetsConsequence,
  SeqvarsTranscriptTypeChoiceList,
  SeqvarsVariantConsequenceChoiceList,
  SeqvarsVariantTypeChoiceList,
} from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'

import CheckButton from '../ui/CheckButton.vue'
import CollapsibleGroup from '../ui/CollapsibleGroup.vue'
import Input from '../ui/Input.vue'
import PresetSelect from '../ui/PresetSelect.vue'

import { matchesEffectsPreset } from './utils'

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
    disruptive_inframe_deletion: 'disruptive in-frame deletion',
    disruptive_inframe_insertion: 'disruptive in-frame insertion',
    // feature_truncation: 'feature truncation',
    // frameshift_elongation: 'frameshift elongation',
    frameshift_variant: 'frameshift variant',
    // inframe_deletion: 'inframe deletion',
    // inframe_insertion: 'inframe insertion',
    // internal_elongation: 'internal elongation',
    missense_variant: 'missense',
    // mnv: 'MNV',
    start_lost: 'start lost',
    stop_gained: 'stop gained',
    stop_retained_variant: 'stop retained',
    stop_lost: 'stop lost',
    // tandem_duplication: 'tandem duplication',
  },
  'Off-Exome': {
    downstream_gene_variant: 'downstream',
    intron_variant: 'intronic (coding transcript)',
    // intergenic: 'intergenic',
    upstream_gene_variant: 'upstream',
    // exon_loss: 'exon loss',
  },
  'Non-coding': {
    '3_prime_UTR_variant-exon_variant': "3' UTR exonic",
    '3_prime_UTR_variant-intron_variant': "3' UTR intronic",
    '5_prime_UTR_variant-exon_variant': "5' UTR exonic",
    '5_prime_UTR_variant-intron_variant': "5' UTR intronic",
    non_coding_transcript_exon_variant: 'non-coding exonic',
    non_coding_transcript_intron_variant: 'non-coding intronic',
  },
  Splicing: {
    splice_acceptor_variant: 'splice acceptor',
    splice_donor_variant: 'splice donor',
    splice_region_variant: 'splice region',
  },
  Structural: {
    // structural: 'structural ',
    // transcript_ablation: 'transcript ablation',
  },
} satisfies Record<
  string,
  Partial<Record<SeqvarsVariantConsequenceChoiceList[number], string>>
>

const model = defineModel<Query>({ required: true })

const { presets } = defineProps<{
  presets: SeqvarsQueryPresetsConsequence[]
}>()

const maxExonDistance = computed({
  get: () => model.value.consequence.max_distance_to_exon,
  set(value) {
    model.value.consequence.max_distance_to_exon = value
  },
})

const toggle = (arr: string[] | undefined, key: string) => {
  if (arr == undefined) {
    return
  }
  const index = arr.indexOf(key)
  if (index === -1) {
    arr.push(key)
  } else {
    arr.splice(index, 1)
  }
}
</script>

<template>
  <CollapsibleGroup title="Effects">
    <div style="display: flex; flex-direction: column; gap: 8px">
      <PresetSelect
        v-model="model"
        :presets="presets"
        preset-id-field="consequencepresets"
        settings-field="consequence"
        :matcher="matchesEffectsPreset"
      />

      <div>
        <label style="margin: 0; font-size: var(--font-size-sm)" for="max-exon">
          Max distance to next exon</label
        >
        <div
          style="
            display: flex;
            flex-direction: row;
            gap: 8px;
            align-items: center;
          "
        >
          <CheckButton
            :model-value="
              maxExonDistance == null || maxExonDistance == undefined
            "
            @update:model-value="maxExonDistance = null"
          >
            any
          </CheckButton>
          <CheckButton
            :model-value="maxExonDistance == 20"
            @update:model-value="maxExonDistance = 20"
          >
            20
          </CheckButton>
          <CheckButton
            :model-value="maxExonDistance == 100"
            @update:model-value="maxExonDistance = 100"
          >
            100
          </CheckButton>
          <Input
            id="max-exon"
            v-model="maxExonDistance"
            type="number"
            style="max-width: 100px"
          />
        </div>
      </div>

      <div>
        <div>Variant Type</div>
        <v-checkbox
          v-for="(label, key) in VARIANT_TYPES"
          :key="key"
          :label="label"
          :hide-details="true"
          density="compact"
          :model-value="model.consequence.variant_types?.includes(key)"
          @update:model-value="toggle(model.consequence.variant_types, key)"
        />
      </div>

      <div>
        <div>Transcript Type</div>
        <v-checkbox
          v-for="(label, key) in TRANSCRIPT_TYPES"
          :key="key"
          :label="label"
          :hide-details="true"
          density="compact"
          style="font-size: var(--font-size-sm)"
          :model-value="model.consequence.transcript_types?.includes(key)"
          @update:model-value="toggle(model.consequence.transcript_types, key)"
        />
      </div>

      <CollapsibleGroup title="Customize effects">
        <div style="display: flex; flex-direction: column; gap: 8px">
          <div v-for="(fields, title) in CUSTOMIZATION">
            {{ title }}

            <v-checkbox
              v-for="(label, key) in fields"
              :key="key"
              :label="label"
              :hide-details="true"
              density="compact"
              style="font-size: var(--font-size-sm)"
              :model-value="
                model.consequence.variant_consequences?.includes(key)
              "
              @update:model-value="
                toggle(model.consequence.variant_consequences, key)
              "
            />
          </div>
        </div>
      </CollapsibleGroup>
    </div>
  </CollapsibleGroup>
</template>
