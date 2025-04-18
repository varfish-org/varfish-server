<script setup>
import isEqual from 'fast-deep-equal'
import { computed, onMounted, reactive, ref, watch } from 'vue'

import { useCaseDetailsStore } from '@/cases/stores/caseDetails'
import { randomString } from '@/varfish/common'
import { useCtxStore } from '@/varfish/stores/ctx'
import { QueryPresetsClient } from '@/variants/api/queryPresetsClient'
import { copy } from '@/variants/helpers'
import { useVariantQueryStore } from '@/variants/stores/variantQuery'

const ctxStore = useCtxStore()
const caseDetailsStore = useCaseDetailsStore()
const variantQueryStore = useVariantQueryStore()

/** The props for this component. */
const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  quickPresets: Object,
  categoryPresets: Object,
  case: Object,
  querySettings: Object,
  idSuffix: {
    type: String,
    default: randomString(),
  },
})

/** Internal store of inheritance preset. If set through here, then it is only applied in the control. */
const inheritanceRef = ref(null)
const presetSource = ref(null)
const presetSetLoading = ref(false)
const presetSetLabel = ref(null)

const updatePresetSetLoading = async () => {
  let uuid
  if (!props.case?.presetset && !variantQueryStore?.defaultPresetSetUuid) {
    presetSetLabel.value = 'Factory Defaults'
    presetSource.value = 'Factory Defaults'
    return // short circuit in case of factory defaults
  } else {
    if (props.case?.presetset) {
      uuid = caseDetailsStore.caseObj.presetset
      presetSource.value = 'Individual Case Setting'
    } else if (variantQueryStore?.defaultPresetSetUuid) {
      uuid = variantQueryStore.defaultPresetSetUuid
      presetSource.value = 'Project Default Setting'
    }
  }
  const queryPresetsClient = new QueryPresetsClient(ctxStore.csrfToken)
  presetSetLoading.value = true
  await queryPresetsClient
    .retrievePresetSet(uuid)
    .then((presetSet) => {
      presetSetLabel.value = presetSet.label
    })
    .catch((err) => {
      console.error('Problem retrieving preset set', err)
    })
    .finally(() => {
      presetSetLoading.value = false
    })
}

/** Refresh qualityRef from actual form values.  Check each for compatibility and pick first matching. */
const refreshInheritanceRef = () => {
  for (const [presetName, presetValues] of Object.entries(
    props.categoryPresets.inheritance,
  )) {
    let isCompatible = true
    for (const member of Object.values(props.case.pedigree)) {
      if (
        !(
          presetValues.genotype[member.name] === null &&
          props.querySettings.genotype[member.name] === 'recessive-parent'
        ) &&
        !(
          presetValues.genotype[member.name] === null &&
          props.querySettings.genotype[member.name] === 'recessive-index'
        ) &&
        !(
          presetValues.genotype[member.name] === null &&
          props.querySettings.genotype[member.name] === 'comphet-index'
        ) &&
        !isEqual(
          props.querySettings.genotype[member.name],
          presetValues.genotype[member.name],
        )
      ) {
        isCompatible = false
        break
      }
    }
    if (
      !isEqual(
        props.querySettings.recessive_index,
        presetValues.recessive_index,
      ) ||
      !isEqual(props.querySettings.recessive_mode, presetValues.recessive_mode)
    ) {
      isCompatible = false
    }
    if (isCompatible) {
      inheritanceRef.value = presetName !== 'de_novo' ? presetName : 'dominant'
      return
    }
  }
  // if we reach here, nothing is compatible, assign "custom"
  inheritanceRef.value = 'custom'
}

/** Computed propery for inheritance.  If set through here, the default is applied (except for custom). */
const inheritanceWrapper = computed({
  get() {
    return inheritanceRef.value
  },
  set(newValue) {
    if (newValue && newValue !== 'custom') {
      props.querySettings.genotype = copy(
        props.categoryPresets.inheritance[newValue].genotype,
      )
      const recessiveIndex =
        props.categoryPresets.inheritance[newValue].recessive_index
      const recessiveMode =
        props.categoryPresets.inheritance[newValue].recessive_mode
      if (recessiveMode === 'compound-recessive') {
        props.querySettings.genotype[recessiveIndex] = 'comphet-index'
      } else if (recessiveMode === 'recessive') {
        props.querySettings.genotype[recessiveIndex] = 'recessive-index'
      }
      const tmp = props.categoryPresets.inheritance[newValue].genotype
      for (const [name, genotype] of Object.entries(tmp)) {
        if (genotype === null && name !== recessiveIndex) {
          props.querySettings.genotype[name] = 'recessive-parent'
        }
      }
      props.querySettings.recessive_index = recessiveIndex
      props.querySettings.recessive_mode = recessiveMode
      inheritanceRef.value = newValue
    }
  },
})

/** Internal store of quality preset.  If set through here, then it is only applied in the control. */
const qualityRef = ref(null)

/** Common keys to strip from presets to get form values. */
const _keysToStrip = [
  'sodar_uuid',
  'date_created',
  'date_modified',
  'label',
  'presetset',
]

/** Return copy of obj without keys. */
const _objectWithoutKeys = (obj, keys) => {
  return Object.fromEntries(
    Object.entries(obj).filter(([key, _value]) => !keys.includes(key)),
  )
}

/** Refresh qualityRef from actual form values.  Check each for compatibility and pick first matching. */
const refreshQualityRef = () => {
  for (const [presetName, presetValues] of Object.entries(
    props.categoryPresets.quality,
  )) {
    const strippedPresetValues = _objectWithoutKeys(presetValues, _keysToStrip)
    let isCompatible = true
    for (const member of Object.values(props.case.pedigree)) {
      if (
        !isEqual(props.querySettings.quality[member.name], strippedPresetValues)
      ) {
        isCompatible = false
      }
    }
    if (isCompatible) {
      qualityRef.value = presetName
      return
    }
  }
  // if we reach here, nothing is compatible, assign "custom"
  qualityRef.value = 'custom'
}

/** Computed property for quality.  If set through here, the default is applied (except for custom). */
const qualityWrapper = computed({
  get() {
    return qualityRef.value
  },
  set(newValue) {
    if (newValue && newValue !== 'custom') {
      for (const member of Object.values(props.case.pedigree)) {
        props.querySettings.quality[member.name] = _objectWithoutKeys(
          props.categoryPresets.quality[newValue],
          _keysToStrip,
        )
      }
      refreshQualityRef()
    }
  },
})

/** Internal store of other presets.  If set through here, then it is only applied in the control. */
const valueRefs = {
  frequency: ref(null),
  impact: ref(null),
  quality: ref(null),
  flagsetc: ref(null),
  chromosomes: ref(null),
}

/** Refresh valueRefs from actual form values.  Check each for compatibility and pick first matching. */
const refreshValueRefs = () => {
  for (const category of Object.keys(valueRefs)) {
    let isCompatible = true
    if (!props.categoryPresets[category]) {
      continue // not fully loaded yet
    }
    for (const [presetName, presetValues] of Object.entries(
      props.categoryPresets[category],
    )) {
      isCompatible = true
      for (const [key, value] of Object.entries(presetValues)) {
        if (
          !_keysToStrip.includes(key) &&
          variantQueryStore.querySettings !== null &&
          !isEqual(variantQueryStore.querySettings[key], value)
        ) {
          isCompatible = false
        }
      }
      if (isCompatible) {
        valueRefs[category].value = presetName
        break
      }
    }
    if (!isCompatible) {
      valueRefs[category].value = 'custom'
    }
  }
}

/** Whether to block the refresh (because setting via shortcut). */
const blockRefresh = ref(false)

/** Helper function to create a computed wrapper for non-inheritance/quality. */
const makeWrapper = (name) =>
  computed({
    get() {
      return valueRefs[name].value
    },
    set(newValue) {
      if (newValue && newValue !== 'custom') {
        const oldBlockRefresh = blockRefresh.value
        blockRefresh.value = true
        for (const [key, value] of Object.entries(
          props.categoryPresets[name][newValue],
        )) {
          if (!_keysToStrip.includes(key)) {
            props.querySettings[key] = value
          }
        }
        blockRefresh.value = oldBlockRefresh
      }
    },
  })

/** Computed property for frequency presets.  If set through here, the default is applied (except for custom). */
const frequencyWrapper = makeWrapper('frequency')
/** Computed property for impact presets.  If set through here, the default is applied (except for custom). */
const impactWrapper = makeWrapper('impact')
/** Computed property for flags presets.  If set through here, the default is applied (except for custom). */
const flagsWrapper = makeWrapper('flagsetc')
/** Computed property for chromosomes presets.  If set through here, the default is applied (except for custom). */
const chromosomesWrapper = makeWrapper('chromosomes')

/** Internal store of selected quick preset.  If set through here, then it is only applied in the control. */
const quickPresetRef = ref(null)

/** Refresh quick presets from actual form values.  Check each for compatibility and pick first matching. */
const refreshQuickPreset = () => {
  if (!props.quickPresets) {
    // skip if none are there yet
    return
  }
  for (const [name, theQuickPresets] of Object.entries(props.quickPresets)) {
    if (
      inheritanceWrapper.value === theQuickPresets.inheritance &&
      frequencyWrapper.value === theQuickPresets.frequency &&
      impactWrapper.value === theQuickPresets.impact &&
      qualityWrapper.value === theQuickPresets.quality &&
      chromosomesWrapper.value === theQuickPresets.chromosomes &&
      flagsWrapper.value === theQuickPresets.flagsetc
    ) {
      quickPresetRef.value = name
      return
    }
  }
  // if we reach here, nothing is compatible, assign "custom"
  quickPresetRef.value = 'custom'
}

/** Computed propery for quick preset.  If set through here, the default is applied (except for custom). */
const quickPresetWrapper = computed({
  get() {
    return quickPresetRef.value
  },

  set(newValue) {
    const oldBlockRefresh = blockRefresh.value
    blockRefresh.value = true
    if (newValue !== 'custom') {
      const newQuickPresets = props.quickPresets[newValue]
      inheritanceWrapper.value = newQuickPresets.inheritance
      frequencyWrapper.value = newQuickPresets.frequency
      impactWrapper.value = newQuickPresets.impact
      qualityWrapper.value = newQuickPresets.quality
      chromosomesWrapper.value = newQuickPresets.chromosomes
      flagsWrapper.value = newQuickPresets.flagsetc
    }
    blockRefresh.value = oldBlockRefresh
  },
})

const quickPresetsComplete = computed(() => {
  const result = {}
  for (const [name, theQuickPresets] of Object.entries(props.quickPresets)) {
    let skip = false
    for (const key of [
      'inheritance',
      'frequency',
      'impact',
      'quality',
      'chromosomes',
      'flagsetc',
    ]) {
      if (!theQuickPresets[key]) {
        skip = true
        break
      }
    }
    if (!skip) {
      result[name] = theQuickPresets
    }
  }
  return result
})

/** Refresh all presets. */
const refreshAllRefs = () => {
  refreshInheritanceRef()
  refreshQualityRef()
  refreshValueRefs()
  refreshQuickPreset()
}

/** React to store changes by adjusting the selection fields. */
onMounted(() => {
  variantQueryStore.initializeRes.then(() => {
    updatePresetSetLoading()
    refreshAllRefs()
    variantQueryStore.$subscribe((_mutation, _state) => {
      if (!blockRefresh.value) {
        refreshAllRefs()
      }
    })
  })
})
</script>

<template>
  <div class="row text-muted small">
    <span class="mr-2 badge badge-secondary">{{ presetSetLabel }}</span>
    <template v-if="variantQueryStore.filtrationComplexityMode === 'dev'">
      &mdash;<span class="ml-2">{{ presetSource }}</span>
    </template>
  </div>
  <div class="row">
    <div class="col-1 pl-0 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'quickPresets-' + idSuffix"
      >
        Quick Presets
        <i-mdi-arrow-right />
      </label>
      <select
        :id="'quickPresets-' + idSuffix"
        v-model="quickPresetWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in quickPresetsComplete" :value="name">
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsInheritance-' + idSuffix"
      >
        Inheritance
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsInheritance-' + idSuffix"
        v-model="inheritanceWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.inheritance"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsFrequency-' + idSuffix"
      >
        Frequency
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsFrequency-' + idSuffix"
        v-model="frequencyWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.frequency"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsImpact-' + idSuffix"
      >
        Impact
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsImpact-' + idSuffix"
        v-model="impactWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in categoryPresets.impact" :value="name">
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsQuality-' + idSuffix"
      >
        Quality
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsQuality-' + idSuffix"
        v-model="qualityWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in categoryPresets.quality" :value="name">
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsChromosomes-' + idSuffix"
      >
        Chromosomes / Genes
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsChromosomes-' + idSuffix"
        v-model="chromosomesWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.chromosomes"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'flagsWrapper-' + idSuffix"
      >
        Flags etc.
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'flagsWrapper-' + idSuffix"
        v-model="flagsWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in categoryPresets.flagsetc" :value="name">
          {{ value.label ?? name }}
        </option>
        <option disabled>custom</option>
      </select>
    </div>
  </div>
  <div>
    <div
      v-if="props.showFiltrationInlineHelp"
      class="alert alert-secondary small p-2 mt-2 mb-0"
    >
      <i-mdi-information />
      You can use the Quick Presets to get sensible settings to start out with,
      e.g, with a "recessive hypothesis." Then, use the category dropdown boxes
      Inheritance, Frequency, etc. to select coarse-grain presets in each filter
      settings category. Finally, you can fine-tune all filter settings in the
      form below.
    </div>
  </div>
</template>

<style scoped>
@import 'bootstrap/dist/css/bootstrap.css';
</style>
