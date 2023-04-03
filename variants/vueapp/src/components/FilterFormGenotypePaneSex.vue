<script setup>
const props = defineProps({
  sex: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-venus
      id="sex-female-icon"
      v-if="props.sex === 2 || props.sex === 'female'"
    />
    <i-fa-solid-mars
      id="sex-male-icon"
      v-else-if="props.sex === 1 || props.sex === 'male'"
    />
    <i-fa-solid-question id="sex-unknown-icon" v-else />
  </span>
</template>
