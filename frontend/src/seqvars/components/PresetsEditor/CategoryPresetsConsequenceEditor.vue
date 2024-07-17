<script setup lang="ts">
import {
  SeqvarsQueryPresetsConsequence,
  SeqvarsVariantConsequenceChoiceList,
} from '@varfish-org/varfish-api/lib'
import { computed, PropType } from 'vue'

/** The consequence presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsConsequence>,
})

/** Helper type to unpack, e.g., `Array<T1 | T2>`. */
type _Unpacked<T> = T extends (infer U)[] ? U : T

/** Define choices for variant consequences. */
type SeqvarsVariantConsequenceChoice =
  _Unpacked<SeqvarsVariantConsequenceChoiceList>

/** Enumeration for consequence groups. */
enum ConsequenceGroup {
  ALL = 'all',
  NONSYNONYMOUS = 'nonsynonymous',
  SPLICING = 'splicing',
  CODING = 'coding',
  UTR_INTRONIC = 'utr_intronic',
  NON_CODING = 'non_coding',
  NONSENSE = 'nonsense',
}

/** One consequence group. */
interface ConsequenceGroupInfo {
  /** Consequence group label. */
  label: string
  /** Key identifying the consequence group. */
  key: ConsequenceGroup
  /** Values in `model.variant_consequences`. */
  valueKeys: SeqvarsVariantConsequenceChoice[]
}

/** One choice of consequence. */
interface ConsequenceChoice {
  label: string
  key: SeqvarsVariantConsequenceChoice
}

/** Consequence choices in "coding" category. */
const codingConsequences: ConsequenceChoice[] = [
  { label: 'frameshift variant', key: 'frameshift_variant' },
  { label: 'rare amino acid', key: 'rare_amino_acid_variant' },
  { label: 'start lost', key: 'start_lost' },
  { label: 'stop gained', key: 'stop_gained' },
  { label: 'stop lost', key: 'stop_lost' },
  {
    label: 'conservative inframe deletion',
    key: 'conservative_inframe_deletion',
  },
  {
    label: 'conservative inframe insertion',
    key: 'conservative_inframe_insertion',
  },
  { label: 'disruptive inframe deletion', key: 'disruptive_inframe_deletion' },
  {
    label: 'disruptive inframe insertion',
    key: 'disruptive_inframe_insertion',
  },
  { label: 'missense', key: 'missense_variant' },
  { label: 'initiator codon synonymous', key: 'initiator_codon_variant' },
  { label: 'start retained', key: 'start_retained' },
  { label: 'stop retained', key: 'stop_retained_variant' },
  { label: 'synonymous', key: 'synonymous_variant' },
]

/** Consequence choices in "off-exomes" category. */
const offExomesConsequences: ConsequenceChoice[] = [
  { label: 'upstream', key: 'upstream_gene_variant' },
  { label: 'downstream', key: 'downstream_gene_variant' },
  { label: 'intronic', key: 'intron_variant' },
]

/** Consequence choices in "non-coding" category. */
const nonCodingConsequences: ConsequenceChoice[] = [
  { label: 'non-coding exonic', key: 'non_coding_transcript_exon_variant' },
  { label: 'non-coding intronic', key: 'non_coding_transcript_intron_variant' },
  { label: "5' UTR truncation", key: '5_prime_UTR_truncation' },
  { label: "3' UTR truncation", key: '3_prime_UTR_truncation' },
  { label: "5' UTR exonic", key: '5_prime_UTR_variant-exon_variant' },
  { label: "3' UTR exonic", key: '3_prime_UTR_variant-exon_variant' },
  { label: "5' UTR intronic", key: '5_prime_UTR_variant-intron_variant' },
  { label: "3' UTR intronic", key: '3_prime_UTR_variant-intron_variant' },
]

/** Consequence choices in "splicing" category. */
const splicingConsequences: ConsequenceChoice[] = [
  { label: 'splice acceptor (-1, -2)', key: 'splice_acceptor_variant' },
  { label: 'splice donor (+1, +2)', key: 'splice_donor_variant' },
  { label: 'splice region (-3, +3, ..., +8)', key: 'splice_region_variant' },
]

/** Defined consequence groups. */
const consequenceGroupsInfos: ConsequenceGroupInfo[] = [
  {
    label: 'all',
    key: ConsequenceGroup.ALL,
    valueKeys: codingConsequences
      .map((elem) => elem.key)
      .concat(offExomesConsequences.map((elem) => elem.key))
      .concat(nonCodingConsequences.map((elem) => elem.key))
      .concat(splicingConsequences.map((elem) => elem.key)),
  },
  {
    label: 'nonsynonymous',
    key: ConsequenceGroup.NONSYNONYMOUS,
    valueKeys: [
      'frameshift_variant',
      'rare_amino_acid_variant',
      'splice_acceptor_variant',
      'splice_donor_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'conservative_inframe_deletion',
      'conservative_inframe_insertion',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'missense_variant',
    ],
  },
  {
    label: 'splicing',
    key: ConsequenceGroup.SPLICING,
    valueKeys: [
      'splice_acceptor_variant',
      'splice_donor_variant',
      'splice_region_variant',
    ],
  },
  {
    label: 'coding',
    key: ConsequenceGroup.CODING,
    valueKeys: [
      'frameshift_variant',
      'rare_amino_acid_variant',
      'splice_acceptor_variant',
      'splice_donor_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'conservative_inframe_deletion',
      'conservative_inframe_insertion',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'missense_variant',
      'splice_region_variant',
      'initiator_codon_variant',
      'start_retained',
      'stop_retained_variant',
      'synonymous_variant',
    ],
  },
  {
    label: 'UTR / intronic',
    key: ConsequenceGroup.UTR_INTRONIC,
    valueKeys: [
      '3_prime_UTR_truncation',
      '5_prime_UTR_truncation',
      'intron_variant',
      '3_prime_UTR_variant-exon_variant',
      '5_prime_UTR_variant-exon_variant',
      '3_prime_UTR_variant-intron_variant',
      '5_prime_UTR_variant-intron_variant',
    ],
  },
  {
    label: 'non-coding',
    key: ConsequenceGroup.NON_CODING,
    valueKeys: [
      'non_coding_transcript_exon_variant',
      'non_coding_transcript_intron_variant',
    ],
  },
  {
    label: 'nonsense',
    key: ConsequenceGroup.NONSENSE,
    valueKeys: [
      'frameshift_variant',
      'rare_amino_acid_variant',
      'splice_acceptor_variant',
      'splice_donor_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
    ],
  },
]


/** Type for the consequence group checkbox state. */
interface ConsequenceGroupState {
  /** Whether the group is checked. */
  checked: boolean
  /** Whether the group is indeterminate. */
  indeterminate: boolean
}

/** The consequence groups state. */
const consequenceGroups = computed<
  Record<ConsequenceGroup, ConsequenceGroupState>
>(() => {
  // Guard in case of undefined `model`.
  if (!model.value) {
    return consequenceGroupsInfos.reduce(
      (acc, group) => {
        acc[group.key] = { checked: false, indeterminate: false }
        return acc
      },
      {} as Record<ConsequenceGroup, ConsequenceGroupState>,
    )
  }

  const checkedGroups = consequenceGroupsInfos.filter((group) =>
    group.valueKeys.every((key) =>
      model.value?.variant_consequences?.includes(key),
    ),
  )
  const indeterminateGroups = consequenceGroupsInfos.filter((group) =>
    group.valueKeys.some((key) =>
      model.value?.variant_consequences?.includes(key),
    ),
  )
  return consequenceGroupsInfos.reduce(
    (acc, group) => {
      acc[group.key] = {
        checked: checkedGroups.includes(group),
        indeterminate:
          indeterminateGroups.includes(group) && !checkedGroups.includes(group),
      }
      return acc
    },
    {} as Record<ConsequenceGroup, ConsequenceGroupState>,
  )
})

/** Toggles the given consequence group. */
const toggleConsequenceGroup = (key: ConsequenceGroup) => {
  // Guard in case of undefined `model`.
  if (!model.value) {
    return
  }

  if (consequenceGroups.value[key].checked) {
    model.value.variant_consequences = model.value.variant_consequences!.filter(
      (elem) => !consequenceGroupsInfos.find((group) => group.key === key)?.valueKeys.includes(elem),
    )
  } else {
    model.value.variant_consequences = model.value.variant_consequences!.concat(
      consequenceGroupsInfos.find((group) => group.key === key)?.valueKeys ?? [],
    )
  }
}
</script>

<template>
  <h3>Consequence Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h3>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <h4 class="pt-3">Distance</h4>

    <v-text-field
      v-model="model.max_distance_to_exon"
      label="Maximal distance to next exon (e.g., 2 for consensus splice sites)"
      type="number"
      hide-details
      clearable
    />

    <h4 class="pt-3">Variant Type</h4>

    <v-checkbox
      v-model="model.variant_types"
      value="snv"
      label="SNV"
      density="compact"
      hide-details
    />
    <v-checkbox
      v-model="model.variant_types"
      value="indel"
      label="Indel"
      density="compact"
      hide-details
    />
    <v-checkbox
      v-model="model.variant_types"
      value="mnv"
      label="MNV"
      density="compact"
      hide-details
    />

    <h4 class="pt-3">Transcript Type</h4>

    <v-checkbox
      v-model="model.transcript_types"
      value="coding"
      label="Coding"
      density="compact"
      hide-details
    />
    <v-checkbox
      v-model="model.transcript_types"
      value="non_coding"
      label="Non-Coding"
      density="compact"
      hide-details
    />

    <h4 class="pt-3">Effect Group</h4>

    <v-checkbox
      v-for="group in consequenceGroupsInfos"
      :label="group.label"
      v-model="consequenceGroups[group.key].checked"
      :indeterminate="consequenceGroups[group.key].indeterminate"
      @click="toggleConsequenceGroup(group.key)"
      density="compact"
      hide-details
    />

    <h4 class="pt-3">Customize Effects</h4>

    <h5>Coding</h5>

    <v-checkbox
      v-for="consequence in codingConsequences"
      :value="consequence.key"
      :label="consequence.label"
      v-model="model.variant_consequences"
      density="compact"
      hide-details
    />

    <h5>Off-Exomes</h5>

    <v-checkbox
      v-for="consequence in offExomesConsequences"
      :value="consequence.key"
      :label="consequence.label"
      v-model="model.variant_consequences"
      density="compact"
      hide-details
    />

    <h5>Non-coding</h5>

    <v-checkbox
      v-for="consequence in nonCodingConsequences"
      :value="consequence.key"
      :label="consequence.label"
      v-model="model.variant_consequences"
      density="compact"
      hide-details
    />

    <h5>Splicing</h5>

    <v-checkbox
      v-for="consequence in splicingConsequences"
      :value="consequence.key"
      :label="consequence.label"
      v-model="model.variant_consequences"
      density="compact"
      hide-details
    />
  </v-form>
</template>
