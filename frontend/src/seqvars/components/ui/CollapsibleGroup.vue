<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{ title: string; summary?: string }>()

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
    <summary style="display: flex">
      <v-icon
        :icon="isOpen ? 'mdi-chevron-down' : 'mdi-chevron-right'"
        size="small"
        style="opacity: 0.4"
      ></v-icon>
      <div style="display: flex; flex-direction: column">
        <div class="group-title" style="margin-top: 1px">
          {{ props.title }}
        </div>
        <div v-if="!isOpen">{{ summary }}</div>
      </div>
    </summary>
    <div style="display: flex">
      <button type="button" class="side-toggle" @click="isOpen = !isOpen">
        <div class="indicator"></div>
      </button>
      <div style="width: 100%">
        <slot />
      </div>
    </div>
  </details>
</template>

<style scoped>
summary {
  list-style: none;
}
.side-toggle {
  padding: 0 9.5px;

  &:focus {
    outline: 0;
  }

  .indicator {
    width: 1px;
    height: 100%;
    background: #0003;
  }

  &:hover > .indicator {
    background: #6c7bff;
  }
}
</style>
