<script setup lang="ts">
import { computed, ref } from 'vue'

import { roundIt, separateIt as sep } from '@varfish/more-utils'

const props = defineProps<{
  smallVar: any
  varAnnos: any
  dataset: string
}>()

const FREQ_DIGITS = 5

const selAnnos = computed(() => {
  return props.varAnnos[props.dataset]
})

const noCohort = computed(() => {
  for (const elem of selAnnos.value?.allele_counts ?? []) {
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
  for (const record of noCohort.value?.by_population ?? []) {
    res[record.population] = record
  }
  return res
})

const allPopLabels = {
  afr: 'African-American/African',
  asj: 'Ashkenazy Jewish',
  eas: 'East Asian',
  fin: 'European (Finnish)',
  nfe: 'European (North-Western)',
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
    <div class="ml-2 mr-2 mb-3 mt-2">
      <span class="font-weight-bolder" style="font-size: 120%">
        <template v-if="props.dataset === 'gnomad-exomes'">
          gnomAD Exomes
        </template>
        <template v-if="props.dataset === 'gnomad-genomes'">
          gnomAD Genomes
        </template>
      </span>
      <a
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          ''
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r2_1`"
        v-if="smallVar.release == 'GRCh37'"
      >
        <i-mdi-launch />
        @gnomAD
      </a>
      <a
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          ''
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r3`"
        v-if="smallVar.release == 'GRCh38'"
      >
        <i-mdi-launch />
        @gnomAD
      </a>
    </div>
    <table class="table table-reactive" v-if="selAnnos">
      <thead>
        <tr>
          <th>Population</th>
          <th></th>
          <th class="text-right text-nowrap">Allele Count</th>
          <th class="text-right text-nowrap">Homozygotes</th>
          <th class="text-right text-nowrap">Allele Frequency</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="(label, key) of allPopLabels">
          <template v-if="byPop[key]?.counts?.overall?.an">
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
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.overall?.an) }}
              </td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.overall?.nhomalt) }}
              </td>
              <td
                class="text-right text-nowrap"
                v-html="roundIt(byPop[key]?.counts?.overall?.af, FREQ_DIGITS)"
              ></td>
            </tr>
            <tr
              :id="idKey(key) + '-xx'"
              class="bg-light"
              :class="{ 'd-none': !sexExpanded[key] }"
            >
              <td></td>
              <td class="text-right text-nowrap">XX</td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.xx?.an) }}
              </td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.xx?.nhomalt) }}
              </td>
              <td
                class="text-right text-nowrap"
                v-html="roundIt(byPop[key]?.counts?.xx?.af, FREQ_DIGITS)"
              ></td>
            </tr>
            <tr
              :id="idKey(key) + '-xy'"
              class="bg-light"
              :class="{ 'd-none': !sexExpanded[key] }"
            >
              <td></td>
              <td class="text-right text-nowrap">XY</td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key].counts?.xy?.an) }}
              </td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key].counts?.xy?.nhomalt) }}
              </td>
              <td
                class="text-right text-nowrap"
                v-html="roundIt(byPop[key].counts?.xy?.af, FREQ_DIGITS)"
              ></td>
            </tr>
          </template>
        </template>

        <tr>
          <th>Total</th>
          <td></td>
          <td class="text-right text-nowrap">{{ sep(bySex?.overall?.an) }}</td>
          <td class="text-right text-nowrap">
            {{ sep(bySex?.overall?.nhomalt) }}
          </td>
          <td
            class="text-right text-nowrap"
            v-html="roundIt(bySex?.overall?.af, FREQ_DIGITS)"
          ></td>
        </tr>

        <tr>
          <td></td>
          <td class="text-right text-nowrap">XX</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xx?.an) }}</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xx?.nhomalt) }}</td>
          <td
            class="text-right text-nowrap"
            v-html="roundIt(bySex?.xx?.af, FREQ_DIGITS)"
          ></td>
        </tr>

        <tr>
          <td></td>
          <td class="text-right text-nowrap">XY</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xy?.an) }}</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xy?.nhomalt) }}</td>
          <td
            class="text-right text-nowrap"
            v-html="roundIt(bySex?.xy?.af, FREQ_DIGITS)"
          ></td>
        </tr>
      </tbody>
    </table>

    <div class="text-muted text-center font-italic pb-3" v-else>
      No allele frequency information available in local database.
      Try to lookup the variant directly:
      <a
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          ''
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r2_1`"
        v-if="smallVar.release == 'GRCh37'"
      >
        <i-mdi-launch />
        gnomAD
      </a>
      <a
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          ''
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r3`"
        v-if="smallVar.release == 'GRCh38'"
      >
        <i-mdi-launch />
        gnomAD
      </a>
    </div>
  </div>
</template>
