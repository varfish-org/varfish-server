<script setup>
import { computed, onMounted, ref } from 'vue'

import { QueryStates } from '@/variants/enums'
import { declareWrapper } from '@/variants/helpers'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const props = defineProps({
  filtrationComplexityMode: String,
  queryState: String,
  anyHasError: Boolean,
  database: String,
  hasAnyChanges: Boolean,
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

const getChanges = computed(() => {
  if (
    !variantQueryStore.lastSubmittedQuerySettings ||
    !variantQueryStore.querySettings
  ) {
    return []
  }

  const changes = []
  const current = variantQueryStore.querySettings
  const previous = variantQueryStore.lastSubmittedQuerySettings

  const formatValue = (val) => {
    if (val === null || val === undefined) return 'null'
    if (typeof val === 'object') return JSON.stringify(val, null, 2)
    if (typeof val === 'boolean') return val ? 'true' : 'false'
    return String(val)
  }

  const allKeys = new Set([...Object.keys(current), ...Object.keys(previous)])

  for (const key of allKeys) {
    const currentVal = current[key]
    const previousVal = previous[key]

    if (JSON.stringify(currentVal) !== JSON.stringify(previousVal)) {
      changes.push({
        field: key,
        previous: formatValue(previousVal),
        current: formatValue(currentVal),
      })
    }
  }

  return changes
})

const restorePreviousSettings = () => {
  if (variantQueryStore.lastSubmittedQuerySettings) {
    // Deep copy each property to maintain reactivity and trigger watchers
    const previousSettings = JSON.parse(
      JSON.stringify(variantQueryStore.lastSubmittedQuerySettings),
    )

    // Clear existing settings and copy all properties
    for (const key in variantQueryStore.querySettings) {
      delete variantQueryStore.querySettings[key]
    }
    for (const key in previousSettings) {
      variantQueryStore.querySettings[key] = previousSettings[key]
    }
  }
}

onMounted(() => {
  // Ensure Bootstrap modal is initialized
  if (typeof window !== 'undefined' && window.$ && window.$.fn.modal) {
    window.$('#changesModal').modal({ show: false })
  }
})
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
      <div class="ml-auto col-auto p-0 d-flex align-items-center">
        <div v-if="hasAnyChanges" class="mr-3 change-indicator">
          <div class="d-flex gap-1">
            <button
              type="button"
              class="btn btn-xs btn-info ml-2"
              title="View changes"
              data-toggle="modal"
              data-target="#changesModal"
            >
              <i-mdi-format-list-bulleted />
            </button>
          </div>
          <span class="tooltip-text"
            >Settings modified after query submitted.<br />
            Click <i-mdi-format-list-bulleted /> to show differences and restore
            if needed.
          </span>
        </div>
        <div>
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
  </div>

  <!-- Changes Modal -->
  <div
    id="changesModal"
    class="modal fade"
    tabindex="-1"
    role="dialog"
    aria-labelledby="changesModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog modal-lg" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 id="changesModalLabel" class="modal-title">Changed Settings</h5>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body" style="max-height: 60vh; overflow-y: auto">
          <div v-if="getChanges.length === 0" class="alert alert-info">
            No changes detected.
          </div>
          <div v-else>
            <table class="table table-sm table-bordered">
              <thead>
                <tr>
                  <th style="width: 30%">Field</th>
                  <th style="width: 35%">Previous Value</th>
                  <th style="width: 35%">Current Value</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="change in getChanges" :key="change.field">
                  <td class="font-weight-bold">{{ change.field }}</td>
                  <td>
                    <pre class="mb-0" style="font-size: 0.85rem">{{
                      change.previous
                    }}</pre>
                  </td>
                  <td>
                    <pre class="mb-0" style="font-size: 0.85rem">{{
                      change.current
                    }}</pre>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-dismiss="modal">
            Close
          </button>
          <button
            type="button"
            class="btn btn-info"
            data-dismiss="modal"
            @click="restorePreviousSettings"
          >
            <i-mdi-undo-variant class="mr-1" />
            Restore Previous
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

.change-indicator {
  cursor: help;
  position: relative;
  display: inline-block;
}

.change-box {
  display: inline-flex;
  align-items: center;
  background-color: #d1ecf1;
  border: 1px solid #bee5eb;
  color: #0c5460;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.875rem;
}

.change-indicator .tooltip-text {
  visibility: hidden;
  width: 320px;
  background-color: #333;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px 12px;
  position: absolute;
  z-index: 1000;
  bottom: 125%;
  left: 50%;
  margin-left: -160px;
  opacity: 0;
  transition: opacity 0.3s;
  font-size: 0.75rem;
  white-space: normal;
  line-height: 1.4;
}

.change-indicator .tooltip-text::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}

.change-indicator:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}
</style>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
