<script setup lang="ts">
import {
  LinearStrucvar,
  Strucvar,
} from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { computed, onMounted, ref, toRaw, watch } from 'vue'

import {
  AcmgRating,
  acmgRatingEqual,
  strucvarAssign,
} from '@/svs/api/strucvarClient'
import { useSvAcmgRatingStore } from '@/svs/stores/svAcmgRating'
import { State } from '@/varfish/storeUtils'
import { useCtxStore } from '@/varfish/stores/ctx'

import { EMPTY_ACMG_RATING_TEMPLATE } from './constants'
import { acmgColor, acmgLabel } from './lib'

/** This component's props. */
const props = defineProps<{
  /** Project UUID. */
  projectUuid?: string
  /** Case UUID. */
  caseUuid?: string
  /** Sequence variant to assess. */
  strucvar?: Strucvar
  /** UUID of the result row. */
  resultRowUuid: string
}>()

const strucvar = computed<LinearStrucvar>(() => {
  return props.strucvar as LinearStrucvar
})

/** Context store. */
const ctxStore = useCtxStore()
/** Store for loading/storing Seqvar ACMG Ratings. */
const acmgRatingStore = useSvAcmgRatingStore()

/** component state; currently edited `AcmgRating` */
const acmgRatingToSubmit = ref<AcmgRating>(EMPTY_ACMG_RATING_TEMPLATE)

/** Convert empty string to undefined for `classOverride`. */
const convertEmptyToUndefined = () => {
  if (!acmgRatingToSubmit.value.classOverride) {
    acmgRatingToSubmit.value.classOverride = undefined
  }
}

/** clears the ACMG rating to the blank table */
const clearAcmgRating = () => {
  acmgRatingToSubmit.value = structuredClone(EMPTY_ACMG_RATING_TEMPLATE)
  if (strucvar.value) {
    strucvarAssign(acmgRatingToSubmit.value, strucvar.value)
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
  if (strucvar.value) {
    strucvarAssign(acmgRatingToSubmit.value, strucvar.value)
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
      strucvar.value!,
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
  () => [
    props.strucvar,
    props.projectUuid,
    props.caseUuid,
    acmgRatingStore.storeState,
  ],
  async () => {
    if (strucvar.value && props.projectUuid && props.caseUuid) {
      if (acmgRatingStore.storeState.state !== State.Active) {
        await acmgRatingStore.initialize(props.projectUuid, props.caseUuid)
      }
      acmgRatingStore.setStrucvar(strucvar.value)
      resetAcmgRatingToStore()
    }
  },
)
onMounted(async () => {
  if (strucvar.value && props.projectUuid && props.caseUuid) {
    await acmgRatingStore.initialize(props.projectUuid, props.caseUuid)
    acmgRatingStore.setStrucvar(strucvar.value)
    resetAcmgRatingToStore()
  }
})
</script>

<template>
  <!-- missing data => display loader-->
  <template
    v-if="!strucvar || acmgRatingStore.storeState?.state === State.Initial"
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
      <v-card-text>
        <v-row no-gutters>
          <v-col cols="4">
            <div class="text-overline">Classification</div>
            <v-sheet class="bg-grey-lighten-2 pa-3">
              <div class="text-center">
                <v-chip
                  variant="flat"
                  rounded="xl"
                  :color="acmgColor(acmgRatingToSubmit.classOverride!)"
                >
                  <div class="text-h4">
                    {{ acmgRatingToSubmit.classOverride || '-' }}
                  </div>
                </v-chip>
                <div class="text-h6">
                  {{ acmgLabel(acmgRatingToSubmit.classOverride!) }}
                </div>
                <v-responsive class="mx-auto" max-width="300">
                  <v-text-field
                    v-model.number="acmgRatingToSubmit.classOverride"
                    class="mt-3"
                    density="compact"
                    variant="outlined"
                    label="ACMG class override"
                    persistent-hint
                    hint="Decimal numbers are allowed."
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
