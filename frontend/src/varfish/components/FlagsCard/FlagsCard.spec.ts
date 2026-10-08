import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import { reactive } from 'vue'

import { State } from '@/varfish/storeUtils'

import FlagsCard from './FlagsCard.vue'

const variant = {
  genomeBuild: 'grch37',
  chrom: '2',
  pos: 200,
  del: 'C',
  ins: 'T',
  userRepr: 'grch37-2-200-C-T',
}

const emptyFlagsTemplate = { flag_bookmarked: false }
const initialFlagsTemplate = { flag_bookmarked: true }

/** Return a fake flags store in the given state. */
const makeFlagsStore = (state: State, caseUuid: string | null) =>
  reactive({
    storeState: { state },
    caseUuid,
    flags: null as any,
    projectWideVariantFlags: [],
    emptyFlagsTemplate,
    initialFlagsTemplate,
    retrieveFlags: vi.fn().mockResolvedValue(undefined),
    retrieveProjectWideVariantFlags: vi.fn().mockResolvedValue(undefined),
    updateFlags: vi.fn().mockResolvedValue(undefined),
    deleteFlags: vi.fn().mockResolvedValue(undefined),
    createFlags: vi.fn().mockResolvedValue(undefined),
  })

const mountCard = (flagsStore: any) =>
  shallowMount(FlagsCard, {
    props: {
      flagsStore,
      variant,
      resultRowUuid: 'result-row-uuid',
      caseUuid: 'case-uuid',
    },
  })

describe('FlagsCard', () => {
  test('loads the flags of the displayed variant while another request of the store is running', async () => {
    const flagsStore = makeFlagsStore(State.Fetching, 'case-uuid')

    mountCard(flagsStore)
    await flushPromises()

    expect(flagsStore.retrieveFlags).toHaveBeenCalledWith(variant, 'case-uuid')
    expect(flagsStore.retrieveProjectWideVariantFlags).toHaveBeenCalledWith(
      variant,
    )
  })

  test('loads the flags once the store has been initialized for the case', async () => {
    const flagsStore = makeFlagsStore(State.Initial, null)

    mountCard(flagsStore)
    await flushPromises()
    expect(flagsStore.retrieveFlags).not.toHaveBeenCalled()

    flagsStore.storeState.state = State.Active
    flagsStore.caseUuid = 'case-uuid'
    await flushPromises()

    expect(flagsStore.retrieveFlags).toHaveBeenCalledWith(variant, 'case-uuid')
  })

  test('submits flag changes for the displayed variant', async () => {
    const flagsStore = makeFlagsStore(State.Active, 'case-uuid')
    flagsStore.flags = { sodar_uuid: 'flags-uuid', flag_bookmarked: false }
    const wrapper = mountCard(flagsStore)
    await flushPromises()

    const submitButton = wrapper
      .findAll('v-btn')
      .find((button) => button.text().includes('Submit'))
    await submitButton!.trigger('click')
    await flushPromises()

    expect(flagsStore.updateFlags).toHaveBeenCalledWith(
      variant,
      expect.anything(),
    )
  })
})
