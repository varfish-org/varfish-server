import { ref } from 'vue'
import type { Meta, StoryObj } from '@storybook/vue3'

import InheritanceModeControls from './InheritanceModeControls.vue'

const meta: Meta<typeof InheritanceModeControls> = {
  title: 'Variants New / InheritanceModeControls',
  component: InheritanceModeControls,
}

export default meta

type Story = StoryObj<typeof InheritanceModeControls>

export const Example: Story = {
  render: () => ({
    components: { InheritanceModeControls },
    setup() {
      const model = ref(new Set())
      const updateModel = (event) => (model.value = event)
      return { model, updateModel }
    },
    template:
      '<div style="background: white; padding: 16px"><InheritanceModeControls :modelValue="model" @update:modelValue="updateModel"/></div>',
  }),
}
