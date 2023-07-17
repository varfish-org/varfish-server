<script setup>
import {
  variantTypesFields,
  transcriptTypeFields,
  effectGroupsFields,
  detailedEffectGroups,
  effectGroups,
} from './FilterFormEffectPane.fields.js'
import { useVuelidate } from '@vuelidate/core'
import { integer, minValue } from '@vuelidate/validators'
import { computed, onMounted } from 'vue'

const props = defineProps({
  showFiltrationInlineHelp: Boolean,
  filtrationComplexityMode: String,
  querySettings: Object,
})

// const soBaseUrl = 'http://www.sequenceontology.org/browser/current_release/term'

const buildEffectWrapper = (key) => {
  return computed({
    get() {
      if (!props.querySettings.effects) {
        return false
      } else {
        return props.querySettings.effects.includes(key)
      }
    },
    set(newValue) {
      if (props.querySettings.effects) {
        const isSet = props.querySettings.effects.includes(key)
        if (newValue && !isSet) {
          props.querySettings.effects.push(key)
        } else if (!newValue && isSet) {
          props.querySettings.effects = props.querySettings.effects.filter(
            val => val !== key
          )
        }
      }
    },
  })
}

const effectWrappers = {}
for (const group of detailedEffectGroups) {
  for (const field of group.fields) {
    effectWrappers[field.id] = buildEffectWrapper(field.id)
  }
}

const buildGroupWrapper = (key) => {
  return computed({
    get() {
      const currentEffects = new Set(props.querySettings.effects)
      const allSet = effectGroups[key].every((value) =>
        currentEffects.has(value)
      )
      return allSet
    },
    set(groupValue) {
      const newEffects = new Set(props.querySettings.effects)
      for (const effect of effectGroups[key]) {
        if (groupValue) {
          newEffects.add(effect)
        } else {
          newEffects.delete(effect)
        }
      }
      props.querySettings.effects = Array.from(newEffects).sort()
    },
  })
}

const groupWrappers = {}
for (const name of Object.keys(effectGroups)) {
  groupWrappers[name] = buildGroupWrapper(name)
}

const buildGroupIndeterminate = (key) => {
  return computed(() => {
    const currentEffects = new Set(props.querySettings.effects)
    const allSet = effectGroups[key].every((value) => currentEffects.has(value))
    const noneSet = effectGroups[key].every(
      (value) => !currentEffects.has(value)
    )
    return !allSet && !noneSet
  })
}

const groupIndeterminates = {}
for (const name of Object.keys(effectGroups)) {
  groupIndeterminates[name] = buildGroupIndeterminate(name)
}

const formState = {
  maxExonDist: computed({
    get() {
      return props.querySettings.max_exon_dist
    },
    set(newValue) {
      props.querySettings.max_exon_dist = newValue
    },
  }),
}

// Define validation rules.
const rules = {
  maxExonDist: {
    integer,
    minValue: minValue(0),
    $autoDirty: true,
  },
}

// Define vuelidate object
const v$ = useVuelidate(rules, formState)

onMounted(() => {
  v$.value.$touch()
})

// Define the exposed functions
defineExpose({
  v$,
})
</script>

<template>
  <div style="position: relative" class="mr-2 mt-2">
    <small
      v-if="props.filtrationComplexityMode != 'advanced'"
      class="alert alert-info"
      style="position: absolute; right: 0px; top: 0px; max-width: 200px"
    >
      <i-mdi-podium style="scale: 80%" />
      This tab has more settings if you increase the complexity to "advanced".
    </small>
    <div
      v-if="props.showFiltrationInlineHelp"
      class="alert alert-secondary small p-2 m-2 mb-0"
    >
      <i-mdi-information />
      This panel allows to fine-tune the filtration of variants based on the
      predicted molecular impact. In most cases, using the quick presets will be
      enough.
      <strong>
        This (quite complex) part of the filtration form is only intended for
        advanced/experienced users.
      </strong>
    </div>

    <!-- Row 1: Variant Types, Transcript Types, Distance to next Exon -->
    <div class="row">
      <div class="col-lg-3 col-md-6 mt-2">
        <h5>Variant Types</h5>
        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <p class="mb-1">
            <i-mdi-information />
            Configure the types of variants to display. SNV - single nucleotide
            variants, e.g., C&gt;T, indels - insertions and deletions e.g.,
            CTA&gt;C or C&gt;CTA. MNVs - multi-nucleotide variants such as
            CTA&gt;TAG. Note that most variant callers will not create MNVs and
            databases such as gnomAD also do not contain them.
          </p>
          <p class="mb-0">
            <strong>
              Most likely, you want to keep all three boxes checked.
            </strong>
          </p>
        </div>
        <div
          v-for="field in variantTypesFields"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`effect-vartypes-${field.id}`"
            type="checkbox"
            class="custom-control-input"
            v-model="props.querySettings[field.id]"
          />
          <label
            class="custom-control-label"
            :for="`effect-vartypes-${field.id}`"
          >
            {{ field.label }}
          </label>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mt-2 mb-2">
        <h5>Transcript Type</h5>
        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <p class="mb-1">
            <i-mdi-information />
            Variants can affect coding and non-coding transcripts. Some genes
            might have both kinds of transcripts, some will be limited to
            either. Effects in coding transcripts have a higher precedence than
            in non-coding ones. Note that the <strong>transcript</strong> is of
            importance here, regardless of whether they are located in exons,
            introns, the UTR, etc.
          </p>
          <p class="mb-0">
            <strong>
              You most likely want to start out with coding transcripts only.
            </strong>
          </p>
        </div>
        <div
          v-for="field in transcriptTypeFields"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`effect-transcripts-${field.id}`"
            type="checkbox"
            class="custom-control-input"
            v-model="props.querySettings[field.id]"
          />
          <label
            class="custom-control-label"
            :for="`effect-transcripts-${field.id}`"
          >
            {{ field.label }}
          </label>
        </div>
      </div>

      <div class="col-lg-3 col-md-6 mt-2 mb-2">
        <h5>Distance to next Exon</h5>

        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <p class="mb-1">
            <i-mdi-information />
            Fill this field to limit the maximal distance of variants to the
            next exon. Of course, this only makes sense if your other filters
            allow intronic variants. If you leave this field empty, no
            additional restriction is applied to the distance of variants to the
            next exon.
          </p>
          <p class="mb-0">
            <strong>
              You will usually start out keeping this field empty. It comes in
              handy if you want to limit how deep you want to consider the
              introns.
            </strong>
          </p>
        </div>
        <div class="input-group input-group-sm">
          <input
            type="number"
            class="form-control"
            placeholder="max. distance to next exon"
            id="max-exon-dist"
            v-model.number.lazy="v$.maxExonDist.$model"
            :class="{
              // 'is-valid': !v$.maxExonDist.$error,
              'is-invalid': v$.maxExonDist.$error,
            }"
          />
          <div class="input-group-append">
            <span class="input-group-text">bp</span>
          </div>
          <div
            v-for="error of v$.maxExonDist.$errors"
            :key="error.$uid"
            class="invalid-feedback"
          >
            {{ error.$message }}
          </div>
        </div>
      </div>
    </div>
    <!-- Row 2: Effect Groups -->
    <div class="row border-top mt-2">
      <div class="col-12 pt-2 mb-2">
        <h5>Effect Groups</h5>

        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-2"
        >
          <i-mdi-information />
          Use these effect group to select variants with certain effects. In
          "expert" mode, you can see the effect fields to display below.
          Explanation: <strong>all</strong> - select all effects;
          <strong>nonsynonymous</strong> - variants affecting the protein
          sequence, e.g., missense variants; <strong>splicing</strong> - splice
          donor/acceptor and splice region variants; <strong>coding</strong> -
          coding variants, e.g., missense, splice site;
          <strong>UTR / intronic</strong> - variants in UTR or introns;
          <strong>non-coding</strong> - intronic, intergenic, on non-coding
          transcripts; <strong>nonsense</strong> - loss of function variants:
          frameshifts, start loss, stop mutations, splice site mutations.
        </div>
        <div
          v-for="field in effectGroupsFields"
          class="custom-control custom-checkbox custom-control-inline"
        >
          <input
            :id="`effect-group-${field.id}`"
            type="checkbox"
            class="custom-control-input"
            :indeterminate.prop="groupIndeterminates[field.id].value"
            v-model="groupWrappers[field.id].value"
          />
          <label class="custom-control-label" :for="`effect-group-${field.id}`">
            {{ field.label }}
          </label>
        </div>
      </div>
    </div>
    <!-- Row 3: Detailed Effects -->
    <div
      class="row border-top mt-2"
      v-if="props.filtrationComplexityMode === 'advanced'"
    >
      <div class="col-12 spt-2 mb-2 mt-2">
        <h5 class="mb-0">Detailed Effects</h5>
        <div
          v-if="props.showFiltrationInlineHelp"
          class="alert alert-secondary small mt-2 p-2 mb-0"
        >
          <p class="mb-1">
            <i-mdi-information />
            Below is a list of all possible transcript-based variant
            annotations. You can select them individually to fine-tune the
            settings.
          </p>
          <p class="mb-0">
            <strong>
              In most cases, you will not need to touch these fields. Start out
              with the quick presents and rather use the effect groups from
              above.
            </strong>
          </p>
        </div>
        <div class="row">
          <div
            class="col-xl-3 col-lg-4 pl-0 pr-0 mt-3"
            v-for="group in detailedEffectGroups"
          >
            <strong>{{ group.title }}</strong>
            <br />
            <div
              v-for="field in group.fields"
              class="custom-control custom-checkbox custom-control-inline"
              :title="`${field.explanation} [${field.so}]`"
            >
              <input
                :id="`detailed-effect-${field.id}`"
                type="checkbox"
                class="custom-control-input"
                v-model="effectWrappers[field.id].value"
              />
              <label
                class="custom-control-label"
                :for="`detailed-effect-${field.id}`"
              >
                {{ field.label }}
              </label>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
