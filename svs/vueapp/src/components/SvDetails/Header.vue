<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { formatLargeInt } from '@varfish/helpers'
import UiToggleMaxButton from '@varfish/components/UiToggleMaxButton/UiToggleMaxButton.vue'

const props = defineProps<{
  case?: any
  svRecord?: any
}>()

const router = useRouter()

const svLabel = computed(() => {
  if (props.svRecord) {
    const start = formatLargeInt(props.svRecord.start)
    const end = formatLargeInt(props.svRecord.end)
    const result = `${props.svRecord.chromosome}:${start}-${end}:${props.svRecord.sv_type}`
    if (!result.startsWith('chr')) {
      return `chr${result}`
    } else {
      return result
    }
  }
})
</script>

<template>
  <div class="row sodar-pr-content-title pb-1" tabindex="0">
    <h2 class="sodar-pr-content-title">
      SV Details for
      <template v-if="props.svRecord">
        <code>{{ svLabel }}</code>
      </template>
      <span v-else>
        ...
        <i-fa-solid-circle-notch class="spin" />
      </span>
    </h2>

    <div class="ml-auto btn-group">
      <UiToggleMaxButton />
    </div>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
