<script setup lang="ts">
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'

import { matchesPredefinedQuery } from './groups'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import ItemButton from './ui/ItemButton.vue'
import { PedigreeObj } from '@/cases/stores/caseDetails'

const selectedIndex = defineModel<number | null>('selectedIndex', {
  required: true,
})
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    presetsDetails: SeqvarsQueryPresetsSetVersionDetails
    pedigree: PedigreeObj
    queries: Query[]
    hintsEnabled?: boolean
  }>(),
  {
    hintsEnabled: false,
  },
)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Remove the given query. */
  remove: [index: number]
  /** Show edit dialog for the query with index. */
  updateQuery: [index: number]
  /** Revert modifications. */
  revert: []
}>()
</script>

<template>
  <CollapsibleGroup
    title="Queries / Results"
    :hints-enabled="hintsEnabled"
    hint="Here you can find the queries and their results."
  >
    <template
      #summary
      v-if="selectedIndex !== null && selectedIndex < queries.length"
    >
      <v-icon
        :icon="`mdi-numeric-${selectedIndex + 1}-box-outline`"
        size="small"
      />
      {{ queries[selectedIndex]?.label }}
    </template>
    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column">
        <Item
          v-for="(query, index) in queries"
          :key="index"
          :selected="index === selectedIndex"
          :modified="
            !!query &&
            !matchesPredefinedQuery(
              pedigree,
              presetsDetails,
              presetsDetails.seqvarspredefinedquery_set.find(
                (pq) => pq.sodar_uuid === query.predefinedquery,
              )!,
              query,
            )
          "
          @click="selectedIndex = index"
          @revert="$emit('revert')"
        >
          <template #default>
            <v-icon
              :icon="`mdi-numeric-${index + 1}-box-outline`"
              size="small"
            />
            {{ queries[index]?.label }}
          </template>
          <template #extra>
            <ItemButton
              title="Update query title"
              @click="$emit('updateQuery', index)"
            >
              <v-icon icon="mdi-pencil" size="xs" />
            </ItemButton>
            <ItemButton title="Delete query" @click="$emit('remove', index)">
              <v-icon icon="mdi-delete" size="xs" />
            </ItemButton>
          </template>
        </Item>
      </div>
    </template>
  </CollapsibleGroup>
</template>
