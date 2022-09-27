import { AppState, WizardState } from '@/store/modules/clinvarExport'

describe('AppState', () => {
  it('defines constants', () => {
    expect(Object.keys(AppState).length).toBe(4)
    expect(AppState.initializing).toBe('initializing')
    expect(AppState.list).toBe('list')
    expect(AppState.edit).toBe('edit')
    expect(AppState.add).toBe('add')
  })
})

describe('WizardState', () => {
  it('defines constants', () => {
    expect(Object.keys(WizardState).length).toBe(2)
    expect(WizardState.submissionSet).toBe('submissionSet')
    expect(WizardState.submissions).toBe('submissions')
  })
})
