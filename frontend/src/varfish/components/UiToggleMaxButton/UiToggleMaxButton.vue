<script setup lang="ts">
import { useUiStore } from '@/varfish/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <v-btn
    title="Toggle maximised UI"
    rounded="xs"
    href="#"
    @click.prevent="uiStore.toggleMaximised()"
  >
    <v-icon
      :icon="
        uiStore.maximized ? 'mdi-arrow-collapse-all' : 'mdi-arrow-expand-all'
      "
    />
  </v-btn>
</template>
