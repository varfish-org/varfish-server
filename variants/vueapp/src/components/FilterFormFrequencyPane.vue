<script setup>
import { useVuelidate } from '@vuelidate/core'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  case: Object,
  querySettings: Object,
})

const v$ = useVuelidate()

const dumpFrequencies = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if (
      key.startsWith('thousand_genomes_') ||
      key.startsWith('exac_') ||
      key.startsWith('gnomad_exomes_') ||
      key.startsWith('gnomad_genomes_') ||
      key.startsWith('inhouse_') ||
      key.startsWith('mtdb_') ||
      key.startsWith('helixmtdb_') ||
      key.startsWith('mitomap')
    ) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

defineExpose({ v$ })
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2"
  >
    <i-mdi-information />

    Adjust the settings allow to fine-tune the filtration of variants based on
    population frequencies, leave fields empty to not filter based on the
    threshold. The checkboxes enable (<i-fa-regular-check-square />) or disable
    (<i-fa-regular-square />) filtration based on the population frequencies of
    the given database. You can provide the number of carriers with maximal
    heterozygous/homozygous (respectively: -plasmid) state or population
    frequencies. For the in-house DB, you can only filter based on carrier state
    as currently it is tracked how many carriers have sufficient coverage for
    each variant.
    <span v-if="props.case && props.case.release === 'GRCh37'"></span>
    <span v-else-if="props.case && props.case.release === 'GRCh38'">
      Thousand genomes and ExAC frequencies are only available GRCh37 cases.
    </span>
    <div v-else class="alert alert-danger">
      <i-bi-exclamation-circle />
      Genomebuild variable is unknown (<strong>{{
        props.case ? props.case.release : 'UNKNOWN'
      }}</strong
      >). The form might not be displayed correctly.
    </div>
  </div>

  <table
    class="table table-striped table-hover sodar-card-table compact-form-groups"
  >
    <thead>
      <tr>
        <th></th>
        <th></th>
        <th
          class="text-center"
          title="Maximal allowed homozygous/homoplasmy count"
        >
          Homozygous<span class="small text-muted">/-plasmy</span> count
        </th>
        <th
          class="text-center"
          title="Maximal allowed heterozygous/heteroplasmy count"
        >
          Heterozygous<span class="small text-muted">/-plasmy</span> count
        </th>
        <th class="text-center" title="Maximal allowed hemizygous count">
          Hemizygous count
        </th>
        <th
          class="text-center"
          title="Maximal allowed frequency (in any sub population if applicable)"
        >
          Frequency / Carriers
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-show="props.case.release === 'GRCh37'">
        <td>
          <input
            v-model="props.querySettings.thousand_genomes_enabled"
            type="checkbox"
          />
        </td>
        <td title="Phase 3 data (healthy individuals)">
          1000 Genomes <small class="text-muted">(samples: 1000)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.thousand_genomes_homozygous"
            type="number"
            placeholder="Maximal hom. count in 1000 genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.thousand_genomes_heterozygous"
            type="number"
            placeholder="Maximal het. count in 1000 genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.thousand_genomes_hemizygous"
            type="number"
            placeholder="Maximal hemi. count in 1000 genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.thousand_genomes_frequency"
            type="number"
            placeholder="Maximal frequency in one 1000 genomes population"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr v-show="props.case.release === 'GRCh37'">
        <td>
          <input v-model="props.querySettings.exac_enabled" type="checkbox" />
        </td>
        <td title="Exomes; project attempts to exclude pediatric disease cases">
          ExAC <small class="text-muted">(samples: 60,706)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.exac_homozygous"
            type="number"
            placeholder="Maximal hom. count in ExAC"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.exac_heterozygous"
            type="number"
            placeholder="Maximal het. count in ExAC"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.exac_hemizygous"
            type="number"
            placeholder="Maximal hemi. count in ExAC"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.exac_frequency"
            type="number"
            placeholder="Maximal frequency in one ExAC population"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.gnomad_exomes_enabled"
            type="checkbox"
          />
        </td>
        <td
          title="ExAC follow-up; exomes; project attempts to exclude pediatric cases"
        >
          gnomAD exomes <small class="text-muted">(samples: 125,748)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_exomes_homozygous"
            type="number"
            placeholder="Maximal hom. count in gnomAD exomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_exomes_heterozygous"
            type="number"
            placeholder="Maximal het. count in gnomAD exomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_exomes_hemizygous"
            type="number"
            placeholder="Maximal hemi. count in gnomAD exomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_exomes_frequency"
            type="number"
            placeholder="Maximal frequency in one gnomAD exomes population"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.gnomad_genomes_enabled"
            type="checkbox"
          />
        </td>
        <td
          title="ExAC follow-up; genomes; project attempts to exclude pediatric cases"
        >
          gnomAD genomes <small class="text-muted">(samples: 15,708)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_genomes_homozygous"
            type="number"
            placeholder="Maximal hom. count in gnomAD genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_genomes_heterozygous"
            type="number"
            placeholder="Maximal het. count in gnomAD genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_genomes_hemizygous"
            type="number"
            placeholder="Maximal hemi. count in gnomAD genomes"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.gnomad_genomes_frequency"
            type="number"
            placeholder="Maximal frequency in one gnomAD genomes population"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.inhouse_enabled"
            type="checkbox"
          />
        </td>
        <td title="In-house database, mostly useful for excluding artifacts">
          in-house DB
        </td>
        <td>
          <input
            v-model="props.querySettings.inhouse_homozygous"
            type="number"
            placeholder="Maximal in-house hom. count"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.inhouse_heterozygous"
            type="number"
            placeholder="Maximal in-house het. count"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.inhouse_hemizygous"
            type="number"
            placeholder="Maximal in-house hemi. count"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.inhouse_carriers"
            type="number"
            placeholder="Maximal in-house carriers"
            class="form-control"
            min="0"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input v-model="props.querySettings.mtdb_enabled" type="checkbox" />
        </td>
        <td title="Mitochondrial frequency database">
          mtDB <small class="text-muted">(samples: ~2704)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.mtdb_count"
            type="number"
            placeholder="Maximal count in mtDB"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            type="number"
            class="form-control"
            placeholder="N/A"
            disabled
          />
        </td>
        <td>
          <input
            type="number"
            class="form-control"
            placeholder="N/A"
            disabled
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.mtdb_frequency"
            type="number"
            placeholder="Maximal frequency in mtDB"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.helixmtdb_enabled"
            type="checkbox"
          />
        </td>
        <td title="Mitochondrial frequency database">
          HelixMTdb <small class="text-muted">(samples: 196,554)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.helixmtdb_hom_count"
            type="number"
            placeholder="Maximal hom. count in HelixMTdb"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.helixmtdb_het_count"
            type="number"
            placeholder="Maximal het. count in HelixMTdb"
            class="form-control"
            min="0"
          />
        </td>
        <td>
          <input type="text" class="form-control" placeholder="N/A" disabled />
        </td>
        <td>
          <input
            v-model="props.querySettings.helixmtdb_frequency"
            type="number"
            placeholder="Maximal frequency in HelixMTdb"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.mitomap_enabled"
            type="checkbox"
          />
        </td>
        <td title="Mitochondrial frequency database">
          MITOMAP <small class="text-muted">(samples: 50,174)</small>
        </td>
        <td>
          <input
            v-model="props.querySettings.mitomap_count"
            type="number"
            placeholder="Maximal count in MITOMAP"
            class="form-control"
          />
        </td>
        <td>
          <input
            type="number"
            class="form-control"
            placeholder="N/A"
            disabled
          />
        </td>
        <td>
          <input
            type="number"
            class="form-control"
            placeholder="N/A"
            disabled
          />
        </td>
        <td>
          <input
            v-model="props.querySettings.mitomap_frequency"
            type="number"
            placeholder="Maximal frequency in MITOMAP"
            class="form-control"
            min="0"
            max="1"
            step="0.001"
          />
        </td>
      </tr>
    </tbody>
  </table>
  <div v-if="filtrationComplexityMode == 'dev'" class="card-footer">
    <span class="text-nowrap">
      <i-mdi-account-hard-hat />
      <strong class="pl-2">Developer Info:</strong>
    </span>
    <code>
      {{ dumpFrequencies() }}
    </code>
  </div>
</template>
