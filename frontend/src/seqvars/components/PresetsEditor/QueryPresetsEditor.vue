<script setup lang="ts">
import { useSeqvarsPresetsStore } from '@/seqvars/stores/presets'
import {
  SeqvarsQueryPresetsSetVersionDetails,
  SeqvarsQueryPresetsQuality,
} from '@varfish-org/varfish-api/lib'
import PresetsList from '@/seqvars/components/PresetsEditor/PresetsList.vue'
import CategoryPresetsQualityEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsQualityEditor.vue'
import CategoryPresetsFrequencyEditor from '@/seqvars/components/PresetsEditor/CategoryPresetsFrequencyEditor.vue'
import { computed, onMounted, reactive, ref, watch } from 'vue'

/** Props used in this component. */
const props = defineProps<{
  /** The project UUID. */
  projectUuid?: string
  /** UUID of the current preset set. */
  presetSet?: string
  /** UUID of the current preset set version. */
  presetSetVersion?: string
}>()

/** Store with the presets. */
const seqvarsPresetsStore = useSeqvarsPresetsStore()

/* The currently selected preset set version (details, contains preset set info). */
const selectedPresetSetVersion = computed<
  SeqvarsQueryPresetsSetVersionDetails | undefined
>(() => {
  if (props.presetSetVersion) {
    return seqvarsPresetsStore.presetSetVersions.get(props.presetSetVersion)
  } else {
    return undefined
  }
})

/** Enumeration for the presets categories. */
enum Category {
  QUALITY = 'quality',
  FREQUENCY = 'frequency',
  CONSEQUENCE = 'consequence',
  LOCUS = 'locus',
  PHENOTYPE_PRIO = 'phenotype_prioritization',
  VARIANT_PRIO = 'variant_prioritization',
  CLINVAR = 'clinvar',
  COLUMNS = 'columns',
  PREDEFINED_QUERIES = 'predefined_queries',
}

/** Common interface for prests for use in `PresetsList`. */
interface CategoryInfoItem {
  sodar_uuid: string
  label: string
  rank?: number
}

/** Information about one category. */
interface CategoryInfo {
  label: string
  category: Category
  items: CategoryInfoItem[]
}

/** Category information/definition. */
const categories = computed<CategoryInfo[]>(() => {
  return [
    {
      label: 'Quality',
      category: Category.QUALITY,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsquality_set ?? [],
    },
    {
      label: 'Frequency',
      category: Category.FREQUENCY,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsfrequency_set ?? [],
    },
    {
      label: 'Consequence',
      category: Category.CONSEQUENCE,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsconsequence_set ??
        [],
    },
    {
      label: 'Locus',
      category: Category.LOCUS,
      items: selectedPresetSetVersion.value?.seqvarsquerypresetslocus_set ?? [],
    },
    {
      label: 'Phenotype Prioritization',
      category: Category.PHENOTYPE_PRIO,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsphenotypeprio_set ??
        [],
    },
    {
      label: 'Variant Prioritization',
      category: Category.VARIANT_PRIO,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsvariantprio_set ??
        [],
    },
    {
      label: 'ClinVar',
      category: Category.CLINVAR,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetsclinvar_set ?? [],
    },
    {
      label: 'Columns',
      category: Category.COLUMNS,
      items:
        selectedPresetSetVersion.value?.seqvarsquerypresetscolumns_set ?? [],
    },
    {
      label: 'Predefined Queries',
      category: Category.PREDEFINED_QUERIES,
      items: selectedPresetSetVersion.value?.seqvarspredefinedquery_set ?? [],
    },
  ]
})

/** Currently selected category. */
const selectedCategory = ref<Category>(Category.QUALITY)

/** Selected presets in each category. */
const selectedPreset = reactive<{ [key in Category]: string | undefined }>({
  [Category.QUALITY]: undefined,
  [Category.FREQUENCY]: undefined,
  [Category.CONSEQUENCE]: undefined,
  [Category.LOCUS]: undefined,
  [Category.PHENOTYPE_PRIO]: undefined,
  [Category.VARIANT_PRIO]: undefined,
  [Category.CLINVAR]: undefined,
  [Category.COLUMNS]: undefined,
  [Category.PREDEFINED_QUERIES]: undefined,
})

/** The currently selected quality presets, if any. */
const selectedQualityPresets = computed<SeqvarsQueryPresetsQuality | undefined>(
  () => {
    return selectedPresetSetVersion.value?.seqvarsquerypresetsquality_set.find(
      (item) => item.sodar_uuid === selectedPreset[Category.QUALITY],
    )
  },
)

/** The currently selected frequency presets, if any. */
const selectedFrequencyPresets = computed<
  SeqvarsQueryPresetsQuality | undefined
>(() => {
  return selectedPresetSetVersion.value?.seqvarsquerypresetsfrequency_set.find(
    (item) => item.sodar_uuid === selectedPreset[Category.FREQUENCY],
  )
})

/** Select the first presets in each category. */
const selectFirstPresets = () => {
  for (const category of categories.value) {
    if (category.items.length) {
      selectedPreset[category.category] = category.items[0].sodar_uuid
    }
  }
}

// Select first presets when mounted.
onMounted(() => {
  selectFirstPresets()
})
// Also select first when project, preset set, preset set version, or
// the load state of the store changes
watch(
  () => [
    props.projectUuid,
    props.presetSet,
    props.presetSetVersion,
    seqvarsPresetsStore.storeState.state,
  ],
  () => {
    selectFirstPresets()
  },
)
</script>

<template>
  <v-skeleton-loader
    loading
    type="heading,paragraph"
    class="pt-3"
    v-if="!selectedPresetSetVersion?.presetsset"
  />
  <div class="pt-3" v-else>
    <h3 class="pb-3">
      Presets: &raquo;{{
        selectedPresetSetVersion?.presetsset.label ?? 'UNDEFINED'
      }}
      {{
        `v${selectedPresetSetVersion?.version_major ?? 'X'}` +
        `.${selectedPresetSetVersion?.version_minor ?? 'Y'}`
      }}&laquo;
    </h3>

    <v-row class="d-flex flex-nowrap">
      <v-col cols="3">
        <v-expansion-panels
          mandatory
          v-model="selectedCategory"
          :flat="false"
          density="compact"
        >
          <v-expansion-panel
            v-for="item in categories"
            :key="item.category"
            :title="item.label"
            :value="item.category"
          >
            <v-expansion-panel-text>
              <PresetsList
                v-model="selectedPreset[item.category]"
                :items="item.items"
              />
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
      <v-col cols="9">
        <v-sheet class="pa-3">
          <div v-if="selectedCategory === Category.QUALITY">
            <CategoryPresetsQualityEditor
              v-model:model-value="selectedQualityPresets"
            />
          </div>
          <div v-else-if="selectedCategory === Category.FREQUENCY">
            <CategoryPresetsFrequencyEditor
              v-model:model-value="selectedFrequencyPresets"
            />
          </div>
          <v-alert
            :title="`Invalid category ${selectedCategory}`"
            color="error"
            v-else
          />
        </v-sheet>
      </v-col>
    </v-row>
  </div>
</template>
