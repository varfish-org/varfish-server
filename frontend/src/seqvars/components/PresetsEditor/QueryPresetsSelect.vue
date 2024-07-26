<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { useRouter } from 'vue-router'
import {
  EditableState,
  getEditableStateLabel,
} from '@/seqvars/stores/presets/types'

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

/** The string value from the name entry dialog; component state. */
const cloneDialogModel = ref<string>('')
/** Whether the name entry dialog is shown; component state. */
const cloneDialogShow = ref<boolean>(true)
/** The entity to clone */
const cloneDialogEntity = ref<'presets' | 'presetsset'>('presetsset')
/** Whether the "publish" confirmation dialog is shown; component state. */
const publishDialogShow = ref<boolean>(false)
/** Whether the "discard" confirmation dialog is shown; component state. */
const discardDialogShow = ref<boolean>(false)

/**
 * Helper to auto fill `cloneDialogModel` with the name of the preset set.
 */
const autoFillCloneDialogModel = () => {
  if (cloneDialogEntity.value === 'presetsset' && selectedPresetSetUuid.value) {
    const presetSet = seqvarsPresetsStore.presetSets.get(selectedPresetSetUuid.value)
    if (presetSet) {
      cloneDialogModel.value = `Copy of ${presetSet.label}`
    }
  } else {
    cloneDialogModel.value = ''
  }
}

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
    <v-row no-gutters class="d-flex flex-nowrap" justify="space-between">
      <v-col class="flex-grow-1 flex-shrink-0">
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
      <v-col class="flex-grow-1 flex-shrink-0 pl-3">
        <v-select
          v-model="selectedPresetSetVersionUuid"
          :items="presetSetVersionItems"
          :item-props="
            (item: SeqvarsQueryPresetsSetVersionDetails) => {
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

      <v-col
        class="flex-grow-0 flex-shrink-1 pl-3"
        v-if="presetSetVersion"
        cols="auto"
      >
        <div class="ml-auto">
          <v-menu>
            <template v-slot:activator="{ props }">
              <v-btn icon="mdi-dots-vertical" v-bind="props"></v-btn>
            </template>

            <v-list>
              <v-list-subheader class="text-uppercase">
                Presets Version
              </v-list-subheader>
              <template
                v-if="
                  seqvarsPresetsStore.getEditableState(presetSetVersion) ===
                  EditableState.EDITABLE
                "
              >
              <v-list-item
                  prepend-icon="mdi-publish"
                  title="Publish as Active"
                  link
                  @click="publishDialogShow = true"
                />
                <v-list-item
                  prepend-icon="mdi-trash-can-outline"
                  title="Discard"
                  link
                  @click="discardDialogShow = true"
                />
              </template>
              <template v-else>
                <v-list-item
                  prepend-icon="mdi-publish"
                  title="Cannot Publish (Only Draft)"
                  disabled
                />
                <v-list-item
                  prepend-icon="mdi-trash-can-outline"
                  title="Cannot Discard (Only Draft)"
                  disabled
                />
              </template>
              <template
                v-if="
                  seqvarsPresetsStore.getEditableState(presetSetVersion) ===
                  EditableState.IS_ACTIVE
                "
              >
                <v-list-item
                  prepend-icon="mdi-file-document-plus-outline"
                  title="New Version"
                  link
                  @click="cloneDialogEntity = 'presets'; cloneDialogShow = true"
                />
              </template>
              <template v-else>
                <v-list-item
                  prepend-icon="mdi-file-document-plus-outline"
                  title="No New Version (Only Active)"
                  disabled
                />
              </template>

              <v-list-subheader class="text-uppercase">
                Presets Set
              </v-list-subheader>
              <template
                v-if="
                  seqvarsPresetsStore.getEditableState(presetSetVersion) ===
                  EditableState.IS_FACTORY_DEFAULT
                "
              >
                <v-list-item
                  prepend-icon="mdi-folder-multiple-plus-outline"
                  title="Clone Factory Defaults"
                  link
                  @click="cloneDialogEntity = 'presetsset'; autoFillCloneDialogModel(); cloneDialogShow = true"
                />
              </template>
              <template v-else>
                <v-list-item
                  prepend-icon="mdi-folder-multiple-plus-outline"
                  title="Clone Preset Set"
                  link
                />
              </template>
            </v-list>
          </v-menu>
        </div>
      </v-col>
    </v-row>
    <v-row v-if="presetSetVersion" no-gutters class="d-flex flex-nowrap">
      <v-col class="pt-3">
        <v-alert
          :icon="
            seqvarsPresetsStore.getEditableState(presetSetVersion) ===
            EditableState.IS_FACTORY_DEFAULT
              ? 'mdi-factory'
              : 'mdi-information'
          "
        >
          {{
            getEditableStateLabel(
              seqvarsPresetsStore.getEditableState(presetSetVersion),
            )
          }}
        </v-alert>
      </v-col>
    </v-row>
  </v-sheet>

  <!-- Dialog for cloning / new version -->
  <v-dialog v-model="cloneDialogShow" persistent max-width="600px">
    <v-card>
      <template v-if="cloneDialogEntity === 'presetsset'">
        <v-card-title>Clone Presets</v-card-title>
        <v-card-text>
          <v-alert icon="mdi-information" type="info">
            Only the latest version of the presets set will be cloned.
          </v-alert>
        </v-card-text>
        <v-card-text>
          <v-text-field
            v-model="cloneDialogModel"
            label="Name"
            hint="Enter a name for the new presets."
            persistent-hint
          ></v-text-field>
        </v-card-text>
      </template>
      <template v-else>
        <v-card-title>Create New Version</v-card-title>
        <v-card-text>
          Confirm to create new draft version.
        </v-card-text>
      </template>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn @click="cloneDialogShow = false" rounded="xs">Cancel</v-btn>
        <v-btn
          @click="doCloneEntity()" rounded="xs"
        >
        Clone
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
