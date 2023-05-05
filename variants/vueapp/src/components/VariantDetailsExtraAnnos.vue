<script setup>
const props = defineProps({
  extraAnnos: Object,
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Extra Annotations</h4>
    </div>
    <table
      v-if="props.extraAnnos"
      class="card-body table table-striped table-sm"
    >
      <thead>
        <tr>
          <th class="text-center">Score</th>
          <th class="text-center">Value</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="(value, name, index) in props.extraAnnos.annotations"
          :key="index"
        >
          <th class="text-center">{{ name }}</th>
          <td class="text-center">{{ value }}</td>
        </tr>
      </tbody>
    </table>
    <div v-else class="card-body text-center font-italic pb-2 text-muted">
      No extra annotations available.
    </div>
  </div>
</template>
