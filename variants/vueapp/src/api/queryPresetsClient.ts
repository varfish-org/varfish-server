import { ClientBase } from '@varfish/apiUtils'

type FrequencyPresets = any
type ImpactPresets = any
type QualityPresets = any
type ChromosomePresets = any
type FlagsEtcPresets = any
type QuickPresets = any
type PresetSet = any

/**
 * Class for accessing the variant query presets REST API.
 */
export class QueryPresetsClient extends ClientBase {
  async listPresetSetAll() {
    return await this.fetchHelper(`/variants/ajax/presetset/list/`, 'GET')
  }

  /**
   * List FrequencyPresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listFrequencyPresets(projectUuid: string): Promise<FrequencyPresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create FrequencyPresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createFrequencyPresets(
    projectUuid: string,
    payload: FrequencyPresets,
  ): Promise<FrequencyPresets> {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on FrequencyPresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveFrequencyPresets(
    entityUuid: string,
  ): Promise<FrequencyPresets> {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update FrequencyPresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateFrequencyPresets(
    entityUuid: string,
    payload: FrequencyPresets,
  ): Promise<FrequencyPresets> {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy FrequencyPresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyFrequencyPresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone FrequencyPresets factory defaults.
   *
   * @param name Name of the factory default to clone.
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryFrequencyPresets(
    name: string,
    payload: FrequencyPresets,
  ): Promise<FrequencyPresets> {
    const result = await this.fetchHelper(
      `/variants/ajax/frequencypresets/clone-factory-presets/${name}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  /**
   * Clone other FrequencyPresets.
   */
  async cloneOtherFrequencyPresets(
    entityUuid: string,
    payload: FrequencyPresets,
  ): Promise<FrequencyPresets> {
    return await this.fetchHelper(
      `/variants/ajax/frequencypresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List ImpactPresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listImpactPresets(projectUuid: string): Promise<ImpactPresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create ImpactPresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createImpactPresets(
    projectUuid: string,
    payload: ImpactPresets,
  ): Promise<ImpactPresets> {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on ImpactPresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveImpactPresets(entityUuid: string): Promise<ImpactPresets> {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update ImpactPresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateImpactPresets(
    entityUuid: string,
    payload: ImpactPresets,
  ): Promise<ImpactPresets> {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy ImpactPresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyImpactPresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone ImpactPresets factory defaults.
   *
   * @param name Name of the factory default to clone.
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryImpactPresets(
    name: string,
    payload: ImpactPresets,
  ): Promise<ImpactPresets> {
    const result = await this.fetchHelper(
      `/variants/ajax/impactpresets/clone-factory-presets/${name}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  /**
   * Clone other ImpactPresets.
   */
  async cloneOtherImpactPresets(
    entityUuid: string,
    payload: ImpactPresets,
  ): Promise<ImpactPresets> {
    return await this.fetchHelper(
      `/variants/ajax/impactpresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List QualityPresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listQualityPresets(projectUuid: string): Promise<QualityPresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create QualityPresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createQualityPresets(
    projectUuid: string,
    payload: QualityPresets,
  ): Promise<QualityPresets> {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on QualityPresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveQualityPresets(entityUuid: string): Promise<QualityPresets> {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update QualityPresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateQualityPresets(
    entityUuid: string,
    payload: QualityPresets,
  ): Promise<QualityPresets> {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy QualityPresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyQualityPresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone QualityPresets factory defaults.
   *
   * @param name Name of the factory default to clone.
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryQualityPresets(
    name: string,
    payload: QualityPresets,
  ): Promise<QualityPresets> {
    const result = await this.fetchHelper(
      `/variants/ajax/qualitypresets/clone-factory-presets/${name}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  /**
   * Clone other QualityPresets.
   */
  async cloneOtherQualityPresets(
    entityUuid: string,
    payload: QualityPresets,
  ): Promise<QualityPresets> {
    return await this.fetchHelper(
      `/variants/ajax/qualitypresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List ChromosomePresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listChromosomePresets(
    projectUuid: string,
  ): Promise<ChromosomePresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create ChromosomePresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createChromosomePresets(
    projectUuid: string,
    payload: ChromosomePresets,
  ): Promise<ChromosomePresets> {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on ChromosomePresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveChromosomePresets(
    entityUuid: string,
  ): Promise<ChromosomePresets> {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update ChromosomePresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateChromosomePresets(
    entityUuid: string,
    payload: ChromosomePresets,
  ): Promise<ChromosomePresets> {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy ChromosomePresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyChromosomePresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone ChromosomePresets factory defaults.
   *
   * @param name Name of the factory default to clone.
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryChromosomePresets(
    name: string,
    payload: ChromosomePresets,
  ): Promise<ChromosomePresets> {
    const result = await this.fetchHelper(
      `/variants/ajax/chromosomepresets/clone-factory-presets/${name}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  /**
   * Clone other ChromosomePresets.
   */
  async cloneOtherChromosomePresets(
    entityUuid: string,
    payload: ChromosomePresets,
  ): Promise<ChromosomePresets> {
    return await this.fetchHelper(
      `/variants/ajax/chromosomepresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List FlagsEtcPresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listFlagsEtcPresets(projectUuid: string): Promise<FlagsEtcPresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create FlagsEtcPresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createFlagsEtcPresets(
    projectUuid: string,
    payload: FlagsEtcPresets,
  ): Promise<FlagsEtcPresets> {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on FlagsEtcPresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveFlagsEtcPresets(entityUuid: string): Promise<FlagsEtcPresets> {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update FlagsEtcPresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateFlagsEtcPresets(
    entityUuid: string,
    payload: FlagsEtcPresets,
  ): Promise<FlagsEtcPresets> {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy FlagsEtcPresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyFlagsEtcPresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone FlagsEtcPresets factory defaults.
   *
   * @param name Name of the factory default to clone.
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryFlagsEtcPresets(
    name: string,
    payload: FlagsEtcPresets,
  ): Promise<FlagsEtcPresets> {
    const result = await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/clone-factory-presets/${name}/`,
      'POST',
      payload,
    )
    return await result.json()
  }

  /**
   * Clone other FlagsEtcPresets.
   */
  async cloneOtherFlagsEtcPresets(
    entityUuid: string,
    payload: FlagsEtcPresets,
  ): Promise<FlagsEtcPresets> {
    return await this.fetchHelper(
      `/variants/ajax/flagsetcpresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List QuickPresets in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listQuickPresets(projectUuid: string): Promise<QuickPresets[]> {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create QuickPresets in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createQuickPresets(
    projectUuid: string,
    payload: QuickPresets,
  ): Promise<QuickPresets> {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on QuickPresets object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrieveQuickPresets(entityUuid: string): Promise<QuickPresets> {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update QuickPresets object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updateQuickPresets(
    entityUuid: string,
    payload: QuickPresets,
  ): Promise<QuickPresets> {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy QuickPresets object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyQuickPresets(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone other QuickPresets.
   */
  async cloneOtherQuickPresets(
    entityUuid: string,
    payload: QuickPresets,
  ): Promise<QuickPresets> {
    return await this.fetchHelper(
      `/variants/ajax/quickpresets/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * List PresetSet in the given project.
   *
   * @param projectUuid UUID of project to query for.
   * @returns Promise with list of objects.
   */
  async listPresetSet(projectUuid: string): Promise<PresetSet[]> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/list-create/${projectUuid}/`,
      'GET',
    )
  }

  /**
   * Create PresetSet in the given project.
   *
   * @param projectUuid UUID of project to create within.
   * @param payload Data to use for creation.
   * @returns Promise with data from created object.
   */
  async createPresetSet(
    projectUuid: string,
    payload: PresetSet,
  ): Promise<PresetSet> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/list-create/${projectUuid}/`,
      'POST',
      payload,
    )
  }

  /**
   * Retrieve on PresetSet object.
   *
   * @param entityUuid UUID of the object to retrieve.
   * @returns Promise with the retrieved object's data.
   */
  async retrievePresetSet(entityUuid: string): Promise<PresetSet> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      'GET',
    )
  }

  /**
   * Update PresetSet object.
   *
   * @param entityUuid UUID of the object to update.
   * @param payload Data to use for the update.
   * @returns Promise with the updated object's data.
   */
  async updatePresetSet(
    entityUuid: string,
    payload: PresetSet,
  ): Promise<PresetSet> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      'PATCH',
      payload,
    )
  }

  /**
   * Destroy PresetSet object.
   *
   * @param entityUuid UUID of the object to destroy.
   * @returns Promise with the `fetch` result.
   */
  async destroyPresetSet(entityUuid: string) {
    return await this.fetchHelper(
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      'DELETE',
    )
  }

  /**
   * Clone PresetSet with factory defaults.
   *
   * @param payload Object with `project` and `label` payload to apply.
   * @returns Cloned object.
   */
  async cloneFactoryPresetSet(payload: PresetSet): Promise<PresetSet> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/clone-factory-presets/`,
      'POST',
      payload,
    )
  }

  /**
   * Clone other PresetSet.
   */
  async cloneOtherPresetSet(
    entityUuid: string,
    payload: PresetSet,
  ): Promise<PresetSet> {
    return await this.fetchHelper(
      `/variants/ajax/presetset/clone-other${entityUuid}/`,
      'POST',
      payload,
    )
  }
}
