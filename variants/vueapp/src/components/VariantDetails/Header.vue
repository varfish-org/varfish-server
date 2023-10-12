<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import UiToggleMaxButton from '@varfish/components/UiToggleMaxButton.vue'

const props = defineProps<{
  case?: any
  smallVar?: any
}>()

const emit = defineEmits(['navigateBack'])

const router = useRouter()

const smallVariantLabel = computed(() => {
  const theVar = props.smallVar
  const start = theVar.start.toLocaleString('en-US')
  return `${theVar.chromosome}:${start}${theVar.reference}>${theVar.alternative}`
})
</script>

<template>
  <div class="row sodar-pr-content-title pb-1" tabindex="0">
    <h2 class="sodar-pr-content-title">
      Variant Details for
      <template v-if="props.smallVar">
        <code>
          {{ props.smallVar.payload.symbol }}
          ({{ props.smallVar.payload.hgvs_p ?? props.smallVar.payload.hgvs_c }})
        </code>

        <span class="ml-3">
          {{ smallVariantLabel }}
        </span>
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
