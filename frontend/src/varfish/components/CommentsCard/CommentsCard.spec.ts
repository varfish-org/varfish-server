import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, test, vi } from 'vitest'
import { reactive } from 'vue'

import { State } from '@/varfish/storeUtils'

import CommentsCard from './CommentsCard.vue'

const variant = {
  genomeBuild: 'grch37',
  chrom: '2',
  pos: 200,
  del: 'C',
  ins: 'T',
  userRepr: 'grch37-2-200-C-T',
}

/** Return a fake comments store in the given state. */
const makeCommentsStore = (state: State, caseUuid: string | null) =>
  reactive({
    storeState: { state },
    caseUuid,
    comments: null,
    projectWideVariantComments: [],
    retrieveComments: vi.fn().mockResolvedValue(undefined),
    retrieveProjectWideVariantComments: vi.fn().mockResolvedValue(undefined),
  })

const mountCard = (commentsStore: any) =>
  shallowMount(CommentsCard, {
    props: {
      commentsStore,
      variant,
      resultRowUuid: 'result-row-uuid',
      caseUuid: 'case-uuid',
    },
  })

describe('CommentsCard', () => {
  test('loads the comments of the displayed variant while another request of the store is running', async () => {
    const commentsStore = makeCommentsStore(State.Fetching, 'case-uuid')

    mountCard(commentsStore)
    await flushPromises()

    expect(commentsStore.retrieveComments).toHaveBeenCalledWith(
      variant,
      'case-uuid',
    )
    expect(
      commentsStore.retrieveProjectWideVariantComments,
    ).toHaveBeenCalledWith(variant)
  })

  test('loads the comments once the store has been initialized for the case', async () => {
    const commentsStore = makeCommentsStore(State.Initial, null)

    mountCard(commentsStore)
    await flushPromises()
    expect(commentsStore.retrieveComments).not.toHaveBeenCalled()

    commentsStore.storeState.state = State.Active
    commentsStore.caseUuid = 'case-uuid'
    await flushPromises()

    expect(commentsStore.retrieveComments).toHaveBeenCalledWith(
      variant,
      'case-uuid',
    )
  })
})
