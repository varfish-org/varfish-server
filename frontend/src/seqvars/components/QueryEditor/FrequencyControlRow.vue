<script setup lang="ts">
import { SeqvarsQuerySettingsFrequencyRequest } from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

import Input from '../QueryEditor/ui/Input.vue'
import { ValueOf } from './lib';

const { name, size } = defineProps<{ name: string; size: number | null }>()
const model = defineModel<
  Extract<ValueOf<SeqvarsQuerySettingsFrequencyRequest>, { enabled?: boolean }>
>({
  required: true,
})

type AllKeys<T> = T extends any ? keyof T : never
const getNumberComputedForKeys = (...keys: AllKeys<typeof model.value>[]) =>
  computed<number | null>({
    get() {
      for (const key of keys) {
        if (key in model.value) {
          if (key === 'frequency') {
            // displayed as percentage, stored as fraction
            return (model.value[key as never] as number) * 100.0
          } else {
            return model.value[key as never] as number
          }
        }
      }
      return null
    },
    set(value) {
      for (const key of keys) {
        if (key in model.value) {
          if (key === 'frequency') {
            // displayed as percentage, stored as fraction
            ;(model.value as any)[key] =
              !value || Number.isNaN(Number(value))
                ? null
                : Number(value / 100.0)
          } else {
            ;(model.value as any)[key] =
              !value || Number.isNaN(Number(value)) ? null : Number(value)
          }
          break
        }
      }
    },
  })

const freq = getNumberComputedForKeys('frequency', 'carriers')
const het = getNumberComputedForKeys('heterozygous', 'heteroplasmic')
const hom = getNumberComputedForKeys('homozygous', 'homoplasmic')
</script>

<template>
  <input :id="name" v-model="model.enabled" type="checkbox" />
  <label
    :for="name"
    style="
      grid-column: span 4;
      margin-bottom: 0;
      display: flex;
      align-items: center;
      gap: 4px;
    "
  >
    {{ name }}
    <span v-if="size != null" style="color: #808080"> {{ size }}k </span>
  </label>

  <Input
    v-model="freq"
    :aria-label="'frequency' in model ? 'frequency' : 'carriers'"
    style="grid-column: 2; margin-right: 8px; width: 56px"
    :step="0.1"
  >
    <template v-if="'frequency' in model" #after> % </template>
  </Input>
  <Input
    v-model="het"
    aria-label="heterozygous"
    type="number"
    style="width: 40px"
    :step="1"
  />
  <Input
    v-model="hom"
    aria-label="homozygous"
    type="number"
    style="width: 40px"
    :step="1"
  />
  <Input
    v-if="'hemizygous' in model"
    v-model="model.hemizygous"
    aria-label="hemizygous"
    type="number"
    style="width: 40px"
    :step="1"
  />
  <span v-else />
</template>
