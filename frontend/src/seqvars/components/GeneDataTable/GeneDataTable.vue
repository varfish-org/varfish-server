<script setup lang="ts">
import { swapIndices } from 'remeda'
import { ref } from 'vue'

import { SeqvarsQueryPresetsSetVersionDetails } from '@varfish-org/varfish-api/lib'
import { Query } from '@/seqvars/types'
import { getQueryLabel } from '@/seqvars/utils'

import data from './fixture.GeneDataTable.json'

type GeneItem = {
  gene: string
  effect: string
  '%_freq': number
  hom: number
  pLI_gnomAD: number
  pLI_ExAC: number
  Z_syn_gnomAD: number
  Z_mis_gnomAD: number
  acc_gain: number
  acc_loss: number
  don_gain: number
  CADD_PHRI: number
  index: string
  father: string
  mother: string
  ACMG: string
  ClinVar: string
}

const props = defineProps<{
  selectedQueryIndex: number
  presetDetails: SeqvarsQueryPresetsSetVersionDetails
  queries: Query[]
}>()

const columns = ref(
  (
    [
      { title: 'gene', key: 'gene' },
      { title: 'effect', key: 'effect' },
      { title: '% freq', key: '%_freq' },
      { title: '#hom', key: 'hom' },
      { title: 'pLI - gnomAD', key: 'pLI_gnomAD' },
      { title: 'pLI - ExAC', key: 'pLI_ExAC' },
      { title: 'Z Syn - gnomAD', key: 'Z_syn_gnomAD' },
      { title: 'Z Mis - gnomAD', key: 'Z_mis_gnomAD' },
      { title: 'acc-gain', key: 'acc_gain' },
      { title: 'acc-loss', key: 'acc_loss' },
      { title: 'don-gain', key: 'don_gain' },
      { title: 'CADD-PHRI', key: 'CADD_PHRI' },
      { title: 'index', key: 'index' },
      { title: 'father', key: 'father' },
      { title: 'mother', key: 'mother' },
      { title: 'ACMG', key: 'ACMG' },
      { title: 'ClinVar', key: 'ClinVar' },
    ] satisfies { title: string; key: keyof GeneItem }[]
  ).map((c) => ({ ...c, enabled: true })),
)

const loading = ref(false)
const itemsPerPage = ref(18)
const searchQuery = ref('')
const serverItems = ref<GeneItem[]>([])
const totalItems = ref(data.length)

const emit = defineEmits<{ showDetails: [GeneItem] }>()

async function fakeLoadItems({
  page,
  itemsPerPage,
  sortBy,
}: {
  page: number
  itemsPerPage: number
  sortBy: { key: keyof GeneItem; order: 'desc' | 'asc' }[]
}) {
  loading.value = true
  await new Promise((resolve) => setTimeout(resolve, 500))

  const start = (page - 1) * itemsPerPage
  const end = start + itemsPerPage
  const items = [...data, ...data]

  if (sortBy.length) {
    const [{ key, order }] = sortBy
    items.sort((a, b) => {
      const aValue = a[key]!
      const bValue = b[key]!
      return (order === 'desc' ? bValue > aValue : aValue < bValue) ? 1 : -1
    })
  }

  const paginated = items.slice(start, end)

  serverItems.value = paginated as any
  totalItems.value = items.length
  loading.value = false
}
</script>

<template>
  <div
    style="
      padding: 4px 16px;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      background-color: #f9f9f9;
    "
  >
    <div>
      #{{ props.selectedQueryIndex + 1 }}
      {{ getQueryLabel({ ...props, index: props.selectedQueryIndex }) }}
    </div>
    <v-dialog max-width="500">
      <template #activator="{ props: activatorProps }">
        <v-btn
          v-bind="activatorProps"
          size="small"
          variant="plain"
          append-icon="mdi-tune-variant"
          text="Customize"
        />
      </template>

      <template #default="{ isActive }">
        <v-card title="Customize Columns">
          <v-card-text style="height: auto; overflow-y: auto">
            <div
              v-for="(col, index) in columns"
              :key="col.key"
              style="display: flex; align-items: center; gap: 8px"
            >
              <div style="display: flex; gap: 4px">
                <v-btn
                  density="compact"
                  size="x-small"
                  icon="mdi-arrow-up"
                  @click="
                    columns = swapIndices(
                      columns,
                      index,
                      Math.max(index - 1, 0),
                    )
                  "
                />
                <v-btn
                  density="compact"
                  size="x-small"
                  icon="mdi-arrow-down"
                  @click="
                    columns = swapIndices(
                      columns,
                      index,
                      Math.min(index + 1, columns.length - 1),
                    )
                  "
                />
              </div>
              <v-switch
                v-model="col.enabled"
                :label="col.title"
                :hide-details="true"
                density="compact"
                color="blue"
              />
            </div>
          </v-card-text>

          <v-card-actions>
            <v-spacer></v-spacer>

            <v-btn text="Close Dialog" @click="isActive.value = false"></v-btn>
          </v-card-actions>
        </v-card>
      </template>
    </v-dialog>
  </div>

  <v-data-table-server
    v-model:items-per-page="itemsPerPage"
    density="compact"
    :headers="[
      ...columns.filter((c) => c.enabled),
      { title: 'actions', key: 'actions', align: 'end', sortable: false },
    ]"
    :items="serverItems"
    :items-length="totalItems"
    :loading="loading"
    :search="searchQuery"
    item-value="name"
    class="gene-data-table"
    style="font-size: var(--font-size-xs)"
    @update:options="fakeLoadItems"
    @click:row="(event: unknown, row: any) => emit('showDetails', row.item)"
  >
    <!-- eslint-disable-next-line vue/valid-v-slot -->
    <template #item.actions="{ item }">
      <v-icon class="me-2" size="small" @click="emit('showDetails', item)">
        mdi-arrow-right
      </v-icon>
    </template>
  </v-data-table-server>
</template>

<style>
.gene-data-table th,
.gene-data-table td {
  padding: 0 4px !important;
}
</style>
