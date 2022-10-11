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

defineExpose({
  sizeToFit,
  autoSizeAll,
})
</script>

<template>
  <label for="columnSizeFitter" class="small">Column Size</label>
  <div class="btn-group pl-2" id="columnSizeFitter">
    <button @click="sizeToFit" class="btn btn-outline-secondary">
      <i-mdi-table-column-width />
    </button>
    <button @click="autoSizeAll" class="btn btn-outline-secondary">
      <i-mdi-table-merge-cells />
    </button>
  </div>
</template>
