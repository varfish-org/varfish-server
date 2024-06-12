<script setup>
/** Editor component for quick presets.
 */

import { randomString } from '@/varfish/common'

/** Define props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  presetSet: Object,
  // eslint-disable-next-line vue/require-default-prop
  querySettings: Object,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})
</script>

<template>
  <!-- eslint-disable -->
  <div v-if="querySettings" class="mr-2 mt-2">
    <div class="form-group">
      <label :for="'inheritance' + idSuffix"> Inheritance </label>
      <select
        :id="'inheritance' + idSuffix"
        v-model="querySettings.inheritance"
        class="custom-select"
      >
        <option value="de_novo">de novo</option>
        <option value="dominant">dominant</option>
        <option value="homozygous_recessive">homozygous recessive</option>
        <option value="compound_heterozygous">compound heterozygous</option>
        <option value="recessive">recessive</option>
        <option value="x_recessive">X-recessive</option>
        <option value="affected_carriers">affected carriers</option>
        <option value="any">any</option>
      </select>
      <small class="form-text text-muted">
        The inheritance hypothesis to use for genotype settings.
      </small>
    </div>

    <div class="form-group">
      <label :for="'frequency' + idSuffix"> Frequency Presets </label>
      <select
        :id="'frequency' + idSuffix"
        v-model="querySettings.frequency"
        class="custom-select"
      >
        <template v-if="presetSet">
          <option
            v-for="presets in presetSet.frequencypresets_set"
            :value="presets.sodar_uuid"
          >
            {{ presets.label }}
          </option>
        </template>
      </select>
      <small class="form-text text-muted">
        The frequency presets to use.
      </small>
    </div>

    <div class="form-group">
      <label :for="'impact' + idSuffix"> Variant Effect Presets </label>
      <select
        :id="'impact' + idSuffix"
        v-model="querySettings.impact"
        class="custom-select"
      >
        <template v-if="presetSet">
          <option
            v-for="presets in presetSet.impactpresets_set"
            :value="presets.sodar_uuid"
          >
            {{ presets.label }}
          </option>
        </template>
      </select>
      <small class="form-text text-muted">
        The variant effect presets to use.
      </small>
    </div>

    <div class="form-group">
      <label :for="'quality' + idSuffix"> Quality </label>
      <select
        :id="'quality' + idSuffix"
        v-model="querySettings.quality"
        class="custom-select"
      >
        <template v-if="presetSet">
          <option
            v-for="presets in presetSet.qualitypresets_set"
            :value="presets.sodar_uuid"
          >
            {{ presets.label }}
          </option>
        </template>
      </select>
      <small class="form-text text-muted"> The quality presets to use. </small>
    </div>

    <div class="form-group">
      <label :for="'chromosome' + idSuffix"> Genes &amp; Regions </label>
      <select
        :id="'chromosome' + idSuffix"
        v-model="querySettings.chromosome"
        class="custom-select"
      >
        <template v-if="presetSet">
          <option
            v-for="presets in presetSet.chromosomepresets_set"
            :value="presets.sodar_uuid"
          >
            {{ presets.label }}
          </option>
        </template>
      </select>
      <small class="form-text text-muted">
        The genes &amp; regions presets to use.
      </small>
    </div>

    <div class="form-group">
      <label :for="'flagsetc' + idSuffix"> Flags etc. &amp; ClinVar </label>
      <select
        :id="'flagsetc' + idSuffix"
        v-model="querySettings.flagsetc"
        class="custom-select"
      >
        <template v-if="presetSet">
          <option
            v-for="presets in presetSet.flagsetcpresets_set"
            :value="presets.sodar_uuid"
          >
            {{ presets.label }}
          </option>
        </template>
      </select>
      <small class="form-text text-muted">
        The frequency presets to use.
      </small>
    </div>
  </div>
  <!-- eslint-enable -->
</template>
