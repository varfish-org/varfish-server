<script setup>
import { computed } from 'vue'
import { declareWrapper } from '../helpers.js'
import { QueryStates } from '../enums.js'
import { useFilterQueryStore } from '@variants/stores/filterQuery.js'

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

const showError = computed(() => {
  return props.anyHasError
})

const filterQueryStore = useFilterQueryStore()

const devStoreState = () => {
  return {
    storeState: filterQueryStore.storeState,
    queryState: filterQueryStore.queryState,
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
              v-model="databaseWrapper"
              name="databaseSelect"
              type="radio"
              value="refseq"
              id="id_database_selector_refseq"
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
              v-model="databaseWrapper"
              name="databaseSelect"
              type="radio"
              value="ensembl"
              id="id_database_selector_ensembl"
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
            type="button"
            id="submitFilter"
            name="submit"
            class="btn"
            :class="{ 'btn-primary': !showError, 'btn-danger': showError }"
            @click="emit('submitCancelButtonClick')"
            title="Filter variants with current settings"
          >
            <i-mdi-refresh :class="{ spin: spinButtonIcon }" />
            Filter &amp; Display
          </button>
          <!--              <button-->
          <!--                class="btn btn-secondary dropdown-toggle"-->
          <!--                type="button"-->
          <!--                id="filterdisplayoptions"-->
          <!--                data-toggle="dropdown"-->
          <!--                aria-haspopup="true"-->
          <!--                aria-expanded="false"-->
          <!--              >-->
          <!--                <i-fa-solid-ellipsis-h />-->
          <!--              </button>-->
          <!--              <div-->
          <!--                class="dropdown-menu"-->
          <!--                aria-labelledby="filterdisplayoptions"-->
          <!--                style="z-index: 3000"-->
          <!--              >-->
          <!--                <button-->
          <!--                  type="submit"-->
          <!--                  name="submit"-->
          <!--                  value="download"-->
          <!--                  class="dropdown-item"-->
          <!--                  data-toggle="tooltip"-->
          <!--                  aria-haspopup="true"-->
          <!--                  aria-expanded="false"-->
          <!--                  data-html="true"-->
          <!--                  title="Create downloadable file in the background of <i><b>all</b></i> variants with current settings (ignoring result count limit)."-->
          <!--                >-->
          <!--                  <i-fa-solid-cloud-download-alt /-->
          <!--                  Download as File-->
          <!--                </button>-->
          <!--              </div>-->
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
