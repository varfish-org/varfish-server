<script setup>
import { ref } from 'vue'

import VariantDetailsGene from '@variants/components/VariantDetailsGene.vue'

const props = defineProps({
  genesInfos: Array,
  currentSvRecord: Object,
})

// Which gene to display.
const selectedGene = ref(0)
</script>

<template>
  <div>
    <template v-if="genesInfos && genesInfos.length">
      <div class="card">
        <div class="card-header d-flex">
          <h4 class="card-title">
            <span class="text-muted">Gene:</span>
            {{ genesInfos[selectedGene].symbol }}
            <span class="text-muted small" v-if="genesInfos?.length !== 1">
              ({{ selectedGene + 1 }}/{{ genesInfos.length }})
            </span>
          </h4>
          <div class="ml-auto" v-if="(genesInfos?.length ?? 0) > 1">
            <select class="custom-select" v-model="selectedGene">
              <option v-for="(geneInfos, index) in genesInfos" :value="index">
                {{ geneInfos.symbol }}
              </option>
            </select>
          </div>
        </div>
        <div v-for="(geneInfos, index) in genesInfos">
          <VariantDetailsGene
            :gene="geneInfos"
            :release="currentSvRecord?.release"
            v-if="index === selectedGene"
          />
        </div>
      </div>
    </template>
    <template v-else>
      <div class="text-muted font-italic">
        <i-fa-solid-circle-notch class="spin" />
        Loadin gene information.
      </div>
    </template>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
