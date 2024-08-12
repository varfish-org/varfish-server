<script setup lang="ts">
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'

import { Query } from '@/seqvars/types'

import { matchesPredefinedQuery } from './groups'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import ItemButton from './ui/ItemButton.vue'
import { PedigreeObj } from '@/cases/stores/caseDetails'
import { computed } from 'vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The presets version to use. */
    presets: SeqvarsQueryPresetsSetVersionDetails
    /** The pedigree. */
    pedigree: PedigreeObj
    /** The query that is being modified. */
    query: Query | null
    /** Whether hints are enabled. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Currently selected predefined query UUID, if any. */
const selectedId = defineModel<string | undefined>('selectedId', {
  required: true,
})

/** Currently selected predefined query, if any.*/
const selectedPredefinedQuery = computed<SeqvarsPredefinedQuery | undefined>(
  () => {
    return props.presets.seqvarspredefinedquery_set.find(
      (pq) => pq.sodar_uuid === selectedId.value,
    )
  },
)

/** This component's events. */
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
    :summary="
      presets.seqvarspredefinedquery_set.find(
        (pq) => pq.sodar_uuid === selectedId,
      )?.label
    "
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
            query,
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
            !matchesPredefinedQuery(pedigree, presets, pq, query)
          "
          @click="selectedId = pq.sodar_uuid"
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
