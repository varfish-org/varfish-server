<script setup lang="ts">
import { Query } from '@/seqvars/types'

import Input from './ui/Input.vue'
import SmallText from './ui/SmallText.vue'
import AbbrHint from './ui/AbbrHint.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const model = defineModel<Query>({ required: true })
</script>

<template>
  <div
    style="
      width: fit-content;
      display: grid;
      grid-template-columns: 1fr auto auto auto auto auto auto;
      gap: 4px;
    "
  >
    <SmallText style="grid-column: 2">
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal depth of coverage for het. genotypes."
      >
        min<br />DP het
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal depth of coverage for hom. genotypes."
      >
        min<br />DP hom
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal allelic balance for het. genotypes."
      >
        min<br />AB
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal genotype quality for any genotype."
      >
        min<br />GQ
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Minimal number of reads showing alternate allele for any genotype."
      >
        min<br />AD
      </AbbrHint>
    </SmallText>
    <SmallText>
      <AbbrHint
        :hints-enabled="hintsEnabled"
        hint="Maximal number of reads showing alternate allele for any genotype (useful for parents in de novo search)."
      >
        max<br />AD
      </AbbrHint>
    </SmallText>

    <template
      v-for="(item, index) in model.quality.sample_quality_filters"
      :key="index"
    >
      <div>
        <input
          :id="`quality-sample-${index}`"
          v-model="item.filter_active"
          type="checkbox"
        />
      </div>
      <label
        :for="`quality-sample-${index}`"
        style="
          margin: 0;
          grid-column: span 6;
          display: flex;
          align-items: center;
        "
        >{{ item.sample }}</label
      >

      <fieldset style="display: contents">
        <legend style="display: none">{{ item.sample }}</legend>
        <Input
          v-model="item.min_dp_het"
          aria-label="min DP het"
          style="grid-column: 2; width: 32px"
        />
        <Input
          v-model="item.min_dp_hom"
          aria-label="max DP hom"
          style="width: 32px"
        />
        <Input
          v-model="item.min_ab_het"
          aria-label="min AB"
          style="width: 32px"
        />
        <Input v-model="item.min_gq" aria-label="min GQ" style="width: 32px" />
        <Input v-model="item.min_ad" aria-label="min AD" style="width: 32px" />
        <Input v-model="item.max_ad" aria-label="max AD" style="width: 32px" />
      </fieldset>
    </template>
  </div>
</template>
