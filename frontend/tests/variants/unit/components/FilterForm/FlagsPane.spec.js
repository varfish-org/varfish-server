import { shallowMount } from '@vue/test-utils'
import { describe, expect, test } from 'vitest'

import FilterFormFlagsPane from '@/variants/components/FilterForm/FlagsPane.vue'

import querySettingsSingleton from '../../../data/query-settings-singleton.json'

describe('FilterFormFlagsPane.vue', () => {
  test('flags with help', () => {
    const wrapper = shallowMount(FilterFormFlagsPane, {
      props: {
        showFiltrationInlineHelp: true,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.findAll('.alert-secondary').length).toBe(1)
  })

  test('flags', async () => {
    const wrapper = shallowMount(FilterFormFlagsPane, {
      props: {
        showFiltrationInlineHelp: false,
        querySettings: querySettingsSingleton,
      },
    })

    expect(wrapper.findAll('input').length).toBe(29)

    const effectFlagsFlagBookmarked = wrapper.get(
      '#effect-flags-flag_bookmarked',
    )
    const effectFlagsFlagIncidentasl = wrapper.get(
      '#effect-flags-flag_incidental',
    )
    const effectFlagsFlagCandidate = wrapper.get('#effect-flags-flag_candidate')
    const effectFlagsFlagFinalCausative = wrapper.get(
      '#effect-flags-flag_final_causative',
    )
    const effectFlagsFlagForValidation = wrapper.get(
      '#effect-flags-flag_for_validation',
    )
    const effectFlagsFlagNoDiseaseAssociation = wrapper.get(
      '#effect-flags-flag_no_disease_association',
    )
    const effectFlagsFlagSegregates = wrapper.get(
      '#effect-flags-flag_segregates',
    )
    const effectFlagsFlagDoesntSegregate = wrapper.get(
      '#effect-flags-flag_doesnt_segregate',
    )
    const effectFlagsFlagSimpleEmpty = wrapper.get(
      '#effect-flags-flag_simple_empty',
    )

    const effectFlagsFlagVisualPositive = wrapper.get(
      '#effect-flags-flag_visual-positive',
    )
    const effectFlagsFlagVisualUncertain = wrapper.get(
      '#effect-flags-flag_visual-uncertain',
    )
    const effectFlagsFlagVisualNegative = wrapper.get(
      '#effect-flags-flag_visual-negative',
    )
    const effectFlagsFlagVisualEmpty = wrapper.get(
      '#effect-flags-flag_visual-empty',
    )

    const effectFlagsFlagValidationPositive = wrapper.get(
      '#effect-flags-flag_validation-positive',
    )
    const effectFlagsFlagValidationUncertain = wrapper.get(
      '#effect-flags-flag_validation-uncertain',
    )
    const effectFlagsFlagValidationNegative = wrapper.get(
      '#effect-flags-flag_validation-negative',
    )
    const effectFlagsFlagValidationEmpty = wrapper.get(
      '#effect-flags-flag_validation-empty',
    )

    const effectFlagsFlagPhenotypeMatchPositive = wrapper.get(
      '#effect-flags-flag_phenotype_match-positive',
    )
    const effectFlagsFlagPhenotypeMatchUncertain = wrapper.get(
      '#effect-flags-flag_phenotype_match-uncertain',
    )
    const effectFlagsFlagPhenotypeMatchNegative = wrapper.get(
      '#effect-flags-flag_phenotype_match-negative',
    )
    const effectFlagsFlagPhenotypeMatchEmpty = wrapper.get(
      '#effect-flags-flag_phenotype_match-empty',
    )

    const effectFlagsFlagMolecularPositive = wrapper.get(
      '#effect-flags-flag_molecular-positive',
    )
    const effectFlagsFlagMolecularUncertain = wrapper.get(
      '#effect-flags-flag_molecular-uncertain',
    )
    const effectFlagsFlagMolecularNegative = wrapper.get(
      '#effect-flags-flag_molecular-negative',
    )
    const effectFlagsFlagMolecularEmpty = wrapper.get(
      '#effect-flags-flag_molecular-empty',
    )

    const effectFlagsFlagSummaryPositive = wrapper.get(
      '#effect-flags-flag_summary-positive',
    )
    const effectFlagsFlagSummaryUncertain = wrapper.get(
      '#effect-flags-flag_summary-uncertain',
    )
    const effectFlagsFlagSummaryNegative = wrapper.get(
      '#effect-flags-flag_summary-negative',
    )
    const effectFlagsFlagSummaryEmpty = wrapper.get(
      '#effect-flags-flag_summary-empty',
    )

    await effectFlagsFlagBookmarked.setValue()
    await effectFlagsFlagIncidentasl.setValue(false)
    await effectFlagsFlagCandidate.setValue(false)
    await effectFlagsFlagFinalCausative.setValue()
    await effectFlagsFlagForValidation.setValue(false)
    await effectFlagsFlagNoDiseaseAssociation.setValue()
    await effectFlagsFlagSegregates.setValue(false)
    await effectFlagsFlagDoesntSegregate.setValue()
    await effectFlagsFlagSimpleEmpty.setValue(false)

    await effectFlagsFlagVisualPositive.setValue()
    await effectFlagsFlagVisualUncertain.setValue(false)
    await effectFlagsFlagVisualNegative.setValue()
    await effectFlagsFlagVisualEmpty.setValue(false)

    await effectFlagsFlagValidationPositive.setValue()
    await effectFlagsFlagValidationUncertain.setValue(false)
    await effectFlagsFlagValidationNegative.setValue()
    await effectFlagsFlagValidationEmpty.setValue(false)

    await effectFlagsFlagPhenotypeMatchPositive.setValue()
    await effectFlagsFlagPhenotypeMatchUncertain.setValue(false)
    await effectFlagsFlagPhenotypeMatchNegative.setValue()
    await effectFlagsFlagPhenotypeMatchEmpty.setValue(false)

    await effectFlagsFlagMolecularPositive.setValue()
    await effectFlagsFlagMolecularUncertain.setValue(false)
    await effectFlagsFlagMolecularNegative.setValue()
    await effectFlagsFlagMolecularEmpty.setValue(false)

    await effectFlagsFlagSummaryPositive.setValue()
    await effectFlagsFlagSummaryUncertain.setValue(false)
    await effectFlagsFlagSummaryNegative.setValue()
    await effectFlagsFlagSummaryEmpty.setValue(false)

    expect(effectFlagsFlagBookmarked.element.checked).toBeTruthy()
    expect(effectFlagsFlagIncidentasl.element.checked).toBeFalsy()
    expect(effectFlagsFlagCandidate.element.checked).toBeFalsy()
    expect(effectFlagsFlagFinalCausative.element.checked).toBeTruthy()
    expect(effectFlagsFlagForValidation.element.checked).toBeFalsy()
    expect(effectFlagsFlagNoDiseaseAssociation.element.checked).toBeTruthy()
    expect(effectFlagsFlagSegregates.element.checked).toBeFalsy()
    expect(effectFlagsFlagDoesntSegregate.element.checked).toBeTruthy()
    expect(effectFlagsFlagSimpleEmpty.element.checked).toBeFalsy()

    expect(effectFlagsFlagVisualPositive.element.checked).toBeTruthy()
    expect(effectFlagsFlagVisualUncertain.element.checked).toBeFalsy()
    expect(effectFlagsFlagVisualNegative.element.checked).toBeTruthy()
    expect(effectFlagsFlagVisualEmpty.element.checked).toBeFalsy()

    expect(effectFlagsFlagValidationPositive.element.checked).toBeTruthy()
    expect(effectFlagsFlagValidationUncertain.element.checked).toBeFalsy()
    expect(effectFlagsFlagValidationNegative.element.checked).toBeTruthy()
    expect(effectFlagsFlagValidationEmpty.element.checked).toBeFalsy()

    expect(effectFlagsFlagPhenotypeMatchPositive.element.checked).toBeTruthy()
    expect(effectFlagsFlagPhenotypeMatchUncertain.element.checked).toBeFalsy()
    expect(effectFlagsFlagPhenotypeMatchNegative.element.checked).toBeTruthy()
    expect(effectFlagsFlagPhenotypeMatchEmpty.element.checked).toBeFalsy()

    expect(effectFlagsFlagMolecularPositive.element.checked).toBeTruthy()
    expect(effectFlagsFlagMolecularUncertain.element.checked).toBeFalsy()
    expect(effectFlagsFlagMolecularNegative.element.checked).toBeTruthy()
    expect(effectFlagsFlagMolecularEmpty.element.checked).toBeFalsy()

    expect(effectFlagsFlagSummaryPositive.element.checked).toBeTruthy()
    expect(effectFlagsFlagSummaryUncertain.element.checked).toBeFalsy()
    expect(effectFlagsFlagSummaryNegative.element.checked).toBeTruthy()
    expect(effectFlagsFlagSummaryEmpty.element.checked).toBeFalsy()
  })
})
