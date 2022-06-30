<template>
  <div class="card">
    <div class="card-header d-flex w-100 justify-content-between">
      <h4 class="card-title">ClinVar for Variant</h4>
      <small v-if="detailsStore.clinvar">
        The local ClinVar copy has {{ detailsStore.clinvar.length }} record(s)
        for this variant.
        <a
          :href="
            'https://www.ncbi.nlm.nih.gov/clinvar/?term=' +
            detailsStore.smallVariant.release +
            '%3A' +
            detailsStore.smallVariant.chromosome +
            '%3A' +
            detailsStore.smallVariant.start +
            '-' +
            detailsStore.smallVariant.end
          "
          target="_blank"
          >See all records in NCBI ClinVar.</a
        >
      </small>
    </div>
    <div class="text-muted small p-2">
      <i class="iconify" data-icon="mdi:information"></i>
      Note that VarFish is using a local copy of Clinvar to display this
      information. The link-outs to NCBI ClinVar will display the most current
      data that may differ from our "frozen" copy.
    </div>
    <ul v-if="detailsStore.clinvar" class="list-group list-group-flush">
      <template v-for="(cv, index) in detailsStore.clinvar" :key="index">
        <li
          v-for="(detail, index2) in cv.details"
          :key="index2"
          class="list-group-item flex-column align-items-start border-top px-2 list-group-item-action"
        >
          <div class="d-flex w-100 justify-content-between">
            <strong class="mb-1">{{ detail.title }}</strong>
            <small>
              <a
                :href="
                  'https://www.ncbi.nlm.nih.gov/clinvar/?term=' +
                  detail.ref_cv_assertion.clinvar_accession +
                  '.' +
                  detail.ref_cv_assertion.version_no
                "
                target="_blank"
                >{{ detail.ref_cv_assertion.clinvar_accession }}.{{
                  detail.ref_cv_assertion.version_no
                }}</a
              >
            </small>
          </div>
          <div class="row">
            <div class="col-6 pl-0">
              <template v-if="detail.ref_cv_assertion.trait_sets">
                <template
                  v-for="(trait_set, index3) in detail.ref_cv_assertion
                    .trait_sets"
                  :key="index3"
                >
                  <template
                    v-for="(trait, index4) in trait_set.traits"
                    :key="index4"
                  >
                    <div v-if="trait.preferred_name === 'not specified'">
                      traits
                    </div>
                    {{ trait.preferred_name }}
                    <br />
                  </template>
                </template>
              </template>
              <em v-else>traits not specified</em>
            </div>
            <div class="col-3">
              <template v-if="detail.ref_cv_assertion.clin_sigs">
                <template
                  v-for="(clin_sig, index5) in detail.ref_cv_assertion
                    .clin_sigs"
                  :key="index5"
                >
                  {{ clin_sig.description.toLowerCase() }}
                </template>
              </template>
              <em v-else>review status not specified</em>
            </div>
            <div class="col-3 pr-0">
              <template v-if="detail.ref_cv_assertion.clin_sigs">
                <template
                  v-for="(clin_sig, index6) in detail.ref_cv_assertion
                    .clin_sigs"
                  :key="index6"
                >
                  {{ clin_sig.review_status.toLowerCase() }}
                </template>
              </template>
              <em v-else>clinical significance not specified</em>
            </div>
          </div>
        </li>
      </template>
    </ul>
    <p v-else class="text-muted text-center">
      <i>No ClinVar information available.</i>
    </p>
  </div>
</template>

<script>
import { variantDetailsStore } from "@/stores/variantDetails";

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore();
    return {
      detailsStore,
    };
  },
};
</script>
