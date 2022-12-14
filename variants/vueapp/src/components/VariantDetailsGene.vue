<script setup>
const props = defineProps({
  gene: Object,
  release: String,
  ensemblGeneId: String,
  refseqGeneId: String,
})
</script>

<template>
  <table v-if="gene" class="card-body table table-striped table-sm">
    <tbody>
      <tr>
        <th class="text-right text-nowrap">Symbol / Name</th>
        <td>
          <div v-if="gene.symbol || gene.name">
            {{ gene.symbol }} / {{ gene.name }}
          </div>
          <div v-else class="text-center text-muted">
            <i>No gene symbol or name available.</i>
          </div>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">Gene Family</th>
        <td>
          <div v-if="gene.gene_family">
            {{ gene.gene_family }}
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
            v-if="gene.ncbiSummary?.summary"
            style="max-height: 150px; overflow-y: auto !important"
          >
            {{ gene.ncbiSummary.summary }}
          </div>
          <div v-else class="text-muted text-center">
            <i>No NCBI information available.</i>
          </div>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">ClinVar for Gene</th>
        <td>
          <div v-if="gene.clinvar_pathogenicity">
            <a
              :href="'https://www.ncbi.nlm.nih.gov/gene/' + gene.entrez_id"
              target="_blank"
            >
              <span
                v-if="gene.clinvar_pathogenicity.pathogenic_count"
                class="badge-group"
              >
                <span class="badge badge-light"># PATHOGENIC VARIANTS</span>
                <span class="badge badge-danger">{{
                  gene.clinvar_pathogenicity.pathogenic_count
                }}</span>
              </span>
              <span
                v-if="gene.clinvar_pathogenicity.likely_pathogenic_count"
                class="badge-group"
              >
                <span class="badge badge-light"
                  ># LIKELY PATHOGENIC VARIANTS</span
                >
                <span class="badge badge-warning">{{
                  gene.clinvar_pathogenicity.likely_pathogenic_count
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
              gene?.hpo_terms?.length === 0 &&
              gene?.hpo_inheritance?.length === 0
            "
            class="text-muted text-center"
          >
            <i>No HPO information available.</i>
          </div>
          <div v-else>
            <div v-if="gene?.hpo_inheritance" class="float-right">
              <span
                v-for="[hpo_id, mode] in gene.hpo_inheritance"
                :key="hpo_id"
                class="badge badge-info ml-1"
                :title="hpo_id"
              >
                {{ mode }}
              </span>
            </div>
            <div v-if="gene?.hpo_terms">
              <a
                v-for="[hpo_id, hpo_name] in gene.hpo_terms"
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
          <div v-if="gene.omim && Object.keys(gene.omim).length > 0">
            <a
              v-for="(omim_names, omim_id) in gene.omim"
              :key="omim_id"
              :href="'https://www.omim.org/entry/' + omim_id"
              target="_blank"
            >
              <span class="badge-group omim-popover">
                <span class="badge badge-dark">{{ omim_id }}</span>
                <span class="badge badge-secondary">{{
                  omim_names.join(', ')
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
          <div v-if="gene.ncbiGeneRifs">
            <ul
              class="pl-3"
              style="max-height: 150px; overflow-y: auto !important"
            >
              <li v-for="(geneRif, index) in gene.ncbiGeneRifs" :key="index">
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
            v-if="gene.exac_constraints || gene.gnomad_constraints"
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
                <i-fa-solid-info-circle title="observed/expected with 90% CI" />
              </th>
            </tr>
            <tr v-if="gene.exac_constraints">
              <th rowspan="3">ExAC</th>
              <th>Synonymous</th>
              <td class="text-right">
                {{ parseFloat(gene.exac_constraints.exp_syn) }}
              </td>
              <td class="text-right">
                {{ gene.exac_constraints.n_syn }}
              </td>
              <td class="text-right">
                z =
                {{ parseFloat(gene.exac_constraints.syn_z).toFixed(3) }}
              </td>
              <td class="text-right">-</td>
            </tr>
            <tr v-if="gene.exac_constraints">
              <th>Missense</th>
              <td class="text-right">
                {{ parseFloat(gene.exac_constraints.exp_mis) }}
              </td>
              <td class="text-right">
                {{ gene.exac_constraints.n_mis }}
              </td>
              <td class="text-right">
                z =
                {{ parseFloat(gene.exac_constraints.mis_z).toFixed(3) }}
              </td>
              <td class="text-right">-</td>
            </tr>
            <tr v-if="gene.exac_constraints">
              <th>LoF</th>
              <td class="text-right">
                {{ parseFloat(gene.exac_constraints.exp_lof) }}
              </td>
              <td class="text-right">
                {{ gene.exac_constraints.n_lof }}
              </td>
              <td class="text-right">
                pLI =
                {{ parseFloat(gene.exac_constraints.pLI).toFixed(3) }}
              </td>
              <td class="text-right">-</td>
            </tr>
            <tr v-else>
              <th>ExAC</th>
              <td colspan="5" class="text-center text-muted">
                <i>No ExAC constraint information.</i>
              </td>
            </tr>
            <tr v-if="gene.gnomad_constraints">
              <th rowspan="3">gnomAD</th>
              <th>Synonymous</th>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.exp_syn) }}
              </td>
              <td class="text-right">
                {{ gene.gnomad_constraints.obs_syn }}
              </td>
              <td class="text-right">
                z =
                {{ parseFloat(gene.gnomad_constraints.syn_z).toFixed(3) }}
              </td>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.oe_syn).toFixed(3) }}
                <span class="small text-muted">
                  ({{
                    parseFloat(gene.gnomad_constraints.oe_syn_lower).toFixed(3)
                  }}-{{
                    parseFloat(gene.gnomad_constraints.oe_syn_upper).toFixed(3)
                  }})
                </span>
              </td>
            </tr>
            <tr v-if="gene.gnomad_constraints">
              <th>Missense</th>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.exp_mis).toFixed(3) }}
              </td>
              <td class="text-right">
                {{ gene.gnomad_constraints.obs_mis }}
              </td>
              <td class="text-right">
                z =
                {{ parseFloat(gene.gnomad_constraints.mis_z).toFixed(3) }}
              </td>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.oe_mis).toFixed(3) }}
                <span class="small text-muted">
                  ({{
                    parseFloat(gene.gnomad_constraints.oe_mis_lower).toFixed(3)
                  }}-{{
                    parseFloat(gene.gnomad_constraints.oe_mis_upper).toFixed(3)
                  }})
                </span>
              </td>
            </tr>
            <tr v-if="gene.gnomad_constraints">
              <th>LoF</th>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.exp_lof) }}
              </td>
              <td class="text-right">
                {{ gene.gnomad_constraints.obs_lof }}
              </td>
              <td class="text-right">
                pLI =
                {{ parseFloat(gene.gnomad_constraints.pLI).toFixed(3) }}
              </td>
              <td class="text-right">
                {{ parseFloat(gene.gnomad_constraints.oe_lof).toFixed(3) }}
                <span class="small text-muted">
                  ({{
                    parseFloat(gene.gnomad_constraints.oe_lof_lower).toFixed(3)
                  }}-{{
                    parseFloat(gene.gnomad_constraints.oe_lof_upper).toFixed(3)
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
            v-if="!refseqGeneId && !gene.entrez_id"
            class="text-center text-muted"
          >
            <i>No RefSeq gene id.</i>
          </div>
          <a
            v-else-if="gene.entrez_id"
            :href="'https://www.ncbi.nlm.nih.gov/gene/' + gene.entrez_id"
            target="_blank"
          >
            {{ gene.entrez_id }}
          </a>
          <a
            v-else
            :href="'https://www.ncbi.nlm.nih.gov/gene/' + refseqGeneId"
            target="_blank"
          >
            {{ refseqGeneId }}
          </a>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">EnsEMBL ID</th>
        <td>
          <div
            v-if="!ensemblGeneId && !gene.ensembl_gene_id"
            class="text-center text-muted"
          >
            <i>No EnsEMBL gene id.</i>
          </div>
          <a
            v-else-if="gene.ensembl_gene_id"
            :href="
              'https://' +
              (release === 'GRCh37' ? 'grch37' : 'www') +
              '.ensembl.org/Homo_sapiens/Gene/Summary?g=' +
              gene.ensembl_gene_id
            "
            target="_blank"
          >
            {{ gene.ensembl_gene_id }}
          </a>
          <a
            v-else
            :href="
              'https://' +
              (release === 'GRCh37' ? 'grch37' : 'www') +
              '.ensembl.org/Homo_sapiens/Gene/Summary?g=' +
              ensemblGeneId
            "
            target="_blank"
          >
            {{ ensemblGeneId }}
          </a>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">Alias Symbol</th>
        <td>
          <div v-if="gene.alias_symbol">
            {{ gene.alias_symbol }}
          </div>
          <div v-else class="text-muted text-center">
            <i>No alias symbol available.</i>
          </div>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">Alias Names</th>
        <td>
          <div v-if="gene.alias_name">
            {{ gene.alias_name }}
          </div>
          <div v-else class="text-muted text-center">
            <i>No alias name available.</i>
          </div>
        </td>
      </tr>
      <tr>
        <th class="text-right text-nowrap">OMIM Gene</th>
        <td>
          <div v-if="gene.omim_genes && gene.omim_genes.length > 0">
            <a
              v-for="omim_id in gene.omim_genes"
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
</template>
