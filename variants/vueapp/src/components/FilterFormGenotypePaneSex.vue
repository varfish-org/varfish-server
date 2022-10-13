<script setup>
const props = defineProps({
  sex: Number,
})
</script>

<template>
  <span>
    <i-fa-solid-venus v-if="props.sex === 2 || props.sex === 'female'" />
    <i-fa-solid-mars v-else-if="props.sex === 1 || props.sex === 'male'" />
    <i-fa-solid-question v-else />
  </span>
</template>
