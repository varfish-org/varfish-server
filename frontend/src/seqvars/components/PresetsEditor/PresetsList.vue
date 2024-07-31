<script setup lang="ts">
import { computed, ref } from 'vue'
import { PresetsListItem } from './lib'

/** Props used in this component. */
const props = withDefaults(
  defineProps<{
    /** The items to display. */
    items: PresetsListItem[]
    /** Whether the list of items is readonly. */
    readonly: boolean
  }>(),
  {
    readonly: false,
  },
)

/** Events defined by this component. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Event for creating a new item. */
  create: [partial: { label: string }]
  /** Event for deleting an item. */
  delete: [uuid: string]
}>()

/** The model is the currently selected item's UUID. */
const model = defineModel({
  type: String,
})

/** The name of the new presets in "add new" dialog; component state. */
const createDialogModel = ref<string>('')
/** Whether to display the "add new" dialog; component state. */
const createDialogShow = ref<boolean>(false)
/** The UUID of the entry to delete; component state. */
const deleteDialogModel = ref<string>('')
/** Whether to display the delete dialog; component state. */
const deleteDialogShow = ref<boolean>(false)

/** The items sorted by their rank, default rank is `0`. */
const sortedItems = computed(() => {
  return Array.from(props.items).sort((a, b) => (a.rank ?? 0) - (b.rank ?? 0))
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
    v-model:selected="selectedModel"
    selectable
    mandatory
    density="compact"
  >
    <v-list-item
      v-for="item in sortedItems"
      :key="item.sodar_uuid"
      :value="item.sodar_uuid"
      :title="item.label"
    >
      <template #append>
        <v-btn
          color="grey-lighten-1"
          icon="mdi-delete-outline"
          variant="text"
          :disabled="readonly"
          @click="
            () => {
              deleteDialogModel = item.sodar_uuid
              deleteDialogShow = true
            }
          "
        ></v-btn>
      </template>
    </v-list-item>
  </v-list>
  <v-btn
    class="text-center"
    variant="outlined"
    rounded="xs"
    block
    :disabled="props.readonly"
    @click="
      () => {
        createDialogModel = 'new entry'
        createDialogShow = true
      }
    "
  >
    <v-icon>mdi-plus-box-outline</v-icon>
    add new
  </v-btn>

  <!-- Dialog for creating a new item -->
  <v-dialog v-model="createDialogShow" max-width="600">
    <v-card>
      <v-card-title> Add New Presets </v-card-title>
      <v-card-text>
        <v-text-field
          v-model="createDialogModel"
          label="Name"
          hint="Enter a name for the new presets."
          persistent-hint
        ></v-text-field>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn rounded="xs" @click="createDialogShow = false"> Cancel </v-btn>
        <v-btn
          rounded="xs"
          color="success"
          @click="
            () => {
              emit('create', {
                label: createDialogModel,
              })
              createDialogShow = false
            }
          "
        >
          Add New
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Dialog for deleting an item -->
  <v-dialog v-model="deleteDialogShow" max-width="600">
    <v-card>
      <v-card-title> Reall Delete Presets? </v-card-title>
      <v-card-text>
        <v-alert type="error" icon="mdi-alert-circle-outline">
          Are you sure you want to delete this item?
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn rounded="xs" @click="deleteDialogShow = false"> Cancel </v-btn>
        <v-btn
          rounded="xs"
          color="error"
          @click="
            () => {
              emit('delete', deleteDialogModel)
              deleteDialogShow = false
            }
          "
        >
          Delete Presets
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
