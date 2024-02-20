<script setup>
import { useVariantDetailsStore } from '@variants/stores/variantDetails'
import { getAcmgBadge } from '@variants/helpers'

const variantDetailsStore = useVariantDetailsStore()

// eslint-disable-next-line no-unused-vars
const props = defineProps({
  // eslint-disable-next-line vue/require-default-prop
  params: Object,
})

const selectCommentFlags = () => {
  variantDetailsStore.modalTab = 'comments-flags-tab'
  params.context.emit()
}

const symbol = props.params.data.symbol || props.params.data.gene_symbol
const acmgClass =
  props.params.data.acmg_class_override || props.params.data.acmg_class_auto
const acmgBadgeClasses = ['ml-1', 'badge', getAcmgBadge(acmgClass)]
if (!acmgClass) {
  acmgBadgeClasses.push('icon-inactive')
}
const acmgBadge = acmgBadgeClasses.join(' ')
</script>

<template>
  <div>
    <i-fa-solid-bookmark
      v-if="params.data.flag_count"
      class="text-muted"
      title="flags & bookmarks"
      @click="selectCommentFlags"
    />
    <i-fa-regular-bookmark
      v-else
      class="text-muted icon-inactive"
      title="flags & bookmarks"
    />

    <i-fa-solid-comment
      v-if="params.data.comment_count"
      class="text-muted ml-1"
    />
    <i-fa-regular-comment v-else class="text-muted icon-inactive ml-1" />

    <span
      title="ACMG rating"
      class="ml-1 badge"
      :class="acmgBadge"
      style="width: 22px; display: inline-block"
      >{{ acmgClass || '-' }}</span
    >

    <a
      v-if="params.data.rsid"
      target="_blank"
      :href="
        'https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' +
        params.data.rsid.slice(2)
      "
    >
      <i-fa-solid-database class="ml-1 text-muted" />
    </a>
    <i-fa-solid-database v-else class="ml-1 text-muted icon-inactive" />

    <a
      v-if="params.data.in_clinvar && params.data.summary_pathogenicity_label"
      target="_blank"
      :href="'https://www.ncbi.nlm.nih.gov/clinvar/?term=' + params.data.vcv"
    >
      <i-fa-regular-hospital class="ml-1 text-muted" />
    </a>
    <i-fa-regular-hospital
      v-else
      title="Not in local ClinVar copy"
      class="ml-1 text-muted icon-inactive"
    />

    <a
      v-if="params.data.hgmd_public_overlap"
      target="_blank"
      :href="
        'http://www.hgmd.cf.ac.uk/ac/gene.php?gene=' +
        symbol +
        '&accession=' +
        params.data.hgmd_accession
      "
    >
      <i-fa-solid-globe class="ml-1 text-muted" />
    </a>
    <i-fa-solid-globe v-else class="ml-1 text-muted icon-inactive" />
  </div>
</template>

<style>
.icon-inactive {
  opacity: 20%;
}
</style>
