<script setup>
import { ref } from 'vue'

/** Define component's props. */
const props = defineProps({
  pedigree: Object,
  querySettings: Object,
})

const presetValues = {
  skip: 'skip',
  ref: 'ref',
  any: 'any',
  het: 'het',
  hom: 'hom',
  nonhom: 'non-hom',
  variant: 'variant',
  nonvariant: 'non-variant',
  nonreference: 'non-reference',
}
const genotypePresetAffected = ref(presetValues.skip)
const genotypePresetUnaffected = ref(presetValues.skip)

const memberAffected = {}
for (const member of props.pedigree) {
  memberAffected[member.name] = member.affected === 2
}

const setGenotypePresets = () => {
  for (const name of Object.keys(props.querySettings.genotype)) {
    if (
      memberAffected[name] &&
      genotypePresetAffected.value &&
      genotypePresetAffected.value !== presetValues.skip
    ) {
      props.querySettings.genotype[name] = genotypePresetAffected.value
    }
    if (
      !memberAffected[name] &&
      genotypePresetAffected.value &&
      genotypePresetUnaffected.value !== presetValues.skip
    ) {
      props.querySettings.genotype[name] = genotypePresetUnaffected.value
    }
  }
}
</script>

<template>
  <!-- Button trigger modal -->
  <button
    type="button"
    class="btn btn-sm btn-outline-secondary"
    data-toggle="modal"
    data-target="#genotypePresetModal"
  >
    <i-mdi-tools />
  </button>

  <!-- Modal -->
  <div
    id="genotypePresetModal"
    class="modal fade"
    tabindex="-1"
    role="dialog"
    aria-labelledby="genotypePresetModalLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog" role="document">
      <div class="modal-content">
        <div class="modal-header">
          <h5 id="genotypePresetModalLabel" class="modal-title">
            Genotype Presets
          </h5>
          <button
            type="button"
            class="close"
            data-dismiss="modal"
            aria-label="Close"
          >
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body text-left">
          <div class="row font-weight-bold">
            <div class="col">Unaffected</div>
            <div class="col">Affected</div>
          </div>
          <div class="row font-weight-normal">
            <div class="col">
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-skip"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.skip"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-skip"
                >
                  <i>skip</i>
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-any"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.any"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-any"
                >
                  any
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-ref"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.ref"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-ref"
                >
                  0/0
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-het"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.het"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-het"
                >
                  0/1
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-nohom"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.nonhom"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-nohom"
                >
                  0/0 or 0/1
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-novar"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.nonvariant"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-novar"
                >
                  non-variant
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-unaffected-noref"
                  v-model="genotypePresetUnaffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.nonreference"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-unaffected-noref"
                >
                  non-reference
                </label>
              </div>
            </div>
            <div class="col">
              <div class="form-check">
                <input
                  id="genotype-preset-affected-skip"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.skip"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-skip"
                >
                  <i>skip</i>
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-any"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.any"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-any"
                >
                  any
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-het"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.het"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-het"
                >
                  0/1
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-hom"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.hom"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-hom"
                >
                  1/1
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-nohom"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.nonhom"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-nohom"
                >
                  0/0 or 0/1
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-variant"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.variant"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-variant"
                >
                  variant
                </label>
              </div>
              <div class="form-check">
                <input
                  id="genotype-preset-affected-noref"
                  v-model="genotypePresetAffected"
                  class="form-check-input"
                  type="radio"
                  :value="presetValues.nonreference"
                />
                <label
                  class="form-check-label"
                  for="genotype-preset-affected-noref"
                >
                  non-reference
                </label>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            type="button"
            class="btn btn-primary"
            data-dismiss="modal"
            @click="setGenotypePresets()"
          >
            Apply
          </button>
          <button type="button" class="btn btn-secondary" data-dismiss="modal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
