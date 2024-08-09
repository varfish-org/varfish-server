<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { VBtn } from 'vuetify/lib/components/index.mjs'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  text?: string
  size?: string | number
}>()

const showTooltip = ref<boolean>(false)

const closeTooltip = () => {
  if (showTooltip.value) {
    showTooltip.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeTooltip)
})

onUnmounted(() => {
  document.removeEventListener('click', closeTooltip)
})
</script>

<template>
  <v-tooltip
    v-model="showTooltip"
    :text="text"
    :open-on-hover="false"
    max-width="300px"
  >
    <template #activator="{ props: innerProps }">
      <v-btn
        icon="mdi-information-box"
        variant="plain"
        density="compact"
        v-bind="innerProps"
        :size="size"
        @click.stop="showTooltip = !showTooltip"
      />
    </template>
  </v-tooltip>
</template>
