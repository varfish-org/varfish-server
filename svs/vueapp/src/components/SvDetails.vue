<script setup lang="ts">
/**
 * Detailed display of SV information.
 *
 * Used in the SV filtration app and displayed when the user selects a variant to display
 * the details for.
 *
 * Also used in the case details view for displaying all user-annotated variants.
 *
 * See `SvDetails` for a peer app for sequence variants
 */

import { onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

import CommentsCard from '@varfish/components/CommentsCard/CommentsCard.vue'
import FlagsCard from '@varfish/components/FlagsCard/FlagsCard.vue'
import SimpleCard from '@varfish/components/SimpleCard.vue'

import { useCaseDetailsStore } from '@cases/stores/caseDetails'
import { useSvDetailsStore } from '@svs/stores/svDetails'
import { useSvFlagsStore } from '@svs/stores/svFlags'
import { useSvCommentsStore } from '@svs/stores/svComments'
import { useSvResultSetStore } from '@svs/stores/svResultSet'
import { useHistoryStore } from '@varfish/stores/history'
import { State } from '@varfish/storeUtils'

import Header from '@svs/components/SvDetails/Header.vue'
import SvDetailsGenes from '@svs/components/SvDetails/Genes.vue'
import SvDetailsClinvar from '@svs/components/SvDetails/Clinvar.vue'
import SvDetailsGenotypeCall from '@svs/components/SvDetails/GenotypeCall.vue'
import GenomeBrowser from '@svs/components/GenomeBrowser.vue'
import Overlay from '@varfish/components/Overlay.vue'
import { allNavItems as navItems } from '@svs/components/SvDetails.fields'

/** `SVRecord` is a type alias for easier future interface definition. */
type SvRecord = any

const props = defineProps<{
  /** UUID of the result row to display. */
  resultRowUuid?: string
  /** Identifier of the selected section. */
  selectedSection?: string
}>()

/** Obtain global application content (as for all entry level components) */
const appContext = JSON.parse(
  document.getElementById('sodar-ss-app-context').getAttribute('app-context') ||
    '{}',
)

// Routing-related

const router = useRouter()

// Store-related

const historyStore = useHistoryStore()

const caseDetailsStore = useCaseDetailsStore()
const svResultSetStore = useSvResultSetStore()
const svDetailsStore = useSvDetailsStore()
const svFlagsStore = useSvFlagsStore()
const svCommentsStore = useSvCommentsStore()

const overlayShow = computed(() => {
  return (
    svResultSetStore.storeState.state === State.Fetching ||
    svDetailsStore.storeState.state === State.Fetching ||
    svFlagsStore.storeState.state === State.Fetching ||
    svCommentsStore.storeState.state === State.Fetching
  )
})

const overlayMessage = computed(() => {
  if (overlayShow.value) {
    return 'Loading...'
  } else {
    return ''
  }
})

// Safely return case release.
const genomeRelease = computed(() => {
  const release = caseDetailsStore.caseObj?.release ?? 'GRCh37'
  return release === 'GRCh37' ? 'hg19' : 'b38'
})

// Pretty display of coordinates.
const svLocus = (record: SvRecord): string | null => {
  if (!record) {
    return null
  }

  let locus: string
  if (record.sv_type === 'BND' || record.sv_type === 'INS') {
    locus = `${record.chromosome}:${record.start - 1000}-${record.start + 1000}`
  } else {
    locus = `${record.chromosome}:${record.start - 1000}-${record.end + 1000}`
  }
  if (!locus.startsWith('chr') && record.release === 'GRCh38') {
    locus = `chr${locus}`
  } else if (locus.startsWith('chr') && record.release === 'GRCh37') {
    locus = locus.substring(3)
  }
  return locus
}

/** Event handler for clicking on the given tab.
 *
 * Will select the tab by pushing a route.
 */
const onTabClick = (selectedSection: string) => {
  router.push({
    name: 'sv-details',
    params: {
      row: props.resultRowUuid,
      selectedSection: selectedSection,
    },
  })
}

const navigateBack = () => {
  const dest = historyStore.lastWithDifferentName('sv-details')
  if (dest) {
    router.push(dest)
  } else {
    router.push(`/svs/filter/${caseDetailsStore.caseObj?.sodar_uuid}`)
  }
}

/** Refresh the stores. */
const refreshStores = async () => {
  if (props.resultRowUuid && props.selectedSection) {
    await svResultSetStore.initialize(appContext.csrf_token)
    await svResultSetStore.fetchResultSetViaRow(props.resultRowUuid)
    await Promise.all([
      svFlagsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        svResultSetStore.caseUuid,
      ),
      svCommentsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        svResultSetStore.caseUuid,
      ),
      svDetailsStore.initialize(
        appContext.csrf_token,
        appContext.project?.sodar_uuid,
        svResultSetStore.caseUuid,
      ),
    ])
    svDetailsStore.fetchSvDetails(svResultSetStore.resultRow)
  }

  document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
}

/** Watch change in properties to reload data. */
watch(
  () => [props.resultRowUuid, props.selectedSection],
  () => {
    refreshStores()
  },
)

/** When mounted, scroll to the selected element if any.
 */
onMounted(() => {
  refreshStores()
  document.querySelector(`#${props.selectedSection}`)?.scrollIntoView()
})
</script>

<template>
  <div
    v-if="caseDetailsStore.caseObj !== null"
    class="d-flex flex-column h-100"
  >
    <Header
      :sv-record="svDetailsStore.currentSvRecord"
      :case="caseDetailsStore.caseObj"
    />
    <div class="container-fluid">
      <div class="row">
        <div class="col-10 pl-0 pr-0 pt-2">
          <div>
            <SimpleCard id="genes" title="Genes">
              <SvDetailsGenes
                :genes-infos="svDetailsStore.genesInfos"
                :current-sv-record="svDetailsStore.currentSvRecord"
              />
            </SimpleCard>
            <SimpleCard id="clinvar" title="ClinVar">
              <SvDetailsClinvar />
            </SimpleCard>
            <SimpleCard id="call-details" title="Genotype Call">
              <div class="p-2">
                Precise coordinates:
                <code> {{ svLocus(svDetailsStore.currentSvRecord) }} </code>
              </div>
              <SvDetailsGenotypeCall
                :current-sv-record="svDetailsStore.currentSvRecord"
              />
            </SimpleCard>
            <SimpleCard id="flags" title="Flags">
              <FlagsCard
                :flags-store="svFlagsStore"
                :variant="svDetailsStore.currentSvRecord"
              />
            </SimpleCard>
            <SimpleCard id="comments" title="Comments">
              <CommentsCard
                :comments-store="svCommentsStore"
                :variant="svDetailsStore.currentSvRecord"
              />
            </SimpleCard>
            <SimpleCard id="genome-browser" title="Genome Browser">
              <GenomeBrowser
                :case-uuid="caseDetailsStore.caseUuid"
                :genome="genomeRelease"
                :locus="svLocus(svDetailsStore.currentSvRecord)"
              />
            </SimpleCard>
          </div>
          <Overlay v-if="overlayShow" :message="overlayMessage" />
        </div>

        <div class="col-2">
          <ul
            class="nav flex-column nav-pills position-sticky pt-2"
            style="top: 0px"
          >
            <li class="nav-item mt-0 mb-3">
              <a
                class="nav-link user-select-none btn btn-secondary"
                type="button"
                @click.prevent="navigateBack()"
              >
                <i-mdi-arrow-left-circle />
                Back
              </a>
            </li>
            <li
              v-for="{ name, title } in navItems"
              :key="`section-${name}`"
              class="nav-item mt-0"
            >
              <a
                class="nav-link user-select-none"
                :class="{ active: props.selectedSection === name }"
                type="button"
                @click="onTabClick(name)"
              >
                {{ title }}
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
