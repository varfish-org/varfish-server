<script setup lang="ts">
import {
  SeqvarsQueryPresetsConsequence,
  SeqvarsVariantConsequenceChoiceList,
} from '@varfish-org/varfish-api/lib'
import { debounce } from 'lodash'
import { computed, onMounted, ref, watch } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { CATEGORY_PRESETS_DEBOUNCE_WAIT } from './lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets consequence */
    consequencePresets?: string
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** This component's events. */
const emit = defineEmits<{
  /** Emit event to show a message. */
  message: [message: SnackbarMessage]
}>()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The data that is to be edited by this component; component state. */
const data = ref<SeqvarsQueryPresetsConsequence | undefined>(undefined)

/** Shortcut to the number of consequence presets, used for rank. */
const maxRank = computed<number>(() => {
  if (props.presetSetVersion === undefined) {
    return 0
  }
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    return 0
  }
  return presetSetVersion.seqvarsquerypresetsconsequence_set.length
})

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Fill the data from the store. */
const fillData = () => {
  // Guard against missing preset set version or consequence.
  if (
    props.presetSetVersion === undefined ||
    props.consequencePresets === undefined
  ) {
    return
  }
  // Attempt to obtain the model from the store.
  const presetSetVersion = seqvarsPresetsStore.presetSetVersions.get(
    props.presetSetVersion,
  )
  if (!presetSetVersion) {
    emit('message', {
      text: 'Failed to find preset set version.',
      color: 'error',
    })
    return
  }
  const consequencePresets =
    presetSetVersion?.seqvarsquerypresetsconsequence_set.find(
      (elem) => elem.sodar_uuid === props.consequencePresets,
    )
  if (!consequencePresets) {
    emit('message', {
      text: 'Failed to find consequence presets.',
      color: 'error',
    })
    return
  }

  data.value = { ...consequencePresets }
}
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
  OFF_EXOME = 'off_exome',
  NON_CODING = 'non_coding',
  NONSENSE = 'nonsense',
}

/** One consequence group. */
interface ConsequenceGroupInfo {
  /** Consequence group label. */
  label: string
  /** Key identifying the consequence group. */
  key: ConsequenceGroup
  /** Values in `data.variant_consequences`. */
  valueKeys: SeqvarsVariantConsequenceChoice[]
}

/** One choice of consequence. */
interface ConsequenceChoice {
  label: string
  key: SeqvarsVariantConsequenceChoice
}

/** Consequence choices in "coding" category. */
const codingConsequences: ConsequenceChoice[] = [
  { label: 'transcript ablation', key: 'transcript_ablation' },
  { label: 'transcript amplification', key: 'transcript_amplification' },
  { label: 'exon loss', key: 'exon_loss_variant' },
  { label: 'frameshift variant', key: 'frameshift_variant' },
  { label: 'start lost', key: 'start_lost' },
  { label: 'stop gained', key: 'stop_gained' },
  { label: 'stop lost', key: 'stop_lost' },
  {
    label: 'disruptive inframe insertion',
    key: 'disruptive_inframe_insertion',
  },
  { label: 'disruptive inframe deletion', key: 'disruptive_inframe_deletion' },
  {
    label: 'conservative inframe insertion',
    key: 'conservative_inframe_insertion',
  },
  {
    label: 'conservative inframe deletion',
    key: 'conservative_inframe_deletion',
  },
  { label: 'in-frame indel', key: 'inframe_indel' },
  { label: 'missense', key: 'missense_variant' },
  { label: 'start retained', key: 'start_retained_variant' },
  { label: 'stop retained', key: 'stop_retained_variant' },
  { label: 'synonymous', key: 'synonymous_variant' },
  { label: 'coding', key: 'coding_sequence_variant' },
]

/** Consequence choices in "off-exomes" category. */
const offExomesConsequences: ConsequenceChoice[] = [
  { label: 'upstream', key: 'upstream_gene_variant' },
  { label: 'downstream', key: 'downstream_gene_variant' },
  { label: 'intronic', key: 'intron_variant' },
  { label: 'intergenic', key: 'intergenic_variant' },
]

/** Consequence choices in "non-coding" category. */
const nonCodingConsequences: ConsequenceChoice[] = [
  { label: "5' UTR exon variant", key: '5_prime_UTR_exon_variant' },
  { label: "5' UTR intron variant", key: '5_prime_UTR_intron_variant' },
  { label: "3' UTR exon variant", key: '3_prime_UTR_exon_variant' },
  { label: "3' UTR intron variant", key: '3_prime_UTR_intron_variant' },
  { label: 'non-coding exonic', key: 'non_coding_transcript_exon_variant' },
  { label: 'non-coding intronic', key: 'non_coding_transcript_intron_variant' },
]

/** Consequence choices in "splicing" category. */
const splicingConsequences: ConsequenceChoice[] = [
  { label: 'splice acceptor (-1, -2)', key: 'splice_acceptor_variant' },
  { label: 'splice donor (+1, +2)', key: 'splice_donor_variant' },
  { label: 'splice donor 5th-base', key: 'splice_donor_5th_base_variant' },
  { label: 'splice region (-3, +3, ..., +8)', key: 'splice_region_variant' },
  { label: 'splice donor region', key: 'splice_donor_region_variant' },
  {
    label: 'splice polypyrimidine tract variant',
    key: 'splice_polypyrimidine_tract_variant',
  },
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
      'transcript_ablation',
      'transcript_amplification',
      'exon_loss_variant',
      'frameshift_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'conservative_inframe_insertion',
      'conservative_inframe_deletion',
      'missense_variant',
      'coding_sequence_variant',
    ],
  },
  {
    label: 'splicing',
    key: ConsequenceGroup.SPLICING,
    valueKeys: [
      'splice_acceptor_variant',
      'splice_donor_variant',
      'splice_region_variant',
      'splice_donor_5th_base_variant',
      'splice_donor_region_variant',
      'splice_polypyrimidine_tract_variant',
    ],
  },
  {
    label: 'coding',
    key: ConsequenceGroup.CODING,
    valueKeys: [
      'transcript_ablation',
      'transcript_amplification',
      'exon_loss_variant',
      'frameshift_variant',
      'start_lost',
      'stop_gained',
      'stop_lost',
      'disruptive_inframe_deletion',
      'disruptive_inframe_insertion',
      'conservative_inframe_insertion',
      'conservative_inframe_deletion',
      'missense_variant',
      'synonymous_variant',
    ],
  },
  {
    label: 'UTR / intronic',
    key: ConsequenceGroup.UTR_INTRONIC,
    valueKeys: [
      '5_prime_UTR_exon_variant',
      '5_prime_UTR_intron_variant',
      '3_prime_UTR_exon_variant',
      '3_prime_UTR_intron_variant',
    ],
  },
  {
    label: 'off-exome',
    key: ConsequenceGroup.OFF_EXOME,
    valueKeys: [
      'upstream_gene_variant',
      'downstream_gene_variant',
      'intron_variant',
      'intergenic_variant',
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
      'transcript_ablation',
      'exon_loss_variant',
      'frameshift_variant',
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
  // Guard in case of undefined `data`.
  if (!data.value) {
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
      data.value?.variant_consequences?.includes(key),
    ),
  )
  const indeterminateGroups = consequenceGroupsInfos.filter((group) =>
    group.valueKeys.some((key) =>
      data.value?.variant_consequences?.includes(key),
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
  // Guard in case of undefined `data`.
  if (!data.value) {
    return
  }

  if (consequenceGroups.value[key].checked) {
    data.value.variant_consequences = data.value.variant_consequences!.filter(
      (elem) =>
        !consequenceGroupsInfos
          .find((group) => group.key === key)
          ?.valueKeys.includes(elem),
    )
  } else {
    data.value.variant_consequences = data.value.variant_consequences!.concat(
      consequenceGroupsInfos.find((group) => group.key === key)?.valueKeys ??
        [],
    )
  }
}

/**
 * Update the consequence presets in the store.
 *
 * Used directly when changing the rank (to minimize UI delay).
 *
 * @param rankDelta The delta to apply to the rank, if any.
 */
const updateConsequencePresets = async (rankDelta: number = 0) => {
  // Guard against missing/readonly/non-draft preset set version or missing consequence.
  if (
    props.consequencePresets === undefined ||
    props.presetSetVersion === undefined ||
    seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      props.consequencePresets,
    ) ||
    seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion)
      ?.status !== PresetSetVersionState.DRAFT ||
    data.value === undefined
  ) {
    return
  }

  // If necessary, update the rank of the other item as well via API and set
  // the new rank to `data.value.rank`.
  if (rankDelta !== 0) {
    const version = seqvarsPresetsStore.presetSetVersions.get(
      props.presetSetVersion,
    )
    if (
      version === undefined ||
      data.value.rank === undefined ||
      data.value.rank + rankDelta < 1 ||
      data.value.rank + rankDelta > maxRank.value
    ) {
      // Guard against invalid rank and version.
      return
    }
    // Find the next smaller or larger item, sort by rank.
    const others = version.seqvarsquerypresetsconsequence_set.filter((elem) => {
      if (elem.sodar_uuid === props.consequencePresets) {
        return false
      }
      if (rankDelta < 0) {
        return (elem.rank ?? 0) < (data.value?.rank ?? 0)
      } else {
        return (elem.rank ?? 0) > (data.value?.rank ?? 0)
      }
    })
    others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
    // Then, pick the other item to flip ranks with.
    const other = others[rankDelta < 0 ? others.length - 1 : 0]
    // Store the other's rank in `data.value.rank` and update other via API.
    if (other) {
      const dataRank = data.value.rank
      data.value.rank = other.rank
      other.rank = dataRank
      try {
        await seqvarsPresetsStore.updateQueryPresetsConsequence(
          props.presetSetVersion,
          other,
        )
      } catch (error) {
        emit('message', {
          text: 'Failed to update consequence presets rank.',
          color: 'error',
        })
      }
    }
  }

  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  try {
    await seqvarsPresetsStore.updateQueryPresetsConsequence(
      props.presetSetVersion,
      data.value,
    )
  } catch (error) {
    emit('message', {
      text: 'Failed to update consequence presets.',
      color: 'error',
    })
  }
}

/**
 * Update the consequence presets in the store -- debounced.
 *
 * Used for updating non-rank fields so that the UI does not lag.
 */
const updateConsequencePresetsDebounced = debounce(
  updateConsequencePresets,
  CATEGORY_PRESETS_DEBOUNCE_WAIT,
  { leading: true, trailing: true },
)

// Load model data from store when the UUID changes.
watch(
  () => props.consequencePresets,
  () => fillData(),
)
// Also, load model data from store when mounted.
onMounted(() => fillData())

// Watch the data and trigger a store update.
watch(data, () => updateConsequencePresetsDebounced(), { deep: true })
</script>

<template>
  <h3>Consequence Presets &raquo;{{ data?.label ?? 'UNDEFINED' }}&laquo;</h3>

  <v-skeleton-loader v-if="!data" type="article" />
  <v-form v-else ref="formRef">
    <v-text-field
      v-model="data.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
    />
    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank <= 1
          "
          @click="updateConsequencePresets(-1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly || data.rank === undefined || data.rank >= maxRank
          "
          @click="updateConsequencePresets(1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <h4 class="pt-3">Distance</h4>

    <v-text-field
      v-model="data.max_distance_to_exon"
      label="Maximal distance to next exon (e.g., 2 for consensus splice sites)"
      type="number"
      hide-details
      clearable
      :disabled="readonly"
    />

    <h4 class="pt-3">Variant Type</h4>

    <v-checkbox
      v-model="data.variant_types"
      value="snv"
      label="SNV"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.variant_types"
      value="indel"
      label="Indel"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.variant_types"
      value="mnv"
      label="MNV"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h4 class="pt-3">Transcript Type</h4>

    <v-checkbox
      v-model="data.transcript_types"
      value="coding"
      label="Coding"
      density="compact"
      hide-details
      :disabled="readonly"
    />
    <v-checkbox
      v-model="data.transcript_types"
      value="non_coding"
      label="Non-Coding"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h4 class="pt-3">Effect Group</h4>

    <v-checkbox
      v-for="group in consequenceGroupsInfos"
      :key="`group-${group.key}`"
      v-model="consequenceGroups[group.key].checked"
      :label="group.label"
      :indeterminate="consequenceGroups[group.key].indeterminate"
      density="compact"
      hide-details
      :disabled="readonly"
      @click="toggleConsequenceGroup(group.key)"
    />

    <h4 class="pt-3">Customize Effects</h4>

    <h5>Coding</h5>

    <v-checkbox
      v-for="consequence in codingConsequences"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Off-Exomes</h5>

    <v-checkbox
      v-for="consequence in offExomesConsequences"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Non-coding</h5>

    <v-checkbox
      v-for="consequence in nonCodingConsequences"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />

    <h5>Splicing</h5>

    <v-checkbox
      v-for="consequence in splicingConsequences"
      :key="`consequence-${consequence.key}`"
      v-model="data.variant_consequences"
      :value="consequence.key"
      :label="consequence.label"
      density="compact"
      hide-details
      :disabled="readonly"
    />
  </v-form>
</template>
