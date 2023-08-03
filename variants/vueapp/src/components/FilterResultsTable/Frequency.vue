<script setup>
import { useVariantQueryStore } from '@variants/stores/variantQuery'

const store = useVariantQueryStore()

// eslint-disable-next-line no-unused-vars
const props = defineProps({
  params: Object,
})

const displayAmbiguousFrequencyWarning = (item) => {
  const tables = [
    'exac',
    'thousand_genomes',
    'gnomad_exomes',
    'gnomad_genomes',
    'inhouse',
  ]
  let ambiguousTables = []
  for (const table of tables) {
    const hom_field =
      table === 'inhouse' ? 'inhouse_hom_alt' : table + '_homozygous'
    if (
      item[hom_field] > 50 ||
      (table !== 'inhouse' && item[table + '_frequency'] > 0.1)
    ) {
      ambiguousTables.push(table)
    }
  }
  return ambiguousTables
}

const displayAmbiguousFrequencyWarningMsg = (item) => {
  const tables = displayAmbiguousFrequencyWarning(item)
  const tablesStr = tables.join(' ')
  return `Table(s) {tablesStr} contain(s) freq > 0.1 or #hom > 50`
}

const formatFreq = (value) => {
  return parseFloat(value).toFixed(5)
}
</script>

<template>
  <span>
    {{ formatFreq(props.params.value) }}
    <i-bi-exclamation-circle
      class="text-muted"
      v-if="displayAmbiguousFrequencyWarning(props.params.data).length > 0"
      :title="displayAmbiguousFrequencyWarningMsg(props.params.data)"
    />
  </span>
</template>

<style></style>
