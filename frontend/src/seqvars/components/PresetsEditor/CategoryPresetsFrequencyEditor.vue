<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'
import { merge } from 'object-deep-merge'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsFrequencyRetrieveQuery,
  useSeqvarsQueryPresetsFrequencyUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsFrequency'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import { parseToFloatOrNull, parseToIntOrNull } from './lib/utils'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets frequency */
    frequencyPresets?: string
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** This component's events. */
const emit = defineEmits<{
  /** Emit event to show a message. */
  message: [message: SnackbarMessage]
}>()

/** The `QueryClient` for explicit invalidation.*/
const queryClient = useQueryClient()

/** Presets set UUID as `ComputedRef` for queries. */
const presetsSetUuid = computed<string | undefined>(() => {
  return props.presetSet
})
/** Presets set version UUID as `ComputedRef` for queries. */
const presetsSetVersionUuid = computed<string | undefined>(() => {
  return props.presetSetVersion
})
/** Frequency presets UUID as `ComputedRef` for queries. */
const presetsFrequencyUuid = computed<string | undefined>(() => {
  return props.frequencyPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected frequency presets. */
const presetsFrequencyRetrieveRes =
  useSeqvarsQueryPresetsFrequencyRetrieveQuery({
    presetsSetVersionUuid,
    presetsFrequencyUuid,
  })
/** Mutation for updating the frequency presets. */
const frequencyPresetsUpdate = useSeqvarsQueryPresetsFrequencyUpdateMutation()

/** Shortcut to the number of frequency presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetsfrequency_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsFrequencyRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsFrequency>,
  rankDelta: number = 0,
) => {
  // Guard against invalid form data.
  const validateResult = await formRef.value?.validate()
  if (validateResult?.valid !== true) {
    return
  }
  // Short-circuit if patch is undefined or presets version undefine dor not in draft state.
  if (
    props.presetSet === undefined ||
    props.presetSetVersion === undefined ||
    presetsFrequencyRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsFrequencyRetrieveRes.data.value.rank
  }

  // Helper to update the rank of the other item as well.
  const updateOtherItemRank = async () => {
    if (props.presetSetVersion !== undefined && rankDelta !== 0) {
      const version = presetsSetVersionRetrieveRes.data.value
      if (
        version === undefined ||
        patch.rank === undefined ||
        patch.rank + rankDelta < 1 ||
        patch.rank + rankDelta > maxRank.value
      ) {
        // Guard against invalid or missing data.
        return
      }
      // Find the next smaller or larger item, sort by rank.
      const others = version.seqvarsquerypresetsfrequency_set.filter((elem) => {
        if (elem.sodar_uuid === props.frequencyPresets) {
          return false
        }
        if (rankDelta < 0) {
          return (elem.rank ?? 0) < (patch?.rank ?? 0)
        } else {
          return (elem.rank ?? 0) > (patch?.rank ?? 0)
        }
      })
      others.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
      // Then, pick the other item to flip ranks with.
      const other = { ...others[rankDelta < 0 ? others.length - 1 : 0] }
      // Store the other's rank in `data.rank` and update other via API.
      if (!!other) {
        const newOtherRank = patch.rank
        patch.rank = other.rank
        other.rank = newOtherRank
        try {
          await frequencyPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetsfrequency: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other frequency presets rank: ${error}`,
            color: 'error',
          })
        }
      }
    }
  }

  // First, apply rank update to other data object and to patch if applicable.
  // On success, the patch to the data object.
  try {
    await updateOtherItemRank()
    await frequencyPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetsfrequency:
          presetsFrequencyRetrieveRes.data.value.sodar_uuid,
      },
      body: merge<
        Partial<SeqvarsQueryPresetsFrequency>,
        SeqvarsQueryPresetsFrequency
      >(presetsFrequencyRetrieveRes.data.value ?? {}, patch),
    })
    // Explicitely invalidate the query presets set version as the title and rank
    // can change and the version stores the category presets as well.
    invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
      querypresetsset: props.presetSet,
      querypresetssetversion: props.presetSetVersion,
    })
  } catch (error) {
    emit('message', {
      text: `Failed to update frequency presets: ${error}`,
      color: 'error',
    })
  }
}
</script>

<template>
  <h3>
    Frequency Presets &raquo;{{
      presetsFrequencyRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h3>

  <v-skeleton-loader
    v-if="presetsFrequencyRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsFrequencyRetrieveRes.data.value?.label"
      :rules="[rules.required]"
      label="Label"
      clearable
      :disabled="readonly"
      @update:model-value="
        (label) =>
          applyMutation({
            label,
          })
      "
    />

    <div>
      <v-btn-group variant="outlined" divided>
        <v-btn
          prepend-icon="mdi-arrow-up-circle-outline"
          :disabled="
            props.readonly ||
            presetsFrequencyRetrieveRes.data.value?.rank === undefined ||
            presetsFrequencyRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsFrequencyRetrieveRes.data.value?.rank === undefined ||
            presetsFrequencyRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-table density="compact">
      <thead>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center">freq. [%]</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="px-1">gnomAD exomes</th>
          <td class="px-1">
            <v-checkbox
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_exomes?.enabled
              "
              hide-details
              :disabled="readonly"
              @update:model-value="
                applyMutation({
                  gnomad_exomes: {
                    enabled:
                      !presetsFrequencyRetrieveRes.data.value?.gnomad_exomes
                        ?.enabled,
                  },
                })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_exomes?.max_hom
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hom) =>
                  applyMutation({
                    gnomad_exomes: {
                      max_hom: parseToIntOrNull(max_hom),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_exomes?.max_het
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_het) =>
                  applyMutation({
                    gnomad_exomes: {
                      max_het: parseToIntOrNull(max_het),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_exomes?.max_hemi
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hemi) =>
                  applyMutation({
                    gnomad_exomes: {
                      max_hemi: parseToIntOrNull(max_hemi),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_exomes?.max_af
              "
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
              @update:model-value="
                (max_af) =>
                  applyMutation({
                    gnomad_exomes: {
                      max_af: parseToFloatOrNull(max_af),
                    },
                  })
              "
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD genomes</th>
          <td class="px-1">
            <v-checkbox
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_genomes?.enabled
              "
              hide-details
              :disabled="readonly"
              @update:model-value="
                applyMutation({
                  gnomad_genomes: {
                    enabled:
                      !presetsFrequencyRetrieveRes.data.value?.gnomad_genomes
                        ?.enabled,
                  },
                })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_genomes?.max_hom
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hom) =>
                  applyMutation({
                    gnomad_genomes: {
                      max_hom: parseToIntOrNull(max_hom),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_genomes?.max_het
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_het) =>
                  applyMutation({
                    gnomad_genomes: {
                      max_het: parseToIntOrNull(max_het),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_genomes?.max_hemi
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hemi) =>
                  applyMutation({
                    gnomad_genomes: {
                      max_hemi: parseToIntOrNull(max_hemi),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_genomes?.max_af
              "
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
              @update:model-value="
                (max_af) =>
                  applyMutation({
                    gnomad_genomes: {
                      max_af: parseToFloatOrNull(max_af),
                    },
                  })
              "
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD MT</th>
          <td class="px-1">
            <v-checkbox
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_mtdna?.enabled
              "
              hide-details
              :disabled="readonly"
              @update:model-value="
                applyMutation({
                  gnomad_mtdna: {
                    enabled:
                      !presetsFrequencyRetrieveRes.data.value?.gnomad_mtdna
                        ?.enabled,
                  },
                })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_mtdna?.max_hom
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hom) =>
                  applyMutation({
                    gnomad_mtdna: {
                      max_hom: parseToIntOrNull(max_hom),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_mtdna?.max_het
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_het) =>
                  applyMutation({
                    gnomad_mtdna: {
                      max_het: parseToIntOrNull(max_het),
                    },
                  })
              "
            />
          </td>
          <td class="px-1 text-center text-grey">N/A</td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.gnomad_mtdna?.max_af
              "
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
              @update:model-value="
                (max_af) =>
                  applyMutation({
                    gnomad_mtdna: {
                      max_af: parseToFloatOrNull(max_af),
                    },
                  })
              "
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">HelixMtDb</th>
          <td class="px-1">
            <v-checkbox
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.helixmtdb?.enabled
              "
              hide-details
              :disabled="readonly"
              @update:model-value="
                applyMutation({
                  helixmtdb: {
                    enabled:
                      !presetsFrequencyRetrieveRes.data.value?.helixmtdb
                        ?.enabled,
                  },
                })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.helixmtdb?.max_hom
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hom) =>
                  applyMutation({
                    helixmtdb: {
                      max_hom: parseToIntOrNull(max_hom),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.helixmtdb?.max_het
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_het) =>
                  applyMutation({
                    helixmtdb: {
                      max_het: parseToIntOrNull(max_het),
                    },
                  })
              "
            />
          </td>
          <td class="px-1 text-center text-grey">N/A</td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.helixmtdb?.max_af
              "
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
              :disabled="readonly"
              @update:model-value="
                (max_af) =>
                  applyMutation({
                    helixmtdb: {
                      max_af: parseToFloatOrNull(max_af),
                    },
                  })
              "
            />
          </td>
        </tr>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center"># carriers</th>
        </tr>
        <tr>
          <th class="px-1">In-House</th>
          <td class="px-1">
            <v-checkbox
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.inhouse?.enabled
              "
              hide-detail
              :disabled="readonly"
              @update:model-value="
                applyMutation({
                  inhouse: {
                    enabled:
                      !presetsFrequencyRetrieveRes.data.value?.inhouse?.enabled,
                  },
                })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.inhouse?.max_hom
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hom) =>
                  applyMutation({
                    inhouse: {
                      max_hom: parseToIntOrNull(max_hom),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.inhouse?.max_het
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_het) =>
                  applyMutation({
                    inhouse: {
                      max_het: parseToIntOrNull(max_het),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.inhouse?.max_hemi
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_hemi) =>
                  applyMutation({
                    inhouse: {
                      max_hemi: parseToIntOrNull(max_hemi),
                    },
                  })
              "
            />
          </td>
          <td class="px-1">
            <v-text-field
              :model-value="
                presetsFrequencyRetrieveRes.data.value?.inhouse?.max_carriers
              "
              hide-details
              density="compact"
              clearable
              type="number"
              :disabled="readonly"
              @update:model-value="
                (max_carriers) =>
                  applyMutation({
                    inhouse: {
                      max_carriers: parseToIntOrNull(max_carriers),
                    },
                  })
              "
            />
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-form>
</template>
