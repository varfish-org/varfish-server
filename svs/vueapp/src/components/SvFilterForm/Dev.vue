<script setup>
import { computed, onMounted, ref } from 'vue'

// Define the component's props.
const props = defineProps({
  querySettings: Object,
})

const rawFilterCriteriaRef = ref(null)

const loadSettings = () => {
  rawFilterCriteriaRef.value.value = JSON.stringify(
    props.querySettings.genotype_criteria,
    null,
    2,
  )
}

const applySettings = () => {
  props.querySettings.genotype_criteria = JSON.parse(
    rawFilterCriteriaRef.value.value,
  )
}
</script>

<template>
  <div class="row">
    <div class="col mt-2 mb-2">
      <div class="form-group">
        <label for="raw-filter-criteria-ref">Raw Filter Criteria</label>
        <textarea
          ref="rawFilterCriteriaRef"
          id="raw-filter-criteria-ref"
          class="form-control"
          rows="5"
        ></textarea>
      </div>

      <div class="mt-2">
        <button class="btn btn-primary" @click.prevent="loadSettings()">
          <i-mdi-download />
          Fetch Criteria
        </button>

        <button class="btn btn-primary ml-2" @click.prevent="applySettings()">
          <i-mdi-upload />
          Apply Criteria
        </button>
      </div>
    </div>
  </div>
</template>
