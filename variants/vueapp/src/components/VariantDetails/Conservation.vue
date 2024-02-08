<script setup lang="ts">
import { computed, ref, watch, onMounted } from 'vue'
import { separateIt as sepIt } from '@varfish/moreUtils'

const props = defineProps<{
  varAnnos: any
}>()

/** Return the conservation records. */
const ucscConservation = computed(() => {
  if (props.varAnnos?.ucsc_conservation?.length) {
    return props.varAnnos?.ucsc_conservation[0].records
  } else {
    return []
  }
})

const transcriptIds = computed(() => {
  let res: string[] = ucscConservation.value.map(({ enstId }) => enstId)
  res = [...new Set(res)]
  res.sort()
  return res
})

const consInfo = computed(() => {
  let seen = new Set()
  let res = {}
  for (const {
    chrom,
    enstId,
    start,
    stop,
    alignment,
  } of ucscConservation.value) {
    const key = `${enstId}-${chrom}-${enstId}-${start}-${stop}`
    if (!seen.has(key)) {
      seen.add(key)
      if (!(enstId in res)) {
        res[enstId] = []
      }
      res[enstId].push({ chrom, start, stop, alignment })
    }
  }

  for (const key in res) {
    res[key].sort((a, b) => a.start - b.start)
  }

  return res
})

const selectedTranscript = ref(null)

const initSelectedTranscript = () => {
  if (transcriptIds.value?.length) {
    if (
      !selectedTranscript.value ||
      (transcriptIds.value || []).includes(selectedTranscript.value)
    ) {
      selectedTranscript.value = transcriptIds.value[0]
    }
  }
}

watch(() => props.varAnnos, initSelectedTranscript)
onMounted(initSelectedTranscript)
</script>

<template>
  <div class="m-2">
    <div v-if="ucscConservation">
      <div class="float-right">
        <select
          v-model="selectedTranscript"
          class="form-control custom-select custom-select-sm"
        >
          <option v-for="transcript in transcriptIds" :value="transcript">
            {{ transcript }}
          </option>
        </select>
      </div>
      <p>The following shows UCSC 100 vertebrate conservation.</p>
      <pre><b><u>  chr  start      end          |  alignment                                                                                           </u></b>
<template v-for="row in consInfo[selectedTranscript]">{{ row.chrom.padStart(5) }} {{ sepIt(row.start, ',').padStart(11) }}-{{ sepIt(row.stop, ',').padEnd(11) }}  |  {{ row.alignment }}
</template></pre>
    </div>
    <div v-else class="text-muted text-center font-italic"></div>
  </div>
  <!-- <div class="card">
    <div class="card-header">
      <h4 class="card-title">UCSC 100 Vertebrate Conservation</h4>
    </div>
    <div class="card-body">
      <pre
        v-if="props.knownGeneAa.length > 0"
      ><b><u>  chr  start      end          |  alignment                                                                                           </u></b>
<template v-for="(row, index) in props.knownGeneAa" :key="index">{{ row.chrom.padStart(5) }} {{ row.start.toLocaleString().padStart(11) }}-{{ row.end.toLocaleString().padEnd(11) }}  |  {{ row.alignment }}
</template></pre>
      <p v-else class="text-muted text-center">
        <i>No conservation information available.</i>
      </p>
    </div>
  </div> -->
</template>
