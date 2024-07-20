<script setup lang="ts">
import ItemButton from './ItemButton.vue'
import ModifiedIcon from './ModifiedIcon.vue'

const props = withDefaults(
  defineProps<{ selected?: boolean; modified?: boolean }>(),
  { selected: false, modified: false },
)
const emit = defineEmits<{ revert: [] }>()
</script>

<template>
  <div class="root" :aria-selected="props.selected">
    <button type="button" class="item">
      <slot />
    </button>
    <div style="display: flex; align-items: center">
      <ModifiedIcon v-if="props.selected && props.modified" />
      <ItemButton
        v-if="props.selected && props.modified"
        @click="() => emit('revert')"
        ><i-fluent-arrow-undo-20-regular style="font-size: 0.9em"
      /></ItemButton>
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
