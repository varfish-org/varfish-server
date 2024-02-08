<script setup lang="ts">
import { computed, ref } from 'vue'

import { roundIt, separateIt as sep } from '@varfish/moreUtils'

const props = defineProps<{
  smallVar: any
  varAnnos: any
  dataset: string
}>()

const FREQ_DIGITS = 5

const selAnnos = computed(() => {
  if (!props.varAnnos) {
    return null
  } else {
    return props.varAnnos[props.dataset]
  }
})

const noCohort = computed(() => {
  for (const elem of selAnnos.value?.alleleCounts ?? []) {
    if (!elem.cohort) {
      return elem
    }
  }
  return null
})

const bySex = computed(() => {
  return noCohort.value?.bySex
})

const byPop = computed(() => {
  const res = {}
  for (const record of noCohort.value?.byPopulation ?? []) {
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
        <template v-if="props.dataset === 'gnomad_exomes'">
          gnomAD Exomes
        </template>
        <template v-if="props.dataset === 'gnomad_genomes'">
          gnomAD Genomes
        </template>
      </span>
      <a
        v-if="smallVar.release == 'GRCh37'"
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          '',
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r2_1`"
        target="_blank"
      >
        <i-mdi-launch />
        @gnomAD
      </a>
      <a
        v-if="smallVar.release == 'GRCh38'"
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          '',
        )}-${smallVar.start}-${smallVar.reference}-${
          smallVar.alternative
        }?dataset=gnomad_r3`"
        target="_blank"
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
          <th class="text-right text-nowrap">
            <abbr title="total number of alleles"> Allele Count </abbr>
          </th>
          <th class="text-right text-nowrap">
            <abbr title="variant alleles in high-quality calls">
              Allele Number
            </abbr>
          </th>
          <th class="text-right text-nowrap">
            <abbr title="number of individuals with homozygote alleles">
              Homozygotes
            </abbr>
          </th>
          <th class="text-right text-nowrap">
            <abbr title="frequency of variant alleles called with high quality">
              Allele Frequency
            </abbr>
          </th>
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
                {{ sep(byPop[key]?.counts?.overall?.an ?? 0) }}
              </td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.overall?.ac ?? 0) }}
              </td>
              <td class="text-right text-nowrap">
                {{ sep(byPop[key]?.counts?.overall?.nhomalt ?? 0) }}
              </td>
              <td
                class="text-right text-nowrap"
                v-html="
                  roundIt(byPop[key]?.counts?.overall?.af ?? 0.0, FREQ_DIGITS)
                "
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
                {{ sep(byPop[key].counts?.xy?.ac) }}
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

        <tr class="table-info">
          <th>Total</th>
          <td></td>
          <td class="text-right text-nowrap">{{ sep(bySex?.overall?.an) }}</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.overall?.ac) }}</td>
          <td class="text-right text-nowrap">
            {{ sep(bySex?.overall?.nhomalt) }}
          </td>
          <td
            class="text-right text-nowrap"
            v-html="roundIt(bySex?.overall?.af ?? 0.0, FREQ_DIGITS)"
          ></td>
        </tr>

        <tr>
          <td></td>
          <td class="text-right text-nowrap">XX</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xx?.an) }}</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xx?.ac) }}</td>
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
          <td class="text-right text-nowrap">{{ sep(bySex?.xy?.ac) }}</td>
          <td class="text-right text-nowrap">{{ sep(bySex?.xy?.nhomalt) }}</td>
          <td
            class="text-right text-nowrap"
            v-html="roundIt(bySex?.xy?.af, FREQ_DIGITS)"
          ></td>
        </tr>
      </tbody>
    </table>

    <div class="text-muted text-center font-italic pb-3" v-else>
      No allele frequency information available in local database. Try to lookup
      the variant directly:
      <a
        :href="`https://gnomad.broadinstitute.org/variant/${smallVar.chromosome.replace(
          /^chr/,
          '',
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
          '',
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
