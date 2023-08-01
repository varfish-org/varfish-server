<script setup lang="ts">
import { useSvDetailsStore } from '@svs/stores/detailsSv'

const detailsStore = useSvDetailsStore()

const vcvUrl = (vcv: string): string => {
  const stripped = vcv.replace(/^VCV0+/, '')
  return `https://www.ncbi.nlm.nih.gov/clinvar/variation/${stripped}/`
}
</script>

<template>
  <div class="p-2">
    <template
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
    </template>
    <template v-else>
      <div class="text-muted text-center font-italic">
        SV has not been annotated with (likely) pathogenic ClinVar SV records.
      </div>
    </template>
  </div>
</template>
