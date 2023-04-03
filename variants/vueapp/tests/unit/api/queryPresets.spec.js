import queryPresetsApi from '@variants/api/queryPresets.js'
import { afterEach, beforeEach, describe, expect, test, vi } from 'vitest'
import createFetchMock from 'vitest-fetch-mock'

import listChromosomePresetsResponse from '../../data/listChromosomePresetsResponse.json'
import listFlagsEtcPresetsResponse from '../../data/listFlagsEtcPresetsResponse.json'
import listFrequencyPresetsResponse from '../../data/listFrequencyPresetsResponse.json'
import listImpactPresetsResponse from '../../data/listImpactPresetsResponse.json'
import listPresetSetResponse from '../../data/listPresetSetResponse.json'
import listQualityPresetsResponse from '../../data/listQualityPresetsResponse.json'
import listQuickPresetsResponse from '../../data/listQuickPresetsResponse.json'
import retrieveChromosomePresetsResponse from '../../data/retrieveChromosomePresetsResponse.json'
import retrieveFlagsEtcPresetsResponse from '../../data/retrieveFlagsEtcPresetsResponse.json'
import retrieveFrequencyPresetsResponse from '../../data/retrieveFrequencyPresetsResponse.json'
import retrieveImpactPresetsResponse from '../../data/retrieveImpactPresetsResponse.json'
import retrievePresetSetResponse from '../../data/retrievePresetSetResponse.json'
import retrieveQualityPresetsResponse from '../../data/retrieveQualityPresetsResponse.json'
import retrieveQuickPresetsResponse from '../../data/retrieveQuickPresetsResponse.json'

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()

describe('api', () => {
  const csrfToken = 'fake-token'
  const projectUuid = 'fake-project-uuid'
  const entityUuid = 'fake-entity-uuid'

  beforeEach(() => {
    fetch.resetMocks()
    fetchMock.doMock()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  test('listFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listFrequencyPresetsResponse))

    const res = await queryPresetsApi.listFrequencyPresets(
      csrfToken,
      projectUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listFrequencyPresetsResponse)
  })

  test('createFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.createFrequencyPresets(
      csrfToken,
      projectUuid,
      retrieveFrequencyPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveFrequencyPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFrequencyPresetsResponse)
  })

  test('retrieveFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.retrieveFrequencyPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveFrequencyPresetsResponse)
  })

  test('updateFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.updateFrequencyPresets(
      csrfToken,
      entityUuid,
      retrieveFrequencyPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveFrequencyPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveFrequencyPresetsResponse)
  })

  test('destroyFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.destroyFrequencyPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })

  test('cloneOtherFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.cloneOtherFrequencyPresets(
      csrfToken,
      entityUuid,
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/clone-other/${entityUuid}/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFrequencyPresetsResponse)
  })

  test('cloneFactoryFrequencyPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFrequencyPresetsResponse))

    const res = await queryPresetsApi.cloneFactoryFrequencyPresets(
      csrfToken,
      'the-name',
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/frequencypresets/clone-factory-presets/the-name/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFrequencyPresetsResponse)
  })

  test('listImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listImpactPresetsResponse))

    const res = await queryPresetsApi.listImpactPresets(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listImpactPresetsResponse)
  })

  test('createImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.createImpactPresets(
      csrfToken,
      projectUuid,
      retrieveImpactPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveImpactPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveImpactPresetsResponse)
  })

  test('retrieveImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.retrieveImpactPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveImpactPresetsResponse)
  })

  test('updateImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.updateImpactPresets(
      csrfToken,
      entityUuid,
      retrieveImpactPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveImpactPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveImpactPresetsResponse)
  })

  test('destroyImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.destroyImpactPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })
  test('cloneOtherImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.cloneOtherImpactPresets(
      csrfToken,
      entityUuid,
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/clone-other/${entityUuid}/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveImpactPresetsResponse)
  })

  test('cloneFactoryImpactPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveImpactPresetsResponse))

    const res = await queryPresetsApi.cloneFactoryImpactPresets(
      csrfToken,
      'the-name',
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/impactpresets/clone-factory-presets/the-name/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveImpactPresetsResponse)
  })
  test('listQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listQualityPresetsResponse))

    const res = await queryPresetsApi.listQualityPresets(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listQualityPresetsResponse)
  })

  test('createQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.createQualityPresets(
      csrfToken,
      projectUuid,
      retrieveQualityPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveQualityPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveQualityPresetsResponse)
  })

  test('retrieveQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.retrieveQualityPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveQualityPresetsResponse)
  })

  test('updateQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.updateQualityPresets(
      csrfToken,
      entityUuid,
      retrieveQualityPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveQualityPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveQualityPresetsResponse)
  })

  test('destroyQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.destroyQualityPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })

  test('cloneOtherQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.cloneOtherQualityPresets(
      csrfToken,
      entityUuid,
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/clone-other/${entityUuid}/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveQualityPresetsResponse)
  })

  test('cloneFactoryQualityPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQualityPresetsResponse))

    const res = await queryPresetsApi.cloneFactoryQualityPresets(
      csrfToken,
      'the-name',
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/qualitypresets/clone-factory-presets/the-name/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveQualityPresetsResponse)
  })
  test('listChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listChromosomePresetsResponse))

    const res = await queryPresetsApi.listChromosomePresets(
      csrfToken,
      projectUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listChromosomePresetsResponse)
  })

  test('createChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.createChromosomePresets(
      csrfToken,
      projectUuid,
      retrieveChromosomePresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveChromosomePresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveChromosomePresetsResponse)
  })

  test('retrieveChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.retrieveChromosomePresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveChromosomePresetsResponse)
  })

  test('updateChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.updateChromosomePresets(
      csrfToken,
      entityUuid,
      retrieveChromosomePresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveChromosomePresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveChromosomePresetsResponse)
  })

  test('destroyChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.destroyChromosomePresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })
  test('cloneOtherChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.cloneOtherChromosomePresets(
      csrfToken,
      entityUuid,
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/clone-other/${entityUuid}/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveChromosomePresetsResponse)
  })

  test('cloneFactoryChromosomePresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveChromosomePresetsResponse))

    const res = await queryPresetsApi.cloneFactoryChromosomePresets(
      csrfToken,
      'the-name',
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/chromosomepresets/clone-factory-presets/the-name/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveChromosomePresetsResponse)
  })
  test('listFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.listFlagsEtcPresets(
      csrfToken,
      projectUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listFlagsEtcPresetsResponse)
  })

  test('createFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.createFlagsEtcPresets(
      csrfToken,
      projectUuid,
      retrieveFlagsEtcPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveFlagsEtcPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('retrieveFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.retrieveFlagsEtcPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('updateFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.updateFlagsEtcPresets(
      csrfToken,
      entityUuid,
      retrieveFlagsEtcPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveFlagsEtcPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('destroyFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.destroyFlagsEtcPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })

  test('cloneOtherFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.cloneOtherFlagsEtcPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/clone-other/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('cloneFactoryFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.cloneFactoryFlagsEtcPresets(
      csrfToken,
      'the-name'
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/clone-factory-presets/the-name/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('cloneOtherFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.cloneOtherFlagsEtcPresets(
      csrfToken,
      entityUuid,
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/clone-other/${entityUuid}/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('cloneFactoryFlagsEtcPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveFlagsEtcPresetsResponse))

    const res = await queryPresetsApi.cloneFactoryFlagsEtcPresets(
      csrfToken,
      'the-name',
      { label: 'my-label' }
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/flagsetcpresets/clone-factory-presets/the-name/`,
      {
        body: JSON.stringify({ label: 'my-label' }),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveFlagsEtcPresetsResponse)
  })

  test('listQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(listQuickPresetsResponse))

    const res = await queryPresetsApi.listQuickPresets(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listQuickPresetsResponse)
  })

  test('createQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQuickPresetsResponse))

    const res = await queryPresetsApi.createQuickPresets(
      csrfToken,
      projectUuid,
      retrieveQuickPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrieveQuickPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveQuickPresetsResponse)
  })

  test('retrieveQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQuickPresetsResponse))

    const res = await queryPresetsApi.retrieveQuickPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrieveQuickPresetsResponse)
  })

  test('updateQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQuickPresetsResponse))

    const res = await queryPresetsApi.updateQuickPresets(
      csrfToken,
      entityUuid,
      retrieveQuickPresetsResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrieveQuickPresetsResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrieveQuickPresetsResponse)
  })

  test('destroyQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQuickPresetsResponse))

    const res = await queryPresetsApi.destroyQuickPresets(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })

  test('cloneOtherQuickPresets', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrieveQuickPresetsResponse))

    const res = await queryPresetsApi.cloneOtherQuickPresets(
      csrfToken,
      entityUuid
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/quickpresets/clone-other/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrieveQuickPresetsResponse)
  })

  test('listPresetSetAll', async () => {
    fetch.mockResponseOnce(JSON.stringify(listPresetSetResponse))

    const res = await queryPresetsApi.listPresetSetAll(csrfToken)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/list/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listPresetSetResponse)
  })

  test('listPresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(listPresetSetResponse))

    const res = await queryPresetsApi.listPresetSet(csrfToken, projectUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/list-create/${projectUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(listPresetSetResponse)
  })

  test('createPresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.createPresetSet(
      csrfToken,
      projectUuid,
      retrievePresetSetResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/list-create/${projectUuid}/`,
      {
        body: JSON.stringify(retrievePresetSetResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrievePresetSetResponse)
  })

  test('retrievePresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.retrievePresetSet(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'GET',
      },
    ])
    expect(res).toEqual(retrievePresetSetResponse)
  })

  test('updatePresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.updatePresetSet(
      csrfToken,
      entityUuid,
      retrievePresetSetResponse
    )

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      {
        body: JSON.stringify(retrievePresetSetResponse),
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'PATCH',
      },
    ])
    expect(res).toEqual(retrievePresetSetResponse)
  })

  test('destroyPresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.destroyPresetSet(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/retrieve-update-destroy/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'DELETE',
      },
    ])
    expect(res).toBe(undefined)
  })

  test('cloneOtherPresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.cloneOtherPresetSet(csrfToken, entityUuid)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/clone-other/${entityUuid}/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrievePresetSetResponse)
  })

  test('cloneFactoryPresetSet', async () => {
    fetch.mockResponseOnce(JSON.stringify(retrievePresetSetResponse))

    const res = await queryPresetsApi.cloneFactoryPresetSet(csrfToken)

    expect(fetch.mock.calls.length).toEqual(1)
    expect(fetch.mock.calls[0]).toEqual([
      `/variants/ajax/presetset/clone-factory-presets/`,
      {
        body: null,
        credentials: 'same-origin',
        headers: {
          Accept: 'application/vnd.bihealth.varfish+json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
        method: 'POST',
      },
    ])
    expect(res).toEqual(retrievePresetSetResponse)
  })
})
