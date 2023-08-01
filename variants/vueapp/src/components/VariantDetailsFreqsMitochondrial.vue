<script setup lang="ts">
import { computed } from 'vue'

import { roundIt, isVariantMtHomopolymer } from '@varfish/more-utils'

const props = defineProps<{
  smallVar: any
  varAnnos: any
}>()

const helixMtDb = computed(() => {
  if (props?.varAnnos?.helixmtdb) {
    return props?.varAnnos?.helixmtdb
  } else {
    return null
  }
})

const gnomadMtDna = computed(() => {
  if (props?.varAnnos && props?.varAnnos['gnomad-mtdna']) {
    return props?.varAnnos['gnomad-mtdna']
  } else {
    return null
  }
})
</script>

<template>
  <div>
    <div v-if="!isVariantMtHomopolymer(props.smallVar)" class="text-muted pb-3">
      <small>
        <i-mdi-alert-circle-outline />
        Variant in homopolymeric region
      </small>
    </div>

    <table class="table table-reactive">
      <thead>
        <tr class="text-center">
          <th>Database</th>
          <th>Total Alleles</th>
          <th>Alt Alleles</th>
          <th>Heteroplasmic</th>
          <th>Homoplasmic</th>
          <th>Allele Frequency</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="text-nowrap">gnomAD-MT</td>
          <td class="text-right">{{ gnomadMtDna?.an }}</td>
          <td class="text-right">
            {{ gnomadMtDna?.ac_het + gnomadMtDna?.ac_hom }}
          </td>
          <td class="text-right">{{ gnomadMtDna?.ac_het }}</td>
          <td class="text-right">{{ gnomadMtDna?.ac_hom }}</td>
          <td
            class="text-right"
            v-html="
              roundIt(
                (gnomadMtDna?.ac_het + gnomadMtDna?.ac_hom) / gnomadMtDna?.an,
                4,
              )
            "
          />
        </tr>
        <tr>
          <td>HelixMTdb</td>
          <td class="text-right">{{ helixMtDb?.num_total }}</td>
          <td class="text-right">
            {{ helixMtDb?.num_het + helixMtDb?.num_hom }}
          </td>
          <td class="text-right">{{ helixMtDb?.num_het }}</td>
          <td class="text-right">{{ helixMtDb?.num_hom }}</td>
          <td
            class="text-right"
            v-html="
              roundIt(
                (helixMtDb?.num_het + helixMtDb?.num_hom) /
                  helixMtDb?.num_total,
                4,
              )
            "
          />
        </tr>
      </tbody>
    </table>
  </div>
</template>
