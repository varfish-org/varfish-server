<script setup lang="ts">
/**
 * Container for the query results.
 */
import {
  CaseSerializerNg,
  SeqvarsQueryDetails,
  SeqvarsQueryExecution,
  SeqvarsResultSet,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { useSeqvarQueryRetrieveQueries } from '@/seqvars/queries/seqvarQuery'
import { useSeqvarQueryExecutionListQuery } from '@/seqvars/queries/seqvarQueryExecution'
import { useSeqvarResultSetListQuery } from '@/seqvars/queries/seqvarResultSet'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import QueryResultsTable from './QueryResultsTable.vue'

/** This component's props. */
const props = withDefaults(
  defineProps<{
    /** UUID of the case to edit queries for. */
    caseUuid: string
    /** UUID of the case analysis session to edit queries for. */
    sessionUuid: string
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
    /** The current case. */
    caseObj: CaseSerializerNg
  }>(),
  {
    hintsEnabled: false,
  },
)

/** Teleport target for pagination. */
const teleportPadRef = ref<HTMLElement | undefined>(undefined)

/** This component's events. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const emit = defineEmits<{
  /** Emitted to display a message in the VSnakbarQueue (e.g., on errors). */
  message: [message: SnackbarMessage]
}>()

/** The UUID of the currently selected query; component state. */
const selectedQueryUuid = defineModel<string | undefined>('selectedQueryUuid')
/** UUIDs of the queries for which the results have been opened. */
const openQueryUuids = defineModel<string[]>('openQueryUuids', {
  default: [],
})

/** Provide detailed seqvar queries for the `seqvarQueryListRes` via UUIDs in `sevarQueryListRes`. */
const seqvarQueryRetrieveRes = useSeqvarQueryRetrieveQueries({
  sessionUuid: props.sessionUuid,
  seqvarQueryUuids: openQueryUuids,
})

/** The currently selected query. */
const selectedQuery = computed<SeqvarsQueryDetails | undefined>(() => {
  return seqvarQueryRetrieveRes.value.data?.find(
    (q) => q.sodar_uuid === selectedQueryUuid.value,
  )
})
/** Index of the selected query. */
const selectedQueryIndex = computed<number>(() => {
  return (
    seqvarQueryRetrieveRes.value.data?.findIndex(
      (q) => q.sodar_uuid === selectedQueryUuid.value,
    ) ?? 0
  )
})

/** Provide access to the query executions of the currently selected query. */
const queryExecutionListRes = useSeqvarQueryExecutionListQuery({
  seqvarQueryUuid: selectedQueryUuid,
})
/**
 * Provide access to the latest query execution of the currently selected query.
 * The object is objtained from the list, so it does not feature the full query
 * settings.
 */
const latestQueryExecutionListItem = computed<
  SeqvarsQueryExecution | undefined
>(() => {
  return queryExecutionListRes.data?.value?.results?.[0]
})
/** Provide access to UUID of latest query execution. */
const latestQueryExecutionUuid = computed<string | undefined>(() => {
  return latestQueryExecutionListItem.value?.sodar_uuid
})

/** Provide access to list of seqvar result sets for the execution. */
const resultSetListRes = useSeqvarResultSetListQuery({
  queryExecutionUuid: latestQueryExecutionUuid,
})
/** Provide access to the latest seqvar query result set. */
const latestResultSet = computed<SeqvarsResultSet | undefined>(() => {
  return resultSetListRes.data?.value?.results?.[0]
})
</script>

<template>
  <v-row no-gutter>
    <v-col cols="12">
      <v-card class="ma-2">
        <v-card-item>
          <div class="d-flex flex-row justify-space-between align-center">
            <v-card-title v-if="!!selectedQuery">
              #{{ selectedQueryIndex + 1 }}
              {{ selectedQuery?.label }}
            </v-card-title>
            <v-card-title v-else> No selected query </v-card-title>

            <div ref="teleportPadRef" />
          </div>
        </v-card-item>

        <v-card-text>
          <div
            v-if="
              !selectedQueryUuid ||
              !latestQueryExecutionUuid ||
              !latestResultSet?.sodar_uuid
            "
            class="font-italic text-center text-body-1"
          >
            No query results yet.
          </div>
          <template v-else>
            <QueryResultsTable
              :teleport-to="teleportPadRef"
              :case-uuid="props.caseUuid"
              :session-uuid="props.sessionUuid"
              :query-uuid="selectedQueryUuid"
              :query-execution-uuid="latestQueryExecutionUuid"
              :result-set-uuid="latestResultSet?.sodar_uuid"
              :total-row-count="
                latestResultSet?.output_header?.statistics?.count_passed ?? 0
              "
              :case-obj="caseObj"
              :hints-enabled="hintsEnabled"
              @message="emit('message', $event)"
            />
          </template>
        </v-card-text>
      </v-card>
    </v-col>
  </v-row>
</template>
