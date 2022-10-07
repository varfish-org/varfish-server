<template>
  <span class="badge-group" v-if="params.data.summary_pathogenicity_label">
    <span
      class="badge"
      :class="
        store.getClinvarSignificanceBadge(
          params.data.summary_pathogenicity_label
        )
      "
    >
      {{ params.data.summary_pathogenicity_label }}
    </span>
    <span
      class="badge badge-dark"
      :title="params.data.summary_review_status_label"
    >
      <i
        v-for="i in params.data.summary_gold_stars"
        :key="i"
        class="iconify"
        data-icon="fa-solid:star"
      ></i>
      <i
        v-for="j in 4 - params.data.summary_gold_stars"
        :key="j"
        class="iconify"
        data-icon="fa-regular:star"
      ></i>
    </span>
  </span>
  <span v-else class="badge badge-light">- </span>
</template>
<script>
import { filterQueryStore } from '@variants/stores/filterQuery'

export default {
  setup() {
    const store = filterQueryStore()
    return {
      store,
    }
  },
}
</script>
