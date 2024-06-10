<script setup lang="ts">
import { computed } from 'vue'

import { displayName } from '@/varfish/helpers'
import { ResultRow } from './types'
import { GET_FIELD_MAP as GT_FIELD_MAP, identity } from './constants'

/** This component's props. */
const props = defineProps<{
  resultRow?: ResultRow
}>()

/**
 * List of all keys.
 */
const allKeys = computed<string[]>(() => {
  if (!props.resultRow?.payload?.call_info) {
    return []
  }

  let tmp: string[] = []
  for (const call_info of Object.values(props.resultRow.payload.call_info)) {
    tmp = tmp.concat(
      Object.entries(call_info)
        .filter(([_, value]) => value !== null)
        .map(([key, _]) => key),
    )
  }
  const result = Array.from(new Set(tmp))
  result.sort()
  return result
})
</script>

<template>
  <template v-if="resultRow === undefined">
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
                v-for="sample in Object.keys(resultRow.payload.call_info)"
              >
                <th class="font-weight-bold">
                  {{ displayName(sample) }}
                </th>
              </template>
            </tr>
          </thead>
          <tbody>
            <tr v-for="key in allKeys">
              <th>
                {{ GT_FIELD_MAP[key]?.label ?? GT_FIELD_MAP[key]?.name ?? key }}
              </th>
              <td v-for="genotype in resultRow.payload.call_info">
                {{ (GT_FIELD_MAP[key]?.fmt ?? identity)(genotype[key]) }}
              </td>
            </tr>
          </tbody>
        </v-table>
      </v-card-text>
    </v-card>
  </template>
</template>
