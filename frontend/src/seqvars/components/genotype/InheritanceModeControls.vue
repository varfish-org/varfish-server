<script setup lang="ts">
import isEqual from 'fast-deep-equal/es6'
import { computed } from 'vue'

import {
  SeqvarsGenotypeChoice,
  SeqvarsSampleGenotypePydanticList,
} from '@varfish-org/varfish-api/lib'

import CheckButton from '../ui/CheckButton.vue'

enum InheritanceMode {
  WILD_TYPE = 'wild-type',
  HET_ALT = 'het. alt.',
  HOM_ALT = 'hom. alt.',
  NO_CALL = 'no call',
}

const model = defineModel<SeqvarsSampleGenotypePydanticList[number]>({
  required: true,
})

const { WILD_TYPE, HET_ALT, HOM_ALT } = InheritanceMode

type GenotypeKey = Exclude<
  SeqvarsGenotypeChoice,
  'recessive_index' | 'recessive_father' | 'recessive_mother'
>
type Modes = typeof WILD_TYPE | typeof HET_ALT | typeof HOM_ALT
const GENOTYPE_TO_INHERITANCE_MODE = {
  any: [WILD_TYPE, HET_ALT, HOM_ALT],
  ref: [WILD_TYPE],
  het: [HET_ALT],
  hom: [HOM_ALT],
  non_hom: [WILD_TYPE, HET_ALT],
  variant: [HET_ALT, HOM_ALT],
  non_het: [WILD_TYPE, HOM_ALT],
} satisfies Record<GenotypeKey, Modes[]>
const modes = computed({
  get() {
    const { genotype } = model.value
    return new Set(
      genotype in GENOTYPE_TO_INHERITANCE_MODE
        ? GENOTYPE_TO_INHERITANCE_MODE[genotype as GenotypeKey]
        : [],
    )
  },
  set(value) {
    const entry = Object.entries(GENOTYPE_TO_INHERITANCE_MODE).find(([, m]) =>
      isEqual(new Set(m), value),
    )
    if (entry) {
      model.value.genotype = entry[0] as SeqvarsGenotypeChoice
    }
  },
})

const toggleModes = (key: Modes) => {
  const newModes = new Set(modes.value)
  if (newModes.has(key)) {
    newModes.delete(key)
  } else {
    newModes.add(key)
  }
  modes.value = newModes
}

const ANY_ITEMS_WITH_LABELS = [
  [WILD_TYPE, '0/0'],
  [HET_ALT, '1/0'],
  [HOM_ALT, '1/1'],
] satisfies [InheritanceMode, string][]
</script>

<template>
  <div style="display: flex; gap: 8px">
    <div style="display: flex; gap: 4px">
      <CheckButton
        :model-value="model.genotype == 'any'"
        @update:model-value="
          modes = new Set(
            model.genotype == 'any'
              ? [...modes].filter(
                  (i) => !ANY_ITEMS_WITH_LABELS.some(([item]) => item === i),
                )
              : [...modes, ...ANY_ITEMS_WITH_LABELS.map(([item]) => item)],
          )
        "
        >any</CheckButton
      >

      <CheckButton
        v-for="[key, label] in ANY_ITEMS_WITH_LABELS"
        :key="key"
        :model-value="modes.has(key)"
        @update:model-value="toggleModes(key)"
        >{{ label }}</CheckButton
      >
    </div>

    <CheckButton v-model="model.include_no_call">no call</CheckButton>
  </div>
</template>
