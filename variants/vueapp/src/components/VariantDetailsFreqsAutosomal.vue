<script setup lang="ts">
import { computed, ref } from 'vue'

import { roundIt } from '@varfish/more-utils'

const props = defineProps<{
  smallVar: any
  varAnnos: any
  dataset: string
}>()

const selAnnos = computed(() => {
  return props.varAnnos[props.dataset]
})

const noCohort = computed(() => {
  for (const elem of selAnnos?.value.allele_counts ?? []) {
    if (!elem.cohort) {
      return elem
    }
  }
  return null
})

const bySex = computed(() => {
  return noCohort.value?.by_sex
})

const byPop = computed(() => {
  const res = {}
  for (const record of noCohort.value?.by_population) {
    res[record.population] = record
  }
  return res
})

const allPopLabels = {
  afr: 'African',
  asj: 'Ashkenazy Jewish',
  eas: 'East Asian',
  fin: 'European (Finnish)',
  nfe: 'European (Non-Finnish)',
  amr: 'Latino/Admixed American',
  sas: 'South Asian',
  oth: 'Other',
}

const idKey = (token: string): string => {
  return `id-${props.dataset}-${token}`
}

const sexExpanded = ref({})
</script>

<template>
  <div>
    <div class="font-weight-bolder mb-3" style="font-size: 120%">
      <template v-if="props.dataset === 'gnomad-exomes'">
        gnomAD Exomes
      </template>
      <template v-if="props.dataset === 'gnomad-genomes'">
        gnomAD Genomes
      </template>
    </div>
    <table class="table table-reactive">
      <thead>
        <tr>
          <th>Population</th>
          <th></th>
          <th class="text-right">Allele Count</th>
          <th class="text-right">Homozygotes</th>
          <th class="text-right">Allele Frequency</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(label, key) of allPopLabels">
          <tr>
            <td>
              {{ label }}
              <a
                @click.prevent="sexExpanded[key] = true"
                v-if="!sexExpanded[key]"
              >
                <i-mdi-chevron-right />
              </a>
              <a @click.prevent="sexExpanded[key] = false" v-else>
                <i-mdi-chevron-down />
              </a>
            </td>
            <td></td>
            <td class="text-right">{{ byPop[key].counts.overall.an }}</td>
            <td class="text-right">{{ byPop[key].counts.overall.nhomalt }}</td>
            <td
              class="text-right"
              v-html="roundIt(byPop[key].counts.overall.af, 4)"
            ></td>
          </tr>
          <tr
            :id="idKey(key) + '-xx'"
            class="bg-light"
            :class="{ 'd-none': !sexExpanded[key] }"
          >
            <td></td>
            <td class="text-right">XX</td>
            <td class="text-right">{{ byPop[key].counts.xx.an }}</td>
            <td class="text-right">{{ byPop[key].counts.xx.nhomalt }}</td>
            <td
              class="text-right"
              v-html="roundIt(byPop[key].counts.xx.af, 4)"
            ></td>
          </tr>
          <tr
            :id="idKey(key) + '-xy'"
            class="bg-light"
            :class="{ 'd-none': !sexExpanded[key] }"
          >
            <td></td>
            <td class="text-right">XY</td>
            <td class="text-right">{{ byPop[key].counts.xy.an }}</td>
            <td class="text-right">{{ byPop[key].counts.xy.nhomalt }}</td>
            <td
              class="text-right"
              v-html="roundIt(byPop[key].counts.xy.af, 4)"
            ></td>
          </tr>
        </template>

        <tr>
          <th>Total</th>
          <td></td>
          <td class="text-right">{{ bySex?.overall?.an }}</td>
          <td class="text-right">{{ bySex?.overall?.nhomalt }}</td>
          <td class="text-right" v-html="roundIt(bySex?.overall?.af, 5)"></td>
        </tr>

        <tr>
          <td></td>
          <td class="text-right">XY</td>
          <td class="text-right">{{ bySex?.xy?.an }}</td>
          <td class="text-right">{{ bySex?.xy?.nhomalt }}</td>
          <td class="text-right" v-html="roundIt(bySex?.xy?.af, 5)"></td>
        </tr>

        <tr>
          <td></td>
          <td class="text-right">XX</td>
          <td class="text-right">{{ bySex?.xx?.an }}</td>
          <td class="text-right">{{ bySex?.xx?.nhomalt }}</td>
          <td class="text-right" v-html="roundIt(bySex?.xx?.af, 5)"></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
