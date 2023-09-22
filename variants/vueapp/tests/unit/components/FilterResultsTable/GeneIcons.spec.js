// import FilterResultsTableFrequency from '@variants/components/FilterResultsTable/Frequency.vue'
// import { shallowMount } from '@vue/test-utils'
import { describe, test } from 'vitest'

// TODO [TEST_STUB] Pinia store missing
describe('FilterResultsTable/Frequency.vue', () => {
  test('results gene icons acmg gene', () => {
    /*
    const wrapper = shallowMount(FilterResultsTableFrequency, {
      props: {
        params: {
          data: {
            acmg_symbol: 'true',
            modes_of_inheritance: ['AD', 'AR'],
            disease_gene: 'true',
          },
        },
      },
    })

    const badges = wrapper.findAll('.badge-info')

    expect(wrapper.find('fa-solid-user-md-stub').exists()).toBe(true)
    expect(wrapper.find('fa-solid-lightbulb-stub').exists()).toBe(true)
    expect(badges.length).toBe(2)
    expect(badges[0].text()).toBe('AD')
    expect(badges[1].text()).toBe('AR')
*/
  })

  test('results gene icons disease gene', () => {
    /*    const wrapper = shallowMount(FilterResultsTableFrequency, {
      props: {
        params: {
          data: {
            acmg_symbol: null,
            modes_of_inheritance: ['AR'],
            disease_gene: 'true',
          },
        },
      },
    })

    const badges = wrapper.findAll('.badge-info')

    expect(wrapper.find('fa-regular-user-md-stub').exists()).toBe(true)
    expect(wrapper.find('fa-solid-lightbulb-stub').exists()).toBe(true)
    expect(badges.length).toBe(1)
    expect(badges[1].text()).toBe('AR')*/
  })

  test('results gene icons no disease gene', () => {
    /*    const wrapper = shallowMount(FilterResultsTableFrequency, {
      props: {
        params: {
          data: {
            acmg_symbol: null,
            modes_of_inheritance: [],
            disease_gene: 'false',
          },
        },
      },
    })

    expect(wrapper.find('fa-regular-user-md-stub').exists()).toBe(true)
    expect(wrapper.find('fa-regular-lightbulb-stub').exists()).toBe(true)
    expect(wrapper.findAll('.badge-info').length).toBe(0)*/
  })
})
