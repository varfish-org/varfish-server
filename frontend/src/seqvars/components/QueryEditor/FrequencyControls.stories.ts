import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'

import presetsDetails from './presetsDetails.FrequencyControls.json'
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
      const model = ref(presetsDetails.seqvarsquerypresetsfrequency_set[3])
      return { model }
    },
    template:
      '<div style="background: white; padding: 16px"><FrequencyControls v-model="model"/></div>',
  }),
}
