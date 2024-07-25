<script setup lang="ts">
import {
  SeqvarsPredefinedQuery,
  SeqvarsQueryPresetsSetVersionDetails,
} from '@varfish-org/varfish-api/lib'
import { PropType } from 'vue'
import { GENOTYPE_PRESET_LABELS } from './lib'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** Preset set version to take presets from. */
    presetsSetVersion?: SeqvarsQueryPresetsSetVersionDetails
    /** Whether the editor is readonly. */
    readonly: boolean
  }>(),
  { readonly: false },
)

/** The predefined queries presets to use in this editor. */
const model = defineModel({
  type: Object as PropType<SeqvarsPredefinedQuery>,
})
</script>

<template>
  <h4>
    Predefined Queries Presets &raquo;{{ model?.label ?? 'UNDEFINED' }}&laquo;
  </h4>

  <v-skeleton-loader v-if="!model || !presetsSetVersion" type="article" />
  <v-form v-else>
    <v-checkbox
      v-model="model.included_in_sop"
      label="Include in SOP"
      hint="The queries that are included in SOP can be auto-started together."
      density="compact"
      persistent-hint
      :disabled="readonly"
    />

    <div class="border-t-thin my-3"></div>

    <v-select
      v-model="model.genotype!.choice"
      label="Genotype Preset"
      :items="Object.keys(GENOTYPE_PRESET_LABELS)"
      :item-title="
        (key: keyof typeof GENOTYPE_PRESET_LABELS) =>
          GENOTYPE_PRESET_LABELS[key]
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.quality"
      label="Quality Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsquality_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsquality_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.frequency"
      label="Frequency Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsfrequency_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsfrequency_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.consequence"
      label="Consequence Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsconsequence_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsconsequence_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.locus"
      label="Locus Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetslocus_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetslocus_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.phenotypeprio"
      label="Phenotype Priority Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsphenotypeprio_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsphenotypeprio_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.variantprio"
      label="Variant Priority Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsvariantprio_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsvariantprio_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.clinvar"
      label="Clinvar Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetsclinvar_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetsclinvar_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />

    <v-select
      v-model="model.columns"
      label="Columns Preset"
      :items="
        presetsSetVersion.seqvarsquerypresetscolumns_set.map(
          (elem) => elem.sodar_uuid,
        )
      "
      :item-title="
        (sodar_uuid: string) =>
          presetsSetVersion!.seqvarsquerypresetscolumns_set.find(
            (elem) => elem.sodar_uuid === sodar_uuid,
          )?.label ?? sodar_uuid
      "
      :disabled="readonly"
    />
  </v-form>
</template>
