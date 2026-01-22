<script setup>
const props = defineProps({
  flagState: String,
})
</script>

<template>
  <span>
    <i-fa-solid-exclamation-circle
      v-if="props.flagState === 'positive'"
      class="text-error"
    />
    <i-fa-solid-question
      v-if="props.flagState === 'uncertain'"
      class="text-warning"
    />
    <i-fa-solid-minus-circle
      v-if="props.flagState === 'negative'"
      class="text-success"
    />
    <i-fa-solid-times
      v-if="props.flagState === 'empty'"
      class="text-secondary"
    />
  </span>
</template>
