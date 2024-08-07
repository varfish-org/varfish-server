<script setup lang="ts">
import {
  SeqvarsGenotypeChoice,
  SeqvarsSampleGenotypePydanticList,
} from '@varfish-org/varfish-api/lib'

const model = defineModel<SeqvarsSampleGenotypePydanticList>({ required: true })
const { index } = defineProps<{ index: number }>()

const ITEMS = {
  any: 'any',
  index: 'recessive_index',
  mother: 'recessive_mother',
  father: 'recessive_father',
} satisfies Record<string, SeqvarsGenotypeChoice>
</script>

<template>
  <v-select
    :model-value="
      Object.entries(ITEMS).find(([, v]) => v === model[index].genotype)?.[0] ??
      'any'
    "
    :items="Object.keys(ITEMS)"
    hide-details
    density="compact"
    @update:model-value="
      (v: string) => {
        const value = v as keyof typeof ITEMS
        if (value != 'any') {
          const el = model.find((m) => m.genotype === ITEMS[value])
          if (el) el.genotype = 'any'
        }
        model[index].genotype = ITEMS[value]
      }
    "
  />
</template>
