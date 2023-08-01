<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import VariantDetailsComments from '@varfish/components/VariantDetails/Comments.vue'
import VariantDetailsFlags from '@varfish/components/VariantDetails/Flags.vue'
import SimpleCard from '@varfish/components/SimpleCard.vue'

import { useCaseDetailsStore } from '@cases/stores/case-details'
import { useSvFilterStore } from '@svs/stores/filterSvs'
import { useSvDetailsStore } from '@svs/stores/detailsSv'
import { useSvFlagsStore } from '@svs/stores/svFlags'
import { useSvCommentsStore } from '@svs/stores/svComments'

import SvDetailsGenes from '@svs/components/SvDetailsGenes.vue'
import SvDetailsClinvar from '@svs/components/SvDetailsClinvar.vue'
import SvDetailsGenotypeCall from '@svs/components/SvDetailsGenotypeCall.vue'
import GenomeBrowser from '@svs/components/GenomeBrowser.vue'
import { allNavItems as navItems } from '@svs/components/SvDetails.fields'

/** `SVRecord` is a type alias for easier future interface definition. */
type SvRecord = any

const props = defineProps<{
  resultRowUuid?: string
  selectedTab?: string
}>()

const route = useRoute()
const router = useRouter()

// Get reference to store detailsSv
const caseDetailsStore = useCaseDetailsStore()
const svFilterStore = useSvFilterStore()
const detailsStore = useSvDetailsStore()
const flagsStore = useSvFlagsStore()
flagsStore.initialize(
  { csrf_token: svFilterStore.csrfToken },
  svFilterStore.caseUuid,
)
const commentsStore = useSvCommentsStore()
commentsStore.initialize(
  { csrf_token: svFilterStore.csrfToken },
  svFilterStore.caseUuid,
)

// Safely return case release.
const genomeRelease = computed(() => {
  const release = caseDetailsStore.caseObj?.release ?? 'GRCh37'
  return release === 'GRCh37' ? 'hg19' : 'b38'
})

// Safely return case UUD
const caseUuid = computed(() => caseDetailsStore.caseObj?.sodar_uuid)

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
const onTabClick = (selectedTab: string) => {
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

/** When mounted, scroll to the selected element if any.
 */
onMounted(() => {
  document.querySelector(`#${route.params.selectedTab}`)?.scrollIntoView()
})
</script>

<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col-10 pl-0 pr-0 pt-2">
        <SimpleCard id="genes" title="Genes">
          <SvDetailsGenes
            :genes-infos="detailsStore.genesInfos"
            :current-sv-record="detailsStore.currentSvRecord"
          />
        </SimpleCard>
        <SimpleCard id="clinvar" title="ClinVar">
          <SvDetailsClinvar />
        </SimpleCard>
        <SimpleCard id="call-details" title="Genotype Call">
          <div class="p-2">
            Precise coordinates:
            <code> {{ svLocus(detailsStore.currentSvRecord) }} </code>
          </div>
          <SvDetailsGenotypeCall
            :current-sv-record="detailsStore.currentSvRecord"
          />
        </SimpleCard>
        <SimpleCard id="flags" title="Flags">
          <VariantDetailsFlags
            :details-store="detailsStore"
            :flags-store="flagsStore"
            :variant="detailsStore.currentSvRecord"
          />
        </SimpleCard>
        <SimpleCard id="comments" title="Comments">
          <VariantDetailsComments
            :details-store="detailsStore"
            :comments-store="commentsStore"
            :variant="detailsStore.currentSvRecord"
          />
        </SimpleCard>
        <SimpleCard id="genome-browser" title="Genome Browser">
          <GenomeBrowser
            :case-uuid="caseUuid"
            :genome="genomeRelease"
            :locus="svLocus(detailsStore.currentSvRecord)"
          />
        </SimpleCard>
      </div>

      <div class="col-2">
        <ul
          class="nav flex-column nav-pills position-sticky pt-2"
          style="top: 0px"
        >
          <li class="nav-item mt-0" v-for="{ name, title } in navItems">
            <a
              class="nav-link user-select-none"
              :class="{ active: props.selectedTab === name }"
              @click="onTabClick(name)"
              type="button"
            >
              {{ title }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
