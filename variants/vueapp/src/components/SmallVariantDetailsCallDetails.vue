<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Genotype and Call Infos</h4>
    </div>
    <table class="card-body table table-striped table-sm">
      <thead>
        <tr>
          <th class="text-center">Sample</th>
          <th
            class="text-center"
            v-for="(member, index) in queryStore.case.pedigree"
            :key="index"
          >
            {{ $filters.displayName(member.name) }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="text-center">Genotype</th>
          <td
            class="text-center"
            v-for="(member, index) in queryStore.case.pedigree"
            :key="index"
          >
            {{ detailsStore.smallVariant.genotype[member.name].gt }}
          </td>
        </tr>
        <tr>
          <th class="text-center">Coverage (DP)</th>
          <template
            v-for="(member, index) in queryStore.case.pedigree"
            :key="index"
          >
            <td
              v-if="detailsStore.smallVariant.genotype[member.name].dp === -1"
              class="text-center"
            >
              .
            </td>
            <td v-else class="text-center">
              {{ detailsStore.smallVariant.genotype[member.name].dp }}
            </td>
          </template>
        </tr>
        <tr>
          <th class="text-center">Alt. Depth (AD)</th>
          <template
            v-for="(member, index) in queryStore.case.pedigree"
            :key="index"
          >
            <td
              v-if="detailsStore.smallVariant.genotype[member.name].ad === -1"
              class="text-center"
            >
              .
            </td>
            <td v-else class="text-center">
              {{ detailsStore.smallVariant.genotype[member.name].ad }}
            </td>
          </template>
        </tr>
        <tr>
          <th class="text-center">Allelic Balance</th>
          <template
            v-for="(member, index) in queryStore.case.pedigree"
            :key="index"
          >
            <td class="text-center">
              {{
                allelicBalance(
                  detailsStore.smallVariant.genotype[member.name]
                ).toFixed(2)
              }}
            </td>
          </template>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import { variantDetailsStore } from "@/stores/variantDetails";
import { filterQueryStore } from "@/stores/filterQuery";

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore();
    const queryStore = filterQueryStore();
    return {
      detailsStore,
      queryStore,
    };
  },
  methods: {
    allelicBalance(value) {
      if (!value.dp || !value.ad) {
        return 0.0;
      } else {
        return value.ad / value.dp;
      }
    },
  },
};
</script>
