<script setup>
// eslint-disable-next-line no-unused-vars
const props = defineProps({
  params: Object,
})

const isOnAcmgList = props.params.data.acmg_symbol !== null
let isDiseaseGene =
  new String(props.params.data.disease_gene).toLowerCase() === 'true'

const sortedModesOfInheritance = () => {
  return Array.from(props.params.data.modes_of_inheritance).sort()
}
</script>

<template>
  <div>
    <i-fa-solid-user-md
      :class="{
        'text-danger': isOnAcmgList,
        'text-muted icon-inactive': !isOnAcmgList,
      }"
      title="Gene in ACMG incidental finding list"
    />
    <i-fa-solid-lightbulb
      v-if="isDiseaseGene"
      class="text-danger align-baseline"
      title="Known disease gene"
    />
    <i-fa-regular-lightbulb
      v-if="!isDiseaseGene"
      class="text-muted icon-inactive align-baseline"
      title="Not a known disease gene"
    />
    <span v-if="params.data.modes_of_inheritance">
      <span
        v-for="(mode, index) in sortedModesOfInheritance()"
        :key="index"
        class="badge badge-info ml-1"
        >{{ mode }}</span
      >
    </span>
  </div>
</template>

<style scoped>
.icon-inactive {
  opacity: 20%;
}
</style>
