<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import VariantDetailsComments from '@varfish/components/VariantDetailsComments.vue'
import VariantDetailsFlags from '@varfish/components/VariantDetailsFlags.vue'

import { useCaseDetailsStore } from '@cases/stores/case-details'
import { useSvFilterStore } from '@svs/stores/filterSvs'
import { useSvDetailsStore } from '@svs/stores/detailsSv.js'
import { useSvFlagsStore } from '@svs/stores/svFlags.js'
import { useSvCommentsStore } from '@svs/stores/svComments.js'

import SvDetailsGenes from './SvDetailsGenes.vue'
import SvDetailsGenotypeCall from './SvDetailsGenotypeCall.vue'
import GenomeBrowser from './GenomeBrowser.vue'

const props = defineProps({
  resultRowUuid: String,
  selectedTab: String,
})

/** The currently used router. */
const router = useRouter()

// Get reference to store detailsSv
const caseDetailsStore = useCaseDetailsStore()
const svFilterStore = useSvFilterStore()
const detailsStore = useSvDetailsStore()
const flagsStore = useSvFlagsStore()
flagsStore.initialize(
  { csrf_token: svFilterStore.csrfToken },
  svFilterStore.caseUuid
)
const commentsStore = useSvCommentsStore()
commentsStore.initialize(
  { csrf_token: svFilterStore.csrfToken },
  svFilterStore.caseUuid
)

// Safely return case release.
const genomeRelease = computed(() => {
  const release = caseDetailsStore.caseObj?.release ?? 'GRCh37'
  return release === 'GRCh37' ? 'hg19' : 'b38'
})

// Safely return case UUD
const caseUuid = computed(() => caseDetailsStore.caseObj?.sodar_uuid)

// Pretty display of coordinates.
const svLocus = (record) => {
  if (!record) {
    return null
  }

  let locus
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
const onTabClick = (selectedTab) => {
  router.push({
    name: 'svs-filter-details',
    params: {
      case: svFilterStore.caseUuid,
      query: svFilterStore.previousQueryDetails.sodar_uuid,
      row: props.resultRowUuid,
      selectedTab: selectedTab,
    },
  })
}
</script>

<template>
  <div>
    <ul class="nav nav-pills mb-3">
      <li class="nav-item" role="presentation">
        <a
          class="nav-link"
          :class="{ active: props.selectedTab === 'info' }"
          @click="onTabClick('info')"
          type="button"
        >
          Info
        </a>
      </li>
      <li class="nav-item" role="presentation">
        <a
          class="nav-link"
          :class="{ active: props.selectedTab === 'comments-flags' }"
          @click="onTabClick('comments-flags')"
          type="button"
        >
          Comments &amp; Flags
        </a>
      </li>
      <li class="nav-item" role="presentation">
        <a
          class="nav-link"
          :class="{ active: props.selectedTab === 'genome-browser' }"
          @click="onTabClick('genome-browser')"
          type="button"
        >
          Browser
        </a>
      </li>
    </ul>

    <div v-if="props.selectedTab === 'info'">
      <div class="card">
        <div class="card-body pb-2 pt-2">
          Precise coordinates:
          <code> {{ svLocus(detailsStore.currentSvRecord) }} </code>
        </div>
      </div>

      <div class="row">
        <div class="col-6 pl-0">
          <SvDetailsGenes
            :genes-infos="detailsStore.genesInfos"
            :current-sv-record="detailsStore.currentSvRecord"
          />
        </div>
        <div class="col-6 pr-0">
          <SvDetailsGenotypeCall
            :current-sv-record="detailsStore.currentSvRecord"
          />
        </div>
      </div>
    </div>
    <div v-else-if="props.selectedTab === 'comments-flags'">
      <VariantDetailsFlags
        :details-store="detailsStore"
        :flags-store="flagsStore"
        :variant="detailsStore.currentSvRecord"
      />
      <VariantDetailsComments
        :details-store="detailsStore"
        :comments-store="commentsStore"
        :variant="detailsStore.currentSvRecord"
      />
    </div>
    <div v-else-if="props.selectedTab === 'genome-browser'">
      <GenomeBrowser
        :case-uuid="caseUuid"
        :genome="genomeRelease"
        :locus="svLocus(detailsStore.currentSvRecord)"
      />
    </div>
  </div>
</template>
