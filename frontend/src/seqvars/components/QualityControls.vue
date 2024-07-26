<script setup lang="ts">
import { Query } from '@/seqvars/types'

import Input from './ui/Input.vue'
import SmallText from './ui/SmallText.vue'

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
    <SmallText style="grid-column: 2">min<br />DP het</SmallText>
    <SmallText>max<br />DP hom</SmallText>
    <SmallText>min<br />AB</SmallText>
    <SmallText>min<br />GQ</SmallText>
    <SmallText>min<br />AD</SmallText>
    <SmallText>max<br />AD</SmallText>

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

      <Input v-model="item.min_dp_het" style="grid-column: 2; width: 32px" />
      <Input v-model="item.min_dp_hom" style="width: 32px" />
      <Input v-model="item.min_ab_het" style="width: 32px" />
      <Input v-model="item.min_gq" style="width: 32px" />
      <Input v-model="item.min_ad" style="width: 32px" />
      <Input v-model="item.max_ad" style="width: 32px" />
    </template>
  </div>
</template>
