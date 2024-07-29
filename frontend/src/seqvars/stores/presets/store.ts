import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import {
  PatchedSeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsService,
} from '@varfish-org/varfish-api/lib'
import { client } from '@/cases/plugins/heyApi'
import { PresetSetVersionState, EditableState } from './types'
import { RequestResult } from '@hey-api/client-fetch'

/**
 * Store for the seqvars query presets.
 *
 * The store holds the data for all query presets of a given project and of course
 * the builtin presets.
 *
 * The preset sets and preset versions are stored by their UUID.  To differentiate
 * between the builtin and the custom ones, the UUIDs of the builtin preset sets are
 * stored in `factoryDefaultPresetSetUuids`.
 */
export const useSeqvarsPresetsStore = defineStore('seqvarPresets', () => {
  /** The current store state. */
  const storeState = reactive<StoreState>(new StoreState())

  /** The UUID of the project for the presets. */
  const projectUuid = ref<string | undefined>(undefined)
  /** UUIDs of the factory default preset sets. */
  const factoryDefaultPresetSetUuids = reactive<string[]>([])
  /** The preset sets by UUID. */
  const presetSets = reactive<Map<string, SeqvarsQueryPresetsSet>>(new Map())
  /** The preset set versions by UUID. */
  const presetSetVersions = reactive<
    Map<string, SeqvarsQueryPresetsSetVersionDetails>
  >(new Map())
  /** The latest active preset set version for each preset set; to be used by filtration. */
  const activePresetSetVersions = computed<
    Map<string, SeqvarsQueryPresetsSetVersionDetails>
  >(() => {
    const seenPresetSets = new Set<string>()
    const result = new Map<string, SeqvarsQueryPresetsSetVersionDetails>()
    for (const [uuid, version] of presetSetVersions) {
      if (
        !seenPresetSets.has(version.presetsset.sodar_uuid) &&
        version.status === 'active'
      ) {
        result.set(uuid, version)
        seenPresetSets.add(version.presetsset.sodar_uuid)
      }
    }
    return result
  })

  /**
   * Initialize the store.
   *
   * @param projectUuid$ The UUID of the project to load the presets for.
   * @param forceReload$ Whether to force a reload of the data even if the projectUuuid is the same.
   */
  const initialize = async (
    projectUuid$?: string,
    forceReload$: boolean = false,
  ) => {
    // Do not reinitialize if the project is the same unless forced.
    if (
      (projectUuid$ === projectUuid.value ||
        storeState.state === State.Fetching) &&
      !forceReload$
    ) {
      return
    }

    $reset()
    projectUuid.value = projectUuid$

    try {
      await storeState.execAsync(async () =>
        Promise.all([loadPresets(), loadFactoryDefaultsPresets()]),
      )
    } catch (e) {
      console.log('error', e)
      storeState.message = `Error loading presets: ${e}`
    }
  }

  /**
   * Load the (non-factory default) presets for the project with UUID from `projectUuid`.
   */
  const loadPresets = async (): Promise<void> => {
    // Guard against missing initialization.
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }

    // Paginate through all preset sets.
    let cursor: string | undefined = undefined
    const tmpPresetsSet: SeqvarsQueryPresetsSet[] = []
    do {
      const project = projectUuid.value
      const response = await storeState.execAsync(async () =>
        SeqvarsService.seqvarsApiQuerypresetssetList({
          client,
          path: { project },
          query: { cursor, page_size: 100 },
        }),
      )
      if (response.data && response.data.results) {
        for (const presetSet of response.data.results) {
          tmpPresetsSet.push(presetSet)
          presetSets.set(presetSet.sodar_uuid, presetSet)
        }

        if (response.data.next) {
          const tmpCursor = new URL(response.data.next).searchParams.get(
            'cursor',
          )
          if (tmpCursor !== null) {
            cursor = tmpCursor
          }
        }
      }
    } while (cursor !== undefined)

    // List all versions of all presets set.
    const versionListResponses = await storeState.execAsync(async () =>
      Promise.all(
        tmpPresetsSet.map(({ sodar_uuid: querypresetsset }) =>
          SeqvarsService.seqvarsApiQuerypresetssetversionList({
            client,
            path: { querypresetsset },
            query: { page_size: 100 },
          }),
        ),
      ),
    )
    const versionDetailResponses: RequestResult<
      SeqvarsQueryPresetsSetVersionDetails,
      unknown
    >[] = []
    for (const listResponse of versionListResponses) {
      if (listResponse.data && listResponse.data.results?.length) {
        for (const version of listResponse.data.results) {
          versionDetailResponses.push(
            SeqvarsService.seqvarsApiQuerypresetssetversionRetrieve({
              client,
              path: {
                querypresetsset: version.presetsset,
                querypresetssetversion: version.sodar_uuid,
              },
            }),
          )
        }
      }
    }
    const detailResponses = await storeState.execAsync(async () =>
      Promise.all(versionDetailResponses),
    )
    for (const detailResponse of detailResponses) {
      if (detailResponse.data !== undefined) {
        presetSetVersions.set(
          detailResponse.data.sodar_uuid,
          detailResponse.data,
        )
      }
    }
  }

  /**
   * Load the factory default presets for the project with UUID from `projectUuid`.
   */
  const loadFactoryDefaultsPresets = async (): Promise<void> => {
    // Paginate through all factory default preset sets.
    let cursor: string | undefined = undefined
    const tmpPresetsSet: SeqvarsQueryPresetsSet[] = []
    do {
      const response = await storeState.execAsync(async () =>
        SeqvarsService.seqvarsApiQuerypresetsfactorydefaultsList({
          client,
          query: { cursor, page_size: 100 },
        }),
      )
      if (response.data && response.data.results) {
        for (const presetSet of response.data.results) {
          factoryDefaultPresetSetUuids.push(presetSet.sodar_uuid)
          tmpPresetsSet.push(presetSet)
          presetSets.set(presetSet.sodar_uuid, presetSet)
        }

        if (response.data.next) {
          const tmpCursor = new URL(response.data.next).searchParams.get(
            'cursor',
          )
          if (tmpCursor !== null) {
            cursor = tmpCursor
          }
        }
      }
    } while (cursor !== undefined)

    // Fetch details of all factory defaults presets sets which will give us the
    // versions directly.
    const responses = await storeState.execAsync(async () =>
      Promise.all(
        tmpPresetsSet.map(({ sodar_uuid: querypresetsset }) =>
          SeqvarsService.seqvarsApiQuerypresetsfactorydefaultsRetrieve({
            client,
            path: { querypresetsset },
          }),
        ),
      ),
    )
    for (const response of responses) {
      if (response.data) {
        let tmpVersion = undefined // picked ones
        for (const version of response.data.versions) {
          if (version.status === 'ACTIVE') {
            tmpVersion = version
            break
          }
        }
        if (!tmpVersion && response.data.versions.length > 0) {
          tmpVersion = response.data.versions[0]
        }
        if (tmpVersion) {
          presetSetVersions.set(tmpVersion.sodar_uuid, tmpVersion)
        }
      }
    }
  }

  /**
   * Update the given preset set with the new given label.
   */
  const updatePresetsSet = async (
    presetSetUuid: string,
    body: PatchedSeqvarsQueryPresetsSet,
  ): Promise<SeqvarsQueryPresetsSet> => {
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }
    const origPresetSet = presetSets.get(presetSetUuid)
    if (origPresetSet === undefined) {
      throw new Error(`presetSetUuid not found: {presetSetUuid}`)
    }

    // Update the preset set via API.
    const project = projectUuid.value
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetPartialUpdate({
        client,
        body,
        path: {
          project,
          querypresetsset: presetSetUuid,
        },
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem when updating preset set')
    }

    // Fetch the updated presets set.
    const retrieveResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetRetrieve({
        client,
        path: {
          project,
          querypresetsset: presetSetUuid,
        },
      }),
    )
    if (retrieveResponse.data === undefined) {
      throw new Error('Problem retrieving updated presets version')
    }
    // Update the store and return.
    presetSets.set(retrieveResponse.data.sodar_uuid, retrieveResponse.data)
    return retrieveResponse.data
  }

  /**
   * Copy of the the given preset set with the new given label.
   */
  const copyPresetSet = async (
    presetSetUuid: string,
    label: string,
  ): Promise<
    [SeqvarsQueryPresetsSet, SeqvarsQueryPresetsSetVersionDetails]
  > => {
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }
    const origPresetSet = presetSets.get(presetSetUuid)
    if (origPresetSet === undefined) {
      throw new Error(`presetSetUuid not found: {presetSetUuid}`)
    }

    // Create new presets set copy via API.
    const project = projectUuid.value
    const copyFromResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetCopyFromCreate({
        client,
        path: {
          project,
          querypresetsset: presetSetUuid,
        },
        body: { label },
      }),
    )
    if (copyFromResponse.data === undefined) {
      throw new Error('Problem when copying preset set')
    }
    // Store new new presets set.
    const presetsSet = copyFromResponse.data
    presetSets.set(presetsSet.sodar_uuid, presetsSet)
    // Retrieve the presets set versions and store them.
    const versionListResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionList({
        client,
        path: { querypresetsset: presetsSet.sodar_uuid },
        query: { page_size: 100 },
      }),
    )
    if (versionListResponse.data === undefined) {
      throw new Error('Problem retrieving preset sets version list')
    }
    const versionDetailResponses: RequestResult<
      SeqvarsQueryPresetsSetVersionDetails,
      unknown
    >[] = []
    for (const version of versionListResponse.data.results ?? []) {
      versionDetailResponses.push(
        SeqvarsService.seqvarsApiQuerypresetssetversionRetrieve({
          client,
          path: {
            querypresetsset: version.presetsset,
            querypresetssetversion: version.sodar_uuid,
          },
        }),
      )
    }
    let presetsSetVersion: SeqvarsQueryPresetsSetVersionDetails | undefined
    const detailResponses = await storeState.execAsync(async () =>
      Promise.all(versionDetailResponses),
    )
    for (const detailResponse of detailResponses) {
      if (detailResponse.data !== undefined) {
        presetsSetVersion = detailResponse.data
        presetSetVersions.set(presetsSetVersion.sodar_uuid, presetsSetVersion)
      }
    }
    if (presetsSetVersion === undefined) {
      throw new Error('Problem retrieving preset sets version details')
    }

    return [presetsSet, presetsSetVersion]
  }

  /**
   * Delete the given preset set.
   */
  const deletePresetsSet = async (presetSetUuid: string): Promise<void> => {
    // Guard against missing initialization.
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }
    // Obtain the original preset set object.
    const origPresetSet = presetSets.get(presetSetUuid)
    if (origPresetSet === undefined) {
      throw new Error(`presetSetUuid not found: {presetSetUuid}`)
    }

    // Delete the preset set and all versions from the store.
    presetSets.delete(presetSetUuid)
    for (const [versionUuid, version] of Array.from(presetSetVersions)) {
      if (version.presetsset.sodar_uuid === presetSetUuid) {
        presetSetVersions.delete(versionUuid)
      }
    }

    // Delete the preset set via API.
    const project = projectUuid.value
    await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetDestroy({
        client,
        path: {
          project,
          querypresetsset: presetSetUuid,
        },
      }),
    )
  }

  /**
   * Create a copy of the given preset set version.
   */
  const copyPresetSetVersion = async (
    versionUuid: string,
  ): Promise<SeqvarsQueryPresetsSetVersionDetails> => {
    const origVersion = presetSetVersions.get(versionUuid)
    if (origVersion === undefined) {
      throw new Error(`versionUuid not found: {versionUuid}`)
    }

    // Create new version via API.
    const copyFromResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionCopyFromCreate({
        client,
        path: {
          querypresetsset: origVersion.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (copyFromResponse.data === undefined) {
      throw new Error('copyFromResponse.data is undefined')
    }

    // We must refresh all versions as the previously active version will
    // have changed its state.
    //
    // First, list the versions (assuming there are <100).
    const querypresetsset = origVersion.presetsset.sodar_uuid
    const versionListResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionList({
        client,
        path: { querypresetsset },
        query: { page_size: 100 },
      }),
    )
    // Then, fetch all.
    const versionDetailResponses: RequestResult<
      SeqvarsQueryPresetsSetVersionDetails,
      unknown
    >[] = []
    if (versionListResponse.data && versionListResponse.data.results?.length) {
      for (const version of versionListResponse.data.results) {
        versionDetailResponses.push(
          SeqvarsService.seqvarsApiQuerypresetssetversionRetrieve({
            client,
            path: {
              querypresetsset: version.presetsset,
              querypresetssetversion: version.sodar_uuid,
            },
          }),
        )
      }
    }
    const detailResponses = await storeState.execAsync(async () =>
      Promise.all(versionDetailResponses),
    )
    for (const detailResponse of detailResponses) {
      if (detailResponse.data !== undefined) {
        presetSetVersions.set(
          detailResponse.data.sodar_uuid,
          detailResponse.data,
        )
      }
    }

    // Return the newly created version.
    return copyFromResponse.data
  }

  /**
   * Publish the given presets set version.
   */
  const publishPresetSetVersion = async (
    versionUuid: string,
  ): Promise<SeqvarsQueryPresetsSetVersionDetails> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: {versionUuid}`)
    }

    // Publish the version via API.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionPartialUpdate({
        client,
        body: {
          status: PresetSetVersionState.ACTIVE,
        },
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem publishing presets version')
    }

    // Fetch the updated version.
    const retrieveResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionRetrieve({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (retrieveResponse.data === undefined) {
      throw new Error('Problem retrieving updated presets version')
    }

    // Write to store and return.
    presetSetVersions.set(
      retrieveResponse.data.sodar_uuid,
      retrieveResponse.data,
    )
    return retrieveResponse.data
  }

  /**
   * Discard the given draft presets set version.
   */
  const discardPresetSetVersion = async (
    versionUuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: {versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetssetversionDestroy({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.data === undefined) {
      throw new Error('Problem deleting presets version')
    }

    // Delete from store.
    presetSetVersions.delete(versionUuid)
  }

  /**
   * Queries for the editable state of a given version or reason why it is not.
   */
  const getEditableState = (versionUuid: string): EditableState => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      return EditableState.IS_NOT_SET
    } else if (
      factoryDefaultPresetSetUuids.includes(version.presetsset.sodar_uuid)
    ) {
      return EditableState.IS_FACTORY_DEFAULT
    } else if (version.status === PresetSetVersionState.ACTIVE) {
      return EditableState.IS_ACTIVE
    } else if (version.status === PresetSetVersionState.RETIRED) {
      return EditableState.IS_RETIRED
    } else {
      return EditableState.EDITABLE
    }
  }

  /**
   * Clear the store.
   *
   * This can be useful against artifacts in the UI.
   */
  const $reset = () => {
    storeState.reset()

    projectUuid.value = undefined
    factoryDefaultPresetSetUuids.splice(0, factoryDefaultPresetSetUuids.length)
    presetSets.clear()
    presetSetVersions.clear()
  }

  return {
    // attributes
    storeState,
    projectUuid,
    factoryDefaultPresetSetUuids,
    presetSets,
    presetSetVersions,
    activePresetSetVersions,
    // methods
    initialize,
    getEditableState,
    $reset,
    updatePresetsSet,
    copyPresetSet,
    deletePresetsSet,
    copyPresetSetVersion,
    publishPresetSetVersion,
    discardPresetSetVersion,
  }
})
