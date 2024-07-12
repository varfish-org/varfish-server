<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { useRouter } from 'vue-router'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current preset set version. */
  presetSetVersion?: string
}>()

/** Global router instance. */
const router = useRouter()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The currently selected preset set, manged through route/props; component state */
const selectedPresetSetUuid = computed<string | undefined>({
  get() {
    return props.presetSet
  },
  set(value) {
    if (value) {
      router.push({ params: { presetSet: value } })
    }
  },
})

/** The currently selected preset set version, manged through route/props; component state */
const selectedPresetSetVersionUuid = computed<string | undefined>({
  get() {
    return props.presetSetVersion
  },
  set(value) {
    if (value) {
      router.push({ params: { presetSetVersion: value } })
    }
  },
})

/** Whether the currently selected preset is a factory default. */
const selectedIsFactoryDefault = computed<boolean>(() => {
  return seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
    selectedPresetSetUuid.value ?? 'undefined',
  )
})

/**
 * The items to display in the preset set list.
 *
 * Ensures a sorted order by rank where factory defaults come first.
 */
const presetSetItems = computed<SeqvarsQueryPresetsSet[]>(() => {
  return Array.from(seqvarsPresetsStore.presetSets.values()).sort((a, b) => {
    const aBuiltin = seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      a.sodar_uuid,
    )
    const bBuiltin = seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
      b.sodar_uuid,
    )
    return (
      (aBuiltin ? 0 : 1000) +
      (a.rank ?? 0) -
      (bBuiltin ? 0 : 1000) -
      (b.rank ?? 0)
    )
  })
})

/**
 * The items to display in the preset set version list.
 *
 * Ensures the ones for the selected version are displayed and sorted by `(major, minor)` version.
 */
const presetSetVersionItems = computed<SeqvarsQueryPresetsSetVersionDetails[]>(
  () => {
    return Array.from(seqvarsPresetsStore.presetSetVersions.values())
      .filter((item) => {
        return item.presetsset.sodar_uuid === selectedPresetSetUuid.value
      })
      .sort((a, b) => {
        return (
          (a.version_major ?? 0) * 1000 +
          (a.version_minor ?? 0) -
          (b.version_major ?? 0) * 1000 -
          (b.version_minor ?? 0)
        )
      })
  },
)

/** (Re-)initialize the stores if necessary. */
const initializeStores = async () => {
  await seqvarsPresetsStore.initialize(props.projectUuid)
}

/**
 * Companion to initializeStores()
 *
 * Ensures that when no preset has been selected yet via props then this is done
 * via the router.
 */
const selectPresetSetAndVersion = () => {
  let presetSet = props.presetSet
  if (!presetSet && presetSetItems.value.length) {
    presetSet = presetSetItems.value[0].sodar_uuid
  }

  let presetSetVersion = props.presetSetVersion
  if (!presetSetVersion && presetSetVersionItems.value.length) {
    presetSetVersion = presetSetVersionItems.value[0].sodar_uuid
  }

  if (
    presetSet !== props.presetSet ||
    presetSetVersion !== props.presetSetVersion
  ) {
    router.push({ params: { presetSet, presetSetVersion } })
  }
}

/**
 * Trigger selection of preset set and version when the store, and/or
 * the computed component state changes.
 */
watch(
  () => [
    seqvarsPresetsStore.storeState?.state,
    presetSetItems.value,
    presetSetVersionItems.value,
  ],
  () => {
    selectPresetSetAndVersion()
  },
)

/* Initialize case list store on mount. */
onMounted(async () => {
  await initializeStores()
  selectPresetSetAndVersion()
})

/* Re-initialize case list store when the project changes. */
watch(
  () => props.projectUuid,
  async () => {
    await initializeStores()
    selectPresetSetAndVersion()
  },
)
</script>

<template>
  <v-sheet class="pa-3">
    <v-row no-gutters class="d-flex flex-nowrap">
      <v-col class="flex-grow-1">
        <v-select
          v-model="selectedPresetSetUuid"
          :items="presetSetItems"
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
          hint="Select preset set to work with."
          persistent-hint
        ></v-select>
      </v-col>
      <v-col class="flex-grow-1 pl-3">
        <v-select
          v-model="selectedPresetSetVersionUuid"
          :items="presetSetVersionItems"
          :item-props="
            (item: SeqvarsQueryPresetsSetVersionDetails) => {
              const isBuiltin =
                seqvarsPresetsStore.factoryDefaultPresetSetUuids.includes(
                  item.sodar_uuid,
                )
              return {
                value: item.sodar_uuid,
                title: item
                  ? `${item.version_major}.${item.version_minor}`
                  : undefined,
                subtitle: `${item.status}`,
              }
            }
          "
          :loading="seqvarsPresetsStore.storeState.serverInteractions !== 0"
          label="Presets Set Version"
          hint="Select the version to work with."
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
        <v-btn
          variant="outlined"
          rounded="sm"
          :disabled="selectedIsFactoryDefault"
        >
          <v-icon>mdi-file-document-edit</v-icon>
          Save
        </v-btn>
      </span>
      <span class="pl-3">
        <v-btn
          variant="outlined"
          rounded="sm"
          color="error"
          :disabled="selectedIsFactoryDefault"
        >
          <v-icon>mdi-delete-forever</v-icon>
          Delete
        </v-btn>
      </span>
    </v-row>
  </v-sheet>
</template>
