<script setup lang="ts">
import {
  SeqvarsQueryExecution,
  SeqvarsQueryExecutionStateEnum,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { zip } from '@/variants/components/AcmgRatingCard/lib'

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
    queryExecutions: SeqvarsQueryExecution[]
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
  /** Start query. */
  start: [index: number]
  /** Stop / cancel query. */
  stop: [index: number]
}>()
</script>

<template>
  <CollapsibleGroup
    title="Queries / Results"
    :hints-enabled="hintsEnabled"
    hint="Here you can find the queries and their results."
  >
    <template
      v-if="selectedIndex !== null && selectedIndex < queries.length"
      #summary
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
          v-for="([query, queryExec], index) in zip(queries, queryExecutions)"
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
            <span :title="`execution state: ${queryExec.state}`">
              {{ queries[index]?.label }}

              <v-chip
                variant="outlined"
                size="x-small"
                density="compact"
                class="px-1 py-2"
                :class="{
                  'bg-grey': ['initial', 'queued'].includes(queryExec.state),
                  'bg-primary': queryExec.state === 'running',
                  'bg-error': ['failed', 'canceled'].includes(queryExec.state),
                  'bg-success': queryExec.state === 'done',
                }"
              >
                {{ queryExec.state }}

                <template v-if="queryExec.state === 'running'">
                  <v-progress-circular
                    indeterminate
                    size="10"
                    width="2"
                    class="ml-1"
                  />
                </template>
                <template
                  v-if="['failed', 'canceled'].includes(queryExec.state)"
                >
                  <v-icon icon="mdi-close" class="pl-1" size="10" />
                </template>
                <template v-if="queryExec.state === 'done'">
                  <v-icon icon="mdi-check" class="pl-1" size="10" />
                </template>
              </v-chip>
            </span>
          </template>
          <template #extra>
            <ItemButton
              title="Start query"
              @click="$emit('start', index)"
              v-if="
                ['initial', 'failed', 'canceled', 'done'].includes(
                  queryExec.state,
                )
              "
            >
              <v-icon icon="mdi-play" size="18" />
            </ItemButton>
            <ItemButton
              title="Cancel query"
              @click="$emit('stop', index)"
              v-if="['queued', 'running'].includes(queryExec.state)"
            >
              <v-icon icon="mdi-stop" size="18" />
            </ItemButton>

            <ItemButton
              title="Update query title"
              :disabled="['queued', 'running'].includes(queryExec.state)"
              @click="$emit('updateQuery', index)"
            >
              <v-icon
                :disabled="['queued', 'running'].includes(queryExec.state)"
                icon="mdi-pencil"
                size="xs"
              />
            </ItemButton>

            <ItemButton
              title="Delete query"
              :disabled="['queued', 'running'].includes(queryExec.state)"
              @click="$emit('remove', index)"
            >
              <v-icon
                :disabled="['queued', 'running'].includes(queryExec.state)"
                icon="mdi-delete"
                size="xs"
              />
            </ItemButton>
          </template>
        </Item>
      </div>
    </template>
  </CollapsibleGroup>
</template>
