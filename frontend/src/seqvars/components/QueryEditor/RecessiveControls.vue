<script setup lang="ts">
import {
  SeqvarsGenotypeChoice,
  SeqvarsSampleGenotypePydanticList,
} from '@varfish-org/varfish-api/lib'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Name of the sample. */
    sampleName: string
    /** Index of the field. */
    index: number
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  {
    hintsEnabled: false,
  },
)

const model = defineModel<SeqvarsSampleGenotypePydanticList>({ required: true })

/** Mapping from label to genotype choice. */
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
    :label="`for &quot;${sampleName}&quot;`"
    hide-details
    density="compact"
    variant="outlined"
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
