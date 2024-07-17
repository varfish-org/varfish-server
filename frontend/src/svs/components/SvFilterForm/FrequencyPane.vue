<script setup>
import { computed, onMounted } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { numeric, integer, minValue, maxValue } from '@vuelidate/validators'

// Define the component's props.
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  case: Object,
  querySettings: Object,
})

// Return JSON string with settings from this tab to be displayed in "dev" mode.
const dumpFrequencies = () => {
  const result = {}
  for (const [key, value] of Object.entries(props.querySettings)) {
    if (
      key.startsWith('svdb_g1k_') ||
      key.startsWith('svdb_dgv_') ||
      key.startsWith('svdb_dgv_gs_') ||
      key.startsWith('svdb_gnomad_exomes_') ||
      key.startsWith('svdb_dbvar_') ||
      key.startsWith('svdb_gnomad_genomes_') ||
      key.startsWith('svdb_inhouse_')
    ) {
      result[key] = value
    }
  }
  return JSON.stringify(result)
}

// Define validation for one frequency database.
const makeRule = (dbName) => {
  const result = {}
  result[`${dbName}_min_overlap`] = {
    numeric,
    minValue: minValue(0.0),
    maxValue: maxValue(1.0),
    $autoDirty: true,
  }
  result[`${dbName}_max_count`] = {
    integer,
    minValue: minValue(0),
    $autoDirty: true,
  }
  return result
}

// Define validation rules.
const rules = {
  ...makeRule('svdb_g1k'),
  ...makeRule('svdb_dgv'),
  ...makeRule('svdb_dgv_gs'),
  ...makeRule('svdb_gnomad_exomes'),
  ...makeRule('svdb_dbvar'),
  ...makeRule('svdb_gnomad_genomes'),
  ...makeRule('svdb_inhouse'),
}

// Helper function to build wrappers that catch the case of props.querySettings not being set.
const _vuelidateWrappers = (keys) =>
  Object.fromEntries(
    keys.map((key) => [
      key,
      computed({
        get() {
          return !props.querySettings ? null : props.querySettings[key]
        },
        set(newValue) {
          if (props.querySettings) {
            props.querySettings[key] = newValue
          }
        },
      }),
    ]),
  )

// Define the form state.
const formState = {
  ..._vuelidateWrappers([
    'svdb_g1k_min_overlap',
    'svdb_g1k_max_count',
    'svdb_dgv_min_overlap',
    'svdb_dgv_max_count',
    'svdb_dgv_gs_min_overlap',
    'svdb_dgv_gs_max_count',
    'svdb_gnomad_exomes_min_overlap',
    'svdb_gnomad_exomes_max_count',
    'svdb_dbvar_min_overlap',
    'svdb_dbvar_max_count',
    'svdb_gnomad_genomes_min_overlap',
    'svdb_gnomad_genomes_max_count',
    'svdb_inhouse_min_overlap',
    'svdb_inhouse_max_count',
  ]),
}

// Define vuelidate object.
const v$ = useVuelidate(rules, formState)

// Perform vuelidate validation when mounted.
onMounted(() => {
  v$.value.$touch()
})

// Define the exposed properties.
defineExpose({
  v$, // parent component's vuelidate picks this up
})
</script>

<template>
  <div
    v-if="props.showFiltrationInlineHelp"
    class="alert alert-secondary small p-2 m-2"
  >
    <i-mdi-information />

    Adjust the settings allow to fine-tune the filtration of SVs based on
    population frequencies, leave fields empty to not filter based on the
    threshold. The checkboxes enable (<i-fa-regular-check-square />) or disable
    (<i-fa-regular-square />) filtration based on the population frequencies of
    the given database. You can provide the number of carriers (regardless of
    the heterozygosity/homozygosity state).
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
        <th style="width: 0px"></th>
        <th style="width: 250px"></th>
        <th class="text-center" title="Minimal reciprocal overlap">
          Required Overlap
        </th>
        <th class="text-center" title="Maximal allowed number of carriers">
          Maximal Carriers
        </th>
      </tr>
    </thead>
    <tbody>
      <tr v-show="props.case.release === 'GRCh37'">
        <td>
          <input
            v-model="props.querySettings.svdb_g1k_enabled"
            type="checkbox"
          />
        </td>
        <td title="Phase 3 data (healthy individuals)">
          1000 Genomes <small class="text-muted">(samples: 1000)</small>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_g1k_min_overlap.$model"
            placeholder="Min. SV Overlap with Thousand Genomes"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_g1k_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_g1k_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_g1k_max_count.$model"
            type="text"
            placeholder="Maximal number of alleles in Thousand Genomes"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_g1k_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_g1k_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr v-show="props.case.release === 'GRCh37'">
        <td>
          <input
            v-model="props.querySettings.svdb_gnomad_exomes_enabled"
            type="checkbox"
          />
        </td>
        <td title="Exomes; project attempts to exclude pediatric disease cases">
          ExAC <small class="text-muted">(samples: 60,706)</small>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_gnomad_exomes_min_overlap.$model"
            type="text"
            placeholder="Min. SV Overlap with ExAC"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_gnomad_exomes_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_gnomad_exomes_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_gnomad_exomes_max_count.$model"
            type="text"
            placeholder="Maximal number of carriers in ExAC"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_gnomad_exomes_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_gnomad_exomes_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.svdb_gnomad_genomes_enabled"
            type="checkbox"
          />
        </td>
        <td title="genomes; project attempts to exclude pediatric cases">
          gnomAD-SV <small class="text-muted">(samples: 14,216)</small>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_gnomad_genomes_min_overlap.$model"
            type="text"
            placeholder="Min. SV overlap with gnomAD-SV"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_gnomad_genomes_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_gnomad_genomes_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_gnomad_genomes_max_count.$model"
            type="text"
            placeholder="Maximal number of carriers in gnomAD-SV"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_gnomad_genomes_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_gnomad_genomes_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.svdb_dbvar_enabled"
            type="checkbox"
          />
        </td>
        <td
          title="aggregates variants from many technologies; no attempt to exclude pediatric cases"
        >
          dbVar
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dbvar_min_overlap.$model"
            type="text"
            placeholder="Min. SV overlap with dbVar"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dbvar_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dbvar_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dbvar_max_count.$model"
            type="text"
            placeholder="Maximal number of carriers in dbVar"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dbvar_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dbvar_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.svdb_dgv_enabled"
            type="checkbox"
          />
        </td>
        <td
          title="aggregates variants from many technologies; no attempt to exclude pediatric cases"
        >
          DGV
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dgv_min_overlap.$model"
            type="text"
            placeholder="Min. SV overlap with DGV"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dgv_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dgv_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dgv_max_count.$model"
            type="text"
            placeholder="Maximal number of carriers in DGV"
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dgv_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dgv_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.svdb_dgv_gs_enabled"
            type="checkbox"
          />
        </td>
        <td
          title="aggregates variants from many technologies; no attempt to exclude pediatric cases"
        >
          DGV "gold standard"
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dgv_gs_min_overlap.$model"
            type="text"
            placeholder='Min. SV overlap with DGV "gold standard"'
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dgv_gs_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dgv_gs_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_dgv_gs_max_count.$model"
            type="text"
            placeholder='Maximal number of carriers in DGV "gold standard"'
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_dgv_gs_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_dgv_gs_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
      </tr>
      <tr>
        <td>
          <input
            v-model="props.querySettings.svdb_inhouse_enabled"
            type="checkbox"
          />
        </td>
        <td title="SVs from data in this VarFish instance">In-House</td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_inhouse_min_overlap.$model"
            type="text"
            placeholder='Min. SV overlap with DGV "gold standard"'
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_inhouse_min_overlap.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_inhouse_min_overlap.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </td>
        <td>
          <input
            v-model.trim.lazy="v$.svdb_inhouse_max_count.$model"
            type="text"
            placeholder='Maximal number of carriers in DGV "gold standard"'
            class="form-control"
            :class="{
              'is-invalid': v$.svdb_inhouse_max_count.$error,
            }"
          />
          <div
            v-for="error of v$.svdb_inhouse_max_count.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
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

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
