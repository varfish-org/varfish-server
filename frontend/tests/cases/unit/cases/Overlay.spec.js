import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, test, vi } from 'vitest'

import Overlay from '@/varfish/components/Overlay.vue'

describe('Overlay.vue', () => {
  beforeAll(() => {
    // Disable warnings
    vi.spyOn(console, 'warn').mockImplementation(vi.fn())
  })
  test('render without message', () => {
    const wrapper = mount(Overlay)

    expect(wrapper.findAll('.spinner-border').length).toBe(1)
  })

  test('render with message', () => {
    const wrapper = mount(Overlay, {
      props: {
        message: 'Hello World!',
      },
    })

    expect(wrapper.findAll('.spinner-border').length).toBe(1)
    expect(wrapper.findAll('.text-muted')[0].html()).toMatch(/Hello World!/)
  })
})
