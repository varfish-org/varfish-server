<script setup>
const props = defineProps({
  sex: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-venus
      v-if="props.sex === 2 || props.sex === 'female'"
      id="sex-female-icon"
    />
    <i-fa-solid-mars
      v-else-if="props.sex === 1 || props.sex === 'male'"
      id="sex-male-icon"
    />
    <i-fa-solid-question v-else id="sex-unknown-icon" />
  </span>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
