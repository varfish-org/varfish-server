<script setup lang="ts">
import {
  SeqvarsQueryDetails,
  SeqvarsQueryExecution,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { computed } from 'vue'

import { PedigreeObj } from '@/cases/stores/caseDetails'

import { matchesPredefinedQuery } from './groups'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import ItemButton from './ui/ItemButton.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Prests version details to use. */
    presetsDetails: SeqvarsQueryPresetsSetVersionDetails
    /** Pedigree object. */
    pedigree: PedigreeObj
    /** Map from UUID to query. */
    queries: Map<string, SeqvarsQueryDetails>
    /** Map from UUID to query execution. */
    queryExecutions: Map<string, SeqvarsQueryExecution>
    /** Whether to enable [i] hint buttons. */
    hintsEnabled?: boolean
  }>(),
  {
    // The [i] hint buttons are disabled by default.
    hintsEnabled: false,
  },
)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Remove the given query. */
  remove: [queryUuid: string]
  /** Show edit dialog for the query with UUID. */
  updateQuery: [queryUuid: string]
  /** Revert modifications. */
  revert: []
  /** Start query. */
  start: [queryUuid: string]
  /** Stop / cancel query execution by UUID. */
  stop: [queryExecutionUuid: string]
}>()

/** The selected query UUID as component model. */
const selectedQueryUuid = defineModel<string>('selectedQueryUuid')

/** The currently selected query. */
const selectedQuery = computed<SeqvarsQueryDetails | undefined>(() => {
  return props.queries.get(selectedQueryUuid.value ?? '')
})

/** Helper that provides the current query execution for query UUIDs. */
const queryUuidToQueryExecution = computed<Map<string, SeqvarsQueryExecution>>(
  () => {
    const result = new Map<string, SeqvarsQueryExecution>()
    for (const [_queryExecUuid, queryExec] of props.queryExecutions) {
      result.set(queryExec.query, queryExec)
    }
    return result
  },
)

/** Helper that provides a numeric index for query UUIDs. */
const queryUuidToIndex = computed<Map<string, number>>(() => {
  const result = new Map<string, number>()
  let index = 1
  for (const [uuid] of props.queries) {
    result.set(uuid, index)
    index += 1
  }
  return result
})

/** Helper that returns the query's execution UUID, if any. */
const queryExecution = (
  queryUuid: string,
): SeqvarsQueryExecution | undefined => {
  return queryUuidToQueryExecution.value.get(
    props.queries.get(queryUuid)?.sodar_uuid ?? '',
  )
}

/** Helper that returns the query's execution state, defaulting to `'initial'`. */
const queryExecutionState = (queryUuid: string) => {
  return queryExecution(queryUuid)?.state ?? 'initial'
}
</script>

<template>
  <CollapsibleGroup
    title="Queries / Results"
    :hints-enabled="hintsEnabled"
    hint="Here you can find the queries and their results."
  >
    <template
      v-if="!!selectedQueryUuid && queries.has(selectedQueryUuid)"
      #summary
    >
      <v-icon
        :icon="`mdi-numeric-${queryUuidToIndex.get(selectedQueryUuid) ?? 0}-box-outline`"
        size="small"
      />
      {{ selectedQuery?.label }}
    </template>
    <template #default>
      <div style="width: 100%; display: flex; flex-direction: column">
        <Item
          v-for="query in queries.values()"
          :key="query.sodar_uuid"
          :selected="query.sodar_uuid === selectedQueryUuid"
          :modified="
            !!query &&
            !matchesPredefinedQuery(
              pedigree,
              presetsDetails,
              presetsDetails.seqvarspredefinedquery_set.find(
                (pq) => pq.sodar_uuid === query.settings.predefinedquery,
              )!,
              query.settings,
            )
          "
          @click="selectedQueryUuid = query.sodar_uuid"
          @revert="$emit('revert')"
        >
          <template #default>
            <v-icon
              :icon="`mdi-numeric-${queryUuidToIndex.get(selectedQueryUuid ?? '') ?? 0}-box-outline`"
              size="small"
            />
            <span
              :title="`execution state: ${queryExecutionState(query.sodar_uuid)}`"
            >
              {{ query.label }}

              <v-chip
                variant="outlined"
                size="x-small"
                density="compact"
                class="px-1 py-2"
                :class="{
                  'bg-grey': ['initial', 'queued'].includes(
                    queryExecutionState(query.sodar_uuid),
                  ),
                  'bg-primary':
                    queryExecutionState(query.sodar_uuid) === 'running',
                  'bg-error': ['failed', 'canceled'].includes(
                    queryExecutionState(query.sodar_uuid),
                  ),
                  'bg-success':
                    queryExecutionState(query.sodar_uuid) === 'done',
                }"
              >
                {{ queryExecutionState(query.sodar_uuid) }}

                <template
                  v-if="queryExecutionState(query.sodar_uuid) === 'running'"
                >
                  <v-progress-circular
                    indeterminate
                    size="10"
                    width="2"
                    class="ml-1"
                  />
                </template>
                <template
                  v-if="
                    ['failed', 'canceled'].includes(
                      queryExecutionState(query.sodar_uuid),
                    )
                  "
                >
                  <v-icon icon="mdi-close" class="pl-1" size="10" />
                </template>
                <template
                  v-if="queryExecutionState(query.sodar_uuid) === 'done'"
                >
                  <v-icon icon="mdi-check" class="pl-1" size="10" />
                </template>
              </v-chip>
            </span>
          </template>
          <template #extra>
            <ItemButton
              v-if="
                ['initial', 'failed', 'canceled', 'done'].includes(
                  queryExecutionState(query.sodar_uuid),
                )
              "
              title="Start query"
              @click="$emit('start', query.sodar_uuid)"
            >
              <v-icon icon="mdi-play" size="18" />
            </ItemButton>
            <ItemButton
              v-if="
                ['queued', 'running'].includes(
                  queryExecutionState(query.sodar_uuid),
                )
              "
              title="Cancel query"
              @click="
                () => {
                  if (!!queryExecution(query.sodar_uuid)) {
                    $emit('stop', queryExecution(query.sodar_uuid)!.sodar_uuid)
                  }
                }
              "
            >
              <v-icon icon="mdi-stop" size="18" />
            </ItemButton>

            <ItemButton
              title="Update query title"
              :disabled="
                ['queued', 'running'].includes(
                  queryExecutionState(query.sodar_uuid),
                )
              "
              @click="$emit('updateQuery', query.sodar_uuid)"
            >
              <v-icon
                :disabled="
                  ['queued', 'running'].includes(
                    queryExecutionState(query.sodar_uuid),
                  )
                "
                icon="mdi-pencil"
                size="xs"
              />
            </ItemButton>

            <ItemButton
              title="Delete query"
              :disabled="
                ['queued', 'running'].includes(
                  queryExecutionState(query.sodar_uuid),
                )
              "
              @click="$emit('remove', query.sodar_uuid)"
            >
              <v-icon
                :disabled="
                  ['queued', 'running'].includes(
                    queryExecutionState(query.sodar_uuid),
                  )
                "
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
