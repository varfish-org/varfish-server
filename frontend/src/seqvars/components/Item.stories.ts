import type { Meta, StoryObj } from '@storybook/vue3'

import Item from './Item.vue'

const meta: Meta<typeof Item> = {
  title: 'Seqvars / Item',
  component: Item,
}

export default meta

type Story = StoryObj<typeof Item>

export const Example: Story = {
  args: { default: 'Some text' },

  render: (args) => ({
    components: { Item },
    setup() {
      return { args }
    },
    template:
      '<div style="background: white"><Item v-bind="args">{{args.default}}</Item></div>',
  }),
}
