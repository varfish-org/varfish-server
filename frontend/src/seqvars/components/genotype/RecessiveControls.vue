<script setup lang="ts">
import { SeqvarsSampleGenotypeChoiceList } from '@varfish-org/varfish-api/lib'

const model = defineModel<SeqvarsSampleGenotypeChoiceList>({ required: true })
const { index } = defineProps<{ index: number }>()
</script>

<template>
  <v-radio-group
    inline
    :hide-details="true"
    :model-value="
      {
        recessive_index: 'index',
        recessive_father: 'father',
        recessive_mother: 'mother',
      }[model[index].genotype as never] ?? ''
    "
    @update:model-value="
      (value: any) => {
        if (value === 'index') {
          const el = model.find((m) => m.genotype === 'recessive_index')
          if (el) el.genotype = 'any'
        } else if (
          value === 'father' &&
          model.filter((m) => m.genotype === 'recessive_father').length > 1
        ) {
          const el = model.find((m) => m.genotype === 'recessive_father')
          if (el) el.genotype = 'any'
        } else if (
          value === 'mother' &&
          model.filter((m) => m.genotype === 'recessive_mother').length > 1
        ) {
          const el = model.find((m) => m.genotype === 'recessive_mother')
          if (el) el.genotype = 'any'
        }

        model[index].genotype = (
          {
            index: 'recessive_index',
            father: 'recessive_father',
            mother: 'recessive_mother',
            '': 'any',
          } as const
        )[value as never]
      }
    "
  >
    <v-radio label="None" value=""></v-radio>
    <v-radio label="Index" value="index"></v-radio>
    <v-radio label="Father" value="father"></v-radio>
    <v-radio label="Mother" value="mother"></v-radio>
  </v-radio-group>
</template>
