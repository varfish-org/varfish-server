<script setup lang="ts">
import { SeqvarsQueryPresetsFrequency } from '@varfish-org/varfish-api/lib'
import { PropType, computed } from 'vue'

/** The frequency presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsQueryPresetsFrequency>,
})

interface GnomadFreqs {
  enabled?: boolean
  homozygous?: number | null
  heterozygous?: number | null
  hemizygous?: number | null
  frequency?: number | null
}
const gnomadExomes = computed<GnomadFreqs>(
  () => model.value?.gnomad_exomes ?? ({} as GnomadFreqs),
)
const gnomadGenomes = computed<GnomadFreqs>(
  () => model.value?.gnomad_genomes ?? ({} as GnomadFreqs),
)

interface MitochondrialFreqs {
  enabled?: boolean;
  heteroplasmic?: number | null;
  homoplasmic?: number | null;
  frequency?: number | null;
}
const gnomadMitochondrial = computed<MitochondrialFreqs>(
  () => model.value?.gnomad_mitochondrial ?? ({} as MitochondrialFreqs),
)
const helixMtDb = computed<MitochondrialFreqs>(
  () => model.value?.helixmtdb ?? ({} as MitochondrialFreqs),
)

interface InhouseFreqs {
  enabled?: boolean
  homozygous?: number | null
  heterozygous?: number | null
  hemizygous?: number | null
  carriers?: number | null;
}
const inhouse = computed<InhouseFreqs>(
  () => model.value?.inhouse ?? ({} as InhouseFreqs),
)
</script>

<template>
  <h4>Frequency Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;</h4>

  <v-skeleton-loader v-if="!model" />
  <v-form v-else>
    <v-table density="compact">
      <thead>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center">freq. [%]</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th class="px-1">gnomAD exomes</th>
          <td class="px-1">
            <v-checkbox v-model="gnomadExomes.enabled" hide-details />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadExomes.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD genomes</th>
          <td class="px-1">
            <v-checkbox v-model="gnomadGenomes.enabled" hide-details />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadGenomes.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">gnomAD MT</th>
          <td class="px-1">
            <v-checkbox v-model="gnomadMitochondrial.enabled" hide-details />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.homoplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.heteroplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1 text-center text-grey">
            N/A
          </td>
          <td class="px-1">
            <v-text-field
              v-model="gnomadMitochondrial.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1">HelixMtDb</th>
          <td class="px-1">
            <v-checkbox v-model="helixMtDb.enabled" hide-details />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.homoplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.heteroplasmic"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1 text-center text-grey">
            N/A
          </td>
          <td class="px-1">
            <v-text-field
              v-model="helixMtDb.frequency"
              hide-details
              density="compact"
              clearable
              type="number"
              step="0.001"
            />
          </td>
        </tr>
        <tr>
          <th class="px-1 text-center">database</th>
          <th class="px-1 text-center">enabled</th>
          <th class="px-1 text-center">hom.</th>
          <th class="px-1 text-center">het.</th>
          <th class="px-1 text-center">hemi.</th>
          <th class="px-1 text-center"># carriers</th>
        </tr>
        <tr>
          <th class="px-1">In-House</th>
          <td class="px-1">
            <v-checkbox v-model="inhouse.enabled" hide-details />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.homozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.heterozygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.hemizygous"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
          <td class="px-1">
            <v-text-field
              v-model="inhouse.carriers"
              hide-details
              density="compact"
              clearable
              type="number"
            />
          </td>
        </tr>
      </tbody>
    </v-table>
  </v-form>
</template>
