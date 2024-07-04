<script setup lang="ts">
import Input from '@/seqvars/components/Input.vue'
import { FREQUENCY_DB_K_SIZES, FrequencyDB_Values } from './constants'
import SmallText from './SmallText.vue'

const model = defineModel<FrequencyDB_Values>({ required: true })
</script>

<template>
  <div
    style="
      display: grid;
      grid-template-columns: 1fr auto auto auto auto;
      gap: 4px;
      font-size: 14px;
    "
  >
    <SmallText style="grid-column: 2">Max freq.</SmallText>
    <SmallText style="grid-column: span 3">Max count</SmallText>

    <SmallText style="grid-column: 3">het</SmallText>
    <SmallText>hom</SmallText>
    <SmallText>hemi</SmallText>

    <template
      v-for="[name, size] in Object.entries(FREQUENCY_DB_K_SIZES) as [
        keyof typeof model,
        number | null,
      ][]"
      :key="name"
    >
      <input :id="name" v-model="model[name].checked" type="checkbox" />
      <label
        :for="name"
        style="
          grid-column: span 4;
          margin-bottom: 0;
          display: flex;
          align-items: center;
          gap: 4px;
        "
        >{{ name
        }}<span v-if="size != null" style="color: #808080">{{ size }}k</span>
      </label>

      <Input
        :model-value="model[name].numbers.freq"
        style="grid-column: 2; margin-right: 8px; width: 52px"
        @update:model-value="
          (value) => {
            if (typeof value == 'number') {
              model[name].numbers.freq = value
            } else {
              delete model[name].numbers.freq
            }
          }
        "
      >
        <template #after>%</template></Input
      >
      <Input
        :model-value="model[name].numbers.het"
        type="number"
        style="width: 42px"
        @update:model-value="
          (value) => {
            if (typeof value == 'number') {
              model[name].numbers.het = value
            } else {
              delete model[name].numbers.het
            }
          }
        "
      />
      <Input
        :model-value="model[name].numbers.hom"
        type="number"
        style="width: 42px"
        @update:model-value="
          (value) => {
            if (typeof value == 'number') {
              model[name].numbers.hom = value
            } else {
              delete model[name].numbers.hom
            }
          }
        "
      />
      <Input
        :model-value="model[name].numbers.hemi"
        type="number"
        style="width: 42px"
        @update:model-value="
          (value) => {
            if (typeof value == 'number') {
              model[name].numbers.hemi = value
            } else {
              delete model[name].numbers.hemi
            }
          }
        "
      />
    </template>
  </div>
</template>
