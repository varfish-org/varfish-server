<script setup>
import { displayName, formatLargeInt } from '@varfish/helpers'
import { tsTvRatio } from '@cases/common'

const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  varStats: Object,
})
</script>

<template>
  <table class="table table-striped table-sm table-hover mt-3 mb-3">
    <thead>
      <tr>
        <th>Sample</th>
        <th class="text-right">Ts</th>
        <th class="text-right">Tv</th>
        <th class="text-right">Ts/Tv</th>
        <th class="text-right">SNVs</th>
        <th class="text-right">InDels</th>
        <th class="text-right">MNVs</th>
        <th class="text-right">X hom./het.</th>
      </tr>
    </thead>
    <tbody>
      <template v-if="props.varStats">
        <tr
          v-for="entry in props.varStats"
          :key="`sample-${entry.sample_name}`"
        >
          <td>{{ displayName(entry.sample_name) }}</td>
          <td class="text-right">
            {{ formatLargeInt(entry.ontarget_transitions) }}
          </td>
          <td class="text-right">
            {{ formatLargeInt(entry.ontarget_transversions) }}
          </td>
          <td class="text-right">
            <span
              v-if="tsTvRatio(entry) < 1.0 || tsTvRatio(entry) > 2.9"
              class="text-danger"
            >
              <i-bi-exclamation-circle
                :title="`On-target Ts/Tv ratio should be between 2.0 and 2.9 but was ${tsTvRatio(
                  entry,
                )}.`"
              />
              {{ tsTvRatio(entry).toFixed(2) }}
            </span>
            <template v-else> {{ tsTvRatio(entry).toFixed(2) }} </template>
          </td>
          <td class="text-right">
            {{ formatLargeInt(entry.ontarget_snvs) }}
          </td>
          <td class="text-right">
            {{ formatLargeInt(entry.ontarget_indels) }}
          </td>
          <td class="text-right">
            {{ formatLargeInt(entry.ontarget_mnvs) }}
          </td>
          <td class="text-right">
            {{ entry.chrx_het_hom.toFixed(4) }}
          </td>
        </tr>
      </template>
      <tr v-else>
        <td colspan="8" class="text-muted text-center font-italic">
          No variant statistics to display.
        </td>
      </tr>
    </tbody>
  </table>
</template>
