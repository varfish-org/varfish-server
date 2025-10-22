import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import FrequencyPane from './FrequencyPane.vue'

describe('FrequencyPane', () => {
  let fetchMock: any

  beforeEach(() => {
    // Mock the global fetch function
    fetchMock = vi.fn()
    global.fetch = fetchMock
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  const makeWrapper = (props = {}) => {
    const defaultProps = {
      showFiltrationInlineHelp: false,
      filtrationComplexityMode: 'simple',
      case: {
        release: 'GRCh37',
      },
      querySettings: {
        thousand_genomes_enabled: true,
        exac_enabled: true,
        gnomad_exomes_enabled: true,
        gnomad_genomes_enabled: true,
        inhouse_enabled: true,
        mtdb_enabled: true,
        helixmtdb_enabled: true,
        mitomap_enabled: true,
      },
    }

    return mount(FrequencyPane, {
      props: {
        ...defaultProps,
        ...props,
      },
    })
  }

  it('renders without crashing', () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 0 }),
    })

    const wrapper = makeWrapper()
    expect(wrapper.exists()).toBe(true)
  })

  it('fetches inhouse database count on mount', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 1234 }),
    })

    makeWrapper()
    await flushPromises()

    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledWith('/cases/api/inhouse-db-stats/')
  })

  it('displays inhouse count when fetched successfully', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 5678 }),
    })

    const wrapper = makeWrapper()
    await flushPromises()

    // Check that the count is displayed with proper formatting
    const text = wrapper.text()
    expect(text).toContain('in-house DB')
    expect(text).toContain('5,678')
  })

  it('handles fetch errors gracefully', async () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(() => {})
    fetchMock.mockRejectedValue(new Error('Network error'))

    const wrapper = makeWrapper()
    await flushPromises()

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Failed to fetch inhouse database stats:',
      expect.any(Error),
    )

    // Component should still render even if fetch fails
    expect(wrapper.exists()).toBe(true)

    consoleErrorSpy.mockRestore()
  })

  it('does not display count when fetch returns non-ok response', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 500,
    })

    const wrapper = makeWrapper()
    await flushPromises()

    // Count should remain null, so the sample count should not be displayed
    const text = wrapper.text()
    expect(text).toContain('in-house DB')
    // Count should not be displayed for in-house DB when it's null
    expect(text).not.toMatch(/in-house DB\s*\(samples:/)
  })

  it('shows correct sample counts for GRCh37', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 100 }),
    })

    const wrapper = makeWrapper({
      case: { release: 'GRCh37' },
    })
    await flushPromises()

    const text = wrapper.text()
    // Check for GRCh37-specific counts
    expect(text).toContain('1,000') // 1000 Genomes
    expect(text).toContain('60,706') // ExAC
    expect(text).toContain('125,748') // gnomAD exomes
    expect(text).toContain('15,708') // gnomAD genomes
    expect(text).toContain('100') // inhouse
  })

  it('shows correct sample counts for GRCh38', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 200 }),
    })

    const wrapper = makeWrapper({
      case: { release: 'GRCh38' },
    })
    await flushPromises()

    const text = wrapper.text()
    // Check for GRCh38-specific counts
    expect(text).toContain('730,947') // gnomAD exomes
    expect(text).toContain('76,215') // gnomAD genomes
    expect(text).toContain('200') // inhouse
  })

  it('hides 1000 Genomes and ExAC rows for GRCh38', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 0 }),
    })

    const wrapper = makeWrapper({
      case: { release: 'GRCh38' },
    })
    await flushPromises()

    // Find all visible table rows
    const rows = wrapper.findAll('tbody tr').filter((row) => {
      const style = row.attributes('style')
      return !style || !style.includes('display: none')
    })

    const visibleText = rows.map((row) => row.text()).join(' ')

    // 1000 Genomes and ExAC should not be visible for GRCh38
    expect(visibleText).not.toContain('1000 Genomes')
    expect(visibleText).not.toContain('ExAC')
  })

  it('displays all frequency checkboxes', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 0 }),
    })

    const wrapper = makeWrapper()
    await flushPromises()

    const checkboxes = wrapper.findAll('input[type="checkbox"]')
    expect(checkboxes.length).toBeGreaterThan(0)
  })

  it('displays frequency input fields', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 0 }),
    })

    const wrapper = makeWrapper()
    await flushPromises()

    const inputs = wrapper.findAll('input[type="number"]')
    expect(inputs.length).toBeGreaterThan(0)
  })

  it('exposes vuelidate instance', () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 0 }),
    })

    const wrapper = makeWrapper()
    expect(wrapper.vm.v$).toBeDefined()
  })

  it('formats large numbers with locale separators', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({ count: 1234567 }),
    })

    const wrapper = makeWrapper()
    await flushPromises()

    const text = wrapper.text()
    // Should format with commas (or locale-appropriate separators)
    expect(text).toContain('1,234,567')
  })
})
