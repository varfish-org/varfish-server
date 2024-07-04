import { ref } from 'vue'
import type { Meta, StoryObj } from '@storybook/vue3'

import FrequencyControls from './FrequencyControls.vue'

const meta: Meta<typeof FrequencyControls> = {
  title: 'Seqvars / Frequency Controls',
  component: FrequencyControls,
}

export default meta

type Story = StoryObj<typeof FrequencyControls>

export const Example: Story = {
  render: () => ({
    components: { FrequencyControls },
    setup() {
      const model = ref(new Set())
      const updateModel = (value: Set<string>) => (model.value = value)
      return { model, updateModel }
    },
    template:
      '<div style="background: white; padding: 16px"><FrequencyControls :modelValue="model" @update:modelValue="updateModel"/></div>',
  }),
}
