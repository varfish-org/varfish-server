<script setup lang="ts">
import { computed, watch } from 'vue'

import { RecessiveModeEnum } from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'

import InheritanceModeControls from './InheritanceModeControls.vue'
import RecessiveControls from './RecessiveControls.vue'
import SexAffectedIcon from './SexAffectedIcon'
import { PedigreeObj } from '@/cases/stores/caseDetails'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The pedigree of the case that is analyzed. */
    pedigree: PedigreeObj
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

const model = defineModel<Query>({ required: true })

const recessiveMode = computed<RecessiveModeEnum>({
  get: () => model.value.genotype.recessive_mode ?? 'disabled',
  set: (value) => {
    model.value.genotype.recessive_mode = value
  },
})

/** Items for the recessive mode VSelect. */
const RECESSIVE_MODE_ITEMS: { title: string; value: RecessiveModeEnum }[] = [
  {
    title: 'Disabled',
    value: 'disabled',
  },
  {
    title: 'Comp. Het. Recessive',
    value: 'comphet_recessive',
  },
  {
    title: 'Hom. Recessive',
    value: 'homozygous_recessive',
  },
  {
    title: 'Any Recessive',
    value: 'recessive',
  },
]

/** Coerce genotypes skipping the given sample name. */
const coerceRecessiveMarkers = async (skipSample: string) => {
  const seen = new Set<string>()
  if (model.value.genotype.sample_genotype_choices !== undefined) {
    for (const choice of model.value.genotype.sample_genotype_choices) {
      if (choice.sample === skipSample) {
        seen.add(choice.genotype)
        break
      }
    }
  }
  for (const choice of model.value.genotype.sample_genotype_choices ?? []) {
    if (choice.sample !== skipSample) {
      if (seen.has(choice.genotype)) {
        choice.genotype = 'any'
      }
      seen.add(choice.genotype)
    }
  }
}

/**
 * Resets the recessive marker genotypes to non-recessive value "any".
 *
 * Must be called when switching to "disabled" recessive mode as the recessive
 * role markers are not valid as genotypes.
 */
const resetRecessiveMarkersToGenotypes = async () => {
  for (const choice of model.value.genotype.sample_genotype_choices ?? []) {
    if (
      ['recessive_index', 'recessive_father', 'recessive_mother'].includes(
        choice.genotype,
      )
    ) {
      choice.genotype = 'any'
    }
  }
}

/**
 * Resets the genotypes to value "any"
 *
 * The opposite of `resetRecessiveMarkersToGenotypes()`.
 */
const resetGenotypesToRecessiveMarkers = async () => {
  for (const choice of model.value.genotype.sample_genotype_choices ?? []) {
    if (
      !['recessive_index', 'recessive_father', 'recessive_mother'].includes(
        choice.genotype,
      )
    ) {
      choice.genotype = 'any'
    }
  }
}

watch(
  () => recessiveMode.value,
  async (newValue, oldValue) => {
    if (oldValue !== 'disabled' && newValue === 'disabled') {
      await resetRecessiveMarkersToGenotypes()
    } else if (oldValue === 'disabled' && newValue !== 'disabled') {
      await resetGenotypesToRecessiveMarkers()
    }
  },
  { immediate: true },
)
</script>

<template>
  <div class="w-100 d-flex flex-column ga-2">
    <CollapsibleGroup
      title="Recessive Mode"
      :hints-enabled="hintsEnabled"
      hint="To find biallelic variants beyond homozygous ones in the index, you can use one of the recessive modes."
      :summary="
        RECESSIVE_MODE_ITEMS.find((item) => item.value === recessiveMode)
          ?.title ?? 'NONE'
      "
    >
      <template #default>
        <Item
          v-for="(item, index) in RECESSIVE_MODE_ITEMS"
          :key="index"
          :selected="recessiveMode === item.value"
          @click="() => (recessiveMode = item.value)"
        >
          {{ item.title }}
        </Item>
      </template>
    </CollapsibleGroup>

    <v-divider class="pb-1" />

    <div
      v-for="(choice, index) in model.genotype.sample_genotype_choices"
      :key="index"
      class="w-100 d-flex flex-row align-start ga-2"
    >
      <input
        :id="choice.sample"
        v-model="choice.enabled"
        type="checkbox"
        style="margin-top: 6px"
      />

      <div
        class="w-100 d-flex flex-column"
        v-if="choice !== undefined && choice.genotype !== undefined"
      >
        <label
          :for="choice.sample"
          style="margin-bottom: 0; display: flex; align-items: center; gap: 8px"
          ><span>{{ choice.sample }}</span>

          <SexAffectedIcon
            :sex="
              pedigree.individual_set.find(
                (sample) => sample.name === choice.sample,
              )?.sex
            "
            :affected="
              pedigree.individual_set.find(
                (sample) => sample.name === choice.sample,
              )?.affected
            "
          />
        </label>

        <InheritanceModeControls
          v-if="recessiveMode === 'disabled'"
          v-model:genotype="choice.genotype"
          v-model:include-no-call="choice.include_no_call"
        />

        <RecessiveControls
          v-else-if="model.genotype.sample_genotype_choices"
          v-model:genotype="choice.genotype"
          v-model:include-no-call="choice.include_no_call"
          :index="index"
          :sample-name="choice.sample"
          @update-genotype="() => coerceRecessiveMarkers(choice.sample)"
        />
      </div>
    </div>
  </div>
</template>
