<script setup lang="ts">
import { SeqvarsGenotypeChoice } from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

/** This component's props. */
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

/** This component's emit. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Update the genotype for the sample. */
  updateGenotype: [sample: string, genotype: SeqvarsGenotypeChoice]
}>()

/** The items displayed in the button group. */
type Item = 'any' | 'recessive_index' | 'recessive_mother' | 'recessive_father'

/** Model for "include no-call". */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const includeNoCall = defineModel<boolean | undefined>('includeNoCall')
/** Model for "genotype". */
const genotype = defineModel<SeqvarsGenotypeChoice>('genotype', {
  required: true,
})

/** Provide a `Items` interface for managing `model.value.genotype`. */
const items = computed<Item>({
  get() {
    switch (genotype.value) {
      case 'any':
        return 'any'
      case 'recessive_index':
      case 'recessive_father':
      case 'recessive_mother':
        return genotype.value
      case 'ref':
      case 'het':
      case 'hom':
      case 'non_het':
      case 'non_hom':
      case 'variant':
      default:
        return 'any'
      // throw new Error(`Invalid genotype value: ${genotype.value}`)
    }
  },
  set(value) {
    genotype.value = value
    emit('updateGenotype', props.sampleName, value)
  },
})
</script>

<template>
  <div class="w-100 d-flex pt-1">
    <v-btn-toggle
      v-model="items"
      color="primary"
      variant="outlined"
      divided
      density="default"
    >
      <v-btn title="index" value="recessive_index" class="px-1"> index </v-btn>
      <v-btn title="father" value="recessive_father" class="px-1">
        father
      </v-btn>
      <v-btn title="mother" value="recessive_mother" class="px-1">
        mother
      </v-btn>
    </v-btn-toggle>

    <v-btn-toggle
      v-model="items"
      color="primary"
      variant="outlined"
      divided
      density="default"
      class="ml-3"
    >
      <v-btn title="any" value="any" class="px-1"> any </v-btn>
    </v-btn-toggle>
  </div>
</template>
