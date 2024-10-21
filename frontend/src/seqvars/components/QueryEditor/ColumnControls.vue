<script setup lang="ts">
/**
 * This component allows to edit the columns of the query results table.
 *
 * The component is passed the current seqvar query, the component fetches
 * the corresponding latest execution and updates it via TanStack Query.
 */
import {
  SeqvarsQuery,
  SeqvarsQueryExecution,
} from '@varfish-org/varfish-api/lib'
import { computed, ref } from 'vue'

import { useSeqvarQueryUpdateMutation } from '@/seqvars/queries/seqvarQuery'

import { queryHpoAndOmimTerms } from '../utils'
import CollapsibleGroup from './ui/CollapsibleGroup.vue'
import Item from './ui/Item.vue'
import SelectBox from './ui/SelectBox.vue'
import { type ItemData } from './ui/lib'
import { useSeqvarQueryExecutionListQuery, useSeqvarQueryExecutionRetrieveQuery } from '@/seqvars/queries/seqvarQueryExecution'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The query that is to be edited. */
    modelValue?: SeqvarsQuery
    /** Whether to enable hints. */
    hintsEnabled?: boolean
  }>(),
  { hintsEnabled: false },
)

/** Returns selected query's UUID, guarding against the query being undefined. */
const selectedQueryUuid = computed<string | undefined>(() => {
  return props.modelValue?.sodar_uuid
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
const latestQueryExecutionListItem = computed<SeqvarsQueryExecution | undefined>(() => {
  return queryExecutionListRes.data?.value?.results?.[0]
})
/** Provide access to UUID of latest query execution. */
const latestQueryExecutionUuid = computed<string | undefined>(() => {
  return latestQueryExecutionListItem.value?.sodar_uuid
})
/** Full details of latest query execution item. */
const latestQueryExecutionRes = useSeqvarQueryExecutionRetrieveQuery({
  queryUuid: selectedQueryUuid,
  queryExecutionUuid: latestQueryExecutionUuid,
})


// /** Mapping from prioritzer algorithm to label. */
// const ALGOS = {
//   // 'exomiser.phenix': 'Phenix',  // deprecated
//   // 'exomiser.phive': 'Phive',  // deprecated
//   'exomiser.hiphive_human': 'HiPhive (human only)',
//   'exomiser.hiphive_humanmouse': 'HiPhive (human+mouse)',
//   'exomiser.hiphive_humanmousefishppi': 'HiPhive (human, mouse, fish, PPI)',
// }

// /** Simplified access to the currently selected algorithm item. */
// const selectedAlgo = computed<string | undefined>(() => {
//   const [[_, value]] = Object.entries(ALGOS).filter(
//     ([key, _]) =>
//       key === props.modelValue.settings.phenotypeprio?.phenotype_prio_algorithm,
//   )
//   return value
// })

// /** Whether or not the details are open. */
// const detailsOpen = ref<boolean>(false)

// /** Selected terms from HPO. */
// // TODO: migrate to proper common type
// const items = ref<ItemData[]>([])

// /** Handler for executing the search. */
// const onSearch = async (query: string) => {
//   items.value = (await queryHpoAndOmimTerms(query)).map((i) => ({
//     id: i.term_id,
//     label: i.label,
//     sublabel: i.term_id,
//   }))
// }

// /**
//  * Mutation for updating a seqvar query.
//  *
//  * This is done via TanStack Query which uses optimistic updates for quick
//  * reflection in the UI.
//  */
// const seqvarQueryUpdate = useSeqvarQueryUpdateMutation()

// /** Helper to apply a patch to the current `props.modelValue`. */
// const applyMutation = async (
//   phenotypeprio: SeqvarsQuerySettingsPhenotypePrioRequest,
// ) => {
//   const newData = {
//     ...props.modelValue,
//     settings: {
//       ...props.modelValue.settings,
//       phenotypeprio: {
//         ...props.modelValue.settings.phenotypeprio,
//         ...phenotypeprio,
//       },
//     },
//   }

//   // Apply update via TanStack query; will use optimistic updates for quick
//   // reflection in the UI.
//   await seqvarQueryUpdate.mutateAsync({
//     body: newData,
//     path: {
//       session: props.modelValue.session,
//       query: props.modelValue.sodar_uuid,
//     },
//   })
// }
</script>

<template>
  xxx
  <br>
  {{ latestQueryExecutionRes.data?.value?.querysettings }}
  <br>
  zzz
</template>
