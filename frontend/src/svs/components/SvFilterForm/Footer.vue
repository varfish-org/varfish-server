<script setup>
import { computed } from 'vue'

import { useSvQueryStore } from '@/svs/stores/svQuery'
import { QueryStates } from '@/variants/enums'
import { declareWrapper } from '@/variants/helpers'

const props = defineProps({
  filtrationComplexityMode: String,
  queryState: String,
  anyHasError: Boolean,
  database: String,
})

const emit = defineEmits([
  'submitCancelButtonClick',
  'anyHasError',
  // emits for v-model updates
  'update:database',
])

const databaseWrapper = declareWrapper(props, 'database', emit)

const spinButtonIcon = computed(() => {
  return [
    QueryStates.Initial.value,
    QueryStates.Fetching.value,
    QueryStates.Running.value,
    QueryStates.Resuming.value,
  ].includes(props.queryState)
})

const showError = computed(() => {
  return props.anyHasError
})

const svQueryStore = useSvQueryStore()

const devStoreState = () => {
  return {
    storeState: svQueryStore.storeState,
    queryState: svQueryStore.queryState,
  }
}
</script>

<template>
  <div class="card-footer">
    <div class="row">
      <div class="col-auto p-0">
        <div class="btn-group btn-group-toggle pr-5" data-toggle="buttons">
          <label
            class="btn btn-outline-secondary active"
            title="Select RefSeq transcripts"
            for="id_database_selector_refseq"
          >
            <input
              id="id_database_selector_refseq"
              v-model="databaseWrapper"
              name="databaseSelect"
              type="radio"
              value="refseq"
              required
            />
            RefSeq
          </label>
          <label
            class="btn btn-outline-secondary"
            title="Select EnsEMBL transcripts"
            for="id_database_selector_ensembl"
          >
            <input
              id="id_database_selector_ensembl"
              v-model="databaseWrapper"
              name="databaseSelect"
              type="radio"
              value="ensembl"
              required
            />
            EnsEMBL
          </label>
        </div>
      </div>
      <div v-if="filtrationComplexityMode === 'dev'">
        <code>{{ devStoreState() }}</code>
      </div>
      <div class="ml-auto col-auto p-0">
        <small v-if="anyHasError" class="text-danger">
          <br />You must fix the errors before you can filter.
        </small>
        <div class="btn-group">
          <button
            id="submitFilter"
            type="button"
            name="submit"
            :disabled="anyHasError"
            class="btn"
            :class="{ 'btn-primary': !showError, 'btn-danger': showError }"
            title="Filter variants with current settings"
            @click="emit('submitCancelButtonClick')"
          >
            <i-mdi-refresh :class="{ spin: spinButtonIcon }" />
            Filter &amp; Display
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.spin {
  animation-name: spin;
  animation-duration: 2000ms;
  animation-iteration-count: infinite;
  animation-timing-function: linear;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
