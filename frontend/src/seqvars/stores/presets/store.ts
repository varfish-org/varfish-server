import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import {
  PatchedSeqvarsQueryPresetsSetRequest,
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsClinvar,
  SeqvarsQueryPresetsColumns,
  SeqvarsQueryPresetsConsequence,
  SeqvarsQueryPresetsFrequency,
  SeqvarsQueryPresetsLocus,
  SeqvarsQueryPresetsPhenotypePrio,
  SeqvarsQueryPresetsQuality,
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsQueryPresetsVariantPrio,
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
 *
 * Eventually, we should probably use pinia-colada once it is ready:
 * https://github.com/posva/pinia-colada
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
    body: PatchedSeqvarsQueryPresetsSetRequest,
  ): Promise<SeqvarsQueryPresetsSet> => {
    if (projectUuid.value === undefined) {
      throw new Error('projectUuid is undefined')
    }
    const origPresetSet = presetSets.get(presetSetUuid)
    if (origPresetSet === undefined) {
      throw new Error(`presetSetUuid not found: ${presetSetUuid}`)
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
   * Create a new quality presets.
   *
   * @param versionUuid UUID of the version to create the quality for.
   * @param label The label of the new quality presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsQuality = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsQuality> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsqualityCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsquality_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating quality presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsquality_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the quality query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new quality query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsQuality = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsQuality,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsqualityPartialUpdate({
        client,
        path: {
          querypresetsquality: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets quality')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarsquerypresetsquality_set.length; i++) {
      if (
        version.seqvarsquerypresetsquality_set[i].sodar_uuid === body.sodar_uuid
      ) {
        version.seqvarsquerypresetsquality_set[i] = body
        return
      }
    }
    // If we reach here then the quality was not found.
    throw new Error('Quality not found in version')
  }

  /**
   * Delete the given quality query presets.
   *
   * @param versionUuid UUID of the version to delete the quality presets from.
   * @param uuid UUID of the quality presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsQuality = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsqualityDestroy({
        client,
        path: {
          querypresetsquality: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting quality presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsquality_set.splice(
      0,
      version.seqvarsquerypresetsquality_set.length,
      ...version.seqvarsquerypresetsquality_set.filter(
        (quality) => quality.sodar_uuid !== uuid,
      ),
    )
  }
  /**
   * Create a new frequency presets.
   *
   * @param versionUuid UUID of the version to create the frequency for.
   * @param label The label of the new frequency presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsFrequency = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsFrequency> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsfrequencyCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsfrequency_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating frequency presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsfrequency_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the frequency query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new frequency query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsFrequency = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsFrequency,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsfrequencyPartialUpdate({
        client,
        path: {
          querypresetsfrequency: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets frequency')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarsquerypresetsfrequency_set.length; i++) {
      if (
        version.seqvarsquerypresetsfrequency_set[i].sodar_uuid ===
        body.sodar_uuid
      ) {
        version.seqvarsquerypresetsfrequency_set[i] = body
        return
      }
    }
    // If we reach here then the frequency was not found.
    throw new Error('Frequency not found in version')
  }

  /**
   * Delete the given frequency query presets.
   *
   * @param versionUuid UUID of the version to delete the frequency presets from.
   * @param uuid UUID of the frequency presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsFrequency = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsfrequencyDestroy({
        client,
        path: {
          querypresetsfrequency: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting frequency presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsfrequency_set.splice(
      0,
      version.seqvarsquerypresetsfrequency_set.length,
      ...version.seqvarsquerypresetsfrequency_set.filter(
        (frequency) => frequency.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new consequence presets.
   *
   * @param versionUuid UUID of the version to create the consequence for.
   * @param label The label of the new consequence presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsConsequence = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsConsequence> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsconsequenceCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsconsequence_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating consequence presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsconsequence_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the consequence query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new consequence query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsConsequence = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsConsequence,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsconsequencePartialUpdate({
        client,
        path: {
          querypresetsconsequence: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets consequence')
    }

    // Update locally.
    for (
      let i = 0;
      i < version.seqvarsquerypresetsconsequence_set.length;
      i++
    ) {
      if (
        version.seqvarsquerypresetsconsequence_set[i].sodar_uuid ===
        body.sodar_uuid
      ) {
        version.seqvarsquerypresetsconsequence_set[i] = body
        return
      }
    }
    // If we reach here then the consequence was not found.
    throw new Error('Consequence not found in version')
  }

  /**
   * Delete the given consequence query presets.
   *
   * @param versionUuid UUID of the version to delete the consequence presets from.
   * @param uuid UUID of the consequence presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsConsequence = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsconsequenceDestroy({
        client,
        path: {
          querypresetsconsequence: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting consequence presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsconsequence_set.splice(
      0,
      version.seqvarsquerypresetsconsequence_set.length,
      ...version.seqvarsquerypresetsconsequence_set.filter(
        (consequence) => consequence.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new locus presets.
   *
   * @param versionUuid UUID of the version to create the locus for.
   * @param label The label of the new locus presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsLocus = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsLocus> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetslocusCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetslocus_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating locus presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetslocus_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the locus query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new locus query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsLocus = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsLocus,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetslocusPartialUpdate({
        client,
        path: {
          querypresetslocus: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets locus')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarsquerypresetslocus_set.length; i++) {
      if (
        version.seqvarsquerypresetslocus_set[i].sodar_uuid === body.sodar_uuid
      ) {
        version.seqvarsquerypresetslocus_set[i] = body
        return
      }
    }
    // If we reach here then the locus was not found.
    throw new Error('Locus not found in version')
  }

  /**
   * Delete the given locus query presets.
   *
   * @param versionUuid UUID of the version to delete the locus presets from.
   * @param uuid UUID of the locus presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsLocus = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetslocusDestroy({
        client,
        path: {
          querypresetslocus: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting locus presets')
    }

    // Apply locally.
    version.seqvarsquerypresetslocus_set.splice(
      0,
      version.seqvarsquerypresetslocus_set.length,
      ...version.seqvarsquerypresetslocus_set.filter(
        (locus) => locus.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new phenotypeprio presets.
   *
   * @param versionUuid UUID of the version to create the phenotypeprio for.
   * @param label The label of the new phenotypeprio presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsPhenotypePrio = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsPhenotypePrio> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsphenotypeprioCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsphenotypeprio_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating phenotypeprio presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsphenotypeprio_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the phenotypeprio query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new phenotypeprio query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsPhenotypePrio = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsPhenotypePrio,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsphenotypeprioPartialUpdate({
        client,
        path: {
          querypresetsphenotypeprio: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets phenotypeprio')
    }

    // Update locally.
    for (
      let i = 0;
      i < version.seqvarsquerypresetsphenotypeprio_set.length;
      i++
    ) {
      if (
        version.seqvarsquerypresetsphenotypeprio_set[i].sodar_uuid ===
        body.sodar_uuid
      ) {
        version.seqvarsquerypresetsphenotypeprio_set[i] = body
        return
      }
    }
    // If we reach here then the phenotypeprio was not found.
    throw new Error('PhenotypePrio not found in version')
  }

  /**
   * Delete the given phenotypeprio query presets.
   *
   * @param versionUuid UUID of the version to delete the phenotypeprio presets from.
   * @param uuid UUID of the phenotypeprio presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsPhenotypePrio = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsphenotypeprioDestroy({
        client,
        path: {
          querypresetsphenotypeprio: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting phenotypeprio presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsphenotypeprio_set.splice(
      0,
      version.seqvarsquerypresetsphenotypeprio_set.length,
      ...version.seqvarsquerypresetsphenotypeprio_set.filter(
        (phenotypeprio) => phenotypeprio.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new variantprio presets.
   *
   * @param versionUuid UUID of the version to create the variantprio for.
   * @param label The label of the new variantprio presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsVariantPrio = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsVariantPrio> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsvariantprioCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsvariantprio_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating variantprio presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsvariantprio_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the variantprio query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new variantprio query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsVariantPrio = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsVariantPrio,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsvariantprioPartialUpdate({
        client,
        path: {
          querypresetsvariantprio: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets variantprio')
    }

    // Update locally.
    for (
      let i = 0;
      i < version.seqvarsquerypresetsvariantprio_set.length;
      i++
    ) {
      if (
        version.seqvarsquerypresetsvariantprio_set[i].sodar_uuid ===
        body.sodar_uuid
      ) {
        version.seqvarsquerypresetsvariantprio_set[i] = body
        return
      }
    }
    // If we reach here then the variantprio was not found.
    throw new Error('VariantPrio not found in version')
  }

  /**
   * Delete the given variantprio query presets.
   *
   * @param versionUuid UUID of the version to delete the variantprio presets from.
   * @param uuid UUID of the variantprio presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsVariantPrio = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsvariantprioDestroy({
        client,
        path: {
          querypresetsvariantprio: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting variantprio presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsvariantprio_set.splice(
      0,
      version.seqvarsquerypresetsvariantprio_set.length,
      ...version.seqvarsquerypresetsvariantprio_set.filter(
        (variantprio) => variantprio.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new clinvar presets.
   *
   * @param versionUuid UUID of the version to create the clinvar for.
   * @param label The label of the new clinvar presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsClinvar = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsClinvar> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsclinvarCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetsclinvar_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating clinvar presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetsclinvar_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the clinvar query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new clinvar query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsClinvar = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsClinvar,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsclinvarPartialUpdate({
        client,
        path: {
          querypresetsclinvar: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets clinvar')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarsquerypresetsclinvar_set.length; i++) {
      if (
        version.seqvarsquerypresetsclinvar_set[i].sodar_uuid === body.sodar_uuid
      ) {
        version.seqvarsquerypresetsclinvar_set[i] = body
        return
      }
    }
    // If we reach here then the clinvar was not found.
    throw new Error('Clinvar not found in version')
  }

  /**
   * Delete the given clinvar query presets.
   *
   * @param versionUuid UUID of the version to delete the clinvar presets from.
   * @param uuid UUID of the clinvar presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsClinvar = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetsclinvarDestroy({
        client,
        path: {
          querypresetsclinvar: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting clinvar presets')
    }

    // Apply locally.
    version.seqvarsquerypresetsclinvar_set.splice(
      0,
      version.seqvarsquerypresetsclinvar_set.length,
      ...version.seqvarsquerypresetsclinvar_set.filter(
        (clinvar) => clinvar.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new columns presets.
   *
   * @param versionUuid UUID of the version to create the columns for.
   * @param label The label of the new columns presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsColumns = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsColumns> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetscolumnsCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarsquerypresetscolumns_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating columns presets')
    }

    // Update the store and return.
    version.seqvarsquerypresetscolumns_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the columns query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new columns query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsColumns = async (
    versionUuid: string,
    body: SeqvarsQueryPresetsColumns,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetscolumnsPartialUpdate({
        client,
        path: {
          querypresetscolumns: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets columns')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarsquerypresetscolumns_set.length; i++) {
      if (
        version.seqvarsquerypresetscolumns_set[i].sodar_uuid === body.sodar_uuid
      ) {
        version.seqvarsquerypresetscolumns_set[i] = body
        return
      }
    }
    // If we reach here then the columns was not found.
    throw new Error('Columns not found in version')
  }

  /**
   * Delete the given columns query presets.
   *
   * @param versionUuid UUID of the version to delete the columns presets from.
   * @param uuid UUID of the columns presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsColumns = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiQuerypresetscolumnsDestroy({
        client,
        path: {
          querypresetscolumns: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting columns presets')
    }

    // Apply locally.
    version.seqvarsquerypresetscolumns_set.splice(
      0,
      version.seqvarsquerypresetscolumns_set.length,
      ...version.seqvarsquerypresetscolumns_set.filter(
        (columns) => columns.sodar_uuid !== uuid,
      ),
    )
  }

  /**
   * Create a new predefinedquery presets.
   *
   * @param versionUuid UUID of the version to create the predefinedquery for.
   * @param label The label of the new predefinedquery presets.
   * @returns A promise that resolves with the created object after creation.
   * @throws Error if there is a problem with the creation.
   */
  const createQueryPresetsPredefinedQuery = async (
    versionUuid: string,
    label: string,
  ): Promise<SeqvarsPredefinedQuery> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Create on the server.
    const createResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiPredefinedqueryCreate({
        client,
        path: {
          querypresetsset: version.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body: {
          label,
          rank: version.seqvarspredefinedquery_set.length + 1,
        },
      }),
    )
    if (createResponse.data === undefined) {
      throw new Error('Problem creating predefinedquery presets')
    }

    // Update the store and return.
    version.seqvarspredefinedquery_set.push(createResponse.data)
    return createResponse.data
  }

  /**
   * Update the predefinedquery query presets of the given version.
   *
   * Uses the API to update this on the server, then applies the changes to the store.
   *
   * @param versionUuid The UUID of the version to update.
   * @param body The new predefinedquery query presets.
   * @returns A promise that resolves when the update is done.
   * @throws Error if there is a problem with the update.
   */
  const updateQueryPresetsPredefinedQuery = async (
    versionUuid: string,
    body: SeqvarsPredefinedQuery,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Update on the server.
    const updateResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiPredefinedqueryPartialUpdate({
        client,
        path: {
          predefinedquery: body.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
        body,
      }),
    )
    if (updateResponse.data === undefined) {
      throw new Error('Problem updating query presets predefinedquery')
    }

    // Update locally.
    for (let i = 0; i < version.seqvarspredefinedquery_set.length; i++) {
      if (
        version.seqvarspredefinedquery_set[i].sodar_uuid === body.sodar_uuid
      ) {
        version.seqvarspredefinedquery_set[i] = body
        return
      }
    }
    // If we reach here then the predefinedquery was not found.
    throw new Error('PredefinedQuery not found in version')
  }

  /**
   * Delete the given predefinedquery query presets.
   *
   * @param versionUuid UUID of the version to delete the predefinedquery presets from.
   * @param uuid UUID of the predefinedquery presets to delete.
   * @returns A promise that resolves when the deletion is done.
   * @throws Error if there is a problem with the deletion.
   */
  const deleteQueryPresetsPredefinedQuery = async (
    versionUuid: string,
    uuid: string,
  ): Promise<void> => {
    const version = presetSetVersions.get(versionUuid)
    if (version === undefined) {
      throw new Error(`versionUuid not found: ${versionUuid}`)
    }

    // Delete on the server.
    const deleteResponse = await storeState.execAsync(async () =>
      SeqvarsService.seqvarsApiPredefinedqueryDestroy({
        client,
        path: {
          predefinedquery: uuid,
          querypresetssetversion: versionUuid,
        },
      }),
    )
    if (deleteResponse.error !== undefined) {
      throw new Error('Problem deleting predefinedquery presets')
    }

    // Apply locally.
    version.seqvarspredefinedquery_set.splice(
      0,
      version.seqvarspredefinedquery_set.length,
      ...version.seqvarspredefinedquery_set.filter(
        (predefinedquery) => predefinedquery.sodar_uuid !== uuid,
      ),
    )
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
    createQueryPresetsQuality,
    updateQueryPresetsQuality,
    deleteQueryPresetsQuality,
    createQueryPresetsFrequency,
    updateQueryPresetsFrequency,
    deleteQueryPresetsFrequency,
    createQueryPresetsConsequence,
    updateQueryPresetsConsequence,
    deleteQueryPresetsConsequence,
    createQueryPresetsLocus,
    updateQueryPresetsLocus,
    deleteQueryPresetsLocus,
    createQueryPresetsPhenotypePrio,
    updateQueryPresetsPhenotypePrio,
    deleteQueryPresetsPhenotypePrio,
    createQueryPresetsVariantPrio,
    updateQueryPresetsVariantPrio,
    deleteQueryPresetsVariantPrio,
    createQueryPresetsClinvar,
    updateQueryPresetsClinvar,
    deleteQueryPresetsClinvar,
    createQueryPresetsColumns,
    updateQueryPresetsColumns,
    deleteQueryPresetsColumns,
    createQueryPresetsPredefinedQuery,
    updateQueryPresetsPredefinedQuery,
    deleteQueryPresetsPredefinedQuery,
  }
})

// Enable HMR (Hot Module Replacement)
if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useSeqvarsPresetsStore, import.meta.hot),
  )
}
