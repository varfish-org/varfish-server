<script setup lang="ts">
import isEqual from 'lodash.isequal'
import { State } from '@varfish/storeUtils'
import { getAcmgBadge } from '@variants/helpers'
import { useVariantAcmgRatingStore } from '@variants/stores/variantAcmgRating'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { copy } from '@variants/helpers'
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { EMPTY_ACMG_RATING_TEMPLATE } from './constants'
import { CRITERIA_PATHOGENIC, CRITERIA_BENIGN, CATEGORY_LABELS } from './constants'
import { pairwise, acmgColor, acmgLabel } from './lib'
import { AcmgRating } from '@variants/api/variantClient'

/** This component's props. */
const props = defineProps<{
  /** Project UUID. */
  projectUuid: string
  /** Case UUID. */
  caseUuid: string
  /** Sequence variant to assess. */
  seqvar?: Seqvar
}>()

/** Store for loading/storing Seqvar ACMG Ratings. */
const acmgRatingStore = useVariantAcmgRatingStore()

/** component state; currently edited `AcmgRating` */
const acmgRatingToSubmit = ref<AcmgRating>(
  EMPTY_ACMG_RATING_TEMPLATE
)
/** component state; whether the `AcmgRating` is conflicting. */
const acmgRatingConflicting = ref(false)

/** clears the ACMG rating to the blank table */
const unsetAcmgRating = () => {
  acmgRatingToSubmit.value = structuredClone(EMPTY_ACMG_RATING_TEMPLATE)
}

/** component state; whether to display detailed information */
const showHints = ref<boolean>(false)

/** reset the component state ACMG rating to the one from the store */
const resetAcmgRating = () => {
  if (acmgRatingStore.acmgRating) {
    acmgRatingToSubmit.value.pvs1 = acmgRatingStore.acmgRating.pvs1
    acmgRatingToSubmit.value.ps1 = acmgRatingStore.acmgRating.ps1
    acmgRatingToSubmit.value.ps2 = acmgRatingStore.acmgRating.ps2
    acmgRatingToSubmit.value.ps3 = acmgRatingStore.acmgRating.ps3
    acmgRatingToSubmit.value.ps4 = acmgRatingStore.acmgRating.ps4
    acmgRatingToSubmit.value.pm1 = acmgRatingStore.acmgRating.pm1
    acmgRatingToSubmit.value.pm2 = acmgRatingStore.acmgRating.pm2
    acmgRatingToSubmit.value.pm3 = acmgRatingStore.acmgRating.pm3
    acmgRatingToSubmit.value.pm4 = acmgRatingStore.acmgRating.pm4
    acmgRatingToSubmit.value.pm5 = acmgRatingStore.acmgRating.pm5
    acmgRatingToSubmit.value.pm6 = acmgRatingStore.acmgRating.pm6
    acmgRatingToSubmit.value.pp1 = acmgRatingStore.acmgRating.pp1
    acmgRatingToSubmit.value.pp2 = acmgRatingStore.acmgRating.pp2
    acmgRatingToSubmit.value.pp3 = acmgRatingStore.acmgRating.pp3
    acmgRatingToSubmit.value.pp4 = acmgRatingStore.acmgRating.pp4
    acmgRatingToSubmit.value.pp5 = acmgRatingStore.acmgRating.pp5
    acmgRatingToSubmit.value.ba1 = acmgRatingStore.acmgRating.ba1
    acmgRatingToSubmit.value.bs1 = acmgRatingStore.acmgRating.bs1
    acmgRatingToSubmit.value.bs2 = acmgRatingStore.acmgRating.bs2
    acmgRatingToSubmit.value.bs3 = acmgRatingStore.acmgRating.bs3
    acmgRatingToSubmit.value.bs4 = acmgRatingStore.acmgRating.bs4
    acmgRatingToSubmit.value.bp1 = acmgRatingStore.acmgRating.bp1
    acmgRatingToSubmit.value.bp2 = acmgRatingStore.acmgRating.bp2
    acmgRatingToSubmit.value.bp3 = acmgRatingStore.acmgRating.bp3
    acmgRatingToSubmit.value.bp4 = acmgRatingStore.acmgRating.bp4
    acmgRatingToSubmit.value.bp5 = acmgRatingStore.acmgRating.bp5
    acmgRatingToSubmit.value.bp6 = acmgRatingStore.acmgRating.bp6
    acmgRatingToSubmit.value.bp7 = acmgRatingStore.acmgRating.bp7
    acmgRatingToSubmit.value.classAuto = acmgRatingStore.acmgRating.classAuto
    acmgRatingToSubmit.value.classOverride =
      acmgRatingStore.acmgRating.classOverride
  } else {
    unsetAcmgRating()
  }
}

/** returns whether the ACMG rating equals the submitted one */
const acmgRatingSubmitted = computed(() => {
  if (!acmgRatingStore.acmgRating) {
    return false
  }
  return (
    acmgRatingToSubmit.value.pvs1 === acmgRatingStore.acmgRating.pvs1 &&
    acmgRatingToSubmit.value.ps1 === acmgRatingStore.acmgRating.ps1 &&
    acmgRatingToSubmit.value.ps2 === acmgRatingStore.acmgRating.ps2 &&
    acmgRatingToSubmit.value.ps3 === acmgRatingStore.acmgRating.ps3 &&
    acmgRatingToSubmit.value.ps4 === acmgRatingStore.acmgRating.ps4 &&
    acmgRatingToSubmit.value.pm1 === acmgRatingStore.acmgRating.pm1 &&
    acmgRatingToSubmit.value.pm2 === acmgRatingStore.acmgRating.pm2 &&
    acmgRatingToSubmit.value.pm3 === acmgRatingStore.acmgRating.pm3 &&
    acmgRatingToSubmit.value.pm4 === acmgRatingStore.acmgRating.pm4 &&
    acmgRatingToSubmit.value.pm5 === acmgRatingStore.acmgRating.pm5 &&
    acmgRatingToSubmit.value.pm6 === acmgRatingStore.acmgRating.pm6 &&
    acmgRatingToSubmit.value.pp1 === acmgRatingStore.acmgRating.pp1 &&
    acmgRatingToSubmit.value.pp2 === acmgRatingStore.acmgRating.pp2 &&
    acmgRatingToSubmit.value.pp3 === acmgRatingStore.acmgRating.pp3 &&
    acmgRatingToSubmit.value.pp4 === acmgRatingStore.acmgRating.pp4 &&
    acmgRatingToSubmit.value.pp5 === acmgRatingStore.acmgRating.pp5 &&
    acmgRatingToSubmit.value.ba1 === acmgRatingStore.acmgRating.ba1 &&
    acmgRatingToSubmit.value.bs1 === acmgRatingStore.acmgRating.bs1 &&
    acmgRatingToSubmit.value.bs2 === acmgRatingStore.acmgRating.bs2 &&
    acmgRatingToSubmit.value.bs3 === acmgRatingStore.acmgRating.bs3 &&
    acmgRatingToSubmit.value.bs4 === acmgRatingStore.acmgRating.bs4 &&
    acmgRatingToSubmit.value.bp1 === acmgRatingStore.acmgRating.bp1 &&
    acmgRatingToSubmit.value.bp2 === acmgRatingStore.acmgRating.bp2 &&
    acmgRatingToSubmit.value.bp3 === acmgRatingStore.acmgRating.bp3 &&
    acmgRatingToSubmit.value.bp4 === acmgRatingStore.acmgRating.bp4 &&
    acmgRatingToSubmit.value.bp5 === acmgRatingStore.acmgRating.bp5 &&
    acmgRatingToSubmit.value.bp6 === acmgRatingStore.acmgRating.bp6 &&
    acmgRatingToSubmit.value.bp7 === acmgRatingStore.acmgRating.bp7 &&
    acmgRatingToSubmit.value.classOverride ===
      acmgRatingStore.acmgRating.classOverride
  )
})

/** returns the calculated AMCG rating following Richards et al. (2015) */
const calculateAcmgRating = computed(() => {
  const pvs = acmgRatingToSubmit.value.pvs1
  const ps =
    acmgRatingToSubmit.value.ps1 +
    acmgRatingToSubmit.value.ps2 +
    acmgRatingToSubmit.value.ps3 +
    acmgRatingToSubmit.value.ps4
  const pm =
    acmgRatingToSubmit.value.pm1 +
    acmgRatingToSubmit.value.pm2 +
    acmgRatingToSubmit.value.pm3 +
    acmgRatingToSubmit.value.pm4 +
    acmgRatingToSubmit.value.pm5 +
    acmgRatingToSubmit.value.pm6
  const pp =
    acmgRatingToSubmit.value.pp1 +
    acmgRatingToSubmit.value.pp2 +
    acmgRatingToSubmit.value.pp3 +
    acmgRatingToSubmit.value.pp4 +
    acmgRatingToSubmit.value.pp5
  const ba = acmgRatingToSubmit.value.ba1
  const bs =
    acmgRatingToSubmit.value.bs1 +
    acmgRatingToSubmit.value.bs2 +
    acmgRatingToSubmit.value.bs3 +
    acmgRatingToSubmit.value.bs4
  const bp =
    acmgRatingToSubmit.value.bp1 +
    acmgRatingToSubmit.value.bp2 +
    acmgRatingToSubmit.value.bp3 +
    acmgRatingToSubmit.value.bp4 +
    acmgRatingToSubmit.value.bp5 +
    acmgRatingToSubmit.value.bp6 +
    acmgRatingToSubmit.value.bp7
  const isPathogenic =
    (pvs === 1 && (ps >= 1 || pm >= 2 || (pm === 1 && pp === 1) || pp >= 2)) ||
    ps >= 2 ||
    (ps === 1 && (pm >= 3 || (pm >= 2 && pp >= 2) || (pm === 1 && pp >= 4)))
  const isLikelyPathogenic =
    (pvs === 1 && pm === 1) ||
    (ps === 1 && pm >= 1 && pm <= 2) ||
    (ps === 1 && pp >= 2) ||
    pm >= 3 ||
    (pm === 2 && pp >= 2) ||
    (pm === 1 && pp >= 4)
  const isLikelyBenign = (bs >= 1 && bp >= 1) || bp >= 2
  const isBenign = ba > 0 || bs >= 2
  const isConflicting =
    (isPathogenic || isLikelyPathogenic) && (isBenign || isLikelyBenign)
  acmgRatingToSubmit.value.classAuto = 3
  if (isPathogenic) {
    acmgRatingToSubmit.value.classAuto = 5
  } else if (isLikelyPathogenic) {
    acmgRatingToSubmit.value.classAuto = 4
  } else if (isBenign) {
    acmgRatingToSubmit.value.classAuto = 1
  } else if (isLikelyBenign) {
    acmgRatingToSubmit.value.classAuto = 2
  }
  if (isConflicting) {
    acmgRatingToSubmit.value.classAuto = 3
    acmgRatingConflicting.value = true
  } else {
    acmgRatingConflicting.value = false
  }
  return acmgRatingToSubmit.value.classAuto
})

/** convert empty  */
const convertEmptyToNull = () => {
  if (!acmgRatingToSubmit.value.classOverride) {
    acmgRatingToSubmit.value.classOverride = undefined
  }
}

const onSubmitAcmgRating = async () => {
  const acmgRatingToSubmitNoAuto = copy(acmgRatingToSubmit.value)
  delete acmgRatingToSubmitNoAuto['classAuto']
  const acmgRatingToSubmitEmpty = isEqual(
    acmgRatingToSubmitNoAuto,
    EMPTY_ACMG_RATING_TEMPLATE,
  )
  if (acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the ACMG rating
    await acmgRatingStore.deleteAcmgRating()
  } else if (!acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    acmgRatingToSubmit.value = copy(EMPTY_ACMG_RATING_TEMPLATE)
  } else if (acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the ACMG rating
    await acmgRatingStore.updateAcmgRating(acmgRatingToSubmit.value)
  } else if (!acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the ACMG rating
    await acmgRatingStore.createAcmgRating(
      props.seqvar,
      acmgRatingToSubmit.value,
    )
  }
}

watch(
  () => [props.seqvar, acmgRatingStore.storeState?.state],
  async () => {
    if (
      props.seqvar &&
      acmgRatingStore.storeState?.state === State.Active
    ) {
      await acmgRatingStore.retrieveAcmgRating(props.seqvar)
      resetAcmgRating()
    }
  },
)
onMounted(async () => {
  if (props.seqvar) {
    await acmgRatingStore.initialize(
      'unusedCsrfToken',
      props.projectUuid,
      props.caseUuid,
    )
    await acmgRatingStore.retrieveAcmgRating(props.seqvar)
    resetAcmgRating()
  }
})
</script>

<template>
  <!-- missing data => display loader-->
  <template v-if="!seqvar || acmgRatingStore.storeState?.state === State.Initial">
    <v-skeleton-loader
      class="mt-3 mx-auto border"
      type="heading,subtitle,text,text"
    />
  </template>
  <!-- otherwise, display card with editor -->
  <template v-else>
    <v-card>
      <v-card-title class="pb-0 pr-2">
        ACMG Rating
        <!-- <DocsLink anchor="flags" /> -->
      </v-card-title>
      <v-card-subtitle class="text-overline">
        Fill criteria to compute ACMG rating
      </v-card-subtitle>
      <v-card-text class="py-0">
        <v-checkbox
          v-model="showHints"
          label="show criteria definitions"
          hide-details
          density="compact"
          />
      </v-card-text>
      <v-card-text>
        <v-row no-gutters>
          <v-col cols="4">
            <div class="text-overline">
              Pathogenic Rules
            </div>
            <template v-for="[crit, prev] in pairwise(CRITERIA_PATHOGENIC)" :key="`crit-${crit.name}`">
              <div class="text-caption" v-if="crit?.category !== prev?.category">
                {{ CATEGORY_LABELS[crit.category] }}
              </div>
              <v-checkbox
                v-model="acmgRatingToSubmit[crit.name]"
                :hide-details="!showHints"
                :hint="crit.description"
                persistent-hint
                density="compact"
              >
                <template v-slot:label>
                  {{ crit.title }}
                  <span class="text-caption ml-1">
                    ({{ crit.synopsis }})
                  </span>
                </template>
              </v-checkbox>
            </template>
          </v-col>
          <v-col cols="4">
            <div class="text-overline">
              Benign Rules
            </div>
            <template v-for="[crit, prev] in pairwise(CRITERIA_BENIGN)" :key="`crit-${crit.name}`">
              <div class="text-caption" v-if="crit?.category !== prev?.category">
                {{ CATEGORY_LABELS[crit.category] }}
              </div>
              <v-checkbox
                v-model="acmgRatingToSubmit[crit.name]"
                :true-value="1"
                :false-value="0"
                :hide-details="!showHints"
                :hint="crit.description"
                persistent-hint
                density="compact"
              >
                <template v-slot:label>
                  {{ crit.title }}
                  <span class="text-caption ml-1">
                    ({{ crit.synopsis }})
                  </span>
                </template>
              </v-checkbox>
            </template>
          </v-col>
          <v-col cols="4">
            <div class="text-overline">
              Classification
            </div>
            <v-sheet class="bg-grey-lighten-2 pa-3">
              <div class="text-center text-h5">
                Computed Class
              </div>
              <div class="text-center">
                <v-chip
                  variant="flat"
                  rounded="xl"
                  :color="acmgColor(calculateAcmgRating)">
                  <div class="text-h4">
                    {{ calculateAcmgRating }}
                  </div>
                </v-chip>
                <div class="text-h6">
                  {{ acmgLabel(calculateAcmgRating) }}
                </div>

                <v-responsive
                    class="mx-auto"
                    max-width="300"
                  >
                  <v-text-field
                  class="mt-6"
                  density="compact"
                  variant="outlined"
                  label="ACMG class override"
                  persistent-hint
                  hint="Fill this field to override the automatically determined class."
                  v-model.number="acmgRatingToSubmit.classOverride"
                  />
                </v-responsive>
              </div>
            </v-sheet>
            <div class="text-overline mt-6">
              Data &amp; Actions
            </div>
            <div>
              <v-sheet :border="true" class="text-center py-2">
                <v-icon>mdi-asterisk</v-icon>
                no ACMG rating on server yet
              </v-sheet>
              <v-sheet :border="true" class="text-center py-2 mt-3">
                <v-icon>mdi-check-circle</v-icon>
                in sync with server
              </v-sheet>
              <v-sheet :border="true" class="text-center py-2 mt-3">
                <v-icon>mdi-close-circle-outline</v-icon>
                differences to server
              </v-sheet>
              <v-btn block variant="outlined" rounded="xs" prepend-icon="mdi-cloud-upload" class="mt-3">
                Save to Server
              </v-btn>
              <v-btn block variant="outlined" rounded="xs" prepend-icon="mdi-cloud-download" class="mt-2">
                Reset to Server State
              </v-btn>
              <v-btn block variant="outlined" rounded="xs" prepend-icon="mdi-eraser" class="mt-2">
                Clear all Criteria
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </template>

  <div class="row p-2">
    <div class="col px-0">
      <div class="row pt-4">
        <div class="col px-0">
          <strong class="text-muted mx-1">5</strong> pathogenic
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">4</strong> likely pathogenic
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">3</strong> uncertain significance
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">2</strong> likely benign
        </div>
      </div>
      <div class="row">
        <div class="col px-0">
          <strong class="text-muted mx-1">1</strong> benign
        </div>
      </div>
      <div
        class="row pt-4"
        title="Automatically determined ACMG class (Richards et al., 2015)"
      >
        <div class="col-4 px-0">
          <label for="acmg-class"><strong>ACMG classification</strong></label>
        </div>
        <div class="col px-0 pb-2">
          <div
            title="ACMG rating"
            class="badge"
            style="font-size: 1.5em"
            :class="getAcmgBadge(acmgRatingToSubmit.classAuto)"
          >
            {{ calculateAcmgRating }}
          </div>
        </div>
      </div>
      <div
        class="row"
        title="Manually override the automatically determined class"
      >
        <div class="col-4 px-0">
          <label for="acmg-class-override"
            ><strong>ACMG class override</strong></label
          >
        </div>
        <div class="col px-0">
          <input
            class="form-control form-control-sm"
            id="acmg-class-override"
            type="text"
            style="width: 2em"
            @change="convertEmptyToNull()"
            v-model.number="acmgRatingToSubmit.classOverride"
          />
        </div>
      </div>
      <div class="row pt-2">
        <div class="col px-0">
          <div class="btn-group ml-auto">
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="unsetAcmgRating()"
            >
              Clear
            </button>
            <button
              type="button"
              class="btn btn-sm btn-secondary"
              @click="resetAcmgRating()"
            >
              Reset
            </button>
            <button
              type="submit"
              class="btn btn-sm"
              :class="
                acmgRatingConflicting
                  ? 'btn-warning'
                  : acmgRatingSubmitted
                  ? 'btn-success'
                  : 'btn-primary'
              "
              @click="onSubmitAcmgRating()"
            >
              <i-fa-info-circle v-if="acmgRatingConflicting" />
              <i-fa-solid-star v-else-if="acmgRatingSubmitted" />
              <i-fa-regular-star v-else />
              Submit
            </button>
          </div>
        </div>
      </div>
      <div class="row pt-4 pb-0" v-if="acmgRatingConflicting">
        <div class="col px-0">
          <div class="alert alert-warning p-2">
            <i-fa-solid-info-circle class="mr-1" />
            <strong>Caution!</strong> Conflicting interpretation of variant.
          </div>
        </div>
      </div>
      <div class="row pt-2">
        <div class="col px-0">
          <div class="alert alert-secondary text-small text-muted p-2">
            <i-fa-solid-info-circle />
            Select all fulfilled criteria to get the classification following
            Richards <i>et al.</i> (2015). If necessary, you can also specify a
            manual override.
            <span class="badge badge-primary">Submit</span> indicates that there
            are changes not yet submitted, while
            <span class="badge badge-success">Submit</span> indicates that
            changes have been submitted or not made at all.
            <span class="badge badge-warning">Submit</span> indicates that there
            are conflicting variant interpretations. In that case, submission is
            possible, but not recommended. Press
            <span class="badge badge-secondary">Reset</span> to reset the form
            to the last submitted state. Press
            <span class="badge badge-secondary">Clear</span> and
            <span class="badge badge-primary">Submit</span> to delete ACMG
            rating.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/** fix bootstrap label spacing */
.v-input--density-compact {
  --v-input-control-height: 20px;
}
.v-application label {
  margin-bottom: 0;
}
</style>
