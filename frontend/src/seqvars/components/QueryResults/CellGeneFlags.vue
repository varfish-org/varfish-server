<script setup lang="ts">
import {
  SeqvarsModeOfInheritance,
  SeqvarsResultRow,
} from '@varfish-org/varfish-api/lib'

import AbbrHint from '../QueryEditor/ui/AbbrHint.vue'

/** This component's props. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const props = withDefaults(
  defineProps<{
    /** The result row item to display the cell for. */
    item: SeqvarsResultRow
    /** Whether showing hints is enabled. */
    hintsEnabled?: boolean
  }>(),
  {
    hintsEnabled: false,
  },
)

const moiIncludes = (
  item: SeqvarsResultRow,
  moiType: SeqvarsModeOfInheritance,
) => {
  return (
    item?.payload?.variant_annotation?.gene?.phenotypes?.mode_of_inheritances ??
    []
  ).includes(moiType)
}
</script>

<template>
  <div class="text-no-wrap">
    <AbbrHint
      :hint="
        item?.payload?.variant_annotation?.gene?.phenotypes?.is_acmg_sf
          ? 'PRESENCE of gene on the ACMG Supplementary Findings List'
          : 'ABSENCE of gene on the ACMG Supplementary Findings List'
      "
      :hints-enabled="hintsEnabled"
    >
      <v-icon
        icon="mdi-alarm-light"
        :class="{
          'opacity-20':
            !item?.payload?.variant_annotation?.gene?.phenotypes?.is_acmg_sf,
        }"
      />
    </AbbrHint>

    <AbbrHint
      :hint="
        item?.payload?.variant_annotation?.gene?.phenotypes?.is_disease_gene
          ? 'Flagged as KNOWN disease gene'
          : 'NOT flagged as known disease gene'
      "
      :hints-enabled="hintsEnabled"
    >
      <v-icon
        icon="mdi-doctor"
        :class="{
          'opacity-20':
            !item?.payload?.variant_annotation?.gene?.phenotypes
              ?.is_disease_gene,
        }"
      />
    </AbbrHint>

    <template
      v-if="
        item.chrom?.toLowerCase()?.indexOf('x') === -1 &&
        item.chrom?.toLowerCase()?.indexOf('y') === -1 &&
        item.chrom?.toLowerCase()?.indexOf('m') === -1
      "
    >
      <AbbrHint
        :hint="
          moiIncludes(item, 'autosomal_dominant')
            ? 'AUTOSOMAL DOMINANT is known mode of inheritance for condition'
            : 'Not known to cause autosomal dominant conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'autosomal_dominant'),
          }"
          rounded="lg"
        >
          AD
        </v-chip>
      </AbbrHint>
      <AbbrHint
        :hint="
          moiIncludes(item, 'autosomal_recessive')
            ? 'AUTOSOMAL RECESSIVE is known mode of inheritance for condition'
            : 'Not known to cause autosomal recessive conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'autosomal_recessive'),
          }"
          rounded="lg"
        >
          AR
        </v-chip>
      </AbbrHint>
    </template>

    <template v-else-if="item.chrom?.toLowerCase()?.indexOf('x') !== -1">
      <AbbrHint
        :hint="
          moiIncludes(item, 'x_linked_dominant')
            ? 'X-LINKED DOMINANT is known mode of inheritance for condition'
            : 'Not known to cause X-linked dominant conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'x_linked_dominant'),
          }"
          rounded="lg"
        >
          AD
        </v-chip>
      </AbbrHint>
      <AbbrHint
        :hint="
          moiIncludes(item, 'x_linked_recessive')
            ? 'X-LINKED RECESSIVE is known mode of inheritance for condition'
            : 'Not known to cause X-linked recessive conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'x_linked_recessive'),
          }"
          rounded="lg"
        >
          AR
        </v-chip>
      </AbbrHint>
    </template>

    <template v-else-if="item.chrom?.toLowerCase()?.indexOf('y') !== -1">
      <AbbrHint
        :hint="
          moiIncludes(item, 'y_linked')
            ? 'X-LINKED is known mode of inheritance for condition'
            : 'Not known to cause Y-linked conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'y_linked'),
          }"
          rounded="lg"
        >
          YL
        </v-chip>
      </AbbrHint>
    </template>

    <template v-else-if="item.chrom?.toLowerCase()?.indexOf('m') !== -1">
      <AbbrHint
        :hint="
          moiIncludes(item, 'mitochondrial')
            ? 'MITOCHONDRIAL is known mode of inheritance for condition'
            : 'Not known to cause mitochondrial conditions'
        "
        :hints-enabled="hintsEnabled"
      >
        <v-chip
          density="compact"
          variant="outlined"
          class="ml-1 px-1"
          :class="{
            'opacity-20': !moiIncludes(item, 'mitochondrial'),
          }"
          rounded="lg"
        >
          MT
        </v-chip>
      </AbbrHint>
    </template>

    <template v-else>
      <v-chip
        density="compact"
        variant="outlined"
        class="ml-1 px-1 opacity-0"
        rounded="lg"
      >
        AD
      </v-chip>
      <v-chip
        density="compact"
        variant="outlined"
        class="ml-1 px-1 opacity-0"
        rounded="lg"
      >
        AR
      </v-chip>
    </template>
  </div>
</template>
