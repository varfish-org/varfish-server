import { apiFetch } from '@varfish/api-utils'

/**
 * Construct API object fragment for the given entity.
 *
 * @param entityName The entity name, expected to be in `UpperCase`.
 * @param options.noCloneFactoryPresetsName Whether to skip the name fragment when cloning factory presets.
 * @param options.skipCloneFactory Whether to skip the "clone from factory presets".
 * @returns Object with the API functions.
 */
const constructApiFragment = (entityName, options = {}) => {
  const entityNameLower = entityName.toLowerCase()

  const result = {}

  result[`list${entityName}`] = async (csrfToken, projectUuid) => {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/list-create/${projectUuid}/`,
      'GET',
    )
    return await response.json()
  }

  result[`create${entityName}`] = async (csrfToken, projectUuid, payload) => {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
    return await response.json()
  }

  result[`retrieve${entityName}`] = async (csrfToken, entityUuid) => {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
    return await response.json()
  }

  result[`update${entityName}`] = async (csrfToken, entityUuid, payload) => {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
    return await response.json()
  }

  result[`destroy${entityName}`] = async (csrfToken, entityUuid) => {
    await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  if (!options.skipCloneFactory) {
    if (options.noCloneFactoryPresetsName) {
      result[`cloneFactory${entityName}`] = async (csrfToken, payload) => {
        const result = await apiFetch(
          csrfToken,
          `/variants/ajax/${entityNameLower}/clone-factory-presets/`,
          'POST',
          payload,
        )
        return await result.json()
      }
    } else {
      result[`cloneFactory${entityName}`] = async (
        csrfToken,
        name,
        payload,
      ) => {
        const result = await apiFetch(
          csrfToken,
          `/variants/ajax/${entityNameLower}/clone-factory-presets/${name}/`,
          'POST',
          payload,
        )
        return await result.json()
      }
    }
  }

  result[`cloneOther${entityName}`] = async (
    csrfToken,
    entityUuid,
    payload,
  ) => {
    const result = await apiFetch(
      csrfToken,
      `/variants/ajax/${entityNameLower}/clone-other/${entityUuid}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  return result
}

export default {
  ...constructApiFragment('FrequencyPresets'),
  ...constructApiFragment('ImpactPresets'),
  ...constructApiFragment('QualityPresets'),
  ...constructApiFragment('ChromosomePresets'),
  ...constructApiFragment('FlagsEtcPresets'),
  ...constructApiFragment('QuickPresets', { skipCloneFactory: true }),
  ...constructApiFragment('PresetSet', { noCloneFactoryPresetsName: true }),

  /** List all preset sets visible to user, independent of project. */
  async listPresetSetAll(csrfToken) {
    const response = await apiFetch(
      csrfToken,
      `/variants/ajax/presetset/list/`,
      'GET',
    )
    return await response.json()
  },
}
