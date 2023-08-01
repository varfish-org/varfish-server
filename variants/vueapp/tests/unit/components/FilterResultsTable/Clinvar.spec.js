import FilterResultsTableClinvar from '@variants/components/FilterResultsTable/Clinvar.vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

describe('FilterResultsTableClinvar.vue', () => {
  test('results clinvar pathogenic', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'pathogenic',
            summary_review_status_label: 'practice guideline',
            summary_gold_stars: 4,
          },
        },
      },
    })

    const text = wrapper.find('.badge-danger')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('pathogenic')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(4)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(0)
  })

  test('results clinvar likely pathogenic', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'likely pathogenic',
            summary_review_status_label: 'expert panel',
            summary_gold_stars: 3,
          },
        },
      },
    })

    const text = wrapper.find('.badge-warning')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('likely pathogenic')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(3)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(1)
  })

  test('results clinvar uncertain significance', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'uncertain significance',
            summary_review_status_label:
              'criteria provided, multiple submitters, no conflicts',
            summary_gold_stars: 2,
          },
        },
      },
    })

    const text = wrapper.find('.badge-info')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('uncertain significance')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(2)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(2)
  })

  test('results clinvar likely benign', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'likely benign',
            summary_review_status_label: 'criteria provided, single submitter',
            summary_gold_stars: 1,
          },
        },
      },
    })

    const text = wrapper.find('.badge-secondary')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('likely benign')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(1)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(3)
  })

  test('results clinvar benign', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'benign',
            summary_review_status_label: 'no assertion criteria provided',
            summary_gold_stars: 0,
          },
        },
      },
    })

    const text = wrapper.find('.badge-secondary')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('benign')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(0)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(4)
  })

  test('results clinvar false label', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: 'UNKNOWN',
            summary_review_status_label: '...',
            summary_gold_stars: 2,
          },
        },
      },
    })

    const text = wrapper.find('.badge-secondary')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('UNKNOWN')
    expect(wrapper.findAll('fa-solid-star-stub').length).toBe(2)
    expect(wrapper.findAll('fa-regular-star-stub').length).toBe(2)
  })

  test('results clinvar no data', () => {
    const wrapper = shallowMount(FilterResultsTableClinvar, {
      props: {
        params: {
          data: {
            summary_pathogenicity_label: null,
            summary_review_status_label: null,
            summary_gold_stars: null,
          },
        },
      },
    })

    const text = wrapper.find('.badge-light')

    expect(text.exists()).toBe(true)
    expect(text.text()).toBe('-')
  })
})
