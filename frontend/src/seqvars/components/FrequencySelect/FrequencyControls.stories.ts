import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'

import FrequencyControls from './FrequencyControls.vue'
import { getFrequencyValueFromPreset } from './utils'

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
      const model = ref(getFrequencyValueFromPreset('dominant relaxed').values)
      console.log(model.value)
      const updateModel = (value: typeof model.value) => (model.value = value)
      return { model, updateModel }
    },
    template:
      '<div style="background: white; padding: 16px"><FrequencyControls :modelValue="model" @update:modelValue="updateModel"/></div>',
  }),
}
