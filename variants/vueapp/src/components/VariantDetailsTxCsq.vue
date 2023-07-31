<script setup lang="ts">
const props = defineProps<{ txCsq: any }>()
</script>

<template>
  <div class="table-responsive" style="font-size: 90%">
    <table class="table table-hover">
      <thead>
        <tr>
          <th>Gene</th>
          <th>Transcript</th>
          <th>Consequence</th>
          <th>HGVS.p</th>
          <th>HGVS.t</th>
          <th>Rank</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="txCsq in props.txCsq">
          <td>{{ txCsq['gene-symbol'] }}</td>
          <td>
            {{ txCsq['feature-id'] }}
            ({{ txCsq['feature-biotype'] }})
          </td>
          <td>{{ (txCsq['consequences'] ?? []).join(', ') }}</td>
          <td>{{ txCsq['hgvs-t'] }}</td>
          <td>{{ txCsq['hgvs-p'] }}</td>
          <td>{{ txCsq['rank'].ord }} / {{ txCsq['rank'].total }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
