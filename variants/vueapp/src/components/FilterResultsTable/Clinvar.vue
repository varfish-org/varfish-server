<script setup>
// eslint-disable-next-line no-unused-vars
const props = defineProps({
  params: Object,
})

const getClinvarSignificanceBadge = (patho) => {
  if (patho === 'pathogenic') {
    return 'badge-danger'
  } else if (patho === 'likely pathogenic') {
    return 'badge-warning'
  } else if (patho === 'uncertain significance') {
    return 'badge-info'
  } else if (patho === 'likely benign') {
    return 'badge-secondary'
  } else if (patho === 'benign') {
    return 'badge-secondary'
  }
  return 'badge-secondary'
}
</script>

<template>
  <span class="badge-group" v-if="params.data.summary_pathogenicity_label">
    <span
      class="badge"
      :class="
        getClinvarSignificanceBadge(params.data.summary_pathogenicity_label)
      "
    >
      {{ params.data.summary_pathogenicity_label }}
    </span>
    <span
      class="badge badge-dark"
      :title="params.data.summary_review_status_label"
    >
      <i-fa-solid-star v-for="i in params.data.summary_gold_stars" :key="i" />
      <i-fa-regular-star
        v-for="j in 4 - params.data.summary_gold_stars"
        :key="j"
      />
    </span>
  </span>
  <span v-else class="badge badge-light">-</span>
</template>

<style>
.badge-group {
  padding: 2px;
  display: inline-flex;
}

.badge-group > .badge:not(:first-child):not(:last-child) {
  border-radius: 0;
  margin-left: 0;
  margin-right: 0;
}

.badge-group > .badge:first-child {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  margin-right: 0;
}

.badge-group > .badge:last-child {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  margin-left: 0;
}
</style>
