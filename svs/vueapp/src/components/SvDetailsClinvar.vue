<script setup lang="ts">
import { useSvDetailsStore } from '@svs/stores/detailsSv'

const detailsStore = useSvDetailsStore()

const vcvUrl = (vcv: string): string => {
  const stripped = vcv.replace(/^VCV0+/, '')
  return `https://www.ncbi.nlm.nih.gov/clinvar/variation/${stripped}/`
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Overlapping ClinVar SVs</h4>
    </div>
    <div
      class="card-body"
      v-if="detailsStore.currentSvRecord?.payload?.clinvar_ovl_vcvs?.length"
    >
      <p>
        The following overlapping SVs are flagged as (likely) pathogenic in
        ClinVar.
      </p>

      <ul>
        <li
          v-for="vcv in detailsStore.currentSvRecord?.payload
            ?.clinvar_ovl_vcvs ?? []"
        >
          <a :href="vcvUrl(vcv)">
            {{ vcv }}
          </a>
        </li>
      </ul>
    </div>
    <div class="card-body" v-else>
      <p>
        No overlapping (likely) pathogenic ClinVar SVs found in local database.
      </p>
    </div>
  </div>
</template>
