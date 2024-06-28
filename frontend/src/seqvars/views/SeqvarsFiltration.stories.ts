import type { Meta, StoryObj } from '@storybook/vue3'

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
    template: '<SeqvarsFiltration  />',
  }),
}
