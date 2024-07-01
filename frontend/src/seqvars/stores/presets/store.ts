/**
 * Store for the seqvars query presets.
 */

import { defineStore } from 'pinia'
import { reactive, ref } from 'vue'
import { StoreState, State } from '@/varfish/storeUtils'
import { operations, components } from '@/varfish/api/varfish'

/**
 * Store for the seqvars query presets.
 *
 * The store holds the data for all query presets of a given project and of course
 * the builtin presets.
 */
export const usePresetsStore = defineStore('seqvarPresets', () => {
  /** The current store state. */
  const storeState = reactive<StoreState>(new StoreState())

  /** The UUID of the project for the presets. */
  const projectUuid = ref<string | undefined>(undefined)

  /**
   * Initialize the store.
   *
   * @param projectUuid$ The UUID of the project to load the presets for.
   * @param forceReload$ Whether to force a reload of the data even if the projectUuuid is the same.
   * @returns
   */
  const initialize = async (projectUuid$: string, forceReload$: boolean = false) => {
    // Do not reinitialize if the project is the same unless forced.
    if (projectUuid$ === projectUuid.value && !forceReload$) {
      return
    }

    $reset()

    storeState.state = State.Fetching
    projectUuid.value = projectUuid$
    try {
      storeState.serverInteractions += 1
      loadPresets()
    } catch (e) {
      storeState.state = State.Error
      storeState.message = `Error loading presets: ${e}`
    } finally {
      storeState.serverInteractions -= 1
    }
    storeState.state = State.Active
  }

  /**
   * Load the presets for the project with UUID from `projectUuid`.
   */
  const loadPresets = async () => {
    // Load the presets.
    // ...
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
  }


  return {
    // attributes
    storeState,
    projectUuid,
    // methods
    initialize,
    $reset,
  }
})
