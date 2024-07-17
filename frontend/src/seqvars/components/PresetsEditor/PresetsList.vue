<script setup lang="ts">
import { computed, ref } from 'vue'

/** Type for the items. */
interface Item {
  sodar_uuid: string
  label: string
  rank?: number
}

/** Props used in this component. */
const props = defineProps<{
  /** The items to display. */
  items: Item[]
}>()

/** The model is the currently selected item's UUID. */
const model = defineModel({
  type: String,
})

/** The items sorted by their rank, default rank is `0`. */
const sortedItems = computed(() => {
  return props.items.sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
})

/** Helper glue code between model and `VList` below. */
const selectedModel = computed<string[] | undefined>({
  get: () => {
    if (model.value) {
      return [model.value]
    } else {
      return undefined
    }
  },
  set: (value: string[] | undefined) => {
    if (value?.length) {
      model.value = value[0]
    } else {
      model.value = undefined
    }
  },
})
</script>

<template>
  <v-list
    selectable
    mandatory
    density="compact"
    v-model:selected="selectedModel"
  >
    <v-list-item
      v-for="item in sortedItems"
      :key="item.sodar_uuid"
      :title="item.label"
      :value="item.sodar_uuid"
    ></v-list-item>
  </v-list>
</template>
