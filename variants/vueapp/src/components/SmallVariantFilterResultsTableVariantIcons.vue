<template>
  <div>
    <i
      title="flags & bookmarks"
      class="iconify text-muted"
      :class="params.data.flag_count ? '' : 'iconInactive'"
      :data-icon="
        params.data.flag_count ? 'fa-solid:bookmark' : 'fa-regular:bookmark'
      "
    ></i>
    <i
      title="comments"
      class="iconify text-muted"
      :class="params.data.comment_count ? '' : 'iconInactive'"
      :data-icon="
        params.data.comment_count ? 'fa-solid:comment' : 'fa-regular:comment'
      "
    ></i>
    <span
      title="ACMG rating"
      class="ml-1 badge"
      :class="acmgBadge"
      style="width: 22px; display: inline-block"
      >{{ acmgClass ? acmgClass : "-" }}</span
    >
    <a
      v-if="params.data.rsid"
      target="_blank"
      :href="
        'https://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' +
        params.data.rsid.slice(2)
      "
    >
      <i
        title="dbSNP"
        class="iconify text-muted ml-1"
        data-icon="fa-solid:database"
      ></i>
    </a>
    <i
      v-else
      title="dbSNP"
      class="iconify text-muted iconInactive ml-1"
      data-icon="fa-solid:database"
    ></i>
    <a
      v-if="params.data.in_clinvar && params.data.summary_pathogenicity_label"
      target="_blank"
      :href="
        'https://www.ncbi.nlm.nih.gov/clinvar/?term=' +
        params.data.release +
        '%3A' +
        params.data.chromosome +
        '%3A' +
        params.data.start +
        '-' +
        params.data.end
      "
    >
      <i
        title="ClinVar"
        class="iconify text-muted ml-1"
        data-icon="fa-regular:hospital"
      ></i>
    </a>
    <i
      v-else
      title="ClinVar"
      class="iconify text-muted iconInactive ml-1"
      data-icon="fa-regular:hospital"
    ></i>
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
      <i
        title="HGMD public"
        class="iconify text-muted ml-1"
        data-icon="fa-solid:globe"
      ></i>
    </a>
    <i
      v-else
      title="HGMD public"
      class="iconify text-muted iconInactive ml-1"
      data-icon="fa-solid:globe"
    ></i>
  </div>
</template>

<script>
import { filterQueryStore } from "@/stores/filterQuery";

export default {
  setup(props) {
    const queryStore = filterQueryStore();
    const symbol = props.params.data.symbol
      ? props.params.data.symbol
      : props.params.data.gene_symbol;
    const acmgClass = props.params.data.acmg_class_override
      ? props.params.data.acmg_class_override
      : props.params.data.acmg_class_auto;
    const acmgBadge = queryStore.getAcmgBadge(acmgClass);
    return {
      acmgClass,
      acmgBadge,
      symbol,
    };
  },
};
</script>

<style scoped>
.iconInactive {
  opacity: 20%;
}
</style>
