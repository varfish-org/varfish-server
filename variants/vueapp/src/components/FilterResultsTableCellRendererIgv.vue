<script setup>
const props = defineProps({
  params: Object,
})

const goToLocus = async () => {
  const chrPrefixed = props.params.data.chromosome.startsWith('chr')
    ? props.params.data.chromosome
    : `chr${props.params.data.chromosome}`
  await fetch(
    `http://127.0.0.1:60151/goto?locus=${chrPrefixed}:${props.params.data.start}-${props.params.data.end}`
  ).catch((e) => {
    console.error('IGV not available')
  })
}
const mtLink =
  props.params.data.release === 'GRCh37'
    ? `https://www.genecascade.org/MTc2021/ChrPos102.cgi?chromosome=${props.params.data.chromosome}&position=${props.params.data.start}&ref=${props.params.data.reference}&alt=${props.params.data.alternative}`
    : '#'
</script>

<template>
  <div class="btn-group btn-group-sm">
    <a
      :href="mtLink"
      target="_blank"
      style="font-size: 80%"
      class="btn btn-sm btn-outline-secondary"
      :class="mtLink === '#' ? 'disabled' : ''"
    >
      MT
    </a>
    <button
      @click="goToLocus()"
      type="button"
      title="Go to locus in IGV"
      style="font-size: 80%"
      class="btn btn-sm btn-secondary"
    >
      IGV
    </button>
  </div>
</template>
