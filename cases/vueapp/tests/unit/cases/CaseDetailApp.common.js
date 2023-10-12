/** Common code for the CaseDetail*.spec.js tests. */

import { useCaseListStore } from '@cases/stores/caseList'
import { createTestingPinia } from '@pinia/testing'
import { mount } from '@vue/test-utils'
import { vi } from 'vitest'

import { quoteattr } from '../../helpers'

export const makeWrapper = (
  component,
  initialState = {},
  props = {},
  appContext,
  documentInnerHtml = null,
) => {
  // Define default app context.
  appContext = appContext ?? {
    csrf_token: 'fake-token',
    project: {
      sodar_uuid: 'fake-uuid',
      title: 'fake-title',
    },
  }
  const appContextStr = quoteattr(JSON.stringify(appContext))

  // Define body HTML together with a tag for the app context JSON.
  document.body.innerHTML =
    documentInnerHtml ??
    `
    <div>
      <div id="sodar-ss-app-context" app-context="{appContextStr}" />
      <div id="app"></div>
    </div>
  `.replace('{appContextStr}', appContextStr)

  // Setup testing pinia.
  const testingPinia = createTestingPinia({
    initialState,
    createSpy: vi.fn,
  })

  // Mark case details store as initialized.
  const caseListStore = useCaseListStore()
  caseListStore.initializeRes = Promise.resolve()

  const result = mount(component, {
    props,
    attachTo: document.getElementById('app'),
    global: {
      plugins: [testingPinia],
    },
    shallow: true,
  })

  return result
}
