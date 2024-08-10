<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { computed, onMounted, ref, watch } from 'vue'
import { SnackbarMessage } from '@/seqvars/views/PresetSets/lib'

import TheAppBar from '@/cases/components/TheAppBar/TheAppBar.vue'
import TheNavBar from '@/cases/components/TheNavBar/TheNavBar.vue'
import QueryEditor from '@/seqvars/components/QueryEditor/QueryEditor.vue'
import QueryEditorDrawer from '@/seqvars/components/QueryEditorDrawer/QueryEditorDrawer.vue'
import SeqvarDetails from '@/seqvars/components/SeqvarDetails/SeqvarDetails.vue'
import HintButton from '@/seqvars/components/QueryEditor/ui/HintButton.vue'
import { useProjectStore } from '@/cases/stores/project'
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'
import { useCaseDetailsStore } from '@/cases/stores/caseDetails'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** The case UUID. */
  caseUuid?: string
}>()

/** Whether to hide the navigation bar; component state. */
const navbarShown = ref<boolean>(true)
/** Whether to show the query editor. */
const queryEditorShown = ref<boolean>(true)
/** Whether to enable hints. */
const hintsEnabled = ref<boolean>(true)
/** Whether to hide the variant details pane; component state. */
const detailsShown = ref<boolean>(false)
// Messages to display in VSnackbarQueue; component state. */
const messages = ref<SnackbarMessage[]>([])

const caseDetailsStore = useCaseDetailsStore()
const projectStore = useProjectStore()
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/** (Re-)initialize the stores. */
const initializeStores = async () => {
  await Promise.all([
    (async () => {
      if (props.projectUuid && props.caseUuid) {
        await caseDetailsStore.initialize(props.projectUuid, props.caseUuid)
      }
    })(),
    projectStore.initialize(props.projectUuid),
    seqvarsPresetsStore.initialize(props.projectUuid),
  ])
}

/** The currently selected preset set for the case. */
const selectedPresetSetVersion = computed<
  SeqvarsQueryPresetsSetVersionDetails | undefined
>(() => {
  return seqvarsPresetsStore.presetSetVersions.values().next()?.value
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
  () => [props.projectUuid, props.caseUuid],
  async () => {
    await initializeStores()
  },
)
</script>

<template>
  <v-app id="seqvars-query">
    <TheAppBar
      v-model:show-left-panel="navbarShown"
      v-model:show-right-panel="detailsShown"
      :show-left-panel-button="true"
      :show-right-panel-button="true"
      :title="
        caseDetailsStore.caseObj?.name
          ? `VarFish - ${caseDetailsStore.caseObj?.name}`
          : undefined
      "
      :loading="!selectedPresetSetVersion"
    />

    <TheNavBar :navbar-shown="navbarShown">
      <v-list-item
        prepend-icon="mdi-arrow-left"
        :to="{
          name: 'case-detail-overview',
          params: { project: projectUuid, case: caseUuid },
        }"
      >
        <template v-if="navbarShown"> Back to Case </template>
      </v-list-item>

      <v-list-subheader v-if="navbarShown" class="text-uppercase">
        Variant Analysis (V2)
      </v-list-subheader>
      <v-divider v-else class="mt-1 mb-1"></v-divider>
      <v-list-item
        prepend-icon="mdi-filter-variant"
        :data-x-to="{
          name: 'strucvars-query',
          params: { case: caseUuid },
        }"
      >
        <template v-if="navbarShown"> Go To SV Filtration </template>
      </v-list-item>

      <v-list-subheader v-if="navbarShown" class="text-uppercase">
        Analysis Information
      </v-list-subheader>
      <v-divider v-else class="mt-1 mb-1"></v-divider>

      <v-list-item
        prepend-icon="mdi-tune"
        @click="queryEditorShown = !queryEditorShown"
      >
        <template v-if="navbarShown"> Query Editor </template>
        <template #append>
          <v-btn icon variant="plain" density="compact" readonly>
            <Icon
              :icon="`material-symbols:left-panel-${queryEditorShown ? 'close' : 'open'}-outline`"
              style="font-size: 24px"
            ></Icon>
          </v-btn>
        </template>
      </v-list-item>

      <v-list-item
        :prepend-icon="hintsEnabled ? 'mdi-lightbulb-on' : 'mdi-lightbulb-off'"
        @click="hintsEnabled = !hintsEnabled"
      >
        <template v-if="navbarShown"> Hints </template>
        <template #append>
          <HintButton
            v-if="hintsEnabled"
            text="When hints are enabled, you can
          access them through the [i] icons."
          />
        </template>
      </v-list-item>

      <div id="seqvar-queries-teleport-pad">
        <!-- This is where QueryEditor renders its queries when hidden. -->
      </div>
    </TheNavBar>

    <QueryEditorDrawer :drawer-shown="queryEditorShown">
      <v-skeleton-loader
        v-if="!selectedPresetSetVersion"
        type="list-item, list-item, list-item"
      ></v-skeleton-loader>
      <template v-else>
        <QueryEditor
          :collapsed="!queryEditorShown"
          :presets-details="selectedPresetSetVersion"
          :hints-enabled="hintsEnabled"
          teleport-to-when-collapsed="#seqvar-queries-teleport-pad"
          :teleported-queries-labels="navbarShown"
          @message="queueMessage"
        />
      </template>
    </QueryEditorDrawer>
    <v-main>
      <div>
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam nec
        purus nec nunc tincidunt ultricies. Nullam nec purus nec nunc tincidunt
        ultricies. Nullam nec purus nec nunc tincidunt ultricies. Nullam nec
        purus nec nunc tincidunt ultricies. Nullam nec purus nec nunc tincidunt
        ultricies. Nullam nec purus nec nunc tincidunt ultricies. Nullam nec
        purus nec nunc tincidunt ultricies. Nullam nec purus nec nunc tincidunt
        ultricies. Nullam nec purus nec nunc
      </div>
    </v-main>
    <SeqvarDetails v-model:show-sheet="detailsShown" />

    <v-snackbar-queue
      v-model="messages"
      timer="5000"
      close-on-content-click
    ></v-snackbar-queue>
  </v-app>
</template>
