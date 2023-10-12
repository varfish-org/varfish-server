// import FilterResultsTableVariantIcons from '@variants/components/FilterResultsTable/VariantIcons.vue'
// import { shallowMount } from '@vue/test-utils'
import { describe, test } from 'vitest'

// TODO [TEST_STUB] Pinia store missing
describe('FilterResultsTable/VariantIcons.vue', () => {
  test('results variant icons all active', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 1,
    //         comment_count: 1,
    //         acmg_class_override: null,
    //         acmg_class_auto: 4,
    //         symbol: null,
    //         gene_symbol: 'GENE',
    //         rsid: 'rs12345',
    //         in_clinvar: true,
    //         vcv: 'VCV123',
    //         summary_pathogenicity_label: 'pathogenic',
    //         hgmd_public_overlap: true,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(wrapper.find('fa-solid-bookmark-stub').exists()).toBe(true)
    // expect(wrapper.find('fa-solid-comment-stub').exists()).toBe(true)
    // expect(acmg.text()).toBe('4')
    // expect(
    //   wrapper.get('fa-regular-database-stub').classes('icon-inactive')
    // ).toBe(false)
    // expect(
    //   wrapper.get('fa-regular-hospital-stub').classes('icon-inactive')
    // ).toBe(false)
  })

  test('results variant icons all inactive', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: null,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(wrapper.find('fa-regular-bookmark-stub').exists()).toBe(true)
    // expect(wrapper.find('fa-regular-comment-stub').exists()).toBe(true)
    // expect(acmg.text()).toBe('-')
    // expect(
    //   wrapper.get('fa-regular-database-stub').classes('icon-inactive')
    // ).toBe(true)
    // expect(
    //   wrapper.get('fa-regular-hospital-stub').classes('icon-inactive')
    // ).toBe(true)
  })

  test('results variant icons acmg 1', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 1,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('1')
    // expect(acmg.classes()).toBe('badge-badge')
  })

  test('results variant icons acmg 1', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 1,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('1')
    // expect(acmg.classes()).toBe('badge-success')
  })

  test('results variant icons acmg 2', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 2,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('2')
    // expect(acmg.classes()).toBe('badge-success')
  })

  test('results variant icons acmg 3', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 3,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('3')
    // expect(acmg.classes()).toBe('badge-warning')
  })

  test('results variant icons acmg 4', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 4,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('4')
    // expect(acmg.classes()).toBe('badge-danger')
  })

  test('results variant icons acmg 5', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: null,
    //         acmg_class_auto: 5,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('5')
    // expect(acmg.classes()).toBe('badge-danger')
  })

  test('results variant icons acmg override', () => {
    // const wrapper = shallowMount(FilterResultsTableVariantIcons, {
    //   props: {
    //     params: {
    //       data: {
    //         flag_count: 0,
    //         comment_count: 0,
    //         acmg_class_override: 4,
    //         acmg_class_auto: 2,
    //         symbol: null,
    //         gene_symbol: null,
    //         rsid: null,
    //         in_clinvar: false,
    //         vcv: null,
    //         summary_pathogenicity_label: null,
    //         hgmd_public_overlap: false,
    //       },
    //     },
    //   },
    // })
    //
    // const acmg = wrapper.find('badge')
    //
    // expect(acmg.text()).toBe('4')
    // expect(acmg.classes()).toBe('badge-danger')
  })
})
