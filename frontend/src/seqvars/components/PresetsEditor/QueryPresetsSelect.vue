<script setup lang="ts">
import { useIsFetching, useIsMutating } from '@tanstack/vue-query'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import {
  useSeqvarQueryPresetsSetCopyFromMutation,
  useSeqvarQueryPresetsSetDestroyMutation,
  useSeqvarQueryPresetsSetListQuery, // useSeqvarQueryPresetsSetRetrieveQuery,
  useSeqvarQueryPresetsSetUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetSet'
import {
  EditableState,
  getEditableState,
  getEditableStateLabel,
  useSeqvarQueryPresetsSetVersionDestroyMutation,
  useSeqvarQueryPresetsSetVersionListQuery,
  useSeqvarQueryPresetsSetVersionRetrieveQueries, // useSeqvarQueryPresetsSetVersionRetrieveQuery,
  useSeqvarQueryPresetsSetVersionUpdateMutation,
} from '@/seqvars/queries/seqvarQueryPresetSetVersion'
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

/** Wraps `props.projectUuid` into a `ComputedRef` for use with queries. */
const projectUuid = computed(() => props.projectUuid)
/** Wraps `props.presetSet` into a `ComputedRef` for use with queries. */
const presetsSetUuid = computed(() => props.presetSet)
// /** Wraps `props.presetSetVersion` into a `ComputedRef` for use with queries. */
// const presetsSetVersionUuid = computed(() => props.presetSetVersion)

/** List all presets sets for the current project. */
const presetsSetListRes = useSeqvarQueryPresetsSetListQuery({
  projectUuid,
})
/** Provide the presets sets by from `seqvarsQueryPresetsSetListRes` by UUID. */
const presetsSetByUuid = computed<Map<string, SeqvarsQueryPresetsSet>>(() => {
  const presetsSets = presetsSetListRes.data.value?.results ?? []
  return new Map(presetsSets.map((item) => [item.sodar_uuid, item]))
})
/** Mutation for coyping one presets set from another */
const presetsSetCreateFromPresets = useSeqvarQueryPresetsSetCopyFromMutation()
/** Mutation for updating presets sets. */
const presetsSetUpdate = useSeqvarQueryPresetsSetUpdateMutation()
/** Mutation for deleting presets sets. */
const presetsSetDestroy = useSeqvarQueryPresetsSetDestroyMutation()

// /** Provide detailed seqvar presets set for the one from props, if any. */
// const presetsSetRetrieveRes = useSeqvarQueryPresetsSetRetrieveQuery({
//   projectUuid,
//   presetsSetUuid,
// })
/** List all presets set versions for the current presets set. */
const presetsSetVersionListRes = useSeqvarQueryPresetsSetVersionListQuery({
  presetsSetUuid,
})
/** UUIDs of the preset set versions, for use with queries. */
const presetsSetVersionUuids = computed(() => {
  return (presetsSetVersionListRes.data.value?.results ?? []).map(
    (item) => item.sodar_uuid,
  )
})
/** Query preset set version details for the current presets set. */
const presetsSetVersionDetailsRetrieveRes =
  useSeqvarQueryPresetsSetVersionRetrieveQueries({
    presetsSetUuid,
    presetsSetVersionUuids,
  })

/** Provide the presets set versions details by UUID. */
const presetsSetVersionDetailsByUuid = computed<
  Map<string, SeqvarsQueryPresetsSetVersionDetails>
>(
  () =>
    new Map(
      presetsSetVersionDetailsRetrieveRes.value.data.map((item) => [
        item.sodar_uuid,
        item,
      ]),
    ),
)
/** Provide access to the currently selected presets set version. */
const selectedPresetsSetVersion = computed<
  SeqvarsQueryPresetsSetVersionDetails | undefined
>(() =>
  presetsSetVersionDetailsByUuid.value.get(
    selectedPresetsSetVersionUuid.value ?? '',
  ),
)
// /** Provide detailed seqvar query presets set version for the one from props, if any. */
// const presetsSetVersionRetrieveRes =
//   useSeqvarQueryPresetsSetVersionRetrieveQuery({
//     presetsSetUuid,
//     presetsSetVersionUuid,
//   })
/** Mutation for copying one prests set version from another. */
const presetsSetVersionCreateFromPresets =
  useSeqvarQueryPresetsSetVersionUpdateMutation()
/** Mutation for updating presets set version. */
const presetsSetVersionUpdate = useSeqvarQueryPresetsSetVersionUpdateMutation()
/** Mutation for deleting presets set version. */
const presetsSetVersionDestroy =
  useSeqvarQueryPresetsSetVersionDestroyMutation()

/** Returns number of true (non-background) loads. */
const isQueryFetching = useIsFetching({
  predicate: (query) => query.state.status !== 'pending',
})
/** Returns number of mutations. */
const isQueryMutating = useIsMutating()

/** The currently selected presets set, managed through route/props; component state */
const selectedPresetsSetUuid = computed<string | undefined>({
  get() {
    return props.presetSet
  },
  set(value) {
    if (value) {
      router.push({ params: { presetSet: value, presetSetVersion: '' } })
    }
  },
})

/** The currently selected presets set version, manged through route/props; component state */
const selectedPresetsSetVersionUuid = computed<string | undefined>({
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
  if (selectedPresetsSetUuid.value) {
    const presetSet = presetsSetByUuid.value.get(selectedPresetsSetUuid.value)
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
  if (props.projectUuid !== undefined && props.presetSet !== undefined) {
    let presetsSet
    try {
      presetsSet = await presetsSetCreateFromPresets.mutateAsync({
        body: {
          label: cloneDialogModel.value,
        },
        path: {
          project: props.projectUuid,
          querypresetsset: props.presetSet,
        },
      })
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
        presetSetVersion: '',
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
  if (selectedPresetsSetUuid.value) {
    const presetsSet = presetsSetByUuid.value.get(selectedPresetsSetUuid.value)
    if (presetsSet) {
      renameDialogModel.value = presetsSet.label
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
  if (
    props.projectUuid !== undefined &&
    selectedPresetsSetUuid.value !== undefined
  ) {
    try {
      await presetsSetUpdate.mutateAsync({
        body: {
          label: renameDialogModel.value,
        },
        path: {
          project: props.projectUuid,
          querypresetsset: selectedPresetsSetUuid.value,
        },
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
  if (
    props.projectUuid !== undefined &&
    selectedPresetsSetUuid.value !== undefined
  ) {
    try {
      await presetsSetDestroy.mutateAsync({
        path: {
          project: props.projectUuid,
          querypresetsset: selectedPresetsSetUuid.value,
        },
      })
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
  if (
    selectedPresetsSetUuid.value !== undefined &&
    selectedPresetsSetVersionUuid.value !== undefined
  ) {
    try {
      await presetsSetVersionUpdate.mutateAsync({
        body: {
          status: 'active',
        },
        path: {
          querypresetsset: selectedPresetsSetUuid.value,
          querypresetssetversion: selectedPresetsSetVersionUuid.value,
        },
      })
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
  if (
    selectedPresetsSetUuid.value !== undefined &&
    selectedPresetsSetVersionUuid.value !== undefined
  ) {
    try {
      await presetsSetVersionDestroy.mutateAsync({
        path: {
          querypresetsset: selectedPresetsSetUuid.value,
          querypresetssetversion: selectedPresetsSetVersionUuid.value,
        },
      })
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
  if (selectedPresetsSetVersionUuid.value !== undefined) {
    newVersionDialogShow.value = true
  }
}

/**
 * Helper to execute the creation of a new version.
 */
const doNewVersion = async () => {
  // guard against undefined version
  if (
    selectedPresetsSetUuid.value !== undefined &&
    selectedPresetsSetVersionUuid.value !== undefined
  ) {
    let presetSetVersion
    try {
      presetSetVersion = await presetsSetVersionCreateFromPresets.mutateAsync({
        path: {
          querypresetsset: selectedPresetsSetUuid.value,
          querypresetssetversion: selectedPresetsSetVersionUuid.value,
        },
      })
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
  return Array.from(presetsSetByUuid.value.values()).sort((a, b) => {
    return (
      (a.is_factory_default ? 0 : 1000) +
      (a.rank ?? 0) -
      (b.is_factory_default ? 0 : 1000) -
      (b.rank ?? 0)
    )
  })
})

/**
 * The items to display in the presets set version list.
 *
 * Ensures the ones for the selected version are displayed and sorted by `(major, minor)` version.
 */
const presetsSetVersionItems = computed<SeqvarsQueryPresetsSetVersionDetails[]>(
  () => {
    return Array.from(presetsSetVersionDetailsByUuid.value.values())
      .filter((item) => {
        return item.presetsset.sodar_uuid === selectedPresetsSetUuid.value
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

/**
 * Ensures that when no presets set or version been selected yet via props then
 * this is done via the router.  The first preset set and version are selected.
 *
 * @param force
 *    Whether to force the selection of the presets set and version even if
 *    present already.
 */
const selectPresetsSetAndVersion = (force: boolean = false) => {
  let presetSet = props.presetSet
  if (force || (!presetSet && presetsSetListRes.data.value?.results?.length)) {
    presetSet = presetsSetListRes.data.value!.results![0].sodar_uuid
  }

  let presetSetVersion = props.presetSetVersion
  if (
    force ||
    (!presetSetVersion && presetsSetVersionListRes.data.value?.results?.length)
  ) {
    presetSetVersion =
      presetsSetVersionListRes.data.value!.results![0].sodar_uuid
  }

  if (
    presetSet !== props.presetSet ||
    presetSetVersion !== props.presetSetVersion
  ) {
    router.push({ params: { presetSet, presetSetVersion } })
  }
}

/* Trigger selection of presets set and version on mount. */
onMounted(() => {
  selectPresetsSetAndVersion()
})

/* Trigger selection of presets set and version when data becomes available or
 * the selected presets set or version changes.
 */
watch(
  () => [
    presetsSetListRes.status.value,
    presetsSetVersionListRes.status.value,
    selectedPresetsSetUuid.value,
    selectedPresetsSetVersionUuid.value,
  ],
  () => {
    selectPresetsSetAndVersion()
  },
)

/* Trigger presets set and version selection when the project UUID changes */
watch(
  () => props.projectUuid,
  () => {
    selectPresetsSetAndVersion(true)
  },
)
</script>

<template>
  <div>
    <v-sheet class="pa-3">
      <v-row no-gutters class="d-flex flex-nowrap" justify="space-between">
        <v-col class="flex-grow-1 flex-shrink-0">
          <v-select
            v-model="selectedPresetsSetUuid"
            :items="presetSetItems"
            :item-props="
              (item: SeqvarsQueryPresetsSet) => {
                return {
                  value: item.sodar_uuid,
                  title: item.label,
                  subtitle: item.is_factory_default
                    ? 'Factory Default'
                    : 'User-Defined',
                }
              }
            "
            :loading="isQueryMutating > 0 || isQueryFetching > 0"
            label="Presets Set"
            hint="Select presets set to work with."
            persistent-hint
          ></v-select>
        </v-col>
        <v-col class="flex-grow-1 flex-shrink-0 pl-3">
          <v-select
            v-model="selectedPresetsSetVersionUuid"
            :items="presetsSetVersionItems"
            :item-props="
              (item?: SeqvarsQueryPresetsSetVersionDetails) => {
                if (!item) {
                  return undefined
                } else {
                  return {
                    value: item.sodar_uuid,
                    title: item
                      ? `${item.version_major}.${item.version_minor}`
                      : undefined,
                    subtitle: `${item.status}`,
                  }
                }
              }
            "
            :loading="isQueryMutating > 0 || isQueryFetching > 0"
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
                  :loading="isQueryMutating > 0 || isQueryFetching > 0"
                ></v-btn>
              </template>

              <v-list>
                <v-list-subheader class="text-uppercase">
                  Presets Version
                </v-list-subheader>
                <template
                  v-if="
                    selectedPresetsSetVersion !== undefined &&
                    getEditableState(selectedPresetsSetVersion) ===
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
                    selectedPresetsSetVersion !== undefined &&
                    getEditableState(selectedPresetsSetVersion) ===
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
                    selectedPresetsSetVersion !== undefined &&
                    getEditableState(selectedPresetsSetVersion) ===
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
              selectedPresetsSetVersion !== undefined &&
              getEditableState(selectedPresetsSetVersion) ===
                EditableState.IS_FACTORY_DEFAULT
                ? 'mdi-factory'
                : 'mdi-information'
            "
          >
            {{
              selectedPresetsSetVersion === undefined
                ? '-'
                : getEditableStateLabel(
                    getEditableState(selectedPresetsSetVersion),
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
        <template v-if="presetsSetVersionItems.length > 1">
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
