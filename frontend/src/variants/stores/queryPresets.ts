/**
 * Pinia store for handling per-variant flags.
 *
 * ## Store Dependencies
 *
 * - `caseListStore`
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

import { StoreState, State } from '@/varfish/storeUtils'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'
import { useCaseListStore } from '@/cases/stores/caseList'

// type FrequencyPresets = any
// type ImpactPresets = any
// type QualityPresets = any
// type ChromosomePresets = any
// type FlagsEtcPresets = any
// type QuickPresets = any
type PresetSet = any

export interface CategoryEntry {
  name: string
  title: string
}

export const Category = new Map<string, CategoryEntry>([
  [
    'quickpresets',
    {
      name: 'QuickPresets',
      title: 'Quick Presets',
    },
  ],
  [
    'frequencypresets',
    {
      name: 'FrequencyPresets',
      title: 'Frequency Presets',
    },
  ],
  [
    'impactpresets',
    {
      name: 'ImpactPresets',
      title: 'Variant Effect Presets',
    },
  ],
  [
    'chromosomepresets',
    {
      name: 'ChromosomePresets',
      title: 'Genes & Regions Presets',
    },
  ],
  [
    'qualitypresets',
    {
      name: 'QualityPresets',
      title: 'Quality Presets',
    },
  ],
  [
    'flagsetcpresets',
    {
      name: 'FlagsEtcPresets',
      title: 'Flags etc. / ClinVar Presets',
    },
  ],
])

export const useQueryPresetsStore = defineStore('queryPresets', () => {
  // store dependencies

  /** The caseListStore */
  const caseListStore = useCaseListStore()

  // data passed to `initialize` and store state

  /** The CSRF token. */
  const csrfToken = ref<string | null>(null)
  /** The project UUID. */
  const projectUuid = ref<string | null>(null)
  /** The current application state. */
  const storeState = ref<StoreState>(new StoreState())

  // other data (loaded via REST API or computed)

  /** Mapping from PresetSet UUID to PresetSet object. */
  const presetSets = ref<{ [key: string]: PresetSet }>({})

  /** A promise storing the result of initialize. */
  const initializeRes = ref<Promise<void> | null>(null)

  // functions

  /**
   * Initialize the store for a given project.
   *
   * @param csrfToken$ CSRF token to use.
   * @param projectUuid$ UUID of the project to load.
   * @param forceReload Whether to force reload.
   * @returns Promise for when the store is done initializing.
   */
  const initialize = async (
    csrfToken$: string,
    projectUuid$: string,
    forceReload: boolean = false,
  ): Promise<any> => {
    // Initialize store dependencies.
    await caseListStore.initialize(csrfToken$, projectUuid$, forceReload)

    // Initialize only once for each project.
    if (
      !forceReload &&
      storeState.value.state !== State.Initial &&
      projectUuid.value === projectUuid$
    ) {
      return initializeRes.value
    }

    $reset()

    // Set simple properties.
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$

    // Start fetching.
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    initializeRes.value = queryPresetsClient
      .listPresetSet(projectUuid.value)
      .then((res) => {
        presetSets.value = Object.fromEntries(
          res.map((presetSet) => [presetSet.sodar_uuid, presetSet]),
        )
        storeState.value.state = State.Active
        storeState.value.serverInteractions -= 1
      })
      .catch((err) => {
        console.error('Problem initializing casePresets store', err)
        storeState.value.state = State.Error
        storeState.value.serverInteractions -= 1
      })

    return initializeRes.value
  }

  /** Clone the factory preset set in the current project. */
  const cloneFactoryPresetSet = async (label: string): Promise<PresetSet> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.value.message = 'Cloning factory defaults...'
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let resultPresetSet: PresetSet
    try {
      resultPresetSet = await queryPresetsClient.cloneFactoryPresetSet({
        project: projectUuid.value,
        label,
      })
      presetSets.value[resultPresetSet.sodar_uuid] = resultPresetSet

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in cloneFactoryPresetSet:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error cloning factory preset set'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return resultPresetSet
  }

  /** Clone the factory preset set in the current project. */
  const cloneOtherPresetSet = async (
    presetSetUuid: string,
    label: string,
  ): Promise<PresetSet> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.value.message = 'Cloning preset set...'
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let resultPresetSet: PresetSet
    try {
      resultPresetSet = await queryPresetsClient.cloneOtherPresetSet(
        presetSetUuid,
        { project: projectUuid.value, label },
      )
      presetSets.value[resultPresetSet.sodar_uuid] = resultPresetSet

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in cloneOtherPresetSet:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error cloning other preset set'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return resultPresetSet
  }

  /** Revert the given presetSet to the server value. */
  const revertPresetSet = async (presetSetUuid: string): Promise<PresetSet> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.value.message = 'Loading preset set from server...'
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let revertedPresetSet: PresetSet
    try {
      revertedPresetSet =
        await queryPresetsClient.retrievePresetSet(presetSetUuid)
      presetSets.value[presetSetUuid] = revertedPresetSet

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in revertPresetSet:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error reverting preset set'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return revertedPresetSet
  }

  /** Update the given presetSet. */
  const updatePresetSet = async (
    presetSetUuid: string,
    label: string,
    default_presetset: boolean,
  ): Promise<PresetSet> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.value.message = 'Updating preset set...'
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let updatedPresetSet: PresetSet
    try {
      updatedPresetSet = await queryPresetsClient.updatePresetSet(
        presetSetUuid,
        { label, default_presetset },
      )
      presetSets.value[presetSetUuid] = updatedPresetSet

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in updatePresetSet:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error updating preset set'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return updatedPresetSet
  }

  /** Destroy the given presetSet. */
  const destroyPresetSet = async (presetSetUuid: string): Promise<any> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    storeState.value.message = 'Deleting preset set...'
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    try {
      await queryPresetsClient.destroyPresetSet(presetSetUuid)

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in destroyPresetSet:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error deleting preset set'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    delete presetSets.value[presetSetUuid]
  }

  /** Create a new presets entry of given type within the given preset set with the given payload. */
  const createPresets = async <T>(
    category: string,
    presetSetUuid: string,
    payload: T,
  ): Promise<T | undefined> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    const cat = Category.get(category)
    if (!cat) {
      throw new Error(`Invalid category: ${category}`)
    }
    storeState.value.message = `Creating ${cat.title}...`
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let createdPresets: T | undefined = undefined
    try {
      // @ts-ignore
      createdPresets = await queryPresetsClient[`create${cat.name}`](
        presetSetUuid,
        payload,
      )
      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].concat([createdPresets])

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in createPresets:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error creating preset'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return createdPresets
  }

  /** Clone the given presets of the given type the given type with the given label. */
  const clonePresets = async (
    category: string,
    presetSetUuid: string,
    presetsUuid: string,
    label: string,
  ): Promise<any> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    const cat = Category.get(category)
    if (!cat) {
      throw new Error(`Invalid category: ${category}`)
    }
    storeState.value.message = `Cloning ${cat.title}...`
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let resultPresets
    try {
      // @ts-ignore
      resultPresets = await queryPresetsClient[`cloneOther${cat.name}`](
        presetsUuid,
        { label, presetset: presetSetUuid },
      )
      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].concat([resultPresets])

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in clonePresets:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error cloning preset'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return resultPresets
  }

  /** Revert the given presets of given type within the preset set to the server value. */
  const revertPresets = async (
    category: string,
    presetSetUuid: string,
    presetUuid: string,
  ): Promise<any> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    const cat = Category.get(category)
    if (!cat) {
      throw new Error(`Invalid category: ${category}`)
    }
    storeState.value.message = `Reverting ${cat.title}...`
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let revertedPresets: any
    try {
      revertedPresets =
        // @ts-ignore
        await queryPresetsClient[`retrieve${cat.name}`](presetUuid)
      const presetsSet = presetSets.value[presetSetUuid][`${category}_set`]
      for (let i = 0; i < presetsSet.length; i++) {
        if (presetsSet[i].sodar_uuid === presetUuid) {
          presetsSet[i] = revertedPresets
          break
        }
      }

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in revertPresets:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error reverting preset'
    } finally {
      storeState.value.serverInteractions -= 1
    }

    return revertedPresets
  }

  /** Update the given presets of given type within the preset set. */
  const updatePresets = async <T>(
    category: string,
    presetSetUuid: string,
    presetsUuid: string,
    presetsObj: T,
  ): Promise<T> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    const cat = Category.get(category)
    if (!cat) {
      throw new Error(`Invalid category: ${category}`)
    }
    storeState.value.message = `Updating ${cat.title}...`
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    let updatedPresets: any
    try {
      // @ts-ignore
      updatedPresets = await queryPresetsClient[`update${cat.name}`](
        presetsUuid,
        presetsObj,
      )
      const presetsSet = presetSets.value[presetSetUuid][`${category}_set`]
      for (let i = 0; i < presetsSet.length; i++) {
        if (presetsSet[i].sodar_uuid === presetsUuid) {
          presetsSet[i] = updatedPresets
          break
        }
      }

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in updatePresets:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error updating preset'
    } finally {
      storeState.value.serverInteractions -= 1
    }
    return updatedPresets
  }

  /** Destroy the given presets of given type within the given preset set */
  const destroyPresets = async (
    category: string,
    presetSetUuid: string,
    presetsUuid: string,
  ): Promise<any> => {
    const queryPresetsClient = new QueryPresetsClient(
      csrfToken.value ?? 'undefined-csrf-token',
    )

    const cat = Category.get(category)
    if (!cat) {
      throw new Error(`Invalid category: ${category}`)
    }
    storeState.value.message = `Deleting ${cat.title}...`
    const oldState = storeState.value.state
    storeState.value.state = State.Fetching
    storeState.value.serverInteractions += 1

    try {
      switch (category) {
        case 'quickpresets':
          await queryPresetsClient.destroyQuickPresets(presetsUuid)
          break
        case 'frequencypresets':
          await queryPresetsClient.destroyFrequencyPresets(presetsUuid)
          break
        case 'impactpresets':
          await queryPresetsClient.destroyImpactPresets(presetsUuid)
          break
        case 'chromosomepresets':
          await queryPresetsClient.destroyChromosomePresets(presetsUuid)
          break
        case 'qualitypresets':
          await queryPresetsClient.destroyQualityPresets(presetsUuid)
          break
        case 'flagsetcpresets':
          await queryPresetsClient.destroyFlagsEtcPresets(presetsUuid)
          break
        default:
          console.error(`Invalid category: ${category}`)
      }

      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].filter(
        (p: PresetSet) => p.sodar_uuid !== presetsUuid,
      )

      storeState.value.state = oldState
      storeState.value.message = ''
    } catch (err) {
      console.error('Error in destroyPresets:', err)
      storeState.value.state = State.Error
      storeState.value.message = 'Error destroying preset'
    } finally {
      storeState.value.serverInteractions -= 1
    }
  }

  const getDefaultPresetSetName = (): PresetSet | undefined => {
    for (const presetSet of Object.values(presetSets.value)) {
      if (presetSet.default_presetset) {
        return presetSet.label
      }
    }
    return undefined
  }

  const $reset = () => {
    csrfToken.value = null
    projectUuid.value = null
    storeState.value.state = State.Initial
    presetSets.value = {}
    initializeRes.value = null
  }

  return {
    // data / state
    csrfToken,
    projectUuid,
    storeState,
    presetSets,
    initializeRes,
    // functions
    initialize,
    cloneFactoryPresetSet,
    cloneOtherPresetSet,
    revertPresetSet,
    updatePresetSet,
    destroyPresetSet,
    createPresets,
    clonePresets,
    revertPresets,
    updatePresets,
    destroyPresets,
    getDefaultPresetSetName,
  }
})
