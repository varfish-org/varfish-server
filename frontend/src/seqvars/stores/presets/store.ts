import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsService,
} from '@varfish-org/varfish-api/lib'
import { client } from '@/cases/plugins/heyApi'
import { PresetSetVersionState, EditableState } from './types'

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
        version.status === 'ACTIVE'
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

    storeState.state = State.Fetching
    try {
      storeState.serverInteractions += 1
      await Promise.all([loadPresets(), loadFactoryDefaultsPresets()])
    } catch (e) {
      console.log('error', e)
      storeState.state = State.Error
      storeState.message = `Error loading presets: ${e}`
    } finally {
      storeState.serverInteractions -= 1
    }
    storeState.state = State.Active
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
      const response = await SeqvarsService.seqvarsApiQuerypresetssetList({
        client,
        path: { project: projectUuid.value },
        query: { cursor, page_size: 100 },
      })
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
    const versionListResponses = await Promise.all(
      tmpPresetsSet.map(({ sodar_uuid: querypresetsset }) =>
        SeqvarsService.seqvarsApiQuerypresetssetversionList({
          client,
          path: { querypresetsset },
          query: { page_size: 100 },
        }),
      ),
    )
    const versionDetailResponses = []
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
    for (const detailResponse of await Promise.all(versionDetailResponses)) {
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
      const response =
        await SeqvarsService.seqvarsApiQuerypresetsfactorydefaultsList({
          client,
          query: { cursor, page_size: 100 },
        })
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
    const responses = await Promise.all(
      tmpPresetsSet.map(({ sodar_uuid: querypresetsset }) =>
        SeqvarsService.seqvarsApiQuerypresetsfactorydefaultsRetrieve({
          client,
          path: { querypresetsset },
        }),
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
   * Copy of the the given preset set with the new given label.
   */
  const copyPresetSet = async (
    presetSetUuid: string,
    label: string,
  ): Promise<SeqvarsQueryPresetsSet> => {
    const origPresetSet = presetSets.get(presetSetUuid)
    if (origPresetSet === undefined) {
      throw new Error(`presetSetUuid not found: {presetSetUuid}`)
    }

    // Create new preset set via API.
    const copyFromResponse =
      await SeqvarsService.seqvarsApiQuerypresetssetCopyFromCreate({
        client,
        path: {
          project: origPresetSet.project,
          querypresetsset: presetSetUuid,
        },
        body: {
          label,
          rank: presetSets.size - factoryDefaultPresetSetUuids.size + 1
        }
      })
    if (copyFromResponse.data === undefined) {
      throw new Error('copyFromResponse.data is undefined')
    }
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
    const copyFromResponse =
      await SeqvarsService.seqvarsApiQuerypresetssetversionCopyFromCreate({
        client,
        path: {
          querypresetsset: origVersion.presetsset.sodar_uuid,
          querypresetssetversion: versionUuid,
        },
      })
    if (copyFromResponse.data === undefined) {
      throw new Error('copyFromResponse.data is undefined')
    }

    // We must refresh all versions as the previously active version will
    // have changed its state.
    //
    // First, list the versions (assuming there are <100).
    const querypresetsset = origVersion.presetsset.sodar_uuid
    const versionListResponse =
      await SeqvarsService.seqvarsApiQuerypresetssetversionList({
        client,
        path: { querypresetsset },
        query: { page_size: 100 },
      })
    // Then, fetch all.
    const versionDetailResponses = []
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
    for (const detailResponse of await Promise.all(versionDetailResponses)) {
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
    storeState.state = State.Initial
    storeState.serverInteractions = 0
    storeState.message = null

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
    copyPresetSetVersion,
  }
})
