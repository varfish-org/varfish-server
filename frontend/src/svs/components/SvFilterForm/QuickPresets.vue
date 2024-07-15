<script setup>
import isEqual from 'fast-deep-equal'
import { onMounted, computed, ref } from 'vue'
import { copy } from '@/varfish/helpers'
import { useSvQueryStore } from '@/svs/stores/svQuery'
import { randomString } from '@/varfish/common'

const svQueryStore = useSvQueryStore()

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

/** Internal store of inheritance preset.  If set through here, then it is only applied in the control. */
const inheritanceRef = ref(null)
const presetSource = ref(null)
const presetSetLoading = ref(false)
const presetSetLabel = ref(null)

const updatePresetSetLoading = async () => {
  let uuid
  if (
    !props.case?.presetset &&
    svQueryStore?.defaultPresetSetUuid === undefined
  ) {
    presetSetLabel.value = 'Factory Defaults'
    presetSource.value = 'Factory Defaults'
    return // short circuit in case of factory defaults
  } else {
    if (props.case?.presetset) {
      uuid = caseDetailsStore.caseObj.presetset
      presetSource.value = 'Individual Case Setting'
    } else if (svQueryStore?.defaultPresetSetUuid !== undefined) {
      uuid = svQueryStore.defaultPresetSetUuid
      presetSource.value = 'Project Default Setting'
    }
  }
  const queryPresetsClient = new QueryPresetsClient(caseDetailsStore.csrfToken)
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
  if (!props.categoryPresets.inheritance) {
    return // not fully loaded yet
  }
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
    if (newValue !== 'custom') {
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

/** Internal store of other presets.  If set through here, then it is only applied in the control. */
const valueRefs = {
  frequency: ref(null),
  impact: ref(null),
  svType: ref(null),
  chromosomes: ref(null),
  regulatory: ref(null),
  tad: ref(null),
  knownPatho: ref(null),
  genotypeCriteria: ref(null),
}

const helperIsEqual = (lhs, rhs) => {
  if (Array.isArray(lhs) && Array.isArray(rhs)) {
    return isEqual(lhs.sort(), rhs.sort())
  } else {
    return isEqual(lhs, rhs)
  }
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
      if (category === 'genotypeCriteria') {
        if (svQueryStore.querySettings !== null) {
          isCompatible = isEqual(
            svQueryStore.querySettings.genotype_criteria,
            presetValues,
          )
        }
      } else {
        isCompatible = true
        for (const [key, value] of Object.entries(presetValues)) {
          if (
            !_keysToStrip.includes(key) &&
            svQueryStore.querySettings !== null &&
            !helperIsEqual(svQueryStore.querySettings[key], value)
          ) {
            isCompatible = false
          }
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
      if (newValue !== 'custom') {
        if (!props.categoryPresets[name][newValue]) {
          return // not fully loaded yet?
        }
        const oldBlockRefresh = blockRefresh.value
        blockRefresh.value = true
        if (name === 'genotypeCriteria') {
          props.querySettings.genotype_criteria = copy(
            props.categoryPresets.genotypeCriteria[newValue],
          )
        } else {
          for (const [key, value] of Object.entries(
            props.categoryPresets[name][newValue],
          )) {
            if (!_keysToStrip.includes(key)) {
              props.querySettings[key] = value
            }
          }
        }
        blockRefresh.value = oldBlockRefresh
        if (!oldBlockRefresh) {
          refreshAllRefs()
        }
      }
    },
  })

/** Computed property for frequency presets.  If set through here, the default is applied (except for custom). */
const frequencyWrapper = makeWrapper('frequency')
/** Computed property for impact presets.  If set through here, the default is applied (except for custom). */
const impactWrapper = makeWrapper('impact')
/** Computed property for the SV types. */
const svTypeWrapper = makeWrapper('svType')
/** Computed property for chromosomes presets.  If set through here, the default is applied (except for custom). */
const chromosomesWrapper = makeWrapper('chromosomes')
/** Computed property for regulatory regions presets.  If set through here, the default is applied (except for custom). */
const regulatoryWrapper = makeWrapper('regulatory')
/** Computed property for TAD presets.  If set through here, the default is applied (except for custom). */
const tadWrapper = makeWrapper('tad')
/** Computed property for known pathogenicity presets.  If set through here, the default is applied (except for custom). */
const knownPathoWrapper = makeWrapper('knownPatho')
/** Computed property for genotype criteria presets.  If set through here, the default is applied (except for custom). */
const genotypeCriteriaWrapper = makeWrapper('genotypeCriteria')

/** Internal store of selected quick preset.  If set through here, then it is only applied in the control. */
const quickPresetRef = ref(null)

/** Refresh quick presets from actual form values.  Check each for compatibility and pick first matching. */
const refreshQuickPreset = () => {
  for (const [name, theQuickPresets] of Object.entries(props.quickPresets)) {
    if (
      isEqual(inheritanceWrapper.value, theQuickPresets.inheritance) &&
      isEqual(frequencyWrapper.value, theQuickPresets.frequency) &&
      isEqual(impactWrapper.value, theQuickPresets.impact) &&
      isEqual(svTypeWrapper.value, theQuickPresets.sv_type) &&
      isEqual(chromosomesWrapper.value, theQuickPresets.chromosomes) &&
      isEqual(regulatoryWrapper.value, theQuickPresets.regulatory) &&
      isEqual(
        genotypeCriteriaWrapper.value,
        theQuickPresets.genotype_criteria,
      ) &&
      isEqual(tadWrapper.value, theQuickPresets.tad) &&
      isEqual(knownPathoWrapper.value, theQuickPresets.known_patho)
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
      svTypeWrapper.value = newQuickPresets.sv_type
      chromosomesWrapper.value = newQuickPresets.chromosomes
      regulatoryWrapper.value = newQuickPresets.regulatory
      genotypeCriteriaWrapper.value = newQuickPresets.genotype_criteria
      tadWrapper.value = newQuickPresets.tad
      knownPathoWrapper.value = newQuickPresets.known_patho
    }
    blockRefresh.value = oldBlockRefresh
  },
})

/** Refresh all presets. */
const refreshAllRefs = () => {
  refreshInheritanceRef()
  refreshValueRefs()
  refreshQuickPreset()
}

/** React to store changes by adjusting the selection fields. */
onMounted(() => {
  svQueryStore.initializeRes.then(() => {
    updatePresetSetLoading()
    refreshAllRefs()
    svQueryStore.$subscribe((_mutation, _state) => {
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
    <template v-if="svQueryStore.filtrationComplexityMode === 'dev'">
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
        <option v-for="(value, name) in quickPresets" :value="name">
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-2 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsGenotypeCriteria-' + idSuffix"
      >
        Genotype Criteria
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsGenotypeCriteria-' + idSuffix"
        v-model="genotypeCriteriaWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.genotypeCriteria"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
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
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
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
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
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
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsSvType-' + idSuffix"
      >
        SV Type
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsSvType-' + idSuffix"
        v-model="svTypeWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in categoryPresets.svType" :value="name">
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsRegulatory-' + idSuffix"
      >
        Regulatory
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsRegulatory-' + idSuffix"
        v-model="regulatoryWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.regulatory"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsChromosomes-' + idSuffix"
      >
        Chrom. / Genes
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
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsTad-' + idSuffix"
      >
        TAD
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsTad-' + idSuffix"
        v-model="tadWrapper"
        class="custom-select custom-select-sm"
      >
        <option v-for="(value, name) in categoryPresets.tad" :value="name">
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
      </select>
    </div>

    <div class="col-1 pr-0">
      <label
        class="font-weight-bold small text-nowrap"
        :for="'presetsKnownPatho-' + idSuffix"
      >
        Pathogenic / ClinVar
        <i-mdi-arrow-down />
      </label>
      <select
        :id="'presetsKnownPatho-' + idSuffix"
        v-model="knownPathoWrapper"
        class="custom-select custom-select-sm"
      >
        <option
          v-for="(value, name) in categoryPresets.knownPatho"
          :value="name"
        >
          {{ value.label ?? name }}
        </option>
        <option value="custom">custom</option>
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
