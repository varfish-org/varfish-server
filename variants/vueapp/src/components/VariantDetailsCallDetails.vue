<script setup>
import { displayName } from '@varfish/helpers.js'

const props = defineProps({
  /** Case description object. */
  caseDescription: Object,
  /** Small variant to display for. */
  smallVariant: Object,
})

const allelicBalance = (value) => {
  if (!value.dp || !value.ad) {
    return 0.0
  } else {
    return value.ad / value.dp
  }
}
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Genotype and Call Infos</h4>
    </div>
    <table
      class="card-body table table-striped table-sm"
      v-if="props.caseDescription"
    >
      <thead>
        <tr>
          <th class="text-center">Sample</th>
          <th
            class="text-center"
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            {{ displayName(member.name) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="text-center">Genotype</th>
          <td
            class="text-center"
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            {{ props.smallVariant.genotype[member.name].gt }}
          </td>
        </tr>
        <tr>
          <th class="text-center">Coverage (DP)</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td
              v-if="props.smallVariant.genotype[member.name].dp === -1"
              class="text-center"
            >
              .
            </td>
            <td v-else class="text-center">
              {{ props.smallVariant.genotype[member.name].dp }}
            </td>
          </template>
        </tr>
        <tr>
          <th class="text-center">Alt. Depth (AD)</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td
              v-if="props.smallVariant.genotype[member.name].ad === -1"
              class="text-center"
            >
              .
            </td>
            <td v-else class="text-center">
              {{ props.smallVariant.genotype[member.name].ad }}
            </td>
          </template>
        </tr>
        <tr>
          <th class="text-center">Allelic Balance</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td class="text-center">
              {{
                allelicBalance(
                  props.smallVariant.genotype[member.name]
                ).toFixed(2)
              }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>
  </div>
</template>
