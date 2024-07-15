import type { Meta, StoryObj } from '@storybook/vue3'
import { ref } from 'vue'

import fixture from '../../views/fixture.SeqvarsFiltration.json'
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
      const model = ref(fixture.seqvarsquerypresetsfrequency_set[3])
      return { model }
    },
    template:
      '<div style="background: white; padding: 16px"><FrequencyControls v-model="model"/></div>',
  }),
}
