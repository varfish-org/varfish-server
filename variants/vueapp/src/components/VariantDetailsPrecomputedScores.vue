<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  varAnnos: any,
}>()

const bestOf = (obj: any, keys: string[]) => {
  const values = keys.map((key) => ({score: obj[key] ?? null, key})).filter(({score}) => score !== null)
  if (values.length) {
    values.sort((a, b) => b.score - a.score)
    return values[0]
  } else {
    return {
      score: null,
      which: null,
    }
  }
}

const bestSpliceAi = computed(() => {
  const keys = [
    "SpliceAI-acc-gain",
    "SpliceAi-acc-loss",
    "SpliceAi-don-gain",
    "SpliceAi-don-loss",
  ]
  return bestOf(props.varAnnos.cadd, keys)
})

const bestMMSplice = computed(() => {
  const keys = [
    "MMSp_acceptorIntron",
    "MMSp_acceptor",
    "MMSp_exon",
    "MMSp_donor",
    "MMSp_donorIntron",
  ]
  return bestOf(props.varAnnos.cadd, keys)
})

const decodeMultiDbnsfp = (s: string): string => {
  if (!s) {
    return ""
  } else {
    return Math.max(...(s.split(";").filter((s) => s != ".").map(parseFloat)))
  }
}
</script>

<template>
  <div>
    <div>
      <strong>SIFT:</strong>
      {{ decodeMultiDbnsfp(props.varAnnos.dbnsfp["SIFT_score"]) }}
    </div>
    <div>
      <strong>BayesDel:</strong>
      {{ props.varAnnos.dbnsfp["BayesDel_addAF_score"] }}
    </div>
    <div>
      <strong>FATHMM:</strong>
      {{ props.varAnnos.dbnsfp["FATHMM_score"] }}
    </div>
    <div>
      <strong>Gerp++NR:</strong>
      {{ props.varAnnos.dbnsfp["GERP++_NR"] }}
    </div>
    <div>
      <strong>Gerp++RS:</strong>
      {{ props.varAnnos.dbnsfp["GERP++_RS"] }}
    </div>
    <div>
      <strong>MPC:</strong>
      {{ decodeMultiDbnsfp(props.varAnnos.dbnsfp["MPC_score"]) }}
    </div>
    <div>
      <strong>MutPred:</strong>
      {{ decodeMultiDbnsfp(props.varAnnos.dbnsfp["MutPred_score"]) }}
    </div>
    <div>
      <strong>phyloP100way_vertebrate:</strong>
      {{ props.varAnnos.dbnsfp["phyloP100way_vertebrate"] }}
    </div>
    <div>
      <strong>phyloP470way_mammalian:</strong>
      {{ props.varAnnos.dbnsfp["phyloP470way_mammalian"] }}
    </div>
    <div>
      <strong>phyloP17way_primate:</strong>
      {{ props.varAnnos.dbnsfp["phyloP17way_primate"] }}
    </div>
    <div>
      <strong>PrimateAI_score:</strong>
      {{ props.varAnnos.dbnsfp["PrimateAI_score"] }}
    </div>
    <div>
      <strong>VEST4:</strong>
      {{ decodeMultiDbnsfp(props.varAnnos.dbnsfp["VEST4_score"]) }}
    </div>

    <div>
      <strong>SpliceAI:</strong>
      &nbsp;
      <span v-if="bestSpliceAi.key">
        {{ bestSpliceAi.score }} <span class="text-muted">({{ bestSpliceAi.key }})</span>
      </span>
      <span v-else class="text-muted">
        not available
      </span>
    </div>

    <div>
      <strong>MMSplice:</strong>
      &nbsp;
      <span v-if="bestMMSplice.key !== null">
        {{ bestMMSplice.score }} <span class="text-muted">({{ bestMMSplice.key }})</span>
      </span>
      <span v-else class="text-muted">
        not available
      </span>
    </div>

    <div>
      <strong>CADD:</strong>
      &nbsp;
      <span v-if="'PHRED' in (varAnnos.cadd ?? {})">
        {{ varAnnos.cadd["PHRED"] }}
      </span>
      <span v-else class="text-muted">
        not available
      </span>
    </div>

    <div>
      <strong>REVEL:</strong>
      &nbsp;
      <span v-if="'REVEL_score' in (varAnnos.dbnsfp ?? {})">
        {{ decodeMultiDbnsfp(varAnnos.dbnsfp["REVEL_score"]) }}
      </span>
      <span v-else class="text-muted">
        not available
      </span>
    </div>
  </div>
</template>
