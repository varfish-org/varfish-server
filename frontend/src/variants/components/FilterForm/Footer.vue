<script setup>
import { computed } from 'vue'
import { declareWrapper } from '@/variants/helpers'
import { QueryStates } from '@/variants/enums'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

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
    QueryStates.Fetching.value,
    QueryStates.Running.value,
    QueryStates.Resuming.value,
  ].includes(props.queryState)
})

const filterButtonText = computed(() => {
  return props.queryState === QueryStates.Running.value ||
    props.queryState === QueryStates.Fetching.value ||
    props.queryState === QueryStates.Resuming.value
    ? 'Cancel'
    : 'Filter & Display'
})

const filterButtonColor = computed(() => {
  let color
  if (
    props.queryState === QueryStates.Running.value ||
    props.queryState === QueryStates.Fetching.value ||
    props.queryState === QueryStates.Resuming.value
  ) {
    color = 'btn-warning'
  } else {
    color = 'btn-primary'
  }
  if (props.anyHasError) {
    color = 'btn-danger'
  }
  return color
})

const variantQueryStore = useVariantQueryStore()

const devStoreState = () => {
  return {
    storeState: variantQueryStore.storeState,
    queryState: variantQueryStore.queryState,
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
        <button
          id="submitFilter"
          type="button"
          class="btn"
          :disabled="anyHasError"
          :class="filterButtonColor"
          title="Filter variants with current settings"
          @click="emit('submitCancelButtonClick')"
        >
          <i-mdi-refresh :class="{ spin: spinButtonIcon }" />
          {{ filterButtonText }}
        </button>
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
