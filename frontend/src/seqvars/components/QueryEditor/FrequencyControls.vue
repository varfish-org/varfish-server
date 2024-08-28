<script setup lang="ts">
import {
  SeqvarsQueryDetails,
  SeqvarsQueryDetailsRequest,
  SeqvarsQuerySettingsFrequency,
  SeqvarsQuerySettingsFrequencyRequest,
} from '@varfish-org/varfish-api/lib'

import FrequencyControlRow from './FrequencyControlRow.vue'
import AbbrHint from './ui/AbbrHint.vue'
import SmallText from './ui/SmallText.vue'
import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery';
import { ValueOf } from './lib';
import { toRaw } from 'vue';

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const model = defineModel<SeqvarsQueryDetails>({
  required: true,
})

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
 const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `model.value`. */
const applyMutation = async (name: keyof SeqvarsQuerySettingsFrequencyRequest, freqs: ValueOf<SeqvarsQuerySettingsFrequencyRequest>) => {
  const newData = structuredClone(toRaw(model.value))
  const newFrequency = newData.settings.frequency
  newFrequency[name] = freqs

  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body: newData,
    path: {
      session: model.value.session,
      query: model.value.sodar_uuid,
    },
  })
}

</script>

<template>
  <div
    style="
      width: fit-content;
      display: grid;
      grid-template-columns: 1fr auto auto auto auto;
      gap: 4px;
      font-size: var(--font-size-sm);
    "
  >
    <SmallText style="grid-column: 2">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal population frequency percentage to allow."
      >
        Max freq.
      </AbbrHint>
    </SmallText>
    <SmallText style="grid-column: span 3; text-align: center">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal het./hom./hemi. count to allow."
      >
        Max count
      </AbbrHint>
    </SmallText>

    <SmallText style="grid-column: 3">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of heterozygous carriers to allow."
      >
        het
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of homozygous alternative carriers to allow."
      >
        hom
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of hemizygous carriers to allow."
      >
        hemi
      </AbbrHint>
    </SmallText>

    <template
      v-for="[name, key, size] in [
        ['gnomAd exomes', 'gnomad_exomes', 16],
        ['gnomAd genomes', 'gnomad_genomes', 126],
        ['gnomAd mitochondrial', 'gnomad_mitochondrial', 56],
        ['in-house DB', 'inhouse', null],
        ['HelixMTdb', 'helixmtdb', 197],
      ] satisfies [
        string,
        keyof SeqvarsQuerySettingsFrequency,
        number | null,
      ][]"
      :key="name"
    >
      <FrequencyControlRow
        :model-value="model.settings.frequency[key]!"
        @update:model-value="async () => applyMutation(key, model.settings.frequency[key])"
        :name="name"
        :size="size"
      />
    </template>
  </div>
</template>
