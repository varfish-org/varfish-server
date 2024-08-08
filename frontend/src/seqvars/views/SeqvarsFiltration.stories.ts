import type { Meta, StoryObj } from '@storybook/vue3'
import { delay, http, HttpResponse } from 'msw'

import fixture from './fixture.SeqvarsFiltration.json'
import SeqvarsFiltration from './SeqvarsFiltration.vue'

const meta: Meta<typeof SeqvarsFiltration> = {
  title: 'Seqvars / Seqvars Filtration',
  component: SeqvarsFiltration,
}

export default meta

type Story = StoryObj<typeof SeqvarsFiltration>

export const Example: Story = {
  render: () => ({
    components: { SeqvarsFiltration },
    setup() {
      return { fixture }
    },
    template: '<SeqvarsFiltration :presetsDetails="fixture"  />',
  }),
  parameters: {
    msw: {
      handlers: [
        http.get('/proxy/varfish/viguno/hpo/terms', async () => {
          await delay(1000)
          return HttpResponse.json({
            version: { hpo: '2023-06-06', viguno: '0.2.0' },
            query: {
              term_id: null,
              name: 'foobar',
              max_results: 100,
              genes: false,
            },
            result: [],
          })
        }),
        http.get('/proxy/varfish/viguno/hpo/omims', async () => {
          await delay(1000)
          return HttpResponse.json({
            version: { hpo: '2023-06-06', viguno: '0.2.0' },
            query: {
              omim_id: null,
              name: 'early',
              match_: 'contains',
              max_results: 100,
              hpo_terms: false,
            },
            result: [
              {
                omim_id: 'OMIM:165800',
                name: 'Short stature and advanced bone age, with or without early-onset osteoarthritis and/or osteochondritis dissecans',
              },
              {
                omim_id: 'OMIM:167320',
                name: 'Inclusion body myopathy with early-onset paget disease with or without frontotemporal dementia 1',
              },
              {
                omim_id: 'OMIM:208920',
                name: 'Ataxia, early-onset, with oculomotor apraxia and hypoalbuminemia',
              },
            ],
          })
        }),
      ],
    },
  },
}
