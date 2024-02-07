<script setup>
import { displayName } from '@varfish/helpers'

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
  <div>
    <table
      class="card-body table table-striped table-sm"
      v-if="props.caseDescription && props.smallVariant"
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
            <span
              v-if="!(member.name in props.smallVariant.genotype)"
              title="Info for the admin: the individual has no genotype information for this variant."
            >
              <i-mdi-do-not-disturb-on />
            </span>
            <span
              v-else-if="!('gt' in props.smallVariant.genotype[member.name])"
              title="Info for the admin: the `gt` field in the genotype information of the individual is missing."
            >
              <i-mdi-do-not-disturb-on />
              <em><sup>gt</sup></em>
            </span>
            <template v-else>
              {{ props.smallVariant.genotype[member.name].gt }}
            </template>
          </td>
        </tr>
        <tr>
          <th class="text-center">Coverage (DP)</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td
              v-if="!(member.name in props.smallVariant.genotype)"
              title="Info for the admin: the individual has no genotype information for this variant."
              class="text-center"
            >
              <i-mdi-do-not-disturb-on />
            </td>
            <td
              v-else-if="!('dp' in props.smallVariant.genotype[member.name])"
              title="Info for the admin: the `dp` field in the genotype information of the individual is missing."
              class="text-center"
            >
              <i-mdi-do-not-disturb-on />
              <em><sup>dp</sup></em>
            </td>
            <template v-else>
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
          </template>
        </tr>
        <tr>
          <th class="text-center">Alt. Depth (AD)</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td
              v-if="!(member.name in props.smallVariant.genotype)"
              title="Info for the admin: the individual has no genotype information for this variant."
              class="text-center"
            >
              <i-mdi-do-not-disturb-on />
            </td>
            <td
              v-else-if="!('ad' in props.smallVariant.genotype[member.name])"
              title="Info for the admin: the `dp` field in the genotype information of the individual is missing."
              class="text-center"
            >
              <i-mdi-do-not-disturb-on />
              <em><sup>ad</sup></em>
            </td>
            <template v-else>
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
          </template>
        </tr>
        <tr>
          <th class="text-center">Allelic Balance</th>
          <template
            v-for="(member, index) in props.caseDescription.pedigree"
            :key="index"
          >
            <td
              v-if="!(member.name in props.smallVariant.genotype)"
              title="Info for the admin: the individual has no genotype information for this variant."
              class="text-center"
            >
              <i-mdi-do-not-disturb-on />
            </td>
            <td v-else class="text-center">
              {{
                allelicBalance(
                  props.smallVariant.genotype[member.name],
                ).toFixed(2)
              }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>
    <div v-else class="card-body text-center font-italic pb-2 text-muted">
      No genotype information available.
    </div>
  </div>
</template>
