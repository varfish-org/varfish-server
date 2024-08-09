import type { Meta, StoryObj } from '@storybook/vue3'

import CollapsibleGroup from './CollapsibleGroup.vue'

const meta: Meta<typeof CollapsibleGroup> = {
  title: 'Seqvars / Collapsible Group',
  component: CollapsibleGroup,
}

export default meta

type Story = StoryObj<typeof CollapsibleGroup>

export const Example: Story = {
  args: { title: 'Section Title' },

  render: (args) => ({
    components: { CollapsibleGroup },
    setup() {
      return { args }
    },
    template: '<CollapsibleGroup v-bind="args">Some content</CollapsibleGroup>',
  }),
}
