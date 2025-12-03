import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import FilterFormClinvarPane from '@/variants/components/FilterForm/ClinvarPane.vue'

describe('FilterFormClinvarPane.vue', () => {
  test('clinvar pane all unchecked', () => {
    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: {
        showFiltrationInlineHelp: false,
        querySettings: {
          require_in_clinvar: false,
          clinvar_paranoid_mode: false,
          clinvar_include_pathogenic: false,
          clinvar_include_likely_pathogenic: false,
          clinvar_include_uncertain_significance: false,
          clinvar_include_likely_benign: false,
          clinvar_include_benign: false,
          clinvar_include_conflicting: false,
        },
      },
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    expect(wrapper.find('.alert-secondary').exists()).toBeFalsy()
    expect(requireInClinvar.element.checked).toBeFalsy()
    expect(clinvarParanoidMode.element.disabled).toBeTruthy()
    expect(clinvarParanoidMode.element.checked).toBeFalsy()
    expect(clinvarIncludePathogenic.element.disabled).toBeTruthy()
    expect(clinvarIncludePathogenic.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeFalsy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeTruthy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeFalsy()
    expect(clinvarIncludeBenign.element.disabled).toBeTruthy()
    expect(clinvarIncludeBenign.element.checked).toBeFalsy()
  })

  test('clinvar pane not required in clinvar', () => {
    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: {
        showFiltrationInlineHelp: false,
        querySettings: {
          require_in_clinvar: false,
          clinvar_paranoid_mode: false,
          clinvar_include_pathogenic: true,
          clinvar_include_likely_pathogenic: true,
          clinvar_include_uncertain_significance: false,
          clinvar_include_likely_benign: false,
          clinvar_include_benign: false,
          clinvar_include_conflicting: false,
        },
      },
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    expect(requireInClinvar.element.checked).toBeFalsy()
    expect(clinvarParanoidMode.element.disabled).toBeTruthy()
    expect(clinvarParanoidMode.element.checked).toBeFalsy()
    expect(clinvarIncludePathogenic.element.disabled).toBeTruthy()
    expect(clinvarIncludePathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeTruthy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeFalsy()
    expect(clinvarIncludeBenign.element.disabled).toBeTruthy()
    expect(clinvarIncludeBenign.element.checked).toBeFalsy()
  })

  test('clinvar pane required in clinvar', () => {
    const props = {
      showFiltrationInlineHelp: false,
      querySettings: {
        require_in_clinvar: true,
        clinvar_paranoid_mode: false,
        clinvar_include_pathogenic: true,
        clinvar_include_likely_pathogenic: true,
        clinvar_include_uncertain_significance: false,
        clinvar_include_likely_benign: false,
        clinvar_include_benign: false,
        clinvar_include_conflicting: false,
      },
    }

    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: props,
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    expect(requireInClinvar.element.checked).toBeTruthy()
    expect(clinvarParanoidMode.element.disabled).toBeFalsy()
    expect(clinvarParanoidMode.element.checked).toBeFalsy()
    expect(clinvarIncludePathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludePathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeFalsy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeFalsy()
    expect(clinvarIncludeBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeBenign.element.checked).toBeFalsy()
  })

  test('clinvar pane activate required in clinvar', async () => {
    const props = {
      showFiltrationInlineHelp: false,
      querySettings: {
        require_in_clinvar: false,
        clinvar_paranoid_mode: false,
        clinvar_include_pathogenic: true,
        clinvar_include_likely_pathogenic: true,
        clinvar_include_uncertain_significance: false,
        clinvar_include_likely_benign: false,
        clinvar_include_benign: false,
        clinvar_include_conflicting: false,
      },
    }

    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: props,
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    await requireInClinvar.setValue()
    expect(requireInClinvar.element.checked).toBeTruthy()
    expect(clinvarParanoidMode.element.disabled).toBeFalsy()
    expect(clinvarParanoidMode.element.checked).toBeFalsy()
    expect(clinvarIncludePathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludePathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeFalsy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeFalsy()
    expect(clinvarIncludeBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeBenign.element.checked).toBeFalsy()
  })

  test('clinvar pane activate paranoid mode', async () => {
    const props = {
      showFiltrationInlineHelp: false,
      querySettings: {
        require_in_clinvar: true,
        clinvar_paranoid_mode: false,
        clinvar_include_pathogenic: true,
        clinvar_include_likely_pathogenic: true,
        clinvar_include_uncertain_significance: false,
        clinvar_include_likely_benign: false,
        clinvar_include_benign: false,
        clinvar_include_conflicting: false,
      },
    }

    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: props,
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    await clinvarParanoidMode.setValue()
    expect(requireInClinvar.element.checked).toBeTruthy()
    expect(clinvarParanoidMode.element.disabled).toBeFalsy()
    expect(clinvarParanoidMode.element.checked).toBeTruthy()
    expect(clinvarIncludePathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludePathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeFalsy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeFalsy()
    expect(clinvarIncludeBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeBenign.element.checked).toBeFalsy()
  })

  test('clinvar pane activate include all', async () => {
    const props = {
      showFiltrationInlineHelp: false,
      querySettings: {
        require_in_clinvar: true,
        clinvar_paranoid_mode: false,
        clinvar_include_pathogenic: false,
        clinvar_include_likely_pathogenic: false,
        clinvar_include_uncertain_significance: false,
        clinvar_include_likely_benign: false,
        clinvar_include_benign: false,
        clinvar_include_conflicting: false,
      },
    }

    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: props,
    })
    const requireInClinvar = wrapper.find('#clinvar-require-in-clinvar')
    const clinvarParanoidMode = wrapper.find('#clinvar-paranoid-mode')
    const clinvarIncludePathogenic = wrapper.find('#clinvar-include-pathogenic')
    const clinvarIncludeLikelyPathogenic = wrapper.find(
      '#clinvar-include-likely_pathogenic',
    )
    const clinvarIncludeUncertainSignificance = wrapper.find(
      '#clinvar-include-uncertain_significance',
    )
    const clinvarIncludeLikelyBenign = wrapper.find(
      '#clinvar-include-likely_benign',
    )
    const clinvarIncludeBenign = wrapper.find('#clinvar-include-benign')

    await clinvarIncludePathogenic.setValue()
    await clinvarIncludeLikelyPathogenic.setValue()
    await clinvarIncludeUncertainSignificance.setValue()
    await clinvarIncludeLikelyBenign.setValue()
    await clinvarIncludeBenign.setValue()
    expect(requireInClinvar.element.checked).toBeTruthy()
    expect(clinvarParanoidMode.element.disabled).toBeFalsy()
    expect(clinvarParanoidMode.element.checked).toBeFalsy()
    expect(clinvarIncludePathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludePathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyPathogenic.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyPathogenic.element.checked).toBeTruthy()
    expect(clinvarIncludeUncertainSignificance.element.disabled).toBeFalsy()
    expect(clinvarIncludeUncertainSignificance.element.checked).toBeTruthy()
    expect(clinvarIncludeLikelyBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeLikelyBenign.element.checked).toBeTruthy()
    expect(clinvarIncludeBenign.element.disabled).toBeFalsy()
    expect(clinvarIncludeBenign.element.checked).toBeTruthy()
  })

  test('clinvar pane with help', () => {
    const props = {
      showFiltrationInlineHelp: true,
      querySettings: {
        require_in_clinvar: true,
        clinvar_paranoid_mode: false,
        clinvar_include_pathogenic: true,
        clinvar_include_likely_pathogenic: true,
        clinvar_include_uncertain_significance: false,
        clinvar_include_likely_benign: false,
        clinvar_include_benign: false,
        clinvar_include_conflicting: false,
      },
    }

    const wrapper = shallowMount(FilterFormClinvarPane, {
      props: props,
    })
    expect(wrapper.find('.alert-secondary').exists()).toBeTruthy()
  })
})
