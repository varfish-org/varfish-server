<script setup>
import { onMounted, watch, computed, ref } from 'vue'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpCriteriaDefinitions = () => {
  const result = {
    genotype_criteria: props.querySettings.genotype_criteria,
  }
  return JSON.stringify(result)
}

const selectedCriteriaDefNo = ref(null)
const criteriaDefLabels = computed(() => {
  if (!props.querySettings.genotype_criteria) {
    return []
  }
  return props.querySettings.genotype_criteria.map((def) => {
    const tokens = [def.genotype]
    if (def.select_sv_min_size !== null && def.select_sv_max_size === null) {
      tokens.push(`>=${def.select_sv_min_size}bp`)
    } else if (
      def.select_sv_min_size === null &&
      def.select_sv_max_size !== null
    ) {
      tokens.push(`<=${def.select_sv_max_size}bp`)
    } else if (
      def.select_sv_min_size !== null &&
      def.select_sv_max_size !== null
    ) {
      tokens.push(`${def.select_sv_min_size}-${def.select_sv_max_size}bp`)
    }
    if (def.select_sv_sub_type && def.select_sv_sub_type.length) {
      tokens.push(def.select_sv_sub_type.join('/'))
    }
    return tokens.join(' ')
  })
})
const criteriaDefs = computed(() => {
  return props.querySettings.genotype_criteria ?? []
})

const selectedCriteriaDef = computed(() => {
  if (selectedCriteriaDefNo.value !== null) {
    return criteriaDefs.value[selectedCriteriaDefNo.value]
  } else {
    return {}
  }
})

const initSelectedCriteriaDef = () => {
  if (props.querySettings.genotype_criteria?.length) {
    if (
      !selectedCriteriaDefNo.value ||
      !(selectedCriteriaDefNo.value in criteriaDefs.value)
    ) {
      selectedCriteriaDefNo.value = 0
    }
  }
}

watch(
  () => props.querySettings.genotype_criteria,
  (newValue, _oldValue) => initSelectedCriteriaDef(),
)
onMounted(() => initSelectedCriteriaDef())
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2 mb-0"
  >
    <i-mdi-information />

    You can define filter criteria in this pane. These can then be used in the
    &quot;Matches&quot; pane.
  </div>
  <div class="input-group p-2">
    <div class="input-group-prepend">
      <span class="input-group-text"> Genotype Criteria Definition </span>
    </div>
    <select v-model="selectedCriteriaDefNo" class="custom-select">
      <option v-for="(label, key) in criteriaDefLabels" :value="key">
        {{ label }}
      </option>
    </select>
  </div>
  <div class="p-2">
    comment {{ selectedCriteriaDef.comment ?? '-' }}
    <br />
    select_sv_min_size {{ selectedCriteriaDef.select_sv_min_size ?? '-' }}
    <br />
    select_sv_max_size {{ selectedCriteriaDef.select_sv_max_size ?? '-' }}
    <br />
    select_sv_sub_type {{ selectedCriteriaDef.select_sv_sub_type ?? '-' }}
  </div>
  <div class="p-2">
    max_brk_segdup {{ selectedCriteriaDef.max_brk_segdup ?? '-' }}
    <br />
    max_brk_repeat {{ selectedCriteriaDef.max_brk_repeat ?? '-' }}
    <br />
    max_brk_segduprepeat {{ selectedCriteriaDef.max_brk_segduprepeat ?? '-' }}
    <br />
    gt_one_of {{ selectedCriteriaDef.gt_one_of ?? '-' }}
    <br />
    min_gq {{ selectedCriteriaDef.min_gq ?? '-' }}
    <br />
    min_pr_cov {{ selectedCriteriaDef.min_pr_cov ?? '-' }}
    <br />
    max_pr_cov {{ selectedCriteriaDef.max_pr_cov ?? '-' }}
    <br />
    min_pr_ref {{ selectedCriteriaDef.min_pr_ref ?? '-' }}
    <br />
    max_pr_ref {{ selectedCriteriaDef.max_pr_ref ?? '-' }}
    <br />
    min_pr_var {{ selectedCriteriaDef.min_pr_var ?? '-' }}
    <br />
    max_pr_var {{ selectedCriteriaDef.max_pr_var ?? '-' }}
    <br />
    min_sr_cov {{ selectedCriteriaDef.min_sr_cov ?? '-' }}
    <br />
    max_sr_cov {{ selectedCriteriaDef.max_sr_cov ?? '-' }}
    <br />
    min_sr_ref {{ selectedCriteriaDef.min_sr_ref ?? '-' }}
    <br />
    max_sr_ref {{ selectedCriteriaDef.max_sr_ref ?? '-' }}
    <br />
    min_sr_var {{ selectedCriteriaDef.min_sr_var ?? '-' }}
    <br />
    max_sr_var {{ selectedCriteriaDef.max_sr_var ?? '-' }}
    <br />
    min_srpr_cov {{ selectedCriteriaDef.min_srpr_cov ?? '-' }}
    <br />
    max_srpr_cov {{ selectedCriteriaDef.max_srpr_cov ?? '-' }}
    <br />
    min_srpr_ref {{ selectedCriteriaDef.min_srpr_ref ?? '-' }}
    <br />
    max_srpr_ref {{ selectedCriteriaDef.max_srpr_ref ?? '-' }}
    <br />
    min_srpr_var {{ selectedCriteriaDef.min_srpr_var ?? '-' }}
    <br />
    max_srpr_var {{ selectedCriteriaDef.max_srpr_var ?? '-' }}
    <br />
    min_rd_dev {{ selectedCriteriaDef.min_rd_dev ?? '-' }}
    <br />
    max_rd_dev {{ selectedCriteriaDef.max_rd_dev ?? '-' }}
    <br />
    min_amq {{ selectedCriteriaDef.min_amq ?? '-' }}
    <br />
    max_amq {{ selectedCriteriaDef.max_amq ?? '-' }}
    <br />
    missing_gt_ok {{ selectedCriteriaDef.missing_gt_ok ?? '-' }}
    <br />
    missing_gq_ok {{ selectedCriteriaDef.missing_gq_ok ?? '-' }}
    <br />
    missing_pr_ok {{ selectedCriteriaDef.missing_pr_ok ?? '-' }}
    <br />
    missing_sr_ok {{ selectedCriteriaDef.missing_sr_ok ?? '-' }}
    <br />
    missing_srpr_ok {{ selectedCriteriaDef.missing_srpr_ok ?? '-' }}
    <br />
    missing_rd_dev_ok {{ selectedCriteriaDef.missing_rd_dev_ok ?? '-' }}
    <br />
    missing_amq_ok {{ selectedCriteriaDef.missing_amq_ok ?? '-' }}
  </div>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpCriteriaDefinitions() }}
    </code>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
