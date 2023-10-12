<script setup>
const props = defineProps({
  affected: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-check
      id="affected-icon"
      class="text-danger"
      v-if="props.affected === 2 || props.affected === 'affected'"
    />
    <i-fa-solid-times
      id="unaffected-icon"
      class="text-dark"
      v-else-if="props.affected === 1 || props.affected === 'unaffected'"
    />
    <i-fa-solid-question id="unknown-icon" v-else />
  </span>
</template>
