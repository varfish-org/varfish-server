<script setup>
import { useVariantQueryStore } from '@variants/stores/variantQuery'

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
    @click="variantQueryStore.generateDownloadResults(props.fileType)"
    :disabled="
      variantQueryStore.getDownloadStatus(props.fileType) === 'running'
    "
    onclick="event.stopPropagation();"
  >
    <i-fa-solid-circle-notch
      class="spin"
      v-if="variantQueryStore.getDownloadStatus(props.fileType) === 'running'"
    />
    <i-fa-solid-cloud-download-alt v-else />
    Export as {{ props.fileType.toUpperCase() }}
  </button>
</template>
