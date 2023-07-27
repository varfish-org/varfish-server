<!--
  Component to display gene details.

  The component uses a wrapping list of cards to present the information.
-->
<script setup lang="ts">
import { roundIt } from '@varfish/more-utils'

const props = defineProps<{
  /** Gene information from annonars. */
  gene: any
  /** Small variant information record. */
  smallVar: any
  /** Whether HGMD Pro display is enabled. */
  hgmdProEnabled: boolean
  /** The URL prefix to HGMD Pro. */
  hgmdProPrefix: string
}>()
</script>

<template>
  <div class="row row-cols-3 pr-2 pt-2" style="font-size: 90%">
    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%"> HGNC </span>
        </div>
        <div class="card-body pb-2 pt-2">
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

    <div class="col mb-2 pl-2 pr-0" v-if="gene?.gnomad_constraints">
      <div class="card h-100">
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            Constraints / Scores
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
          <div>
            <strong>gnomAD</strong>
            <table style="width: 100%" class="constraints-table">
              <thead class="text-center">
                <tr>
                  <th>Category</th>
                  <th>SNVs exp.</th>
                  <th>SNVs obs.</th>
                  <th>Constraint metrics</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Synonymous</td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.exp_syn, 1)"
                  ></td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.obs_syn, 1)"
                  ></td>
                  <td class="pl-2">
                    Z =
                    <span
                      v-html="roundIt(gene?.gnomad_constraints?.syn_z)"
                    /><br />
                    o/e =
                    <span v-html="roundIt(gene?.gnomad_constraints?.oe_syn)" />
                    (<span
                      v-html="roundIt(gene?.gnomad_constraints?.oe_syn_lower)"
                    />
                    -
                    <span
                      v-html="roundIt(gene?.gnomad_constraints?.oe_syn_upper)"
                    />)
                  </td>
                </tr>
                <tr>
                  <td>Missense</td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.exp_mis, 1)"
                  ></td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.obs_mis, 1)"
                  ></td>
                  <td class="pl-2">
                    Z =
                    <span
                      v-html="roundIt(gene?.gnomad_constraints?.mis_z)"
                    /><br />
                    o/e =
                    <span v-html="roundIt(gene?.gnomad_constraints?.oe_mis)" />
                    (<span
                      v-html="roundIt(gene?.gnomad_constraints?.oe_mis_lower)"
                    />
                    -
                    <span
                      v-html="roundIt(gene?.gnomad_constraints?.oe_mis_upper)"
                    />)
                  </td>
                </tr>
                <tr>
                  <td>pLoF</td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.exp_lof, 1)"
                  ></td>
                  <td
                    class="text-right pr-2"
                    v-html="roundIt(gene?.gnomad_constraints?.obs_lof, 1)"
                  ></td>
                  <td class="pl-2">
                    pLI =
                    <span
                      v-html="roundIt(gene?.gnomad_constraints?.pli)"
                    /><br />
                    o/e =
                    <span v-html="roundIt(gene?.gnomad_constraints?.oe_lof)" />
                    (<span
                      v-html="roundIt(gene?.gnomad_constraints?.oe_lof_lower)"
                    />
                    -
                    <mark
                      class="bg-warning"
                      v-html="
                        roundIt(
                          gene?.gnomad_constraints?.oe_lof_upper,
                          2,
                          'LOEUF'
                        )
                      "
                    />)
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="col mb-2 pl-2 pr-0">
      <div class="card h-100">
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            NCBI Summary
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
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
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            Alternate Identifiers
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
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
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            External Resources
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
          <div class="row">
            <div class="col-6 p-0">
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
            <div class="col-6 p-0">
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
                <a
                  :href="`https://stuart.radboudumc.nl/metadome/dashboard/transcript/${smallVar.ensembl_transcript_id}`"
                >
                  <i-mdi-launch />
                  MetaDome
                </a>
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

    <div class="col mb-2 pl-2 pr-0" v-if="gene?.acmg_sf">
      <div class="card h-100">
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            ACMG Supplementary Findings List
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
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

    <div class="col mb-2 pl-2 pr-0" v-if="gene?.ncbi?.rif_entries?.length">
      <div class="card h-100">
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            GeneRIFs
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
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
        <div class="card-header pl-2 pt-1 pb-1 pr-2">
          <span class="font-weight-bolder" style="font-size: 120%">
            Location-Specific Databases
          </span>
        </div>
        <div class="card-body pb-2 pt-2">
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
</template>

<style scoped="true">
table.constraints-table {
  border: 1px solid #30303030;
}
.constraints-table th,
.constraints-table td {
  border: 1px solid #30303030;
  background-color: #f0f0f0f0;
  padding: 2px;
}
</style>
