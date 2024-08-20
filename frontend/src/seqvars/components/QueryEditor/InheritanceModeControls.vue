<script setup lang="ts">
import { SeqvarsGenotypeChoice } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Model for "include no-call". */
const includeNoCall = defineModel<boolean | undefined>('includeNoCall')
/** Model for "genotype". */
const genotype = defineModel<SeqvarsGenotypeChoice>('genotype', {
  required: true,
})

/**
 * Stores value before "any" is selected for 'click any when already selected'
 * behaviour; component state. */
const genotypeBeforeAny = ref<SeqvarsGenotypeChoice>('ref')

/** The items displayed in the button group. */
type Item = 'any' | 'ref' | 'het' | 'hom' | 'no_call'

/** Provide a `Items[]` interface for managing `model.value.genotype`. */
const items = computed<Item[]>({
  get() {
    const result: Item[] = includeNoCall.value ? ['no_call'] : []
    switch (genotype.value) {
      case 'any':
        result.push(...(['any', 'ref', 'het', 'hom'] as Item[]))
        break
      case 'ref':
        result.push(...(['ref'] as Item[]))
        break
      case 'het':
        result.push(...(['het'] as Item[]))
        break
      case 'hom':
        result.push(...(['hom'] as Item[]))
        break
      case 'non_het':
        result.push(...(['ref', 'hom'] as Item[]))
        break
      case 'non_hom':
        result.push(...(['ref', 'het'] as Item[]))
        break
      case 'variant':
        result.push(...(['het', 'hom'] as Item[]))
        break
      case 'recessive_index':
      case 'recessive_father':
      case 'recessive_mother':
      default:
        throw new Error(`Invalid genotype value: ${genotype.value}`)
    }
    return result
  },
  set(values) {
    // Obtain sorted copy of array.
    let tmp = Array.from(values)
    tmp.sort()
    // Check for `no_call` and remove from array.
    includeNoCall.value = tmp.includes('no_call')
    tmp = tmp.filter((i) => i !== 'no_call')
    // Pop `any` if it is present.
    tmp = tmp.filter((i) => i !== 'any')

    const joint = tmp.join('+')
    switch (joint) {
      case 'het+hom+ref':
        genotype.value = 'any'
        break
      case 'ref':
        genotype.value = 'ref'
        break
      case 'het':
        genotype.value = 'het'
        break
      case 'hom':
        genotype.value = 'hom'
        break
      case 'hom+ref':
        genotype.value = 'non_het'
        break
      case 'het+ref':
        genotype.value = 'non_hom'
        break
      case 'het+hom':
        genotype.value = 'variant'
        break
      case '': // do not allow to deselect all
        break
      default:
        throw new Error(`Invalid genotype value: ${joint}`)
    }
  },
})
</script>

<template>
  <div class="w-100 d-flex pt-1">
    <v-btn-toggle
      v-model="items"
      multiple
      color="primary"
      variant="outlined"
      divided
      density="default"
    >
      <v-btn
        icon
        title="any"
        value="any"
        class="pa-0"
        @click.stop="
          () => {
            if (genotype === 'any') {
              genotype = genotypeBeforeAny
            } else {
              genotype = 'any'
            }
          }
        "
        @click.capture="
          () => {
            if (genotype != 'any') {
              genotypeBeforeAny = genotype
            }
          }
        "
      >
        any
      </v-btn>
      <v-btn icon title="wt / ref" value="ref" class="pa-0"> 0/0 </v-btn>
      <v-btn icon title="het." value="het" class="pa-0"> 0/1 </v-btn>
      <v-btn icon title="hom. / hemi. alt" value="hom" class="pa-0">
        1/1
      </v-btn>
    </v-btn-toggle>

    <v-btn-toggle
      v-model="items"
      multiple
      color="primary"
      variant="outlined"
      divided
      density="default"
      class="ml-3 mb-2"
    >
      <v-btn icon title="allow no call" value="no_call" class="pa-0">
        ./.
      </v-btn>
    </v-btn-toggle>
  </div>
</template>
