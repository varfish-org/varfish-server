<template>
  <p v-if="detailsStore.variantValidatorState === VariantValidatorStates.Done">
    <span
      class="badge-group"
      v-if="detailsStore.variantValidatorResults.metadata"
    >
      <span class="badge badge-dark">VariantValidator HGVS Version</span>
      <span class="badge badge-info">{{
        detailsStore.variantValidatorResults.metadata
          .variantvalidator_hgvs_version
      }}</span>
    </span>
    <span
      class="badge-group"
      v-if="detailsStore.variantValidatorResults.metadata"
    >
      <span class="badge badge-dark">VariantValidator Version</span>
      <span class="badge badge-info">{{
        detailsStore.variantValidatorResults.metadata.variantvalidator_version
      }}</span>
    </span>
  </p>
  <div
    class="container-fluid"
    v-if="detailsStore.variantValidatorState === VariantValidatorStates.Done"
  >
    <ul class="nav nav-pills pb-3" id="pills-tab" role="tablist">
      <template
        v-for="(
          data, identifier, index
        ) in detailsStore.variantValidatorResults"
        :key="index"
      >
        <li
          class="nav-item"
          v-if="identifier !== 'metadata' && identifier !== 'flag'"
        >
          <a
            class="nav-link"
            :class="!index ? 'active' : ''"
            :id="'variant-validator-result-' + index + '-tab'"
            data-toggle="pill"
            :href="'#variant-validator-result-' + index"
            role="tab"
            :aria-controls="'variant-validator-result-' + index"
            :aria-selected="!index ? 'true' : 'false'"
          >
            {{ identifier }}
          </a>
        </li>
      </template>
    </ul>
    <div class="tab-content">
      <template
        v-for="(
          data, identifier, index
        ) in detailsStore.variantValidatorResults"
        :key="index"
      >
        <div
          v-if="identifier !== 'metadata' && identifier !== 'flag'"
          class="tab-pane fade"
          :class="!index ? 'show active' : ''"
          :id="'variant-validator-result-' + index"
          role="tabpanel"
          :aria-labelledby="'variant-validator-result-' + index + '-tab'"
        >
          <div
            v-if="data.validation_warnings && data.validation_warnings.length"
            class="alert alert-warning"
          >
            <ul>
              <li
                v-for="(warning, indexW) in data.validation_warnings"
                :key="indexW"
              >
                {{ warning }}
              </li>
            </ul>
          </div>
          <div class="row">
            <div class="col-6 pl-0">
              <div class="card">
                <div class="card-header">
                  <h4>HGVS-Compliant Variant Descriptions</h4>
                </div>
                <table class="card-body table table-hover table-striped">
                  <thead>
                    <tr>
                      <th>Type</th>
                      <th>Variant Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-if="
                        data.hgvs_transcript_variant &&
                        data.hgvs_transcript_variant.length
                      "
                    >
                      <td>
                        Transcript <span class="badge badge-dark">:c.</span>
                      </td>
                      <td>{{ data.hgvs_transcript_variant }}</td>
                    </tr>
                    <tr
                      v-if="
                        data.hgvs_refseqgene_variant &&
                        data.hgvs_refseqgene_variant.length
                      "
                    >
                      <td>
                        RefSeq Gene <span class="badge badge-dark">:g.</span>
                      </td>
                      <td>{{ data.hgvs_refseqgene_variant }}</td>
                    </tr>
                    <tr
                      v-if="
                        data.hgvs_lrg_transcript_variant &&
                        data.hgvs_lrg_transcript_variant.length
                      "
                    >
                      <td>
                        LRG Transcript <span class="badge badge-dark">:c.</span>
                      </td>
                      <td>{{ data.hgvs_lrg_transcript_variant }}</td>
                    </tr>
                    <tr
                      v-if="
                        data.hgvs_lrg_variant && data.hgvs_lrg_variant.length
                      "
                    >
                      <td>LRG <span class="badge badge-dark">:g.</span></td>
                      <td>{{ data.hgvs_lrg_variant }}</td>
                    </tr>
                    <tr
                      v-if="
                        data.hgvs_predicted_protein_consequence &&
                        data.hgvs_predicted_protein_consequence.length
                      "
                    >
                      <td>Protein <span class="badge badge-dark">:p.</span></td>
                      <td>{{ data.hgvs_predicted_protein_consequence.tlr }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="col-6 pr-0">
              <div class="card" v-if="data.primary_assembly_loci">
                <div class="card-header">
                  <h4>Genomic Variants</h4>
                </div>
                <table class="card-body table table-hover table-striped">
                  <thead>
                    <tr>
                      <th>Variant Description</th>
                      <th>VCF Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-if="
                        data.primary_assembly_loci.grch37 &&
                        data.primary_assembly_loci.grch37
                          .hgvs_genomic_description
                      "
                    >
                      <td>
                        {{
                          data.primary_assembly_loci.grch37
                            .hgvs_genomic_description
                        }}
                      </td>
                      <td>
                        GRCh37:{{
                          data.primary_assembly_loci.grch37.vcf.chr
                        }}:{{ data.primary_assembly_loci.grch37.vcf.pos }}:{{
                          data.primary_assembly_loci.grch37.vcf.ref
                        }}:{{ data.primary_assembly_loci.grch37.vcf.alt }}
                      </td>
                    </tr>
                    <tr
                      v-if="
                        data.primary_assembly_loci.grch38 &&
                        data.primary_assembly_loci.grch38
                          .hgvs_genomic_description
                      "
                    >
                      <td>
                        {{
                          data.primary_assembly_loci.grch38
                            .hgvs_genomic_description
                        }}
                      </td>
                      <td>
                        GRCh38:{{
                          data.primary_assembly_loci.grch38.vcf.chr
                        }}:{{ data.primary_assembly_loci.grch38.vcf.pos }}:{{
                          data.primary_assembly_loci.grch38.vcf.ref
                        }}:{{ data.primary_assembly_loci.grch38.vcf.alt }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
  <div
    v-else-if="
      detailsStore.variantValidatorState === VariantValidatorStates.Running
    "
  >
    <div class="alert alert-info">
      <i class="iconify spin" data-icon="fa-solid:circle-notch"></i>&nbsp;
      <strong>Loading ...</strong>
    </div>
  </div>
  <div v-else>
    <div class="alert alert-secondary text-muted">
      <i class="iconify" data-icon="fa-solid:info-circle"></i>
      Click&nbsp;
      <span class="badge badge-primary"
        ><i class="iconify" data-icon="fa-solid:cloud-upload-alt"></i>
        Submit</span
      >&nbsp; to submit the variant to VariantValidator.org. Results will be
      displayed here.
    </div>
  </div>
  <div class="row pb-3">
    <div class="col pl-0">
      <button
        class="btn btn-primary"
        type="button"
        @click="detailsStore.queryVariantValidatorApi()"
      >
        <i class="iconify" data-icon="fa-solid:cloud-upload-alt"></i>
        Submit
      </button>
    </div>
  </div>
</template>

<script>
import { variantDetailsStore } from '@variants/stores/variantDetails'
import { filterQueryStore } from '@variants/stores/filterQuery'
import { VariantValidatorStates } from '@variants/enums'

export default {
  components: {},
  setup() {
    const detailsStore = variantDetailsStore()
    const queryStore = filterQueryStore()
    return {
      detailsStore,
      queryStore,
      VariantValidatorStates,
    }
  },
}
</script>
