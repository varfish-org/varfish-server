<script setup lang="ts">
import { computed, ref } from 'vue'

/** Type for the items. */
interface Item {
  sodar_uuid: string
  label: string
  rank?: number
}

/** Props used in this component. */
const props = withDefaults(
  defineProps<{
    /** The items to display. */
    items: Item[]
    /** Whether the list of items is readonly. */
    readonly: boolean
  }>(),
  {
    readonly: false,
  },
)

/** Events defined by this component. */
const emit = defineEmits<{
  /** Event for creating a new item. */
  create: [label: string, rank: number]
}>()

/** The model is the currently selected item's UUID. */
const model = defineModel({
  type: String,
})

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

/** Whether to display the "add new" dialog. */
const showCreateDialog = ref(false)
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
      :title="item.label"
      :value="item.sodar_uuid"
    ></v-list-item>
  </v-list>
  <v-btn
    class="text-center"
    variant="outlined"
    rounded="xs"
    block
    :disabled="props.readonly"
    @click="showCreateDialog = true"
  >
    <v-icon>mdi-plus-box-outline</v-icon>
    add new
  </v-btn>

  <v-dialog v-model="showCreateDialog" max-width="600">
    <v-card prepend-icon="mdi-account" title="User Profile">
      <v-card-text>
        <v-row dense>
          <v-col cols="12" md="4" sm="6">
            <v-text-field label="First name*" required></v-text-field>
          </v-col>

          <v-col cols="12" md="4" sm="6">
            <v-text-field
              hint="example of helper text only on focus"
              label="Middle name"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="4" sm="6">
            <v-text-field
              hint="example of persistent helper text"
              label="Last name*"
              persistent-hint
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="4" sm="6">
            <v-text-field label="Email*" required></v-text-field>
          </v-col>

          <v-col cols="12" md="4" sm="6">
            <v-text-field
              label="Password*"
              type="password"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="4" sm="6">
            <v-text-field
              label="Confirm Password*"
              type="password"
              required
            ></v-text-field>
          </v-col>

          <v-col cols="12" sm="6">
            <v-select
              :items="['0-17', '18-29', '30-54', '54+']"
              label="Age*"
              required
            ></v-select>
          </v-col>

          <v-col cols="12" sm="6">
            <v-autocomplete
              :items="[
                'Skiing',
                'Ice hockey',
                'Soccer',
                'Basketball',
                'Hockey',
                'Reading',
                'Writing',
                'Coding',
                'Basejump',
              ]"
              label="Interests"
              auto-select-first
              multiple
            ></v-autocomplete>
          </v-col>
        </v-row>

        <small class="text-caption text-medium-emphasis"
          >*indicates required field</small
        >
      </v-card-text>

      <v-divider></v-divider>

      <v-card-actions>
        <v-spacer></v-spacer>

        <v-btn
          text="Close"
          variant="plain"
          @click="showCreateDialog = false"
        ></v-btn>

        <v-btn
          color="primary"
          text="Save"
          variant="tonal"
          @click="showCreateDialog = false"
        ></v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
