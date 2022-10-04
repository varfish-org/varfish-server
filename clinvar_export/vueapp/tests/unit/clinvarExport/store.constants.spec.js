import { describe, expect, test } from 'vitest'

import { AppState, WizardState } from '@/stores/clinvar-export'

describe('AppState', () => {
  test('defines constants', () => {
    expect(Object.keys(AppState).length).toBe(4)
    expect(AppState.initializing).toBe('initializing')
    expect(AppState.list).toBe('list')
    expect(AppState.edit).toBe('edit')
    expect(AppState.add).toBe('add')
  })
})

describe('WizardState', () => {
  test('defines constants', () => {
    expect(Object.keys(WizardState).length).toBe(2)
    expect(WizardState.submissionSet).toBe('submissionSet')
    expect(WizardState.submissions).toBe('submissions')
  })
})
