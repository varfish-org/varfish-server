import queryPresetsApi from '@variants/api/queryPresets'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const StoreState = Object.freeze({
  initial: 'initial',
  initializing: 'initializing',
  active: 'active',
  error: 'error',
})

/** Helper constant value table. */
export const Category = Object.freeze({
  quickpresets: {
    name: 'QuickPresets',
    title: 'Quick Presets',
  },
  frequencypresets: {
    name: 'FrequencyPresets',
    title: 'Frequency Presets',
  },
  impactpresets: {
    name: 'ImpactPresets',
    title: 'Variant Effect Presets',
  },
  chromosomepresets: {
    name: 'ChromosomePresets',
    title: 'Genes & Regions Presets',
  },
  qualitypresets: {
    name: 'QualityPresets',
    title: 'Quality Presets',
  },
  flagsetcpresets: {
    name: 'FlagsEtcPresets',
    title: 'Flags etc. / ClinVar Presets',
  },
})

export const useQueryPresetsStore = defineStore('queryPresets', () => {
  /** CSRF Token to use. */
  const csrfToken = ref(null)
  /** Project UUID. */
  const projectUuid = ref(null)

  /** State of the store. */
  const storeState = ref(StoreState.initial)
  /** Message to display for store state, e.g., in overlay. */
  const storeStateMessage = ref('Initializing...')
  /** How many server interactions are running */
  const serverInteractions = ref(0)

  /** Mapping from PresetSet UUID to PresetSet object. */
  const presetSets = ref({})

  /** A promise storing the result of initialize. */
  const initializeRes = ref(null)

  /** Initialize the store from the given project. */
  const initialize = (csrfToken$, projectUuid$) => {
    if (storeState.value !== 'initial') {
      // only once
      return initializeRes.value
    }
    csrfToken.value = csrfToken$
    projectUuid.value = projectUuid$
    serverInteractions.value += 1

    initializeRes.value = new Promise((resolve, reject) => {
      queryPresetsApi
        .listPresetSet(csrfToken.value, projectUuid.value)
        .then((result) => {
          serverInteractions.value -= 1
          presetSets.value = Object.fromEntries(
            result.map((presetSet) => [presetSet.sodar_uuid, presetSet]),
          )
          storeState.value = StoreState.active
          resolve()
        })
        .catch((err) => {
          serverInteractions.value -= 1
          storeState.value = StoreState.error
          reject(err)
        })
    })

    return initializeRes.value
  }

  /** Clone the factory preset set in the current project. */
  const cloneFactoryPresetSet = async (label) => {
    storeStateMessage.value = 'Cloning factory defaults...'
    serverInteractions.value += 1
    let resultPresetSet
    try {
      resultPresetSet = await queryPresetsApi.cloneFactoryPresetSet(
        csrfToken.value,
        { project: projectUuid.value, label },
      )
      presetSets.value[resultPresetSet.sodar_uuid] = resultPresetSet
    } finally {
      serverInteractions.value -= 1
    }
    return resultPresetSet
  }

  /** Clone the factory preset set in the current project. */
  const cloneOtherPresetSet = async (presetSetUuid, label) => {
    storeStateMessage.value = 'Cloning preset set...'
    serverInteractions.value += 1
    let resultPresetSet
    try {
      resultPresetSet = await queryPresetsApi.cloneOtherPresetSet(
        csrfToken.value,
        presetSetUuid,
        { project: projectUuid.value, label },
      )
      presetSets.value[resultPresetSet.sodar_uuid] = resultPresetSet
    } finally {
      serverInteractions.value -= 1
    }
    return resultPresetSet
  }

  /** Revert the given presetSet to the server value. */
  const revertPresetSet = async (presetSetUuid) => {
    storeStateMessage.value = 'Loading preset set from server...'
    serverInteractions.value += 1
    let revertedPresetSet
    try {
      revertedPresetSet = await queryPresetsApi.retrievePresetSet(
        csrfToken.value,
        presetSetUuid,
      )
      presetSets.value[presetSetUuid] = revertedPresetSet
    } finally {
      serverInteractions.value -= 1
    }
    return revertedPresetSet
  }

  /** Update the given presetSet. */
  const updatePresetSet = async (presetSetUuid, label) => {
    storeStateMessage.value = 'Updating preset set...'
    serverInteractions.value += 1
    let updatedPresetSet
    try {
      updatedPresetSet = await queryPresetsApi.updatePresetSet(
        csrfToken.value,
        presetSetUuid,
        { label },
      )
      presetSets.value[presetSetUuid] = updatedPresetSet
    } finally {
      serverInteractions.value -= 1
    }
    return updatedPresetSet
  }

  /** Destroy the given presetSet. */
  const destroyPresetSet = async (presetSetUuid) => {
    storeStateMessage.value = 'Deleting preset set...'
    serverInteractions.value += 1
    try {
      await queryPresetsApi.destroyPresetSet(csrfToken.value, presetSetUuid)
    } finally {
      serverInteractions.value -= 1
    }
    delete presetSets.value[presetSetUuid]
  }

  /** Create a new presets entry of given type within the given preset set with the given payload. */
  const createPresets = async (category, presetSetUuid, payload) => {
    const cat = Category[category]
    storeStateMessage.value = `Creating ${cat.title}...`
    serverInteractions.value += 1
    let createdPresets
    try {
      createdPresets = await queryPresetsApi[`create${cat.name}`](
        csrfToken.value,
        presetSetUuid,
        payload,
      )
      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].concat([createdPresets])
    } finally {
      serverInteractions.value -= 1
    }
  }

  /** Clone the given presets of the given type the given type with the given label. */
  const clonePresets = async (category, presetSetUuid, presetsUuid, label) => {
    const cat = Category[category]
    storeStateMessage.value = `Cloning ${cat.title}...`
    serverInteractions.value += 1
    let resultPresets
    try {
      resultPresets = await queryPresetsApi[`cloneOther${cat.name}`](
        csrfToken.value,
        presetsUuid,
        { label, presetset: presetSetUuid },
      )
      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].concat([resultPresets])
    } finally {
      serverInteractions.value -= 1
    }
  }

  /** Revert the given presets of given type within the preset set to the server value. */
  const revertPresets = async (category, presetSetUuid, presetUuid) => {
    const cat = Category[category]
    storeStateMessage.value = `Reverting ${cat.title}...`
    serverInteractions.value += 1
    let revertedPresets
    try {
      revertedPresets = await queryPresetsApi[`retrieve${cat.name}`](
        csrfToken.value,
        presetUuid,
      )
      const presetsSet = presetSets.value[presetSetUuid][`${category}_set`]
      for (let i = 0; i < presetsSet.length; i++) {
        if (presetsSet[i].sodar_uuid === presetUuid) {
          presetsSet[i] = revertedPresets
          break
        }
      }
    } finally {
      serverInteractions.value -= 1
    }
    return revertedPresets
  }

  /** Update the given presets of given type within the preset set. */
  const updatePresets = async (
    category,
    presetSetUuid,
    presetsUuid,
    presetsObj,
  ) => {
    const cat = Category[category]
    storeStateMessage.value = `Updating ${cat.title}...`
    serverInteractions.value += 1
    let updatedPresets
    try {
      updatedPresets = await queryPresetsApi[`update${cat.name}`](
        csrfToken.value,
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
    } finally {
      serverInteractions.value -= 1
    }
    return updatedPresets
  }

  /** Destroy the given presets of given type within the given preset set */
  const destroyPresets = async (category, presetSetUuid, presetsUuid) => {
    const cat = Category[category]
    storeStateMessage.value = `Deleting ${cat.title}...`
    serverInteractions.value += 1
    try {
      await queryPresetsApi[`destroy${cat.name}`](csrfToken.value, presetsUuid)
      presetSets.value[presetSetUuid][`${category}_set`] = presetSets.value[
        presetSetUuid
      ][`${category}_set`].filter((p) => p.sodar_uuid !== presetsUuid)
    } finally {
      serverInteractions.value -= 1
    }
  }

  return {
    csrfToken,
    projectUuid,
    storeState,
    storeStateMessage,
    serverInteractions,
    presetSets,
    initializeRes,
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
  }
})
