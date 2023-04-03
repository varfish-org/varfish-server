<script setup>
import Multiselect from '@vueform/multiselect'
import {
  DisplayDetails,
  DisplayFrequencies,
  DisplayConstraints,
  DisplayColumns,
} from '@variants/enums'
import { computed } from 'vue'

const components = { Multiselect }

// We define two-way bound props here.  Internally, they are accessed through computed *Wrapper properties
// that perform the appropriate ag-grid calls to apply the changes.

const props = defineProps({
  // model props
  displayDetails: Number,
  displayFrequency: Number,
  displayConstraint: Number,
  displayColumns: Array,
  // props to control the ag-grid with
  columnApi: Object,
  // the defined extra anno fields
  extraAnnoFields: Array,
})

const emit = defineEmits([
  'update:displayDetails',
  'update:displayFrequency',
  'update:displayConstraint',
  'update:displayColumns',
])

// The static column options.
const staticColumnOptions = Object.values(DisplayColumns).map((elem) => {
  return {
    value: elem.value,
    label: elem.text,
  }
})

// The columns for extra_annos.
const extraColumnOptions = (props.extraAnnoFields ?? []).map(
  ({ field, label }) => ({
    value: `extra_anno-${field}`,
    label: label,
  })
)

// Concatenate to column options.
const columnOptions = staticColumnOptions.concat(extraColumnOptions)

const displayDetailsWrapper = computed({
  get() {
    return props.displayDetails
  },
  set(newValue) {
    emit('update:displayDetails', newValue)
    if (!props.columnApi) {
      return // in case we are not connected to an ag-grid
    }
    props.columnApi.setColumnsVisible(
      ['position', 'reference', 'alternative'],
      newValue === DisplayDetails.Coordinates.value
    )
    props.columnApi.setColumnVisible(
      'clinvar',
      newValue === DisplayDetails.Clinvar.value
    )
  },
})

const displayFrequencyWrapper = computed({
  get() {
    return props.displayFrequency
  },
  set(newValue) {
    emit('update:displayFrequency', newValue)
    if (!props.columnApi) {
      return // in case we are not connected to an ag-grid
    }
    props.columnApi.setColumnsVisible(
      ['exac_frequency', 'exac_homozygous'],
      newValue === DisplayFrequencies.Exac.value
    )
    props.columnApi.setColumnsVisible(
      ['thousand_genomes_frequency', 'thousand_genomes_homozygous'],
      newValue === DisplayFrequencies.ThousandGenomes.value
    )
    props.columnApi.setColumnsVisible(
      ['gnomad_exomes_frequency', 'gnomad_exomes_homozygous'],
      newValue === DisplayFrequencies.GnomadExomes.value
    )
    props.columnApi.setColumnsVisible(
      ['gnomad_genomes_frequency', 'gnomad_genomes_homozygous'],
      newValue === DisplayFrequencies.GnomadGenomes.value
    )
    props.columnApi.setColumnsVisible(
      ['inhouse_carriers', 'inhouse_hom_alt'],
      newValue === DisplayFrequencies.InhouseDb.value
    )
    props.columnApi.setColumnsVisible(
      ['mtdb_frequency', 'mtdb_count'],
      newValue === DisplayFrequencies.MtDb.value
    )
    props.columnApi.setColumnsVisible(
      ['helixmtdb_frequency', 'helixmtdb_hom_count'],
      newValue === DisplayFrequencies.HelixMtDb.value
    )
    props.columnApi.setColumnsVisible(
      ['mitomap_frequency', 'mitomap_count'],
      newValue === DisplayFrequencies.Mitomap.value
    )
  },
})

const displayConstraintWrapper = computed({
  get() {
    return props.displayConstraint
  },
  set(newValue) {
    emit('update:displayConstraint', newValue)
    if (!props.columnApi) {
      return // in case we are not connected to an ag-grid
    }
    props.columnApi.setColumnVisible(
      'exac_pLI',
      newValue === DisplayConstraints.ExacPli.value
    )
    props.columnApi.setColumnVisible(
      'exac_mis_z',
      newValue === DisplayConstraints.ExacZMis.value
    )
    props.columnApi.setColumnVisible(
      'exac_syn_z',
      newValue === DisplayConstraints.ExacZSyn.value
    )
    props.columnApi.setColumnVisible(
      'gnomad_loeuf',
      newValue === DisplayConstraints.GnomadLoeuf.value
    )
    props.columnApi.setColumnVisible(
      'gnomad_pLI',
      newValue === DisplayConstraints.GnomadPli.value
    )
    props.columnApi.setColumnVisible(
      'gnomad_mis_z',
      newValue === DisplayConstraints.GnomadZMis.value
    )
    props.columnApi.setColumnVisible(
      'gnomad_syn_z',
      newValue === DisplayConstraints.GnomadZSyn.value
    )
  },
})

const displayColumnsWrapper = computed({
  get() {
    return props.displayColumns || []
  },
  set(newValue) {
    emit('update:displayColumns', newValue)
    if (!props.columnApi || newValue == null) {
      // in case we are not connected to an ag-grid or not bound to an array value
      return
    }
    props.columnApi.setColumnVisible(
      'effect_summary',
      newValue.includes(DisplayColumns.Effect.value)
    )
    props.columnApi.setColumnVisible(
      'effect',
      newValue.includes(DisplayColumns.EffectText.value)
    )
    props.columnApi.setColumnVisible(
      'hgvs_p',
      newValue.includes(DisplayColumns.EffectProtein.value)
    )
    props.columnApi.setColumnVisible(
      'hgvs_c',
      newValue.includes(DisplayColumns.EffectCdna.value)
    )
    props.columnApi.setColumnVisible(
      'exon_dist',
      newValue.includes(DisplayColumns.DistanceSplicesite.value)
    )
    for (const { value } of extraColumnOptions) {
      props.columnApi.setColumnVisible(value, newValue.includes(value))
    }
  },
})
</script>

<template>
  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap">
        Coordinates / ClinVar
      </label>
    </div>
    <select
      v-model="displayDetailsWrapper"
      class="custom-select custom-select-sm"
      style="width: 150px"
    >
      <option
        v-for="option in DisplayDetails"
        :value="option.value"
        :key="option"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap"> Frequency </label>
    </div>
    <select
      class="custom-select custom-select-sm"
      style="width: 150px"
      v-model="displayFrequencyWrapper"
    >
      <option
        v-for="option in DisplayFrequencies"
        :value="option.value"
        :key="option"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start">
    <div>
      <label class="font-weight-bold small mb-0 text-nowrap">
        Constraints
      </label>
    </div>
    <select
      v-model="displayConstraintWrapper"
      class="custom-select custom-select-sm"
      style="width: 150px"
    >
      <option
        v-for="option in DisplayConstraints"
        :value="option.value"
        :key="option"
      >
        {{ option.text }}
      </option>
    </select>
  </div>

  <div class="pr-3 align-self-start extra-columns">
    <div style="width: 250px">
      <label class="font-weight-bold small mb-0 text-nowrap">
        Extra Columns
      </label>
    </div>
    <Multiselect
      v-model="displayColumnsWrapper"
      mode="multiple"
      :hide-selected="false"
      :allow-empty="true"
      :close-on-select="true"
      :searchable="true"
      :options="columnOptions"
    />
  </div>
</template>

<style src="@vueform/multiselect/themes/default.css"></style>

<style>
.extra-columns {
  --ms-font-size: 0.875rem;
  --ms-line-height: 1.5;
  --ms-py: 0.26rem;
  --ms-caret-color: #343a40;
  --ms-clear-color: #343a40;
}

.multiselect {
  color: #343a40;
}
</style>
