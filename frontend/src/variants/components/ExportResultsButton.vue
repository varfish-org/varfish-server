<script setup>
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const variantQueryStore = useVariantQueryStore()

const props = defineProps({
  fileType: String,
})
</script>

<template>
  <a
    v-if="variantQueryStore.getDownloadStatus(props.fileType) === 'done'"
    :href="variantQueryStore.serveDownloadResults(props.fileType)"
    class="dropdown-item text-success"
    download
  >
    <i-fa-solid-cloud-download-alt />
    Download {{ props.fileType.toUpperCase() }}
  </a>
  <button
    v-else
    type="button"
    class="dropdown-item"
    :class="
      variantQueryStore.getDownloadStatus(props.fileType) === 'failed'
        ? 'text-danger'
        : ''
    "
    :disabled="
      variantQueryStore.getDownloadStatus(props.fileType) === 'running'
    "
    onclick="event.stopPropagation();"
    @click="variantQueryStore.generateDownloadResults(props.fileType)"
  >
    <i-fa-solid-circle-notch
      v-if="variantQueryStore.getDownloadStatus(props.fileType) === 'running'"
      class="spin"
    />
    <i-fa-solid-cloud-download-alt v-else />
    Export as {{ props.fileType.toUpperCase() }}
  </button>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
