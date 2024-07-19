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
      { recessive_index: 'index', recessive_parent: 'parent' }[
        model[index].genotype as never
      ] ?? ''
    "
    @update:model-value="
      (value: any) => {
        if (value === 'index') {
          const el = model.find((m) => m.genotype === 'recessive_index')
          if (el) el.genotype = 'any'
        } else if (
          value === 'parent' &&
          model.filter((m) => m.genotype === 'recessive_parent').length > 1
        ) {
          const el = model.find((m) => m.genotype === 'recessive_parent')
          if (el) el.genotype = 'any'
        }

        model[index].genotype = (
          {
            index: 'recessive_index',
            parent: 'recessive_parent',
            '': 'any',
          } as const
        )[value as never]
      }
    "
  >
    <v-radio label="None" value=""></v-radio>
    <v-radio label="Index" value="index"></v-radio>
    <v-radio label="Parent" value="parent"></v-radio>
  </v-radio-group>
</template>
