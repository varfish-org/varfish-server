<script setup lang="ts">
import { jumpToLocus } from './lib'
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Strucvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { SECTIONS } from './constants'
import { useHistoryStore } from '@/varfish/stores/history'
import { useStrucvarInfoStore } from '@bihealth/reev-frontend-lib/stores/strucvarInfo'

/** The component's props. */
const props = defineProps<{
  /** The seqvar to display for. */
  strucvar?: Strucvar
  /** The case UUID (for navigation). */
  caseUuid?: string
}>()

/** The global Router objects. */
const router = useRouter()

/** Component state; use for opening top level sections by default. */
const openedTopLevel = ref<string[]>(['gene', 'strucvar'])

/** History utility store. */
const historyStore = useHistoryStore()
/** Information about the strucvar, used to fetch information on load. */
const strucvarInfoStore = useStrucvarInfoStore()

/** Component state; HGNC identifier of selected gene. */
const selectedGeneHgncId = ref<string | undefined>(undefined)
/** Selected gene information. */
const selectedGeneInfo = computed<any | undefined>(() => {
  return (strucvarInfoStore.genesInfos || []).find((geneInfo) => {
    return geneInfo.hgnc?.hgncId === selectedGeneHgncId.value
  })
})

/** Navigate back. */
const navigateBack = () => {
  const dest = historyStore.lastWithDifferentName('strucvar-details')
  if (dest) {
    router.push(dest)
  } else {
    router.push({
      name: 'svs-filter',
      params: { case: props.caseUuid },
    })
  }
}

/** Initialize all stores. */
const initStores = async () => {
  if (props.strucvar && props.caseUuid) {
    await strucvarInfoStore.initialize(props.strucvar)
  }
}

// Initialize when mounted and when props change.
onMounted(initStores)
watch(() => [props.strucvar, props.caseUuid], initStores)
</script>

<template>
  <v-list v-model:opened="openedTopLevel" density="compact" rounded="lg">
    <!-- Navigate back in history -->
    <div class="px-2 pb-3">
      <v-btn
        block
        rounded="xs"
        variant="outlined"
        prepend-icon="mdi-arrow-left"
        @click.prevent="navigateBack"
      >
        Back
      </v-btn>
    </div>

    <!-- Jump to IGV -->
    <div class="px-2 pb-3">
      <v-btn
        block
        rounded="xs"
        variant="outlined"
        prepend-icon="mdi-launch"
        @click.prevent="jumpToLocus(strucvar)"
      >
        Jump in Local IGV
      </v-btn>
    </div>

    <v-list-item
      v-for="section in SECTIONS.TOP"
      :id="`${section.id}-nav`"
      :key="section.id"
      density="compact"
      prepend-icon="mdi-table-filter"
      @click="router.push({ params: { selectedSection: section.id } })"
    >
      <v-list-item-title class="text-no-break">
        {{ section.title }}
      </v-list-item-title>
    </v-list-item>

    <v-list-group value="gene">
      <template #activator="{ props: vProps }">
        <v-list-item
          :value="vProps"
          prepend-icon="mdi-dna"
          v-bind="vProps"
          class="text-no-break"
        >
          Gene
          <span class="font-italic">
            {{ selectedGeneInfo?.hgnc?.symbol || selectedGeneInfo?.hgnc?.agr }}
          </span>
        </v-list-item>
      </template>

      <v-list-item
        v-for="section in SECTIONS.GENE"
        :id="`${section.id}-nav`"
        :key="section.id"
        density="compact"
        @click="router.push({ params: { selectedSection: section.id } })"
      >
        <v-list-item-title class="text-no-break">
          {{ section.title }}
        </v-list-item-title>
      </v-list-item>
    </v-list-group>

    <v-list-group value="strucvar">
      <template #activator="{ props: vProps }">
        <v-list-item
          :value="vProps"
          prepend-icon="mdi-magnify-expand"
          v-bind="vProps"
        >
          <v-list-item-title class="text-no-break">
            Variant Details
          </v-list-item-title>
        </v-list-item>
      </template>

      <v-list-item
        v-for="section in SECTIONS.STRUCVAR"
        :id="`${section.id}-nav`"
        :key="section.id"
        density="compact"
        @click="router.push({ params: { selectedSection: section.id } })"
      >
        <v-list-item-title class="text-no-break">
          {{ section.title }}
        </v-list-item-title>
      </v-list-item>
    </v-list-group>
  </v-list>
</template>
