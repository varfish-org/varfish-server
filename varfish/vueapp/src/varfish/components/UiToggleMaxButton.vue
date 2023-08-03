<script setup lang="ts">
import { useUiStore } from '@varfish/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <a
    class="btn btn-secondary"
    title="Toggle maximised UI"
    href="#"
    @click.prevent="uiStore.toggleMaximised()"
  >
    <i-mdi-arrow-expand-all v-if="!uiStore.maximized" />
    <i-mdi-arrow-collapse-all v-if="uiStore.maximized" />
  </a>
</template>
