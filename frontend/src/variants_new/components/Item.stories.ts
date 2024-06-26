import type { Meta, StoryObj } from '@storybook/vue3'

import Item from './Item.vue'

const meta: Meta<typeof Item> = {
  title: 'Variants New / Item',
  component: Item,
}

export default meta

type Story = StoryObj<typeof Item>

export const Example: Story = {
  args: { body: 'Item text' },

  render: (args) => ({
    components: { Item },
    setup() {
      return { args }
    },
    template:
      '<div style="background: white"><Item v-bind="args">{{args.body}}</Item></div>',
  }),
}
