<script setup>
import VariantDetailsFlagsIndicator from '@/varfish/components/VariantDetails/FlagsIndicator.vue'
import {
  flagNames,
  flagValues,
  simpleFlags,
} from '@/variants/components/FilterForm/FlagsPane.fields'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})
</script>

<template>
  <div
    style="position: relative"
    class="p-2"
    v-if="querySettings !== null && querySettings !== undefined"
  >
    <div
      v-if="props.showFiltrationInlineHelp"
      class="alert alert-secondary small p-2 m-2 mb-0"
    >
      <p class="mb-1">
        <i-mdi-information />
        Use the settings below to filter your variants based on variant flagging
        and color-coding. For example, you could limit your query to flagged
        variants by removing all "empty" flag values.
      </p>
      <p class="mb-0 font-weight-bold">
        In most cases, you will want to keep all options checked here.
      </p>
    </div>

    <div class="form-group row">
      <label class="col-3 col-lg-2 col-form-label text-nowrap"> Flags </label>
      <div class="col-9 col-lg-10 col-form-label">
        <div
          v-for="flag in simpleFlags"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`effect-flags-${flag.id}`"
            v-model="props.querySettings[flag.id]"
            type="checkbox"
            class="custom-control-input"
          />
          <label class="custom-control-label" :for="`effect-flags-${flag.id}`">
            <i-fa-solid-star v-if="flag.id === 'flag_bookmarked'" />
            <i-fa-solid-flask v-if="flag.id === 'flag_for_validation'" />
            <i-fa-solid-heart v-if="flag.id === 'flag_candidate'" />
            <i-fa-solid-flag-checkered
              v-if="flag.id === 'flag_final_causative'"
            />
            <i-cil-link-broken
              v-if="flag.id === 'flag_no_disease_association'"
            />
            <i-fa-solid-thumbs-up v-if="flag.id === 'flag_segregates'" />
            <i-fa-solid-thumbs-down
              v-if="flag.id === 'flag_doesnt_segregate'"
            />
            <i-mdi-dice-5 v-if="flag.id === 'flag_incidental'" />
            {{ flag.label }}
          </label>
        </div>
      </div>
    </div>

    <div v-for="flagName in flagNames" class="form-group row">
      <label class="col-3 col-lg-2 col-form-label text-nowrap">
        {{ flagName.label }}
      </label>
      <div class="col-9 col-lg-10 col-form-label">
        <div
          v-for="flagValue in flagValues"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`effect-flags-${flagName.id}-${flagValue.id}`"
            v-model="props.querySettings[`${flagName.id}_${flagValue.id}`]"
            type="checkbox"
            class="custom-control-input"
          />
          <label
            class="custom-control-label"
            :for="`effect-flags-${flagName.id}-${flagValue.id}`"
          >
            <VariantDetailsFlagsIndicator :flag-state="flagValue.id" />
            {{ flagValue.label }}
          </label>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
