<script lang="ts" setup>
const { label, termId } = defineProps<{
  label: string | null
  termId: string
}>()
</script>

<template>
  <div>
    <div
      style="
        max-width: 200px;
        font-size: var(--font-size-sm);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      "
    >
      {{ label }}
    </div>
    <div style="font-size: var(--font-size-xs)">
      {{ termId }}
    </div>
  </div>
</template>
