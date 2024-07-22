import type { Meta, StoryObj } from '@storybook/vue3'
import { delay, http, HttpResponse } from 'msw'

import hpoFixture from '@/../ext/reev-frontend-lib/src/api/viguno/fixture.resolveHpoTermByName.foobar.json'
import omimFixture from '@/../ext/reev-frontend-lib/src/api/viguno/fixture.queryOmimTermsByName.early.json'

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
    template: '<SeqvarsFiltration :presets="fixture"  />',
  }),
  parameters: {
    msw: {
      handlers: [
        http.get('/proxy/varfish/viguno/hpo/terms', async () => {
          await delay(1000)
          return HttpResponse.json(hpoFixture)
        }),
        http.get('/proxy/varfish/viguno/hpo/omims', async () => {
          await delay(1000)
          return HttpResponse.json(omimFixture)
        }),
      ],
    },
  },
}
