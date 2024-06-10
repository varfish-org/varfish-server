<script setup lang="ts">
import isEqual from 'fast-deep-equal'
import { computed, onMounted, ref, watch } from 'vue'

import { State } from '@/varfish/storeUtils'
import { copy } from '@/varfish/helpers'
// import DocsLink from '@bihealth/reev-frontend-lib/components/DocsLink/DocsLink.vue'
import { BOOLEAN_FLAGS, COLOR_VALUES, COLOR_FLAGS } from './constants'

/** This component's props. */
const props_ = defineProps<{
  flagsStore: any
  variant: any
  resultRowUuid: string
  caseUuid?: string
}>()

const flagsToSubmit = ref(copy({ ...props_.flagsStore.initialFlagsTemplate }))

const unsetFlags = async () => {
  flagsToSubmit.value = copy(props_.flagsStore.emptyFlagsTemplate)
}

const flagsSubmitted = computed(() => {
  if (!props_.flagsStore.flags) {
    return false
  }
  return (
    flagsToSubmit.value.flag_bookmarked ===
      props_.flagsStore.flags.flag_bookmarked &&
    flagsToSubmit.value.flag_incidental ===
      props_.flagsStore.flags.flag_incidental &&
    flagsToSubmit.value.flag_for_validation ===
      props_.flagsStore.flags.flag_for_validation &&
    flagsToSubmit.value.flag_candidate ===
      props_.flagsStore.flags.flag_candidate &&
    flagsToSubmit.value.flag_final_causative ===
      props_.flagsStore.flags.flag_final_causative &&
    flagsToSubmit.value.flag_no_disease_association ===
      props_.flagsStore.flags.flag_no_disease_association &&
    flagsToSubmit.value.flag_segregates ===
      props_.flagsStore.flags.flag_segregates &&
    flagsToSubmit.value.flag_doesnt_segregate ===
      props_.flagsStore.flags.flag_doesnt_segregate &&
    flagsToSubmit.value.flag_visual === props_.flagsStore.flags.flag_visual &&
    flagsToSubmit.value.flag_molecular ===
      props_.flagsStore.flags.flag_molecular &&
    flagsToSubmit.value.flag_validation ===
      props_.flagsStore.flags.flag_validation &&
    flagsToSubmit.value.flag_phenotype_match ===
      props_.flagsStore.flags.flag_phenotype_match &&
    flagsToSubmit.value.flag_summary === props_.flagsStore.flags.flag_summary
  )
})

const resetFlags = async () => {
  if (props_.flagsStore.flags) {
    flagsToSubmit.value.flag_bookmarked =
      props_.flagsStore.flags.flag_bookmarked
    flagsToSubmit.value.flag_incidental =
      props_.flagsStore.flags.flag_incidental
    flagsToSubmit.value.flag_for_validation =
      props_.flagsStore.flags.flag_for_validation
    flagsToSubmit.value.flag_candidate = props_.flagsStore.flags.flag_candidate
    flagsToSubmit.value.flag_final_causative =
      props_.flagsStore.flags.flag_final_causative
    flagsToSubmit.value.flag_no_disease_association =
      props_.flagsStore.flags.flag_no_disease_association
    flagsToSubmit.value.flag_segregates =
      props_.flagsStore.flags.flag_segregates
    flagsToSubmit.value.flag_doesnt_segregate =
      props_.flagsStore.flags.flag_doesnt_segregate
    flagsToSubmit.value.flag_visual = props_.flagsStore.flags.flag_visual
    flagsToSubmit.value.flag_molecular = props_.flagsStore.flags.flag_molecular
    flagsToSubmit.value.flag_validation =
      props_.flagsStore.flags.flag_validation
    flagsToSubmit.value.flag_phenotype_match =
      props_.flagsStore.flags.flag_phenotype_match
    flagsToSubmit.value.flag_summary = props_.flagsStore.flags.flag_summary
  } else {
    flagsToSubmit.value = { ...props_.flagsStore.initialFlagsTemplate }
  }
}

const onSubmitFlags = async () => {
  const flagsToSubmitEmpty = isEqual(
    flagsToSubmit.value,
    props_.flagsStore.emptyFlagsTemplate,
  )
  if (props_.flagsStore.flags && flagsToSubmitEmpty) {
    // IS not empty but SHOULD be empty, so delete the flags
    await props_.flagsStore.deleteFlags()
  } else if (!props_.flagsStore.flags && flagsToSubmitEmpty) {
    // IS empty and SHOULD be empty, so no update needed
    flagsToSubmit.value = copy(props_.flagsStore.initialFlagsTemplate)
  } else if (props_.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS not empty and SHOULD not be empty, so update the flags
    await props_.flagsStore.updateFlags(
      flagsToSubmit.value,
      props_.resultRowUuid,
    )
  } else if (!props_.flagsStore.flags && !flagsToSubmitEmpty) {
    // IS empty but SHOULD not be empty, so create the flags
    await props_.flagsStore.createFlags(
      props_.variant,
      flagsToSubmit.value,
      props_.resultRowUuid,
    )
  }
}

watch(
  () => [props_.variant, props_.caseUuid],
  async () => {
    if (
      props_.variant &&
      props_.caseUuid &&
      props_.flagsStore.storeState.state === State.Active
    ) {
      await props_.flagsStore.retrieveFlags(props_.variant, props_.caseUuid)
      await props_.flagsStore.retrieveProjectWideVariantFlags(props_.variant)
      resetFlags()
    }
  },
)

onMounted(async () => {
  if (
    props_.variant &&
    props_.caseUuid &&
    props_.flagsStore.storeState.state === State.Active
  ) {
    await props_.flagsStore.retrieveFlags(props_.variant, props_.caseUuid)
    await props_.flagsStore.retrieveProjectWideVariantFlags(props_.variant)
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
        Flags
        <!-- <DocsLink anchor="flags" /> -->
      </v-card-title>
      <v-card-subtitle class="text-overline">
        View, create, or update flags
      </v-card-subtitle>
      <v-card-text>
        <template v-if="flagsStore.projectWideVariantFlags?.length">
          <v-hover v-slot="{ isHovering, props }">
            <v-sheet
              v-for="(flags, index) in flagsStore.projectWideVariantFlags"
              :key="`projectFlags-${index}`"
              class="bg-blue-grey-lighten-3 p-3"
              :class="{ 'mt-2': index > 0 }"
              v-bind="props"
            >
              <div>
                <span class="font-weight-bold">
                  {{ flags.case }}
                </span>
                <span v-if="isHovering" class="text-blue-grey-darken-1">
                  &mdash;&nbsp;This flag is from another case in the project for
                  the same variant.
                </span>
              </div>
              <v-row no-gutters>
                <v-col cols="4">
                  <v-layout row wrap>
                    <template
                      v-for="flag in BOOLEAN_FLAGS"
                      :key="`projectFlags-${index}-boolean-flag-${flag.key}`"
                    >
                      <template v-if="flags[flag.key]">
                        <v-icon>{{ flag.icon }}</v-icon>
                      </template>
                    </template>
                  </v-layout>
                </v-col>
                <v-col cols="4">
                  <v-row no-gutters>
                    <template
                      v-for="colorFlag in COLOR_FLAGS"
                      :key="`projectFlags-${index}-color-flag-${colorFlag}`"
                    >
                      <template
                        v-for="colorValue in COLOR_VALUES"
                        :key="`projectFlags-${index}-color-value-${colorFlag}-${colorValue}`"
                      >
                        <template
                          v-if="colorValue.value === flags[colorFlag.key]"
                        >
                          <v-col cols="3">
                            <span class="text-nowrap">
                              {{ colorFlag.label }}:
                            </span>
                            <v-icon :color="colorValue.color">
                              {{ colorValue.icon }}
                            </v-icon>
                          </v-col>
                        </template>
                      </template>
                    </template>
                  </v-row>
                </v-col>
              </v-row>
            </v-sheet>
          </v-hover>
        </template>
      </v-card-text>
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
                  v-model="flagsToSubmit[flag.key]"
                  hide-details
                  density="compact"
                  :label="flag.label"
                  class="mr-2"
                >
                  <template #label>
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
                        <template #label>
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
              :loading="flagsStore.storeState.state === State.Fetching"
              @click="onSubmitFlags()"
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
