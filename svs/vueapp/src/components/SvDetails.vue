<script setup>
import { ref } from 'vue'

import { formatLargeInt } from '@varfish/helpers.js'
import VariantDetailsComments from '@varfish/components/VariantDetailsComments.vue'
import VariantDetailsFlags from '@varfish/components/VariantDetailsFlags.vue'

import { useSvFilterStore } from '@svs/stores/filterSvs'
import { useSvDetailsStore } from '@svs/stores/detailsSv.js'
import { useSvFlagsStore } from '@svs/stores/svFlags.js'
import { useSvCommentsStore } from '@svs/stores/svComments.js'

import SvDetailsGenes from './SvDetailsGenes.vue'
import SvDetailsGenotypeCall from './SvDetailsGenotypeCall.vue'

// Get reference to store detailsSv
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

// Pretty display of coordinates.
const svCoordinates = (record) => {
  if (!record) {
    return 'NO SV'
  }
  const chromosome = record.chromosome.startsWith('chr')
    ? record.chromosome
    : `chr${record.chromosome}`
  const start = formatLargeInt(record.start)
  const end = formatLargeInt(record.end)
  return `${chromosome}:${start}:${end}`
}

// Enumeration for the screens.
const Screen = Object.freeze({
  info: 'info',
  commentsFlags: 'commentsFlags',
  flags: 'flags',
})

// The currently active details screen.
const activeScreen = ref('info')
</script>

<template>
  <div>
    <ul class="nav nav-pills mb-3">
      <li class="nav-item" role="presentation">
        <a
          class="nav-link"
          type="button"
          @click="activeScreen = Screen.info"
          :class="{ active: activeScreen === Screen.info }"
        >
          Info
        </a>
      </li>
      <li class="nav-item" role="presentation">
        <a
          class="nav-link"
          type="button"
          @click="activeScreen = Screen.commentsFlags"
          :class="{ active: activeScreen === Screen.commentsFlags }"
        >
          Comments &amp; Flags
        </a>
      </li>
    </ul>

    <div v-if="activeScreen === 'info'">
      <div class="card">
        <div class="card-body pb-2 pt-2">
          Precise coordinates:
          <code> {{ svCoordinates(detailsStore.currentSvRecord) }} </code>
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
    <div v-else-if="activeScreen === Screen.commentsFlags">
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
  </div>
</template>
