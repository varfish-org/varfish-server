import type { Meta, StoryObj } from '@storybook/vue3'

import Layout from './Layout.vue'

const meta: Meta<typeof Layout> = {
  title: 'Variants New / Layout',
  component: Layout,
}

export default meta

type Story = StoryObj<typeof Layout>

export const Example: Story = {
  render: () => ({
    components: { Layout },
    template: '<Layout  />',
  }),
}
