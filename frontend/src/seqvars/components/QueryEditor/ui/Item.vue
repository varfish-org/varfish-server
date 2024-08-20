<script setup lang="ts">
import { Icon } from '@iconify/vue'

import ItemButton from './ItemButton.vue'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** Whether the item is selected. */
    selected?: boolean
    /** Whether the item has been modified. */
    modified?: boolean
  }>(),
  { selected: false, modified: false },
)

/** This component's events. */
const emit = defineEmits<{
  /** Revert modifications for this item. */
  revert: []
}>()
</script>

<template>
  <div class="root" :aria-selected="props.selected">
    <button type="button" class="item">
      <slot />
    </button>
    <div style="display: flex; align-items: center">
      <Icon
        v-if="props.modified"
        icon="mdi:alpha-m-box-outline"
        color="#DC9E00"
        :data-test-modified="props.modified && props.selected ? '' : undefined"
        title="There are modifications that you could revert."
      />
      <ItemButton
        v-if="props.modified"
        title="Revert modifications"
        @click="() => emit('revert')"
      >
        <v-icon icon="mdi-undo-variant" size="xs" />
      </ItemButton>
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<style scoped>
.root {
  display: flex;
  justify-content: space-between;

  &[aria-selected='true'] {
    background: rgb(var(--v-theme-selected-bg));
  }

  &:hover {
    background: rgb(var(--v-theme-hover-bg));
  }
}

button.item {
  padding: 2px;
  padding-bottom: 3px;
  width: 100%;
  box-sizing: border-box;

  text-align: start;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;

  &:not(:focus-visible) {
    outline: none;
  }
}
</style>
