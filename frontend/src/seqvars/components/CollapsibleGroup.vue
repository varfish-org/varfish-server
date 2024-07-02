<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ title: string }>()

const isOpen = ref(true)
</script>

<template>
  <details
    :open="isOpen"
    @toggle="
      (event: ToggleEvent) => {
        isOpen = (event.target as HTMLDetailsElement).open
      }
    "
  >
    <summary style="display: flex; align-items: center">
      <v-icon
        :icon="isOpen ? 'mdi-chevron-down' : 'mdi-chevron-right'"
        size="small"
        style="opacity: 0.4"
      ></v-icon>
      <div class="group-title">{{ props.title }}</div>
    </summary>
    <div style="display: flex">
      <button type="button" class="side-toggle" @click="isOpen = !isOpen">
        <div class="indicator"></div>
      </button>
      <slot />
    </div>
  </details>
</template>

<style scoped>
.side-toggle {
  padding: 0 9.5px;

  &:focus {
    outline: 0;
  }

  .indicator {
    width: 1px;
    height: 100%;
    background: rgba(0, 0, 0, 0.2);
  }

  &:hover > .indicator {
    background: #6c7bff;
  }
}
</style>
