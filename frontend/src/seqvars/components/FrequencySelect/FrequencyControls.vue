<script setup lang="ts">
import { SeqvarsQuerySettingsFrequency } from '@varfish-org/varfish-api/lib'

import { LocalFields } from '@/seqvars/types'
import SmallText from '../ui/SmallText.vue'
import FrequencyControlRow from './FrequencyControlRow.vue'

const model = defineModel<LocalFields<SeqvarsQuerySettingsFrequency>>({
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
    <SmallText style="grid-column: 2">Max freq.</SmallText>
    <SmallText style="grid-column: span 3">Max count</SmallText>

    <SmallText style="grid-column: 3">het</SmallText>
    <SmallText>hom</SmallText>
    <SmallText>hemi</SmallText>

    <template
      v-for="[name, key, size] in [
        ['gnomAd exomes', 'gnomad_exomes', 16],
        ['gnomAd genomes', 'gnomad_genomes', 126],
        ['gnomAd mitochondrial', 'gnomad_mitochondrial', null],
        ['in-house DB', 'inhouse', null],
        ['HelixMTdb', 'helixmtdb', 197],
      ] satisfies [
        string,
        keyof SeqvarsQuerySettingsFrequency,
        number | null,
      ][]"
      :key="name"
    >
      <FrequencyControlRow v-model="model[key]" :name="name" :size="size" />
    </template>
  </div>
</template>
