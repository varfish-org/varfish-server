<script setup lang="ts">
import { useQueryClient } from '@tanstack/vue-query'
import { SeqvarsQueryPresetsColumns } from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'
import { VForm } from 'vuetify/lib/components/index.mjs'

import {
  invalidateSeqvarQueryPresetsSetVersionKeys,
  useSeqvarQueryPresetsSetVersionRetrieveQuery,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
import {
  useSeqvarsQueryPresetsColumnsRetrieveQuery,
  useSeqvarsQueryPresetsColumnsUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetsColumns'
import { PresetSetVersionState } from '@/seqvars/stores/presets/types'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the current presets set. */
    presetSet?: string
    /** UUID of the current preset set version. */
    presetSetVersion?: string
    /** UUID of the query presets columns */
    columnsPresets?: string
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
/** Columns presets UUID as `ComputedRef` for queries. */
const presetsColumnsUuid = computed<string | undefined>(() => {
  return props.columnsPresets
})

/** Query with the currently selected presets set version. */
const presetsSetVersionRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQuery({
    presetsSetUuid,
    presetsSetVersionUuid,
  })
/** Query with the currently selected columns presets. */
const presetsColumnsRetrieveRes = useSeqvarsQueryPresetsColumnsRetrieveQuery({
  presetsSetVersionUuid,
  presetsColumnsUuid,
})
/** Mutation for updating the columns presets. */
const columnsPresetsUpdate = useSeqvarsQueryPresetsColumnsUpdateMutation()

/** Shortcut to the number of columns presets, used for rank. */
const maxRank = computed<number>(
  () =>
    presetsSetVersionRetrieveRes.data.value?.seqvarsquerypresetscolumns_set
      .length ?? 0,
)

/** Rules for data validation. */
const rules = {
  required: (value: any) => !!value || 'Required.',
}

/** Ref to the form. */
const formRef = ref<VForm | undefined>(undefined)

/** Helper to apply a patch to the current `presetsColumnsRetrieveRes.data.value`. */
const applyMutation = async (
  patch: Partial<SeqvarsQueryPresetsColumns>,
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
    presetsColumnsRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value === undefined ||
    presetsSetVersionRetrieveRes.data.value.status !==
      PresetSetVersionState.DRAFT
  ) {
    return
  } else {
    patch.rank = presetsColumnsRetrieveRes.data.value.rank
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
      const others = version.seqvarsquerypresetscolumns_set.filter((elem) => {
        if (elem.sodar_uuid === props.columnsPresets) {
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
          await columnsPresetsUpdate.mutateAsync({
            path: {
              querypresetssetversion: props.presetSetVersion,
              querypresetscolumns: other.sodar_uuid,
            },
            body: {
              ...other,
              rank: newOtherRank,
            },
          })
        } catch (error) {
          emit('message', {
            text: `Failed to update other columns presets rank: ${error}`,
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
    await columnsPresetsUpdate.mutateAsync({
      path: {
        querypresetssetversion: props.presetSetVersion,
        querypresetscolumns: presetsColumnsRetrieveRes.data.value.sodar_uuid,
      },
      body: {
        ...presetsColumnsRetrieveRes.data.value,
        ...patch,
      },
    })
    // Explicitely invalidate the query presets set version as the title and rank
    // can change and the version stores the category presets as well.
    invalidateSeqvarQueryPresetsSetVersionKeys(queryClient, {
      querypresetsset: props.presetSet,
      querypresetssetversion: props.presetSetVersion,
    })
  } catch (error) {
    emit('message', {
      text: `Failed to update columns presets: ${error}`,
      color: 'error',
    })
  }
}

const moveColumn = async (index: number, delta: number) => {
  if (
    presetsColumnsRetrieveRes.data.value === undefined ||
    presetsColumnsRetrieveRes.data.value.column_settings === undefined
  ) {
    return
  }
  const newIndex = index + delta
  if (
    newIndex < 0 ||
    newIndex >= presetsColumnsRetrieveRes.data.value.column_settings.length ||
    index < 0 ||
    index >= presetsColumnsRetrieveRes.data.value.column_settings.length
  ) {
    return
  }
  const columnSettings = [
    ...presetsColumnsRetrieveRes.data.value.column_settings,
  ]
  const tmp = columnSettings[index]
  columnSettings[index] = columnSettings[newIndex]
  columnSettings[newIndex] = tmp
  await applyMutation({
    column_settings: columnSettings,
  })
}
</script>

<template>
  <h4>
    Columns Presets &raquo;{{
      presetsColumnsRetrieveRes.data.value?.label ?? 'UNDEFINED'
    }}&laquo;
  </h4>

  <v-skeleton-loader
    v-if="presetsColumnsRetrieveRes.status.value !== 'success'"
    type="article"
  />

  <v-form v-else ref="formRef">
    <v-text-field
      :model-value="presetsColumnsRetrieveRes.data.value?.label"
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
            presetsColumnsRetrieveRes.data.value?.rank === undefined ||
            presetsColumnsRetrieveRes.data.value?.rank <= 1
          "
          @click="applyMutation({}, -1)"
        >
          Move Up
        </v-btn>
        <v-btn
          prepend-icon="mdi-arrow-down-circle-outline"
          :disabled="
            props.readonly ||
            presetsColumnsRetrieveRes.data.value?.rank === undefined ||
            presetsColumnsRetrieveRes.data.value?.rank >= maxRank
          "
          @click="applyMutation({}, 1)"
        >
          Move Down
        </v-btn>
      </v-btn-group>
    </div>

    <v-list lines="two">
      <v-list-item
        v-for="(item, index) in presetsColumnsRetrieveRes.data.value
          ?.column_settings ?? []"
        :key="index"
        :title="item.label"
        :subtitle="item.description ?? '-'"
        class="bg-grey-lighten-3 rounded-lg mb-2"
      >
        <template #prepend>
          <div class="mr-6"># {{ index + 1 }}</div>
        </template>
        <template #append>
          <div class="d-flex flex-row align-self-end">
            <v-switch
              v-model="item.visible"
              hide-details
              :color="item.visible ? 'primary' : 'red'"
              variant="outlined"
              class="mr-3"
            />

            <v-number-input
              v-model="item.width"
              :reverse="false"
              density="compact"
              label="width"
              :hide-input="false"
              :inset="true"
              variant="outlined"
              class="mr-3"
              hide-details
              :step="10"
            />
            <v-btn-group variant="outlined" divided>
              <v-btn
                icon="mdi-arrow-up"
                :disabled="index === 0"
                size="small"
                @click="moveColumn(index, -1)"
              />
              <v-btn
                icon="mdi-arrow-down"
                :disabled="
                  index ===
                  presetsColumnsRetrieveRes.data.value!.column_settings!
                    .length -
                    1
                "
                size="small"
                @click="moveColumn(index, 1)"
              />
            </v-btn-group>
          </div>
        </template>
      </v-list-item>
    </v-list>
  </v-form>
</template>
