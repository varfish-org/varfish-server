<script setup lang="ts">
/**
 * This component allows to edit the columns of the query results table.
 *
 * The component is passed the current seqvar query, the component fetches
 * the corresponding latest execution and updates it via TanStack Query.
 */
import { SeqvarsQueryDetails } from '@varfish-org/varfish-api/lib'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue: SeqvarsQueryDetails
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/**
 * Mutation for updating a seqvar query.
 *
 * This is done via TanStack Query which uses optimistic updates for quick
 * reflection in the UI.
 */
const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

/** Helper to apply a patch to the current `props.modelValue`. */
const applyMutation = async (data: { name: string; visible: boolean }) => {
  const newData = {
    ...props.modelValue,
    columnsconfig: {
      ...props.modelValue.columnsconfig,
      column_settings: (
        props.modelValue.columnsconfig.column_settings || []
      ).map((column) => {
        const res = {
          ...column,
          visible: data.name === column.name ? data.visible : column.visible,
        }
        return res
      }),
    },
  }

  // Apply update via TanStack query; will use optimistic updates for quick
  // reflection in the UI.
  await seqvarQueryUpdate.mutateAsync({
    body: newData,
    path: {
      session: props.modelValue.session,
      query: props.modelValue.sodar_uuid,
    },
  })
}
</script>

<template>
  <v-list density="compact">
    <v-list-item
      density="compact"
      v-for="column in props.modelValue.columnsconfig?.column_settings ?? []"
      :key="column.name"
      :title="column.label"
      :active="column.visible"
      @click="
        applyMutation({
          name: column.name,
          visible: !column.visible,
        })
      "
    >
      <template v-slot:prepend>
        <v-list-item-action start>
          <v-checkbox-btn
            density="compact"
            :model-value="column.visible"
            @update:modelValue="
              applyMutation({
                name: column.name,
                visible: !column.visible,
              })
            "
          ></v-checkbox-btn>
        </v-list-item-action>
      </template>
    </v-list-item>
  </v-list>
</template>
