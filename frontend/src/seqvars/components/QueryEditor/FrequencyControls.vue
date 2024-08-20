<script setup lang="ts">
import { SeqvarsQuerySettingsFrequency } from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'

import FrequencyControlRow from './FrequencyControlRow.vue'
import AbbrHint from './ui/AbbrHint.vue'
import SmallText from './ui/SmallText.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const model = defineModel<Query>({
  required: true,
})
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
        v-model="model.frequency[key]!"
        :name="name"
        :size="size"
      />
    </template>
  </div>
</template>
