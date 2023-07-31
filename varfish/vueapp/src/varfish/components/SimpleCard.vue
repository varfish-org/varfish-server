<script setup lang="ts">
/**
 * A simple Bootstrap card with a title and ID.
 */

const props = defineProps<{
  id: string
  title: string
}>()
</script>

<template>
  <div class="d-block pt-2 pb-2" :id="props.id">
    <div class="card mb-0 mt-0">
      <div class="p-2 card-header font-weight-bolder">
        {{ props.title }}
      </div>
      <div class="card-body p-0">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
