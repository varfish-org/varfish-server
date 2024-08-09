<script setup lang="ts">
import { ItemData } from './lib'
import SelectItem from './SelectItem.vue'

const model = defineModel<ItemData[]>({
  required: true,
})
const { label, items } = defineProps<{ label: string; items: ItemData[] }>()
defineEmits<{ 'update:search': [string] }>()
</script>

<template>
  <div
    style="
      margin-top: 4px;
      border: 1px solid #0003;
      padding: 4px 8px;
      display: flex;
      flex-direction: column;
      gap: 4px;
    "
  >
    <div
      v-for="(item, index) in model"
      style="
        padding: 2px 6px;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        color: #595959;
        background: #f5f5f5;
      "
    >
      <SelectItem v-bind="item" />
      <button
        type="button"
        style="height: fit-content; padding: 4px"
        @click="model = model.toSpliced(index, 1)"
      >
        <i-mdi-close />
      </button>
    </div>
    <v-autocomplete
      :items="items.map((i) => ({ value: i.id, label: i.label }))"
      :model-value="model.map(({ id }) => id)"
      :label="label"
      density="compact"
      no-filter
      multiple
      hide-details
      hide-selected
      @update:search="$emit('update:search', $event)"
      @update:model-value="
        (ids: string[]) => {
          model = ids
            .map((id) => items.find((i) => i.id == id))
            .filter((i): i is ItemData => !!i)
        }
      "
    >
      <template #selection="" />
      <template #item="{ item, props }">
        <v-list-item v-bind="props" :title="''">
          <SelectItem
            :label="(props.title as any).label"
            :sublabel="item.value"
            style="padding: 4px 16px; cursor: pointer"
          />
        </v-list-item>
      </template>
    </v-autocomplete>
  </div>
</template>
