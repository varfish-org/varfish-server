<script setup lang="ts">
/**
 * A simple Bootstrap card with a title and ID.
 */

const props = defineProps<{
  id: string
  title?: string
  class?: string
}>()
</script>

<template>
  <div class="d-block pt-2 pb-2" :class="props.class" :id="props.id">
    <div class="card mb-0 mt-0">
      <div class="p-2 card-header font-weight-bolder">
        <slot name="header">
          {{ props.title }}
        </slot>
      </div>
      <div class="card-body p-0">
        <slot></slot>
      </div>
    </div>
  </div>
</template>
