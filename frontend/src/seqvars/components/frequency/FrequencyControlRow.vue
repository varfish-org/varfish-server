<script setup lang="ts">
import { computed } from 'vue'

import { SeqvarsQuerySettingsFrequency } from '@varfish-org/varfish-api/lib'

import Input from '../ui/Input.vue'

type ValueOf<T> = T[keyof T]

const { name, size } = defineProps<{ name: string; size: number | null }>()
const model = defineModel<
  Extract<ValueOf<SeqvarsQuerySettingsFrequency>, { enabled?: boolean }>
>({
  required: true,
})

type AllKeys<T> = T extends any ? keyof T : never
const getNumberComputedForKeys = (...keys: AllKeys<typeof model.value>[]) =>
  computed({
    get() {
      for (const key of keys) {
        if (key in model.value) {
          return model.value[key as never] as number
        }
      }
      return null
    },
    set(value) {
      for (const key of keys) {
        if (key in model.value) {
          ;(model.value as any)[key] =
            !value || Number.isNaN(Number(value)) ? null : Number(value)
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
    >{{ name
    }}<span v-if="size != null" style="color: #808080">{{ size }}k</span>
  </label>

  <Input
    v-model="freq"
    :aria-label="'frequency' in model ? 'frequency' : 'carriers'"
    style="grid-column: 2; margin-right: 8px; width: 56px"
  >
    <template v-if="'frequency' in model" #after>%</template></Input
  >
  <Input
    v-model="het"
    aria-label="heterozygous"
    type="number"
    style="width: 40px"
  />
  <Input
    v-model="hom"
    aria-label="homozygous"
    type="number"
    style="width: 40px"
  />
  <Input
    v-if="'hemizygous' in model"
    v-model="model.hemizygous"
    aria-label="hemizygous"
    type="number"
    style="width: 40px"
  />
  <span v-else />
</template>
