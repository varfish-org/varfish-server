<script setup lang="ts">
import { useIsFetching } from '@tanstack/vue-query'
import { VueQueryDevtools } from '@tanstack/vue-query-devtools'
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'
import { computed, onMounted, ref, watch } from 'vue'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import { useCaseAnalysisSessionListQuery } from '@/cases/queries/caseAnalysisSession'
import { useCaseRetrieveQuery } from '@/cases/queries/cases'
import { useProjectStore } from '@/cases/stores/project'
import QueryEditor from '@/seqvars/components/QueryEditor/QueryEditor.vue'
import HintButton from '@/seqvars/components/QueryEditor/ui/HintButton.vue'
import QueryEditorDrawer from '@/seqvars/components/QueryEditorDrawer/QueryEditorDrawer.vue'
import QueryResults from '@/seqvars/components/QueryResults/QueryResults.vue'
import {
  useSeqvarQueryListInfiniteQuery,
  useSeqvarQueryRetrieveQueries,
} from '@/seqvars/queries/seqvarQuery'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** The project UUID. */
  projectUuid: string
  /** The case UUID. */
  caseUuid?: string
}>()

/** Whether to hide the navigation bar; component state. */
const navbarShown = ref<boolean>(true)
/** Whether to enable hints. */
const hintsEnabled = ref<boolean>(true)
/** Whether to hide the variant details pane; component state. */
const detailsShown = ref<boolean>(false)
// Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])
/** Wraps `props.caseUuid` into a `ComputedRef` for use with queries. */
const caseUuid = computed(() => props.caseUuid)

const projectStore = useProjectStore()
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** (Re-)initialize the stores. */
const initializeStores = async () => {
  await Promise.all([
    projectStore.initialize(props.projectUuid),
    seqvarsPresetsStore.initialize(props.projectUuid),
  ])
}

/** Retrieve Case through TanStack Query. */
const caseRetrieveRes = useCaseRetrieveQuery({ caseUuid })
/** Retrieve CaseAnalysisSession through TanStack Query. */
const sessionRetrieveRes = useCaseAnalysisSessionListQuery({ caseUuid })
/** Wraps the session UUID into a `ComputedRef` for easier access. */
const sessionUuid = computed<string | undefined>(
  () => sessionRetrieveRes.data!.value?.results?.[0]?.sodar_uuid,
)
/** List all queries for the given case in the given session. */
const seqvarQueryListRes = useSeqvarQueryListInfiniteQuery({ sessionUuid })
/** Provide the UUIDs from `seqvarsQueryListRes` as an `ComputedRef<string[]>` for use with queries. */
const seqvarQueryUuids = computed<string[] | undefined>(() => {
  const res = seqvarQueryListRes.data?.value?.pages?.reduce(
    (acc, page) => acc.concat(page.results?.map((q) => q.sodar_uuid) ?? []),
    [] as string[],
  )
  if ((res?.length ?? 0) > 0) {
    return res
  } else {
    return undefined
  }
})
/** Provide detailed seqvar queries for the `seqvarQueryListRes` via UUIDs in `sevarQueryListRes`. */
const seqvarQueriesRetrieveRes = useSeqvarQueryRetrieveQueries({
  sessionUuid,
  seqvarQueryUuids,
})

/** The currently selected preset set for the case. */
const selectedPresetSetVersionDetails = computed<
  SeqvarsQueryPresetsSetVersionDetails | undefined
>(() => {
  return Array.from(seqvarsPresetsStore.presetSetVersions.values())[0]
})

/** The UUID of the currently selected query in the query results view. */
const selectedQueryUuidRef = ref<string | undefined>(undefined)
/** UUIDs of the queries for which the results have been opened. */
const openQueryUuids = ref<string[]>([])
/** Manage `selectedQueryUuidRef` and update `openQueryUuids` if necessary. */
const selectedQueryUuid = computed<string | undefined>({
  get: () => selectedQueryUuidRef.value,
  set: (value) => {
    selectedQueryUuidRef.value = value
    if (value && !openQueryUuids.value.includes(value)) {
      openQueryUuids.value.push(value)
    }
  },
})

/** Event handler for queueing message in VSnackbarQueue. */
const queueMessage = (message: SnackbarMessage) => {
  messages.value.push(message)
}

// Initialize case list store on mount.
onMounted(async () => {
  await initializeStores()
})
// Re-initialize case list store when the project changes.
watch(
  () => [
    props.projectUuid,
    props.caseUuid,
    selectedPresetSetVersionDetails.value,
  ],
  async () => {
    await initializeStores()
  },
)

// Hook into TanStack Query.
const isQueryFetching = useIsFetching()
</script>

<template>
  <div>
    <v-app id="seqvars-query">
      <TheAppBar
        v-model:show-left-panel="navbarShown"
        v-model:show-right-panel="detailsShown"
        :show-left-panel-button="true"
        :show-right-panel-button="true"
        :title="caseRetrieveRes.data?.value?.name"
        :loading="!selectedPresetSetVersionDetails || isQueryFetching > 0"
      />

      <QueryEditorDrawer :drawer-shown="navbarShown">
        <v-skeleton-loader
          v-if="!selectedPresetSetVersionDetails || !caseUuid || !sessionUuid"
          type="list-item, list-item, list-item"
          class="bg-background"
        ></v-skeleton-loader>
        <template v-else>
          <div :class="{ 'd-flex flex-column h-100': navbarShown }">
            <div :class="{ 'overflow-y-auto flex-grow-1': navbarShown }">
              <v-list density="compact" class="pt-0 pb-0">
                <v-list-item
                  prepend-icon="mdi-arrow-left"
                  :to="{
                    name: 'case-detail-overview',
                    params: { project: projectUuid, case: caseUuid },
                  }"
                >
                  <template v-if="navbarShown"> Back to Case </template>
                </v-list-item>
                <v-divider class="mt-1 mb-1"></v-divider>
              </v-list>

              <QueryEditor
                v-show="navbarShown"
                v-model:selected-query-uuid="selectedQueryUuid"
                v-model:open-query-uuids="openQueryUuids"
                :case-uuid="caseUuid"
                :session-uuid="sessionUuid"
                :collapsed="!navbarShown"
                :presets-details="selectedPresetSetVersionDetails"
                :hints-enabled="hintsEnabled"
                teleport-to-when-collapsed="#seqvar-queries-teleport-pad"
                :teleported-queries-labels="navbarShown"
                @message="queueMessage"
              />
            </div>
            <div v-if="navbarShown" class="mt-auto">
              <v-divider class="mt-1 mb-1"></v-divider>
              <v-list-item density="compact">
                <v-switch
                  v-model="hintsEnabled"
                  class="ml-2"
                  density="compact"
                  :label="`Hints ${hintsEnabled ? 'hidden' : 'shown'}`"
                  hide-details
                ></v-switch>
                <template #append>
                  <HintButton
                    v-if="hintsEnabled"
                    text="When hints are enabled, you can access them through the [i] icons."
                  />
                </template>
              </v-list-item>
            </div>
          </div>
          <div v-show="!navbarShown">
            <div v-show="seqvarQueriesRetrieveRes.data.length > 0">
              <v-list density="compact" class="pt-0 pb-0">
                <div id="seqvar-queries-teleport-pad">
                  <!-- This is where QueryEditor renders its queries when hidden. -->
                </div>
              </v-list>
              <v-divider class="mt-1 mb-1"></v-divider>
            </div>

            <v-list density="compact">
              <v-list-item
                :prepend-icon="
                  hintsEnabled ? 'mdi-lightbulb-on' : 'mdi-lightbulb-off'
                "
                @click="hintsEnabled = !hintsEnabled"
              />
            </v-list>
          </div>
        </template>
      </QueryEditorDrawer>
      <v-main>
        <v-skeleton-loader
          v-if="
            !selectedPresetSetVersionDetails ||
            !caseUuid ||
            !sessionUuid ||
            !caseRetrieveRes.data?.value
          "
          type="list-item, list-item, list-item"
          class="bg-background"
        ></v-skeleton-loader>
        <template v-else>
          <QueryResults
            v-model:selected-query-uuid="selectedQueryUuid"
            v-model:open-query-uuids="openQueryUuids"
            :hints-enabled="hintsEnabled"
            :case-uuid="caseUuid"
            :session-uuid="sessionUuid"
            :case-obj="caseRetrieveRes.data?.value"
            @message="queueMessage"
          />
        </template>
      </v-main>
      <!-- <SeqvarDetails
        v-model:show-sheet="detailsShown"
        :project-uuid="projectUuid"
        :result-row-uuid="caseDetailsStore.caseObj?.sodar_uuid"
      /> -->

      <v-snackbar-queue
        v-model="messages"
        timer="5000"
        close-on-content-click
      ></v-snackbar-queue>
    </v-app>
    <VueQueryDevtools />
  </div>
</template>
