<template>
  <div>
    <i
      class="iconify"
      :class="
        params.data.acmg_symbol != null
          ? 'text-danger'
          : 'text-muted iconInactive'
      "
      data-icon="fa-solid:user-md"
      title="Gene on ACMG incidental findings list"
    ></i>
    <i
      class="iconify ml-1"
      :class="diseaseGene ? 'text-danger' : 'text-muted iconInactive'"
      :data-icon="diseaseGene ? 'fa-solid:lightbulb' : 'fa-regular:lightbulb'"
      title="Disease Gene"
    ></i>
    <span v-if="params.data.modes_of_inheritance">
      <span
        v-for="(mode, index) in params.data.modes_of_inheritance.sort()"
        :key="index"
        class="badge badge-info ml-1"
        >{{ mode }}</span
      >
    </span>
  </div>
</template>
<script>
import { filterQueryStore } from "@/stores/filterQuery";

export default {
  setup(props) {
    const store = filterQueryStore();
    const diseaseGene = JSON.parse(
      props.params.data.disease_gene.toLowerCase()
    );
    return {
      diseaseGene,
      store,
    };
  },
};
</script>

<style scoped>
.iconInactive {
  opacity: 20%;
}
</style>
