<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import isEqual from 'lodash.isequal'

import { State } from '@varfish/storeUtils'
import { copy } from '@varfish/helpers'
// import DocsLink from '@bihealth/reev-frontend-lib/components/DocsLink/DocsLink.vue'
import { BOOLEAN_FLAGS, COLOR_VALUES, COLOR_FLAGS } from './constants'

/** This component's props. */
const props = defineProps<{
  flagsStore: any
  variant: any
}>()

const flagsToSubmit = ref(copy({ ...props.flagsStore.initialFlagsTemplate }))

const unsetFlags = async () => {
  flagsToSubmit.value = copy(props.flagsStore.emptyFlagsTemplate)
}

const flagsSubmitted = computed(() => {
  if (!props.flagsStore.flags) {
    return false
  }
  return (
    flagsToSubmit.value.flag_bookmarked ===
      props.flagsStore.flags.flag_bookmarked &&
    flagsToSubmit.value.flag_for_validation ===
      props.flagsStore.flags.flag_for_validation &&
    flagsToSubmit.value.flag_candidate ===
      props.flagsStore.flags.flag_candidate &&
    flagsToSubmit.value.flag_final_causative ===
      props.flagsStore.flags.flag_final_causative &&
    flagsToSubmit.value.flag_no_disease_association ===
      props.flagsStore.flags.flag_no_disease_association &&
    flagsToSubmit.value.flag_segregates ===
      props.flagsStore.flags.flag_segregates &&
    flagsToSubmit.value.flag_doesnt_segregate ===
      props.flagsStore.flags.flag_doesnt_segregate &&
    flagsToSubmit.value.flag_visual === props.flagsStore.flags.flag_visual &&
    flagsToSubmit.value.flag_molecular ===
      props.flagsStore.flags.flag_molecular &&
    flagsToSubmit.value.flag_validation ===
      props.flagsStore.flags.flag_validation &&
    flagsToSubmit.value.flag_phenotype_match ===
      props.flagsStore.flags.flag_phenotype_match &&
    flagsToSubmit.value.flag_summary === props.flagsStore.flags.flag_summary
  )
})

const resetFlags = async () => {
  if (props.flagsStore.flags) {
    flagsToSubmit.value.flag_bookmarked = props.flagsStore.flags.flag_bookmarked
    flagsToSubmit.value.flag_for_validation =
      props.flagsStore.flags.flag_for_validation
    flagsToSubmit.value.flag_candidate = props.flagsStore.flags.flag_candidate
    flagsToSubmit.value.flag_final_causative =
      props.flagsStore.flags.flag_final_causative
    flagsToSubmit.value.flag_no_disease_association =
      props.flagsStore.flags.flag_no_disease_association
    flagsToSubmit.value.flag_segregates = props.flagsStore.flags.flag_segregates
    flagsToSubmit.value.flag_doesnt_segregate =
      props.flagsStore.flags.flag_doesnt_segregate
    flagsToSubmit.value.flag_visual = props.flagsStore.flags.flag_visual
    flagsToSubmit.value.flag_molecular = props.flagsStore.flags.flag_molecular
    flagsToSubmit.value.flag_validation = props.flagsStore.flags.flag_validation
    flagsToSubmit.value.flag_phenotype_match =
      props.flagsStore.flags.flag_phenotype_match
    flagsToSubmit.value.flag_summary = props.flagsStore.flags.flag_summary
  } else {
    flagsToSubmit.value = { ...props.flagsStore.initialFlagsTemplate }
  }
}

const onSubmitFlags = async () => {
  const flagsToSubmitEmpty = isEqual(
    flagsToSubmit.value,
    props.flagsStore.emptyFlagsTemplate,
  )
  if (props.flagsStore.flags && flagsToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the flags
    await props.flagsStore.deleteFlags()
  } else if (!props.flagsStore.flags && flagsToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    flagsToSubmit.value = copy(props.flagsStore.initialFlagsTemplate)
  } else if (props.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the flags
    await props.flagsStore.updateFlags(flagsToSubmit.value)
  } else if (!props.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the flags
    await props.flagsStore.createFlags(props.variant, flagsToSubmit.value)
  }
}

watch(
  () => props.variant,
  async () => {
    if (props.variant && props.flagsStore.storeState.state === State.Active) {
      await props.flagsStore.retrieveFlags(props.variant)
      resetFlags()
    }
  },
)

onMounted(async () => {
  if (props.variant) {
    await props.flagsStore.retrieveFlags(props.variant)
    resetFlags()
  }
})
</script>

<template>
  <!-- missing data => display loader-->
  <template v-if="!(flagsStore && variant)">
    <v-skeleton-loader
      class="mt-3 mx-auto border"
      type="heading,subtitle,text,text"
    />
  </template>
  <!-- otherwise, display actual card -->
  <template v-else>
    <v-card>
      <v-card-title class="pb-0 pr-2">
        Comments
        <!-- <DocsLink anchor="comments" /> -->
      </v-card-title>
      <v-card-subtitle class="text-overline">
        View, create, or update comments
      </v-card-subtitle>
      <v-card-text>
        <v-row no-gutters>
          <v-col cols="4">
            <div class="text-body-1">Markers</div>
            <v-layout row wrap>
              <template
                v-for="flag in BOOLEAN_FLAGS"
                :key="`boolean-flag-${flag.key}`"
              >
                <v-checkbox
                  hide-details
                  density="compact"
                  v-model="flagsToSubmit[flag.key]"
                  :label="flag.label"
                  class="mr-2"
                >
                  <template v-slot:label>
                    <v-icon>{{ flag.icon }}</v-icon>
                    <v-tooltip
                      activator="parent"
                      location="top"
                      :transition="false"
                    >
                      {{ flag.label }}
                    </v-tooltip>
                  </template>
                </v-checkbox>
              </template>
            </v-layout>
          </v-col>
          <v-col cols="4">
            <v-row no-gutters>
              <template
                v-for="colorFlag in COLOR_FLAGS"
                :key="`color-flag-${colorFlag}`"
              >
                <v-col cols="3">
                  <v-radio-group v-model="flagsToSubmit[colorFlag.key]">
                    <div class="text-body-1 text-nowrap">
                      {{ colorFlag.label }}
                    </div>
                    <div
                      v-for="colorValue of COLOR_VALUES"
                      :key="`color-value-${colorFlag}-${colorValue}`"
                    >
                      <v-radio hide-details :value="colorValue.value">
                        <template v-slot:label>
                          <v-icon :color="colorValue.color">{{
                            colorValue.icon
                          }}</v-icon>
                          <v-tooltip
                            activator="parent"
                            location="top"
                            :transition="false"
                          >
                            {{ colorFlag.label }}: {{ colorValue.label }}
                          </v-tooltip>
                        </template>
                      </v-radio>
                    </div>
                  </v-radio-group>
                </v-col>
              </template>
            </v-row>
          </v-col>
          <v-col cols="4" class="px-10">
            <v-btn
              block
              class="mb-3"
              prepend-icon="mdi-close-circle-outline"
              variant="outlined"
              rounded="xs"
              @click="unsetFlags()"
            >
              Clear Selection
            </v-btn>
            <v-btn
              block
              class="mb-3"
              prepend-icon="mdi-undo"
              variant="outlined"
              rounded="xs"
              @click="resetFlags()"
            >
              Undo Changes
            </v-btn>
            <v-btn
              block
              class="mb-3"
              prepend-icon="mdi-cloud-upload"
              variant="tonal"
              rounded="xs"
              @click="onSubmitFlags()"
              :loading="flagsStore.storeState.state === State.Fetching"
            >
              Submit
            </v-btn>
            <div>
              <template v-if="flagsSubmitted">
                <v-icon>mdi-check-circle-outline</v-icon>
                up to date with server
              </template>
              <template v-else>
                <v-icon>mdi-alert-outline</v-icon>
                not bookmarked yet or local changes exist
              </template>
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
  </template>
</template>
