<script setup>
const props = defineProps({
  affected: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-check
      class="text-danger"
      v-if="props.affected === 2 || props.affected === 'affected'"
    />
    <i-fa-solid-times
      class="text-dark"
      v-else-if="props.affected === 1 || props.affected === 'unaffected'"
    />
    <i-fa-solid-question v-else />
  </span>
</template>
