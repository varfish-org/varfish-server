<template>
  <div class="card">
    <div class="card-header">
      <h4 class="card-title">Gene</h4>
    </div>
    <table class="card-body table table-striped table-sm">
      <tbody>
        <tr>
          <th class="text-right text-nowrap">Symbol / Name</th>
          <td>
            <div v-if="detailsStore.gene.symbol || detailsStore.gene.name">
              {{ detailsStore.gene.symbol }} / {{ detailsStore.gene.name }}
            </div>
            <div v-else class="text-center text-muted">
              <i>No gene symbol or name available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Gene Family</th>
          <td>
            <div v-if="detailsStore.gene.gene_family">
              {{ detailsStore.gene.gene_family }}
            </div>
            <div v-else class="text-muted text-center">
              <i>No gene family information available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">NCBI Summary</th>
          <td>
            <div
              v-if="detailsStore.ncbiSummary.summary"
              style="max-height: 150px; overflow-y: auto !important"
            >
              {{ detailsStore.ncbiSummary.summary }}
            </div>
            <div v-else class="text-muted text-center">
              <i>No NCBI information available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">ClinVar for Gene</th>
          <td>
            <div v-if="detailsStore.gene.clinvar_pathogenicity">
              <a
                :href="
                  'https://www.ncbi.nlm.nih.gov/gene/' +
                  detailsStore.gene.entrez_id
                "
                target="_blank"
              >
                <span
                  v-if="
                    detailsStore.gene.clinvar_pathogenicity.pathogenic_count
                  "
                  class="badge-group"
                >
                  <span class="badge badge-light"># PATHOGENIC VARIANTS</span>
                  <span class="badge badge-danger">{{
                    detailsStore.gene.clinvar_pathogenicity.pathogenic_count
                  }}</span>
                </span>
                <span
                  v-if="
                    detailsStore.gene.clinvar_pathogenicity
                      .likely_pathogenic_count
                  "
                  class="badge-group"
                >
                  <span class="badge badge-light"
                    ># LIKELY PATHOGENIC VARIANTS</span
                  >
                  <span class="badge badge-warning">{{
                    detailsStore.gene.clinvar_pathogenicity
                      .likely_pathogenic_count
                  }}</span>
                </span>
              </a>
            </div>
            <div v-else class="text-muted text-center">
              <i>No ClinVar information available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">HPO Terms</th>
          <td>
            <div
              v-if="
                detailsStore.gene.hpo_terms.length === 0 &&
                detailsStore.gene.hpo_inheritance.length === 0
              "
              class="text-muted text-center"
            >
              <i>No HPO information available.</i>
            </div>
            <div v-else>
              <div v-if="detailsStore.gene.hpo_inheritance" class="float-right">
                <span
                  v-for="[hpo_id, mode] in detailsStore.gene.hpo_inheritance"
                  :key="hpo_id"
                  class="badge badge-info ml-1"
                  :title="hpo_id"
                >
                  {{ mode }}
                </span>
              </div>
              <div v-if="detailsStore.gene.hpo_terms">
                <a
                  v-for="[hpo_id, hpo_name] in detailsStore.gene.hpo_terms"
                  :key="hpo_id"
                  :href="'https://hpo.jax.org/app/browse/term/' + hpo_id"
                  target="_blank"
                >
                  <span class="badge-group">
                    <span class="badge badge-dark">{{ hpo_id }}</span>
                    <span class="badge badge-secondary">{{ hpo_name }}</span>
                  </span>
                </a>
              </div>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">OMIM Phenotypes</th>
          <td>
            <div v-if="Object.keys(detailsStore.gene.omim).length > 0">
              <a
                v-for="(omim_names, omim_id) in detailsStore.gene.omim"
                :key="omim_id"
                :href="'https://www.omim.org/entry/' + omim_id"
                target="_blank"
              >
                <span class="badge-group omim-popover">
                  <span class="badge badge-dark">{{ omim_id }}</span>
                  <span class="badge badge-secondary">{{
                    omim_names.join(", ")
                  }}</span>
                </span>
              </a>
            </div>
            <div v-else class="text-muted text-center">
              <i>No OMIM phenotype information available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Gene RIFs</th>
          <td>
            <div v-if="detailsStore.ncbiGeneRifs">
              <ul
                class="pl-3"
                style="max-height: 150px; overflow-y: auto !important"
              >
                <li
                  v-for="(geneRif, index) in detailsStore.ncbiGeneRifs"
                  :key="index"
                >
                  {{ geneRif.rif_text }}
                  <a
                    :href="
                      'https://www.ncbi.nlm.nih.gov/pubmed/?term=' +
                      geneRif.pubmed_ids.join('+')
                    "
                    target="_blank"
                    class="badge badge-secondary"
                  >
                    PubMed
                  </a>
                </li>
              </ul>
            </div>
            <div v-else class="text-center text-muted">
              <i>No Reference-into-Function Information available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Constraints</th>
          <td>
            <table
              v-if="
                detailsStore.gene.exac_constraints ||
                detailsStore.gene.gnomad_constraints
              "
              class="table"
            >
              <tr class="text-center">
                <th></th>
                <th>Category</th>
                <th>Exp. # SNVs</th>
                <th>Obs. # SNVs</th>
                <th>Constraint</th>
                <th>
                  o/e
                  <i
                    class="iconify"
                    data-icon="fa-solid:info-circle"
                    title="observed/expected with 90% CI"
                  ></i>
                </th>
              </tr>
              <tr v-if="detailsStore.gene.exac_constraints">
                <th rowspan="3">ExAC</th>
                <th>Synonymous</th>
                <td class="text-right">
                  {{ parseFloat(detailsStore.gene.exac_constraints.exp_syn) }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.exac_constraints.n_syn }}
                </td>
                <td class="text-right">
                  z =
                  {{
                    parseFloat(
                      detailsStore.gene.exac_constraints.syn_z
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">-</td>
              </tr>
              <tr v-if="detailsStore.gene.exac_constraints">
                <th>Missense</th>
                <td class="text-right">
                  {{ parseFloat(detailsStore.gene.exac_constraints.exp_mis) }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.exac_constraints.n_mis }}
                </td>
                <td class="text-right">
                  z =
                  {{
                    parseFloat(
                      detailsStore.gene.exac_constraints.mis_z
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">-</td>
              </tr>
              <tr v-if="detailsStore.gene.exac_constraints">
                <th>LoF</th>
                <td class="text-right">
                  {{ parseFloat(detailsStore.gene.exac_constraints.exp_lof) }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.exac_constraints.n_lof }}
                </td>
                <td class="text-right">
                  pLI =
                  {{
                    parseFloat(detailsStore.gene.exac_constraints.pLI).toFixed(
                      3
                    )
                  }}
                </td>
                <td class="text-right">-</td>
              </tr>
              <tr v-else>
                <th>ExAC</th>
                <td colspan="5" class="text-center text-muted">
                  <i>No ExAC constraint information.</i>
                </td>
              </tr>
              <tr v-if="detailsStore.gene.gnomad_constraints">
                <th rowspan="3">gnomAD</th>
                <th>Synonymous</th>
                <td class="text-right">
                  {{ parseFloat(detailsStore.gene.gnomad_constraints.exp_syn) }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.gnomad_constraints.obs_syn }}
                </td>
                <td class="text-right">
                  z =
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.syn_z
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.oe_syn
                    ).toFixed(3)
                  }}
                  <span class="small text-muted">
                    ({{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_syn_lower
                      ).toFixed(3)
                    }}-{{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_syn_upper
                      ).toFixed(3)
                    }})
                  </span>
                </td>
              </tr>
              <tr v-if="detailsStore.gene.gnomad_constraints">
                <th>Missense</th>
                <td class="text-right">
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.exp_mis
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.gnomad_constraints.obs_mis }}
                </td>
                <td class="text-right">
                  z =
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.mis_z
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.oe_mis
                    ).toFixed(3)
                  }}
                  <span class="small text-muted">
                    ({{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_mis_lower
                      ).toFixed(3)
                    }}-{{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_mis_upper
                      ).toFixed(3)
                    }})
                  </span>
                </td>
              </tr>
              <tr v-if="detailsStore.gene.gnomad_constraints">
                <th>LoF</th>
                <td class="text-right">
                  {{ parseFloat(detailsStore.gene.gnomad_constraints.exp_lof) }}
                </td>
                <td class="text-right">
                  {{ detailsStore.gene.gnomad_constraints.obs_lof }}
                </td>
                <td class="text-right">
                  pLI =
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.pLI
                    ).toFixed(3)
                  }}
                </td>
                <td class="text-right">
                  {{
                    parseFloat(
                      detailsStore.gene.gnomad_constraints.oe_lof
                    ).toFixed(3)
                  }}
                  <span class="small text-muted">
                    ({{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_lof_lower
                      ).toFixed(3)
                    }}-{{
                      parseFloat(
                        detailsStore.gene.gnomad_constraints.oe_lof_upper
                      ).toFixed(3)
                    }})
                  </span>
                </td>
              </tr>
              <tr v-else>
                <th>gnomAD</th>
                <td colspan="5" class="text-center text-muted">
                  <i>No gnomAD constraint information.</i>
                </td>
              </tr>
            </table>
            <div v-else class="text-center text-muted">
              <i>No constraint information.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Entrez ID</th>
          <td>
            <div
              v-if="
                !detailsStore.smallVariant.refseq_gene_id &&
                !detailsStore.gene.entrez_id
              "
              class="text-center text-muted"
            >
              <i>No RefSeq gene id.</i>
            </div>
            <a
              v-else-if="detailsStore.gene.entrez_id"
              :href="
                'https://www.ncbi.nlm.nih.gov/gene/' +
                detailsStore.gene.entrez_id
              "
              target="_blank"
            >
              {{ detailsStore.gene.entrez_id }}
            </a>
            <a
              v-else
              :href="
                'https://www.ncbi.nlm.nih.gov/gene/' +
                detailsStore.smallVariant.refseq_gene_id
              "
              target="_blank"
            >
              {{ detailsStore.smallVariant.refseq_gene_id }}
            </a>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">EnsEMBL ID</th>
          <td>
            <div
              v-if="
                !detailsStore.smallVariant.ensembl_gene_id &&
                !detailsStore.gene.ensembl_gene_id
              "
              class="text-center text-muted"
            >
              <i>No EnsEMBL gene id.</i>
            </div>
            <a
              v-else-if="detailsStore.gene.ensembl_gene_id"
              :href="
                'https://' +
                (detailsStore.smallVariant.release === 'GRCh37'
                  ? 'grch37'
                  : 'www') +
                '.ensembl.org/Homo_sapiens/Gene/Summary?g=' +
                detailsStore.gene.ensembl_gene_id
              "
              target="_blank"
            >
              {{ detailsStore.gene.ensembl_gene_id }}
            </a>
            <a
              v-else
              :href="
                'https://' +
                (detailsStore.smallVariant.release === 'GRCh37'
                  ? 'grch37'
                  : 'www') +
                '.ensembl.org/Homo_sapiens/Gene/Summary?g=' +
                detailsStore.smallVariant.ensembl_gene_id
              "
              target="_blank"
            >
              {{ detailsStore.smallVariant.ensembl_gene_id }}
            </a>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Alias Symbol</th>
          <td>
            <div v-if="detailsStore.gene.alias_symbol">
              {{ detailsStore.gene.alias_symbol }}
            </div>
            <div v-else class="text-muted text-center">
              <i>No alias symbol available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">Alias Names</th>
          <td>
            <div v-if="detailsStore.gene.alias_name">
              {{ detailsStore.gene.alias_name }}
            </div>
            <div v-else class="text-muted text-center">
              <i>No alias name available.</i>
            </div>
          </td>
        </tr>
        <tr>
          <th class="text-right text-nowrap">OMIM Gene</th>
          <td>
            <div v-if="detailsStore.gene.omim_genes.length > 0">
              <a
                v-for="omim_id in detailsStore.gene.omim_genes"
                :key="omim_id"
                :href="'https://www.omim.org/entry/' + omim_id"
                target="_blank"
              >
                {{ omim_id }}
              </a>
            </div>
            <div v-else class="text-muted text-center">
              <i>No OMIM gene information available.</i>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
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
