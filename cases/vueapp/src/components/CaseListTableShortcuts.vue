<script setup>
const props = defineProps({
  params: Object,
})
</script>

<template>
  <div class="btn-group">
    <button
      title="Legacy filter small variants"
      type="button"
      class="btn btn-sm btn-primary"
      style="font-size: 80%"
      :disabled="!params.data.num_small_vars"
    >
      <i-mdi-filter />
    </button>
    <button
      title="Next-gen small variants (beta)"
      type="button"
      class="btn btn-sm btn-primary"
      style="font-size: 80%"
      :disabled="!params.data.num_small_vars"
    >
      <i-mdi-beta />
    </button>
    <button
      title="Filter SVs"
      type="button"
      class="btn btn-sm btn-primary pl-2"
      style="font-size: 80%"
      :disabled="!params.data.num_svs"
    >
      <i-mdi-filter-variant />
    </button>
  </div>
</template>

<style scoped>
.icon-inactive {
  opacity: 20%;
}
</style>
