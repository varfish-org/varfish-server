<script setup lang="ts">
/**
 * Display navigation sidebard for seqvar details view.
 */

import { useSeqvarInfoStore } from '@bihealth/reev-frontend-lib/stores/seqvarInfo'
import { useGeneInfoStore } from '@bihealth/reev-frontend-lib/stores/geneInfo'
import { jumpToLocus } from './lib'
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Seqvar } from '@bihealth/reev-frontend-lib/lib/genomicVars'
import { SECTIONS } from './constants'
import { useHistoryStore } from '@/varfish/stores/history'

/** The component's props. */
const props = defineProps<{
  /** The seqvar to display for. */
  seqvar?: Seqvar
  /** The HGNC ID of the affected gene. */
  hgncId?: string
  /** The case UUID (for navigation). */
  caseUuid?: string
}>()

/** Global router instance. */
const router = useRouter()

/** Component state; use for opening top level sections by default. */
const openedTopLevel = ref<string[]>(['gene', 'seqvar'])

/** History utility store. */
const historyStore = useHistoryStore()
/** Information about the sequence variant, used to fetch information on load. */
const seqvarInfoStore = useSeqvarInfoStore()
/** Information about the affected gene, used to fetch information on load. */
const geneInfoStore = useGeneInfoStore()

/** Navigate back. */
const navigateBack = () => {
  const dest = historyStore.lastWithDifferentName('seqvar-details')
  if (dest) {
    router.push(dest)
  } else {
    router.push({
      name: 'variants-filter',
      params: { case: props.caseUuid },
    })
  }
}

/** Initialize all stores. */
const initStores = async () => {
  if (props.seqvar && props.hgncId) {
    await Promise.all([
      seqvarInfoStore.initialize(props.seqvar, props.hgncId),
      geneInfoStore.initialize(props.hgncId, props.seqvar.genomeBuild),
    ])
  }
}

// Initialize when mounted and when props change.
onMounted(initStores)
watch(() => [props.seqvar, props.hgncId], initStores)
</script>

<template>
  <div>
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
          @click.prevent="jumpToLocus(props.seqvar)"
        >
          Jump in Local IGV
        </v-btn>
      </div>

      <template v-if="geneInfoStore.hgncId?.length">
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
                {{
                  seqvarInfoStore?.geneInfo?.hgnc?.symbol ||
                  seqvarInfoStore?.geneInfo?.hgnc?.agr
                }}
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
      </template>
      <template v-else>
        <v-list-item
          prepend-icon="mdi-dna"
          class="font-italic text-grey-darken-2"
        >
          No Gene
        </v-list-item>
      </template>

      <v-list-group value="seqvar">
        <template #activator="{ props: vProps }">
          <v-list-item
            :value="vProps"
            v-bind="vProps"
            prepend-icon="mdi-magnify-expand"
            class="text-no-wrap"
          >
            Variant
          </v-list-item>
        </template>

        <v-list-item
          v-for="section in SECTIONS.SEQVAR"
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
  </div>
</template>
