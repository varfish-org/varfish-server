<script setup lang="ts">
import { useStorage } from '@vueuse/core'
import { watch } from 'vue'

import HintButton from './HintButton.vue'

const props = withDefaults(
  defineProps<{
    /** Whether the group is open. */
    modelValue: boolean
    /** The title to display. */
    title: string
    /** Whether to enable the `[i]` icon with `hint`. */
    hintsEnabled?: boolean
    /** Any hint to display in the `[i]` icon if `hintsEnabled`. */
    hint?: string
    /**
     * An optional string to display as the summary; not displayed if the `summary`
     * slot is used.
     */
    summary?: string
    /** Whether to display "modified" icon if non-default selection is made. */
    modified?: boolean
    /** Name for storing the result, if any. */
    storageName?: string
    /** Type of the storage. */
    storageType?: 'local' | 'session'
  }>(),
  {
    modelValue: true,
    hintsEnabled: false,
    modified: false,
    storageName: 'default',
    storageType: 'local',
  },
)

/** This component's events. */
const emit = defineEmits<{
  /** Revert modifications for this item. */
  revert: []
  /** Update the state. */
  'update:modelValue': [newValue: boolean]
}>()

interface State {
  isOpen: boolean
}

const state = useStorage(
  `collapsible-group-${props.storageName}`,
  { isOpen: true } as State,
  props.storageType === 'local' ? localStorage : sessionStorage,
  { mergeDefaults: true },
)

const updateValueAndEmit = (newValue: boolean) => {
  if (newValue !== state.value.isOpen) {
    state.value.isOpen = newValue
    emit('update:modelValue', newValue)
  }
}

watch(
  () => props.modelValue,
  (newValue) => updateValueAndEmit(newValue),
)
</script>

<template>
  <details
    :open="state.isOpen"
    @toggle="
      (event: ToggleEvent) => {
        if (!!state) {
          state.isOpen = (event.target as HTMLDetailsElement).open
        }
      }
    "
  >
    <summary style="display: flex">
      <v-icon
        :icon="state.isOpen ? 'mdi-chevron-down' : 'mdi-chevron-right'"
        size="small"
        style="opacity: 0.4"
      ></v-icon>
      <div style="display: flex; flex-direction: column; width: 100%">
        <div>
          <slot name="title">
            <div class="text-caption d-flex justify-space-between">
              <div class="font-weight-bold text-uppercase">
                {{ title }}
              </div>
              <div>
                <template v-if="modified">
                  <v-icon
                    icon="mdi-alpha-m-box-outline"
                    color="#DC9E00"
                    title="The selected preset is not the default."
                  />
                  <v-btn
                    icon="mdi-undo-variant"
                    title="Select default preset."
                    size="xs"
                    variant="text"
                    class="rounded-0"
                    @click="() => emit('revert')"
                  />
                </template>
                <span v-if="hintsEnabled && hint" class="ml-auto">
                  <HintButton :text="hint" size="xs" />
                </span>
              </div>
            </div>
          </slot>
        </div>
        <div v-if="!state.isOpen">
          <slot name="summary">
            {{ props.summary }}
          </slot>
        </div>
      </div>
    </summary>
    <div style="display: flex" :aria-label="props.title">
      <button
        type="button"
        class="side-toggle"
        @click="updateValueAndEmit(!state.isOpen)"
      >
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
