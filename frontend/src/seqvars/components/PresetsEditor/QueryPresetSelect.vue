<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsService,
} from '@varfish-org/varfish-api/lib'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { useRouter } from 'vue-router'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** Identifier of the current preset set. */
  presetSet?: string
}>()

/** Global router instance. */
const router = useRouter()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The currently selected item, manged through route/props; component state */
const selectedItem = computed<string | undefined>({
  get() {
    return props.presetSet
  },
  set(value) {
    if (value) {
      router.push({ params: { presetSet: value } })
    }
  },
})

/** (Re-)initialize the stores. */
const initializeStores = async () => {
  await Promise.all([seqvarsPresetsStore.initialize(props.projectUuid)])
  // Set the current preset set after initialization via route unless previously set.
  if (!props.presetSet && seqvarsPresetsStore.presetSets?.size) {
    const presetSet = Array.from(seqvarsPresetsStore.presetSets.values())[0]
      .sodar_uuid
    router.push({ params: { presetSet } })
  }
}

/** The items to display in the presets list. */
const presetsItems = computed<SeqvarsQueryPresetsSet[]>(() => {
  const result = Array.from(seqvarsPresetsStore.presetSets.values()).sort(
    (a, b) => {
      const aBuiltin =
        seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(a.sodar_uuid)
      const bBuiltin =
        seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(b.sodar_uuid)
      return (
        (aBuiltin ? 0 : 1000) +
        (a.rank ?? 0) -
        ((bBuiltin ? 0 : 1000) + (b.rank ?? 0))
      )
    },
  )

  return result
})

// Initialize case list store on mount.
onMounted(async () => {
  await initializeStores()
})
// Re-initialize case list store when the project changes.
watch(
  () => props.projectUuid,
  async () => {
    await initializeStores()
  },
)
</script>

<template>
  <v-sheet class="pa-3">
    <v-row no-gutters class="d-flex flex-nowrap">
      <v-col class="flex-grow-1">
        <v-select
          v-model="selectedItem"
          :items="presetsItems"
          :item-props="
            (item: SeqvarsQueryPresetsSet) => {
              const isBuiltin =
                seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
                  item.sodar_uuid,
                )
              return {
                value: item.sodar_uuid,
                title: item.label,
                subtitle: isBuiltin ? 'Factory Default' : 'User-Defined',
              }
            }
          "
          :loading="seqvarsPresetsStore.storeState.serverInteractions !== 0"
          label="Presets Set"
          hint="Select a preset to work with"
          persistent-hint
        ></v-select>
      </v-col>

      <span class="pl-3">
        <v-btn variant="outlined" rounded="sm">
          <v-icon>mdi-content-copy</v-icon>
          Clone Preset
        </v-btn>
      </span>
      <span class="pl-3">
        <v-btn variant="outlined" rounded="sm">
          <v-icon>mdi-file-document-edit</v-icon>
          Save
        </v-btn>
      </span>
      <span class="pl-3">
        <v-btn variant="outlined" rounded="sm" color="error ">
          <v-icon>mdi-delete-forever</v-icon>
          Delete
        </v-btn>
      </span>
    </v-row>
  </v-sheet>
</template>
