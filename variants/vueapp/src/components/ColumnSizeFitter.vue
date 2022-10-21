<script setup>
const props = defineProps({ gridApi: Object, columnApi: Object })

const sizeToFit = () => {
  if (props.gridApi) {
    props.gridApi.sizeColumnsToFit()
  }
}

const autoSizeAll = () => {
  if (!props.columnApi) {
    return
  }

  const allColumnIds = props.columnApi
    .getColumns()
    .map((column) => column.getId())
  props.columnApi.autoSizeColumns(allColumnIds)
}
</script>

<template>
  <div class="pr-3 align-self-start column-size-fitter">
    <label for="columnSizeFitter" class="font-weight-bold small mb-0">
      Resize Cols
    </label>
    <br />
    <div class="btn-group" id="columnSizeFitter">
      <button @click="sizeToFit" class="btn btn-sm btn-outline-secondary">
        <i-mdi-table-column-width />
      </button>
      <button @click="autoSizeAll" class="btn btn-sm btn-outline-secondary">
        <i-mdi-table-merge-cells />
      </button>
    </div>
  </div>
</template>

<style>
.column-size-fitter .btn {
  height: calc(1.5em + 0.5rem + 2px);
}
</style>
