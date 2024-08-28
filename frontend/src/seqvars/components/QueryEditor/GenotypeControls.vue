<script setup lang="ts">
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import {
  RecessiveModeEnum,
  SeqvarsQueryDetails,
  SeqvarsQueryDetailsRequest,
  SeqvarsSampleGenotypePydantic,
} from '@varfish-org/varfish-api/lib'
import { toRaw } from 'vue'

import { PedigreeObj } from '@/cases/stores/caseDetails'
import CollapsibleGroup from '@/seqvars/components/QueryEditor/ui/CollapsibleGroup.vue'
import Item from '@/seqvars/components/QueryEditor/ui/Item.vue'
import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import InheritanceModeControls from './InheritanceModeControls.vue'
import RecessiveControls from './RecessiveControls.vue'
import SexAffectedIcon from './SexAffectedIcon'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The current `SeqvarsQueryDetails` that is being edited. */
    seqvarsQuery: SeqvarsQueryDetails
    /** The pedigree of the case that is analyzed. */
    pedigree: PedigreeObj
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

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

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.seqvarsQuery`. */
const applyMutation = async (body: SeqvarsQueryDetailsRequest) => {
  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body,
    path: {
      session: props.seqvarsQuery.session,
      query: props.seqvarsQuery.sodar_uuid,
    },
  })
}

/**
 * Update `props.seqvarsQuery.settings.genotype.recessive_mode`.
 */
const updateRecessiveMode = async (newValue: RecessiveModeEnum) => {
  // Copy old query and get shortcut to the genotype to update below.
  const newData = structuredClone(toRaw(props.seqvarsQuery))
  const newGenotype = newData.settings.genotype

  // Update recessive mode.
  newData.settings.genotype.recessive_mode = newValue
  // Apply necessary updates to `newGenotype` for chagne of recessive mode.
  const markers = ['recessive_index', 'recessive_father', 'recessive_mother']
  const oldValue =
    props.seqvarsQuery.settings.genotype.recessive_mode ?? 'disabled'
  if (oldValue !== 'disabled' && newValue === 'disabled') {
    // Clear any recessive markers and set to 'any'.
    for (const choice of newGenotype.sample_genotype_choices ?? []) {
      if (markers.includes(choice.genotype)) {
        choice.genotype = 'any'
      }
    }
  }

  // Store new data on server.
  await applyMutation(newData)
}

/**
 * Update the sample genotype choice value for a given sample.
 *
 * @param index The index of the sample genotype choice to update.
 * @param newValue The new value to set.
 * @param preHook A function to run before the update (used for updateRecessiveMode).
 */
const updateSampleGenotypeChoice = async (
  index: number,
  newValue: SeqvarsSampleGenotypePydantic,
  {
    postHook,
  }: {
    postHook?: (arg: SeqvarsQueryDetails) => SeqvarsQueryDetails
  } = { postHook: (arg: SeqvarsQueryDetails) => arg },
) => {
  // Copy old query and get shortcut to the genotype to update below.
  let newData = structuredClone(toRaw(props.seqvarsQuery))

  // Update the sample genotype choice.
  newData.settings.genotype.sample_genotype_choices![index] = newValue

  // Execute post-hook, e.g., to coerce recessive markers.
  if (postHook) {
    newData = postHook(newData)
  }

  // Store new data on server.
  await applyMutation(newData)
}

/** Coerce genotypes skipping the given sample name. */
const coerceRecessiveMarkers = (
  body: SeqvarsQueryDetails,
  skipSample: string,
) => {
  // Copy old query and get shortcut to the genotype to update below.
  const newData = structuredClone(body)
  const newGenotype = newData.settings.genotype

  // Apply changes as necessary to the local copy.
  const seen = new Set<string>()
  if (newGenotype.sample_genotype_choices !== undefined) {
    for (const choice of newGenotype.sample_genotype_choices) {
      if (choice.sample === skipSample) {
        seen.add(choice.genotype)
        break
      }
    }
  }
  for (const choice of newGenotype.sample_genotype_choices ?? []) {
    if (choice.sample !== skipSample) {
      if (seen.has(choice.genotype)) {
        choice.genotype = 'any'
      }
      seen.add(choice.genotype)
    }
  }

  return newData
}
</script>

<template>
  <div class="w-100 d-flex flex-column ga-2">
    <CollapsibleGroup
      title="Recessive Mode"
      :hints-enabled="hintsEnabled"
      hint="To find biallelic variants beyond homozygous ones in the index, you can use one of the recessive modes."
      :summary="
        RECESSIVE_MODE_ITEMS.find(
          (item) =>
            item.value === seqvarsQuery.settings.genotype.recessive_mode,
        )?.title ?? 'NONE'
      "
    >
      <template #default>
        <Item
          v-for="(item, index) in RECESSIVE_MODE_ITEMS"
          :key="index"
          :selected="
            seqvarsQuery.settings.genotype.recessive_mode === item.value
          "
          @click="() => updateRecessiveMode(item.value)"
        >
          {{ item.title }}
        </Item>
      </template>
    </CollapsibleGroup>

    <v-divider class="pb-1" />

    <div
      v-for="(choice, index) in seqvarsQuery.settings.genotype
        .sample_genotype_choices"
      :key="index"
      class="w-100 d-flex flex-row align-start ga-2"
    >
      <input
        :id="choice.sample"
        :checked="choice.enabled"
        @change="
          async () =>
            updateSampleGenotypeChoice(index, {
              ...choice,
              enabled: !choice.enabled,
            })
        "
        type="checkbox"
        style="margin-top: 6px"
      />

      <div
        v-if="choice !== undefined && choice.genotype !== undefined"
        class="w-100 d-flex flex-column"
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
          v-if="seqvarsQuery.settings.genotype.recessive_mode === 'disabled'"
          :genotype="choice.genotype"
          :include-no-call="choice.include_no_call"
          @update:genotype="
            async (genotype) =>
              await updateSampleGenotypeChoice(index, {
                ...choice,
                genotype,
              })
          "
          @update:include-no-call="
            async (include_no_call) =>
              await updateSampleGenotypeChoice(index, {
                ...choice,
                include_no_call,
              })
          "
        />

        <RecessiveControls
          v-else-if="seqvarsQuery.settings.genotype.sample_genotype_choices"
          :index="index"
          :sample-name="choice.sample"
          :genotype="choice.genotype"
          :include-no-call="choice.include_no_call"
          @update:genotype="
            async (genotype) =>
              await updateSampleGenotypeChoice(
                index,
                {
                  ...choice,
                  genotype,
                },
                {
                  postHook: (body: SeqvarsQueryDetails) =>
                    coerceRecessiveMarkers(body, choice.sample),
                },
              )
          "
          @update:include-no-call="
            async (include_no_call) =>
              await updateSampleGenotypeChoice(index, {
                ...choice,
                include_no_call,
              })
          "
        />
      </div>
    </div>
  </div>
</template>
