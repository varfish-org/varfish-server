<script setup>
const props = defineProps({
  affected: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-check
      v-if="props.affected === 2 || props.affected === 'affected'"
      id="affected-icon"
      class="text-danger"
    />
    <i-fa-solid-times
      v-else-if="props.affected === 1 || props.affected === 'unaffected'"
      id="unaffected-icon"
      class="text-dark"
    />
    <i-fa-solid-question v-else id="unknown-icon" />
  </span>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
