<script setup>
import { ref } from 'vue'

const props = defineProps({
  smallVariant: Object,
})

const beaconAddress = ref(null)

const loadBeacon = () => {
  beaconAddress.value =
    'https://beacon-network.org:443/#/widget?rs=' +
    props.smallVariant.release +
    '&chrom=' +
    props.smallVariant.chromosome +
    '&pos=' +
    props.smallVariant.start +
    '&ref=' +
    props.smallVariant.reference +
    '&allele=' +
    props.smallVariant.alternative
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">
        Query Beacon
        <button class="btn btn-sm btn-warning pull-right" @click="loadBeacon()">
          <i class="iconify" data-icon="mdi:refresh"></i> Load
        </button>
      </h4>
    </div>
    <div class="card-body">
      <iframe
        v-if="beaconAddress"
        ref="beaconFrame"
        :src="beaconAddress"
        style="width: 100%; height: 300px; overflow: auto; border: 0"
        vspace="0"
        hspace="0"
      >
      </iframe>
      <p v-else class="text-muted text-center">
        <i>Click</i>&nbsp;
        <span class="badge badge-warning"
          ><i class="iconify" data-icon="mdi:refresh"></i> Load</span
        >
        <i>
          to submit the variant to the GA4GH Beacon network. The results will
          appear here.
        </i>
      </p>
    </div>
  </div>
</template>
