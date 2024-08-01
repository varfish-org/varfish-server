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
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current presets set. */
  presetSet?: string
  /** UUID of the current presets set version. */
  presetSetVersion?: string
}>()

/** This component's events. */
const emit = defineEmits<{
  message: [message: SnackbarMessage]
}>()

/** Global router instance. */
const router = useRouter()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** The currently selected presets set, manged through route/props; component state */
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

/** The currently selected presets set version, manged through route/props; component state */
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
/** Whether the clone presets set dialog is shown; component state. */
const cloneDialogShow = ref<boolean>(false)
/** Whether to show the dialog for confirming presets set deletion; component state. */
const deleteDialogShow = ref<boolean>(false)
/** Whether the new version dialog is shown; component state. */
const newVersionDialogShow = ref<boolean>(false)
/** Whether the "publish" confirmation dialog is shown; component state. */
const publishDialogShow = ref<boolean>(false)
/** Whether the "discard" confirmation dialog is shown; component state. */
const discardDialogShow = ref<boolean>(false)
/** The string value from the rename dialog; component state. */
const renameDialogModel = ref<string>('')
/** Whether the "rename" dialog is shown; component state. */
const renameDialogShow = ref<boolean>(false)

/**
 * Helper to auto fill `cloneDialogModel` with the name of the presets set, then show dialog.
 */
const showCloneDialog = () => {
  // guard against undefined presets set
  if (selectedPresetSetUuid.value) {
    const presetSet = seqvarsPresetsStore.presetSets.get(
      selectedPresetSetUuid.value,
    )
    if (presetSet) {
      cloneDialogModel.value = `Copy of ${presetSet.label}`
    } else {
      cloneDialogModel.value = ''
    }

    cloneDialogShow.value = true
  }
}

/**
 * Helper to execute the cloning.
 */
const doClone = async () => {
  // guard against undefined presets set
  if (props.presetSet !== undefined) {
    let presetsSet, presetsSetVersion
    try {
      ;[presetsSet, presetsSetVersion] =
        await seqvarsPresetsStore.copyPresetSet(
          props.presetSet,
          cloneDialogModel.value,
        )
    } catch (e) {
      emit('message', {
        text: `Cloning presets set failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets set was cloned.`,
      color: 'success',
    })
    router.push({
      params: {
        presetSet: presetsSet.sodar_uuid,
        presetSetVersion: presetsSetVersion.sodar_uuid,
      },
    })
    cloneDialogShow.value = false
  }
}

/**
 * Helper to auto fill `renameDialogModel` with the name of the presets set, then show dialog.
 */
const showRenameDialog = () => {
  // guard against undefined presets set
  if (selectedPresetSetUuid.value) {
    const presetSet = seqvarsPresetsStore.presetSets.get(
      selectedPresetSetUuid.value,
    )
    if (presetSet) {
      renameDialogModel.value = presetSet.label
    } else {
      renameDialogModel.value = ''
    }

    renameDialogShow.value = true
  }
}

/**
 * Helper to execute the renaming.
 */
const doRename = async () => {
  // guard against undefined presets set
  if (selectedPresetSetUuid.value) {
    try {
      await seqvarsPresetsStore.updatePresetsSet(selectedPresetSetUuid.value, {
        label: renameDialogModel.value,
      })
    } catch (e) {
      emit('message', {
        text: `Renaming presets set failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets set was renamed.`,
      color: 'success',
    })
    renameDialogShow.value = false
  }
}

/**
 * Helper to delete a presets set.
 */
const doDeletePresetsSet = async () => {
  // guard against undefined presets set
  if (selectedPresetSetUuid.value) {
    try {
      await seqvarsPresetsStore.deletePresetsSet(selectedPresetSetUuid.value)
    } catch (e) {
      emit('message', {
        text: `Deleting presets set failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets set was deleted.`,
      color: 'success',
    })
    router.push({ params: { presetSet: '', presetSetVersion: '' } })
    deleteDialogShow.value = false
  }
}

/**
 * Helper to publish a presets set version.
 */
const doPublishVersion = async () => {
  // guard against undefined version
  if (selectedPresetSetVersionUuid.value) {
    try {
      await seqvarsPresetsStore.publishPresetSetVersion(
        selectedPresetSetVersionUuid.value,
      )
    } catch (e) {
      emit('message', {
        text: `Publishing presets version failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets version was published.`,
      color: 'success',
    })
    publishDialogShow.value = false
  }
}

/**
 * Helper to discard a presets set version.
 */
const doDiscardVersion = async () => {
  // guard against undefined version
  if (selectedPresetSetVersionUuid.value) {
    try {
      await seqvarsPresetsStore.discardPresetSetVersion(
        selectedPresetSetVersionUuid.value,
      )
    } catch (e) {
      emit('message', {
        text: `Discarding presets version failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets version was discarded.`,
      color: 'success',
    })
    router.push({ params: { presetSetVersion: '' } })
    discardDialogShow.value = false
  }
}

/**
 * Helper to show the new version dialog.
 */
const showNewVersionDialog = () => {
  // guard against undefined version
  if (selectedPresetSetVersionUuid.value) {
    newVersionDialogShow.value = true
  }
}

/**
 * Helper to execute the creation of a new version.
 */
const doNewVersion = async () => {
  // guard against undefined version
  if (selectedPresetSetVersionUuid.value) {
    let presetSetVersion
    try {
      presetSetVersion = await seqvarsPresetsStore.copyPresetSetVersion(
        selectedPresetSetVersionUuid.value,
      )
    } catch (e) {
      emit('message', {
        text: `Creating new presets version failed: ${e}`,
        color: 'error',
      })
      return
    }
    emit('message', {
      text: `Presets version created successfully.`,
      color: 'success',
    })
    router.push({ params: { presetSetVersion: presetSetVersion.sodar_uuid } })
    newVersionDialogShow.value = false
  }
}

/**
 * The items to display in the presets set list.
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
 * The items to display in the presets set version list.
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
  try {
    await seqvarsPresetsStore.initialize(props.projectUuid)
  } catch (e) {
    emit('message', {
      text: `Communication with server failed: ${e}`,
      color: 'error',
    })
  }
}

/**
 * Companion to initializeStores()
 *
 * Ensures that when no preset has been selected yet via props then this is done
 * via the router.
 *
 * @param force Whether to force the selection of the presets set and version.
 */
const selectPresetSetAndVersion = (force: boolean = false) => {
  let presetSet = props.presetSet
  if (force || (!presetSet && presetSetItems.value.length)) {
    presetSet = presetSetItems.value[0].sodar_uuid
  }

  let presetSetVersion = props.presetSetVersion
  if (force || (!presetSetVersion && presetSetVersionItems.value.length)) {
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
 * Trigger selection of presets set and version when the store, and/or
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
  <div>
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
            hint="Select presets set to work with."
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
          v-if="presetSetVersion"
          class="flex-grow-0 flex-shrink-1 pl-3"
          cols="auto"
        >
          <div class="ml-auto">
            <v-menu>
              <template #activator="{ props: localProps }">
                <v-btn
                  icon="mdi-dots-vertical"
                  v-bind="localProps"
                  :loading="
                    seqvarsPresetsStore.storeState.serverInteractions > 0
                  "
                ></v-btn>
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
                    title="New Draft"
                    link
                    @click="showNewVersionDialog()"
                  />
                </template>
                <template v-else>
                  <v-list-item
                    prepend-icon="mdi-file-document-plus-outline"
                    title="No New Draft (Only Active)"
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
                    @click="showCloneDialog()"
                  />
                  <v-list-item
                    prepend-icon="mdi-file-edit-outline"
                    title="Cannot Rename (Factory Defaults)"
                    disabled
                  />
                  <v-list-item
                    prepend-icon="mdi-trash-can-outline"
                    title="Cannot Delete (Factory Defaults)"
                    disabled
                  />
                </template>
                <template v-else>
                  <v-list-item
                    prepend-icon="mdi-folder-multiple-plus-outline"
                    title="Clone Presets Set"
                    link
                    @click="showCloneDialog()"
                  />
                  <v-list-item
                    prepend-icon="mdi-file-edit-outline"
                    title="Rename Presets Set"
                    link
                    @click="showRenameDialog()"
                  />
                  <v-list-item
                    prepend-icon="mdi-trash-can-outline"
                    title="Delete Presets Set"
                    color="error"
                    link
                    @click="deleteDialogShow = true"
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

    <!-- Dialog for cloning presets set -->
    <v-dialog v-model="cloneDialogShow" max-width="600px">
      <v-card>
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
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn rounded="xs" @click="cloneDialogShow = false"> Cancel </v-btn>
          <v-btn rounded="xs" @click="doClone()"> Clone </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for creating new version -->
    <v-dialog v-model="newVersionDialogShow" max-width="600px">
      <v-card>
        <v-card-title>Create New Version</v-card-title>
        <v-card-text> Confirm to create new draft version. </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn rounded="xs" @click="newVersionDialogShow = false">
            Cancel
          </v-btn>
          <v-btn rounded="xs" @click="doNewVersion()"> Create New Draft </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for deleting presets set -->
    <v-dialog v-model="deleteDialogShow" max-width="600px">
      <v-card>
        <v-card-title>Delete Presets Set</v-card-title>
        <v-card-text> Confirm to delete the presets set. </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn rounded="xs" @click="deleteDialogShow = false"> Cancel </v-btn>
          <v-btn rounded="xs" color="error" @click="doDeletePresetsSet()">
            Delete Presets Set
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for renaming presets set -->
    <v-dialog v-model="renameDialogShow" max-width="600px">
      <v-card>
        <v-card-title>Rename Presets</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="renameDialogModel"
            label="Name"
            hint="Adjust the presets set name."
            persistent-hint
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn rounded="xs" @click="renameDialogShow = false"> Cancel </v-btn>
          <v-btn rounded="xs" @click="doRename()"> Rename </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for publishing presets set version -->
    <v-dialog v-model="publishDialogShow" max-width="600px">
      <v-card>
        <v-card-title>Publish Presets Version</v-card-title>
        <v-card-text> Confirm to publish the presets version. </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn rounded="xs" @click="publishDialogShow = false">
            Cancel
          </v-btn>
          <v-btn rounded="xs" color="success" @click="doPublishVersion()">
            Publish Presets Version
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog for discarding presets set version -->
    <v-dialog v-model="discardDialogShow" max-width="600px">
      <v-card>
        <v-card-title>Discard Presets Version</v-card-title>
        <template v-if="presetSetVersionItems.length > 1">
          <v-card-text> Confirm to discard the presets version. </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn rounded="xs" @click="discardDialogShow = false">
              Cancel
            </v-btn>
            <v-btn rounded="xs" color="error" @click="doDiscardVersion()">
              Discard Presets
            </v-btn>
          </v-card-actions>
        </template>
        <template v-else>
          <v-card-text> Cannot discard only version. </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn rounded="xs" @click="discardDialogShow = false">
              Cancel
            </v-btn>
          </v-card-actions>
        </template>
      </v-card>
    </v-dialog>
  </div>
</template>
