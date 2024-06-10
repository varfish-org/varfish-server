<script setup lang="ts">
import { State } from '@/varfish/storeUtils'
import { useVariantAcmgRatingStore } from '@/variants/stores/variantAcmgRating'
import { computed, onMounted, ref, toRaw, watch } from 'vue'
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { EMPTY_ACMG_RATING_TEMPLATE } from './constants'
import {
  CRITERIA_PATHOGENIC,
  CRITERIA_BENIGN,
  CATEGORY_LABELS,
} from './constants'
import { pairwise, acmgColor, acmgLabel } from './lib'
import {
  AcmgRating,
  seqvarAssign,
  acmgRatingEqual,
} from '@/variants/api/variantClient'

/** This component's props. */
const props = defineProps<{
  /** Project UUID. */
  projectUuid?: string
  /** Case UUID. */
  caseUuid?: string
  /** Sequence variant to assess. */
  seqvar?: Seqvar
  /** UUID of the result row. */
  resultRowUuid: string
}>()

/** Store for loading/storing Seqvar ACMG Ratings. */
const acmgRatingStore = useVariantAcmgRatingStore()

/** component state; currently edited `AcmgRating` */
const acmgRatingToSubmit = ref<AcmgRating>(EMPTY_ACMG_RATING_TEMPLATE)
/** component state; whether the `AcmgRating` is conflicting. */
const acmgRatingConflicting = ref(false)
/** component state; whether to display detailed information */
const showHints = ref<boolean>(false)

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
  // TODO: remove these side effects
  /* eslint-disable */
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
  /* eslint-enable */
  return acmgRatingToSubmit.value.classAuto
})

/** Convert empty string to undefined for `classOverride`. */
const convertEmptyToUndefined = () => {
  if (!acmgRatingToSubmit.value.classOverride) {
    acmgRatingToSubmit.value.classOverride = undefined
  }
}

/** clears the ACMG rating to the blank table */
const clearAcmgRating = () => {
  acmgRatingToSubmit.value = structuredClone(EMPTY_ACMG_RATING_TEMPLATE)
  if (props.seqvar) {
    seqvarAssign(acmgRatingToSubmit.value, props.seqvar)
  }
}

/** reset the component state ACMG rating to the one from the store */
const resetAcmgRatingToStore = () => {
  if (acmgRatingStore.acmgRating) {
    acmgRatingToSubmit.value = structuredClone(
      toRaw(acmgRatingStore.acmgRating),
    )
  } else {
    clearAcmgRating()
  }
  if (props.seqvar) {
    seqvarAssign(acmgRatingToSubmit.value, props.seqvar)
  }
}

/** Event handler for "submit to server" button. */
const onSubmitAcmgRating = async () => {
  const acmgRatingToSubmitEmpty =
    acmgRatingToSubmit.value &&
    acmgRatingEqual(acmgRatingToSubmit.value, EMPTY_ACMG_RATING_TEMPLATE)
  if (acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the ACMG rating
    await acmgRatingStore.deleteAcmgRating()
  } else if (!acmgRatingStore.acmgRating && acmgRatingToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    acmgRatingToSubmit.value = structuredClone(EMPTY_ACMG_RATING_TEMPLATE)
  } else if (acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the ACMG rating
    await acmgRatingStore.updateAcmgRating(acmgRatingToSubmit.value)
  } else if (!acmgRatingStore.acmgRating && !acmgRatingToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the ACMG rating
    await acmgRatingStore.createAcmgRating(
      props.seqvar!,
      acmgRatingToSubmit.value,
      props.resultRowUuid,
    )
  }
}

/** Enumeration for displaying current server sync state. */
enum ServerSyncState {
  NoRatingOnServer = 'no_rating_on_server',
  InSyncWithServer = 'in_sync_with_server',
  DifferencesToServer = 'differences_to_server',
}

/** Current server sync state. */
const serverSyncState = computed<ServerSyncState>(() => {
  const acmgRatingToSubmitEmpty =
    acmgRatingToSubmit.value &&
    acmgRatingEqual(acmgRatingToSubmit.value, EMPTY_ACMG_RATING_TEMPLATE)
  if (!acmgRatingStore.acmgRating) {
    if (acmgRatingToSubmitEmpty) {
      return ServerSyncState.NoRatingOnServer
    } else {
      return ServerSyncState.DifferencesToServer
    }
  } else if (
    acmgRatingEqual(acmgRatingStore.acmgRating, acmgRatingToSubmit.value)
  ) {
    return ServerSyncState.InSyncWithServer
  } else {
    return ServerSyncState.DifferencesToServer
  }
})

watch(
  () => [props.seqvar, props.projectUuid, props.caseUuid],
  async () => {
    if (
      props.seqvar &&
      props.projectUuid &&
      props.caseUuid &&
      acmgRatingStore.storeState?.state === State.Active
    ) {
      acmgRatingStore.setSeqvar(props.seqvar)
      resetAcmgRatingToStore()
    }
  },
)
onMounted(async () => {
  if (props.seqvar && props.projectUuid && props.caseUuid) {
    await acmgRatingStore.initialize(
      'unusedCsrfToken',
      props.projectUuid,
      props.caseUuid,
    )
    acmgRatingStore.setSeqvar(props.seqvar)
    resetAcmgRatingToStore()
  }
})
</script>

<template>
  <!-- missing data => display loader-->
  <template
    v-if="!seqvar || acmgRatingStore.storeState?.state === State.Initial"
  >
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
            <div class="text-overline">Pathogenic Rules</div>
            <template
              v-for="[crit, prev] in pairwise(CRITERIA_PATHOGENIC)"
              :key="`crit-${crit.name}`"
            >
              <div
                v-if="crit?.category !== prev?.category"
                class="text-caption"
              >
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
                <template #label>
                  {{ crit.title }}
                  <span class="text-caption ml-1"> ({{ crit.synopsis }}) </span>
                </template>
              </v-checkbox>
            </template>
          </v-col>
          <v-col cols="4">
            <div class="text-overline">Benign Rules</div>
            <template
              v-for="[crit, prev] in pairwise(CRITERIA_BENIGN)"
              :key="`crit-${crit.name}`"
            >
              <div
                v-if="crit?.category !== prev?.category"
                class="text-caption"
              >
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
                <template #label>
                  {{ crit.title }}
                  <span class="text-caption ml-1"> ({{ crit.synopsis }}) </span>
                </template>
              </v-checkbox>
            </template>
          </v-col>
          <v-col cols="4">
            <div class="text-overline">Classification</div>
            <v-sheet class="bg-grey-lighten-2 pa-3">
              <div class="text-center text-h5">Computed Class</div>
              <div class="text-center">
                <v-chip
                  variant="flat"
                  rounded="xl"
                  :color="acmgColor(calculateAcmgRating)"
                >
                  <div class="text-h4">
                    {{ calculateAcmgRating }}
                  </div>
                </v-chip>
                <div class="text-h6">
                  {{ acmgLabel(calculateAcmgRating) }}
                </div>

                <v-responsive class="mx-auto" max-width="300">
                  <v-text-field
                    v-model.number="acmgRatingToSubmit.classOverride"
                    class="mt-6"
                    density="compact"
                    variant="outlined"
                    label="ACMG class override"
                    persistent-hint
                    hint="Fill this field to override the automatically determined class."
                    @change="convertEmptyToUndefined()"
                  />
                </v-responsive>
              </div>
            </v-sheet>
            <div class="text-overline mt-6">Data &amp; Actions</div>
            <div>
              <v-sheet
                v-if="serverSyncState === ServerSyncState.NoRatingOnServer"
                :border="true"
                class="text-center py-2 mt-3"
              >
                <v-icon>mdi-file-hidden</v-icon>
                no ACMG rating on server yet
              </v-sheet>
              <v-sheet
                v-else-if="serverSyncState === ServerSyncState.InSyncWithServer"
                class="text-center py-2 mt-3"
                color="green-lighten-4"
              >
                <v-icon>mdi-file-document-check-outline</v-icon>
                in sync with server
              </v-sheet>
              <v-sheet
                v-else-if="
                  serverSyncState === ServerSyncState.DifferencesToServer
                "
                class="text-center py-2 mt-3"
                color="yellow-lighten-4"
              >
                <v-icon>mdi-file-document-edit-outline</v-icon>
                differences to server
              </v-sheet>
              <v-btn
                block
                variant="outlined"
                rounded="xs"
                prepend-icon="mdi-cloud-upload"
                class="mt-3"
                @click="onSubmitAcmgRating()"
              >
                Save to Server
              </v-btn>
              <v-btn
                block
                variant="outlined"
                rounded="xs"
                prepend-icon="mdi-cloud-download"
                class="mt-2"
                @click="resetAcmgRatingToStore()"
              >
                Reset to Server State
              </v-btn>
              <v-btn
                block
                variant="outlined"
                rounded="xs"
                prepend-icon="mdi-eraser"
                class="mt-2"
                @click="clearAcmgRating()"
              >
                Clear all Criteria
              </v-btn>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </template>
</template>

<style>
/** fix bootstrap label spacing */
.v-input--density-compact {
  --v-input-control-height: 20px !important;
}
.v-application label {
  margin-bottom: 0;
}
</style>
