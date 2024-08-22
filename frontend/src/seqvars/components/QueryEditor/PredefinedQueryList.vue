<script setup lang="ts">
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryDetails,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

import { PedigreeObj } from '@/cases/stores/caseDetails'

import { matchesPredefinedQuery } from './groups'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import ItemButton from './ui/ItemButton.vue'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** The presets version to use. */
    presets: SeqvarsQueryPresetsSetVersionDetails
    /** The pedigree. */
    pedigree: PedigreeObj
    /** The query that is being modified, if any selected. */
    query?: SeqvarsQueryDetails
    /** Whether hints are enabled. */
    hintsEnabled?: boolean
    /** The currently selected query UUID. */
    selectedId?: string
  }>(),
  { hintsEnabled: false },
)

/** Currently selected predefined query, if any.*/
const selectedPredefinedQuery = computed<SeqvarsPredefinedQuery | undefined>(
  () => {
    return props.presets.seqvarspredefinedquery_set.find(
      (pq) => pq.sodar_uuid === props.selectedId,
    )
  },
)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Create a query based on the predefined query. */
  addQuery: [preset: SeqvarsPredefinedQuery]
  /** Revert modifications. */
  revert: []
}>()
</script>

<template>
  <CollapsibleGroup
    title="Predefined Queries"
    :hints-enabled="hintsEnabled"
    hint="Create a new query using the buttons on the right. Selected predefined query settings for custom query."
  >
    <template #summary>
      <Item
        :modified="
          !!query &&
          !!selectedPredefinedQuery &&
          !matchesPredefinedQuery(
            pedigree,
            presets,
            selectedPredefinedQuery,
            query.settings,
          )
        "
        @revert="$emit('revert')"
      >
        {{
          presets.seqvarspredefinedquery_set.find(
            (pq) => pq.sodar_uuid === selectedId,
          )?.label
        }}
      </Item>
    </template>
    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column">
        <Item
          v-for="pq in presets.seqvarspredefinedquery_set"
          :key="pq.sodar_uuid"
          :selected="pq.sodar_uuid === selectedId"
          :modified="
            !!query &&
            pq.sodar_uuid === selectedId &&
            !matchesPredefinedQuery(pedigree, presets, pq, query.settings)
          "
          @revert="$emit('revert')"
        >
          <template #default>{{ pq.label }}</template>
          <template #extra>
            <ItemButton
              :title="`Create query based on ${pq.label}`"
              @click="$emit('addQuery', pq)"
            >
              <v-icon icon="mdi-filter-variant-plus" size="xs" />
            </ItemButton>
          </template>
        </Item>
      </div>
    </template>
  </CollapsibleGroup>
</template>
