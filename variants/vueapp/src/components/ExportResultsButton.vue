<script setup>
import { useFilterQueryStore } from '@variants/stores/filterQuery'

const filterQueryStore = useFilterQueryStore()

const props = defineProps({
  fileType: String,
})
</script>

<template>
  <a
    v-if="filterQueryStore.getDownloadStatus(props.fileType) === 'done'"
    :href="filterQueryStore.serveDownloadResults(props.fileType)"
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
      filterQueryStore.getDownloadStatus(props.fileType) === 'failed'
        ? 'text-danger'
        : ''
    "
    @click="filterQueryStore.generateDownloadResults(props.fileType)"
    :disabled="filterQueryStore.getDownloadStatus(props.fileType) === 'running'"
    onclick="event.stopPropagation();"
  >
    <i-fa-solid-circle-notch
      class="spin"
      v-if="filterQueryStore.getDownloadStatus(props.fileType) === 'running'"
    />
    <i-fa-solid-cloud-download-alt v-else />
    Export as {{ props.fileType.toUpperCase() }}
  </button>
</template>
