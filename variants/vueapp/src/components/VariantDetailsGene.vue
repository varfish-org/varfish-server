<script setup lang="ts">
const props = defineProps<{
  gene: any
  hgmdProEnabled: boolean
  hgmdProPrefix: string
}>()
</script>

<template>
  <div class="row row-cols-3 pr-2" style="font-size: 90%">
    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> HGNC </strong>
          </div>
          <div>
            <strong>symbol:</strong>
            {{ gene?.hgnc?.symbol }}
          </div>
          <div>
            <strong>name:</strong>
            {{ gene?.hgnc?.name }}
          </div>
          <div>
            <strong>cytoband:</strong>
            {{ gene?.hgnc?.location }}
          </div>
          <div>
            <strong>aliases:</strong>
            {{ gene?.hgnc?.alias_name?.join(', ') }}
          </div>
          <div>
            <strong>synonyms:</strong>
            {{ gene?.hgnc?.alias_symbol?.join(', ') }}
          </div>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> NCBI Summary </strong>
          </div>
          <div class="overflow-auto" style="max-height: 200px; font-size: 90%">
            {{ gene?.ncbi?.summary }}
            <a :href="`https://www.ncbi.nlm.nih.gov/gene/672`">
              <i-mdi-launch />
              source
            </a>
          </div>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> ACMG Supplementary Findings </strong>
          </div>
          <div>
            <strong>since ACMG SF:</strong>
            v{{ gene.acmg_sf.sf_list_version }}
          </div>
          <div>
            <strong>inheritance:</strong> {{ gene.acmg_sf.inheritance }}
          </div>
          <div>
            <strong>phenotype:</strong>
            {{ gene.acmg_sf.phenotype_category }} /
            {{ gene.acmg_sf.disease_phenotype }}
          </div>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> Alternate Identifiers </strong>
          </div>
          <div>
            <strong> HGNC: </strong>
            <a
              :href="`https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/${gene?.hgnc?.hgnc_id}`"
              target="_blank"
            >
              <i-mdi-launch />
              {{ gene?.hgnc?.hgnc_id }}
            </a>
          </div>
          <div>
            <strong> ENSEMBL: </strong>
            <a
              :href="`https://www.ensembl.org/Homo_sapiens/Gene/Summary?g=${gene?.hgnc?.ensembl_gene_id}`"
              target="_blank"
            >
              <i-mdi-launch />
              {{ gene?.hgnc?.ensembl_gene_id }}
            </a>
          </div>
          <div v-if="gene?.hgnc?.refseq_accession?.length">
            <strong> RefSeq: </strong>
            <template v-for="(accession, index) in gene.hgnc.refseq_accession">
              <template v-if="index > 0">, </template>
              <a
                :href="`https://www.ncbi.nlm.nih.gov/nuccore/?term=${accession}+AND+srcdb_refseq[PROP]`"
                target="_blank"
              >
                {{ accession }}
              </a>
            </template>
          </div>
          <div v-if="gene?.hgnc?.uniprot_ids?.length">
            <strong> UniProt: </strong>
            <template v-for="(uniprotid, index) in gene.hgnc.uniprot_ids">
              <template v-if="index > 0">, </template>
              <a
                :href="`https://www.uniprot.org/uniprotkb/${uniprotid}/entry`"
                target="_blank"
              >
                {{ uniprotid }}
              </a>
            </template>
          </div>
          <div v-if="gene?.hgnc?.pubmed_id?.length">
            <strong>Primary PMID: </strong>
            <template v-for="(pmid, index) in gene.hgnc.pubmed_id">
              <template v-if="index > 0">, </template>
              <a
                :href="`https://pubmed.ncbi.nlm.nih.gov/${pmid}/`"
                target="_blank"
              >
                {{ pmid }}
              </a>
            </template>
          </div>
          <div v-if="gene?.hgnc?.mgd_id?.length">
            <strong>MGI: </strong>
            <template v-for="(mgd_id, index) in gene.hgnc.mgd_id">
              <template v-if="index > 0">, </template>
              <a
                :href="`https://www.informatics.jax.org/marker/${mgd_id}`"
                target="_blank"
              >
                {{ mgd_id }}
              </a>
            </template>
          </div>
          <span class="text-muted" v-else> No MGI </span>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100" v-if="gene?.hgnc?.lsdb?.length">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> External Resources </strong>
          </div>
          <div class="row">
            <div class="col-6">
              <div>
                <a
                  :href="`https://www.deciphergenomics.org/gene/${gene?.hgnc?.symbol}`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  DECIPHER
                </a>
              </div>
              <div>
                <a
                  :href="`https://cancer.sanger.ac.uk/cosmic/gene/analysis?ln=${gene?.hgnc?.cosmic}`"
                  target="_blank"
                  v-if="gene?.hgnc?.cosmic"
                >
                  <i-mdi-launch />
                  COSMIC
                </a>
                <span v-else>COSMIC</span>
              </div>
              <div>
                <a
                  :href="`https://medlineplus.gov/genetics/gene/${gene?.hgnc?.symbol}/`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  MedLinePlus
                </a>
              </div>
              <div>
                <a
                  :href="`https://www.omim.org/entry/${gene?.hgnc?.omim_id[0]}`"
                  target="_blank"
                  v-if="gene?.hgnc?.omim_id.length"
                >
                  <i-mdi-launch />
                  OMIM
                </a>
                <span v-else>OMIM</span>
              </div>
              <div>
                <a
                  :href="`https://www.malacards.org/search/results?query=+[GE]+${gene?.hgnc?.symbol}`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  MalaCards
                </a>
              </div>
              <div>
                <a
                  :href="`https://mastermind.genomenon.com/detail?gene=${gene?.hgnc?.symbol}&disease=all%20diseases`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  MASTERMIND
                </a>
              </div>
              <div>
                <a
                  :href="`https://www.kegg.jp/kegg-bin/search_pathway_text?map=map&keyword=${gene?.hgnc?.symbol}&mode=1&viewImage=true`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  KEGG
                </a>
              </div>
            </div>
            <div class="col-6">
              <div>
                <a
                  :href="`${props.hgmdProPrefix}/gene.php?gene=${gene?.hgnc?.symbol}`"
                  target="_blank"
                  v-if="props.hgmdProEnabled"
                >
                  <i-mdi-launch />
                  HGMD Pro
                </a>
                <span class="text-muted" v-else>
                  <i-mdi-launch />
                  HGMD Pro
                </span>
              </div>
              <div>
                <span class="text-muted">
                  <i-mdi-launch />
                  MetaDome (TODO)
                  <!-- MetaDome need ENSEMBL transcript -->
                </span>
              </div>
              <div>
                <a
                  :href="`https://search.thegencc.org/genes/${gene?.hgnc?.hgnc_id}`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  GenCC
                </a>
              </div>
              <div>
                <template v-if="gene?.hgnc?.uniprot_ids?.length">
                  <template v-for="(uniprotid, index) in gene.hgnc.uniprot_ids">
                    <template v-if="index > 0">, </template>
                    <a
                      :href="`http://missense3d.bc.ic.ac.uk:8080/search_direct?uniprot=${uniprotid}`"
                      target="_blank"
                    >
                      <i-mdi-launch />
                      {{ uniprotid }}
                    </a>
                    (Missense3D)
                  </template>
                </template>
                <span class="text-muted" v-else> Missense3D </span>
              </div>
              <div>
                <a
                  :href="`https://varsome.com/gene/hg19/${gene?.hgnc?.hgnc_id}`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  VarSome
                </a>
              </div>
              <div>
                <a
                  :href="`https://pubmed.ncbi.nlm.nih.gov/?term=${gene?.hgnc?.hgnc_id}`"
                  target="_blank"
                >
                  <i-mdi-launch />
                  PubMed
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0" v-if="gene?.ncbi?.rif_entries?.length">
      <div class="card h-100">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> GeneRIFs </strong>
            <small> (reference into function) </small>
          </div>
          <ul
            class="list-unstyled overflow-auto"
            style="max-height: 200px; font-size: 90%"
          >
            <template v-for="entry in gene.ncbi.rif_entries">
              <li v-if="entry?.text?.length">
                {{ entry.text }}
                <a
                  :href="
                    'https://www.ncbi.nlm.nih.gov/pubmed/?term=' +
                    entry.pmids.join('+')
                  "
                  target="_blank"
                >
                  <i-mdi-launch />
                  PubMed
                </a>
              </li>
            </template>
          </ul>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100" v-if="gene?.hgnc?.lsdb?.length">
        <div class="card-body pb-2 pt-2">
          <div class="card-title mb-1">
            <strong> Location-Specific DBs </strong>
          </div>
          <div v-for="{ name, url } in gene.hgnc.lsdb">
            <a :href="name" target="_blank">
              <i-mdi-launch />
              {{ url }}
            </a>
          </div>
          <div>
            <a
              :href="`https://www.kegg.jp/kegg-bin/search_pathway_text?map=map&keyword=${gene?.hgnc?.symbol}&mode=1&viewImage=true`"
              target="_blank"
            >
              <i-mdi-launch />
              KEGG
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>

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
