<script setup lang="ts">
import { displayName } from '@varfish/helpers'
import { roundIt } from '@bihealth/reev-frontend-lib/lib/utils'

import { ResultRow } from './types'
import { allelicBalance } from './lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps<{
  /** Small variant to display for. */
  resultRow?: ResultRow
}>()
</script>

<template>
  <template v-if="!resultRow || !resultRow.payload">
    <v-skeleton-loader type="card" />
  </template>
  <template v-else>
    <v-card>
      <v-card-title class="pb-0 pr-2">
        Genotype Info
        <!-- <DocsLink anchor="genotype-info" /> -->
      </v-card-title>

      <v-card-subtitle class="text-overline">
        Detailed Information on Genotype Calls
      </v-card-subtitle>
      <v-card-text class="pt-3">
        <v-table>
          <thead>
            <tr>
              <th class="font-weight-bold">Sample</th>
              <template
                v-for="sample in Object.keys(resultRow.payload.genotype)"
              >
                <th class="font-weight-bold">
                  {{ displayName(sample) }}
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th>Genotype</th>
              <td
                v-for="(genotype, index) in Object.values(
                  resultRow.payload.genotype,
                )"
                :key="index"
              >
                {{ genotype.gt }}
              </td>
            </tr>
            <tr>
              <th>Coverage (DP)</th>
              <td
                v-for="(genotype, index) in Object.values(
                  resultRow.payload.genotype,
                )"
                :key="index"
              >
                {{ genotype.dp ?? 'N/A' }}
              </td>
            </tr>
            <tr>
              <th>Coverage (AD)</th>
              <td
                v-for="(genotype, index) in Object.values(
                  resultRow.payload.genotype,
                )"
                :key="index"
              >
                {{ genotype.ad ?? 'N/A' }}
              </td>
            </tr>
            <tr>
              <th>Allelic Balance</th>
              <td
                v-for="(genotype, index) in Object.values(
                  resultRow.payload.genotype,
                )"
                :key="index"
              >
                <!-- eslint-disable vue/no-v-html -->
                <span v-html="roundIt(allelicBalance(genotype))" />
                <!-- eslint-enable -->
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>
  </template>
</template>
