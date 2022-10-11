<script setup>
const props = defineProps({
  knownGeneAa: Object,
})
</script>

<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">UCSC 100 Vertebrate Conservation</h4>
    </div>
    <div class="card-body">
      <pre
        v-if="props.knownGeneAa.length > 0"
      ><b><u>  chr  start      end          |  alignment                                                                                           </u></b>
<template v-for="(row, index) in props.knownGeneAa" :key="index">{{ row.chromosome.padStart(5) }} {{ row.start.toLocaleString().padStart(11) }}-{{ row.end.toLocaleString().padEnd(11) }}  |  {{ row.alignment }}
</template></pre>
      <p v-else class="text-muted text-center">
        <i>No conservation information available.</i>
      </p>
    </div>
  </div>
</template>
