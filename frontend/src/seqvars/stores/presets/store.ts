import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import {
  SeqvarsQueryPresetsSet,
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsService,
} from '@varfish-org/varfish-api/lib'
import { client } from '@/cases/plugins/heyApi'

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
export const useSeqvarPresetsStore = defineStore('seqvarPresets', () => {
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

  /**
   * Initialize the store.
   *
   * @param projectUuid$ The UUID of the project to load the presets for.
   * @param forceReload$ Whether to force a reload of the data even if the projectUuuid is the same.
   */
  const initialize = async (
    projectUuid$: string,
    forceReload$: boolean = false,
  ) => {
    // Do not reinitialize if the project is the same unless forced.
    if (projectUuid$ === projectUuid.value && !forceReload$) {
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

    // List the versions of all presets set and pick the latest active one.
    const versionListResponses = await Promise.all(
      tmpPresetsSet.map(({ sodar_uuid: querypresetsset }) =>
        SeqvarsService.seqvarsApiQuerypresetssetversionList({
          client,
          path: { querypresetsset },
        }),
      ),
    )
    const versionDetailResponses = []
    for (const listResponse of versionListResponses) {
      if (listResponse.data && listResponse.data.results?.length) {
        let tmpVersion = undefined // picked ones
        for (const version of listResponse.data.results) {
          if (version.status === 'ACTIVE') {
            tmpVersion = version
            break
          }
        }
        if (tmpVersion === undefined && listResponse.data.results.length > 0) {
          tmpVersion = listResponse.data.results[0]
        }
        if (tmpVersion !== undefined) {
          versionDetailResponses.push(
            SeqvarsService.seqvarsApiQuerypresetssetversionRetrieve({
              client,
              path: {
                querypresetsset: tmpVersion.presetsset,
                querypresetssetversion: tmpVersion.sodar_uuid,
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
    // methods
    initialize,
    $reset,
  }
})
