<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">
        Frequency Details
        <span
          v-if="$filters.checkIsVariantMtHomopolymer(detailsStore.smallVariant)"
          class="text-muted"
        >
          &nbsp;<i class="iconify" data-icon="bi:exclamation-circle"></i>&nbsp;
          <small>Variant in homopolymeric region</small>
        </span>
      </h4>
    </div>
    <div class="table-responsive">
      <table
        v-if="detailsStore.smallVariant.chromosome === 'MT'"
        class="card-body table table-striped table-sm"
      >
        <thead>
          <tr>
            <th></th>
            <th
              v-for="vari in detailsStore.getMtFrequenciesHeader"
              :key="vari"
              class="text-center"
            >
              {{ vari }}
              <span
                v-if="detailsStore.smallVariant.reference === vari"
                class="badge badge-secondary"
                >REF</span
              >
              <span
                v-else-if="detailsStore.smallVariant.alternative === vari"
                class="badge badge-info"
                >ALT</span
              >
            </th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="(data, index) in detailsStore.getMtFrequencies"
            :key="index"
          >
            <tr>
              <th
                :colspan="detailsStore.getMtFrequenciesHeader.length + 1"
                class="text-center"
              >
                {{ data.name }}
                <span class="text-muted small"
                  >AN: {{ data.an.toLocaleString() }}</span
                >
                <i
                  v-if="data.isTriallelic"
                  class="iconify text-muted"
                  data-icon="bi:exclamation-circle"
                  title="Variant is part of a triallelic site"
                ></i>
                <i
                  v-if="data.dloop"
                  class="iconify text-muted"
                  data-icon="bi:exclamation-circle"
                  title="Variant is in D-loop region"
                ></i>
              </th>
            </tr>
            <tr v-for="(row, index2) in data.rows" :key="index2">
              <th>{{ row.title }}</th>
              <td
                class="text-right"
                v-for="(value, index3) in row.data"
                :key="index3"
              >
                {{ row.formatter(value) }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <table v-else class="card-body table table-striped table-sm">
        <thead>
          <tr>
            <th></th>
            <th
              class="text-center"
              v-for="pop in detailsStore.populations"
              :key="pop"
            >
              {{ pop }}
            </th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="(rows, name, index) in detailsStore.getFrequencies"
            :key="index"
          >
            <tr>
              <th
                :colspan="detailsStore.populations.length + 1"
                class="text-center"
              >
                {{ name }}
              </th>
            </tr>
            <template v-for="(row, index2) in rows" :key="index2">
              <tr v-if="row.display" :class="row.rowClasses">
                <th :class="row.titleClasses">
                  <i
                    v-if="row.titleIcon"
                    class="iconify"
                    :data-icon="row.titleIcon"
                  ></i>
                  {{ row.title }}
                </th>
                <td
                  v-for="(value, index3) in row.data"
                  :key="index3"
                  :class="value.classes"
                  :colspan="row.colspan"
                >
                  {{ row.formatter(value.value) }}
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { variantDetailsStore } from '@variants/stores/variantDetails'

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore()
    return {
      detailsStore,
    }
  },
}
</script>
