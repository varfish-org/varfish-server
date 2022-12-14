import VariantDetailsGene from './VariantDetailsGene.vue'

export default {
  title: 'Variants / Small Variant Details Gene',
  component: VariantDetailsGene,
}

const Template = (args) => ({
  components: { VariantDetailsGene },
  setup() {
    return { args }
  },
  template:
    '<VariantDetailsGene\n' +
    '    :gene="args.gene"\n' +
    '    :ncbiSummary="args.ncbiSummary"\n' +
    '    :ncbiGeneRifs="args.ncbiGeneRifs"\n' +
    '    :release="args.smallVariant.release"\n' +
    '    :refseqGeneId="args.smallVariant.refseq_gene_id"\n' +
    '    :ensemblGeneId="args.smallVariant.ensembl_gene_id"\n' +
    '/>',
})

export const Autosomal = Template.bind({})
Autosomal.args = {
  gene: {
    omim: {
      114480: [
        'BREAST CANCER',
        ['BREAST CANCER, FAMILIALBREAST CANCER, FAMILIAL MALE, INCLUDED'],
      ],
      176807: ['PROSTATE CANCER', []],
      259500: ['OSTEOGENIC SARCOMA', []],
      609265: ['LI-FRAUMENI SYNDROME 2', []],
    },
    omim_genes: [604373],
    hpo_inheritance: [['HP:0000006', 'AD']],
    hpo_terms: [
      ['HP:0001939', 'Abnormality of metabolism/homeostasis'],
      ['HP:0000924', 'Abnormality of the skeletal system'],
      ['HP:0003002', 'Breast carcinoma'],
      ['HP:0009733', 'Glioma'],
      ['HP:0001425', 'Heterogeneous'],
      ['HP:0002858', 'Meningioma'],
      ['HP:0002669', 'Osteosarcoma'],
      ['HP:0012125', 'Prostate cancer'],
      ['HP:0009919', 'Retinoblastoma'],
      ['HP:0100242', 'Sarcoma'],
      ['HP:0012126', 'Stomach cancer'],
    ],
    clinvar_pathogenicity: {
      symbol: 'CHEK2',
      entrez_id: '11200',
      ensembl_gene_id: 'ENSG00000183765',
      pathogenic_count: 314,
      likely_pathogenic_count: 163,
    },
    gnomad_constraints: {
      symbol: 'CHEK2',
      ensembl_transcript_id: 'ENST00000382580',
      obs_mis: 327,
      exp_mis: 304.89,
      oe_mis: 1.0725,
      mu_mis: 0.000016101,
      possible_mis: 3793,
      obs_mis_pphen: 128,
      exp_mis_pphen: 107.9,
      oe_mis_pphen: 1.1863,
      possible_mis_pphen: 1383,
      obs_syn: 95,
      exp_syn: 110.23,
      oe_syn: 0.86181,
      mu_syn: 0.0000056386,
      possible_syn: 1129,
      obs_lof: 34,
      mu_lof: 0.0000014044,
      possible_lof: 394,
      exp_lof: 29.567,
      pLI: 1.2103e-24,
      pNull: 0.99992,
      pRec: 0.000076354,
      oe_lof: 1.1499,
      oe_syn_lower: 0.729,
      oe_syn_upper: 1.022,
      oe_mis_lower: 0.979,
      oe_mis_upper: 1.175,
      oe_lof_lower: 0.874,
      oe_lof_upper: 1.53,
      constraint_flag: null,
      syn_z: 1.1405,
      mis_z: -0.45001,
      lof_z: -0.75547,
      oe_lof_upper_rank: 15687,
      oe_lof_upper_bin: 8,
      oe_lof_upper_bin_6: 4,
      n_sites: 61,
      classic_caf: 0.0028224,
      max_af: 0.0020443,
      no_lofs: 125047,
      obs_het_lof: 701,
      obs_hom_lof: 0,
      defined: 125748,
      p: 0.0027912,
      exp_hom_lof: 0.97969,
      classic_caf_afr: 0.00070977,
      classic_caf_amr: 0.00071021,
      classic_caf_asj: 0.0018056,
      classic_caf_eas: 0.00038863,
      classic_caf_fin: 0.0099322,
      classic_caf_nfe: 0.0032961,
      classic_caf_oth: 0.0022989,
      classic_caf_sas: 0.001375,
      p_afr: 0.0006769,
      p_amr: 0.00069404,
      p_asj: 0.0017873,
      p_eas: 0.00038063,
      p_fin: 0.0099348,
      p_nfe: 0.0032663,
      p_oth: 0.0022827,
      p_sas: 0.0013728,
      transcript_type: 'protein_coding',
      ensembl_gene_id: 'ENSG00000183765',
      transcript_level: 2,
      cds_length: 1758,
      num_coding_exons: 15,
      gene_type: 'protein_coding',
      gene_length: 54680,
      exac_pLI: 1.183e-15,
      exac_obs_lof: 22,
      exac_exp_lof: 20.28,
      exac_oe_lof: 1.0848,
      brain_expression: null,
      chromosome: '22',
      start_position: 29083731,
      end_position: 29138410,
    },
    exac_constraints: null,
    hgnc_id: 'HGNC:16627',
    symbol: 'CHEK2',
    name: 'checkpoint kinase 2',
    locus_group: 'protein-coding gene',
    locus_type: 'gene with protein product',
    status: 'Approved',
    location: '22q12.1',
    location_sortable: '22q12.1',
    alias_symbol: 'CDS1|CHK2|HuCds1|PP1425|bA444G7',
    alias_name: null,
    prev_symbol: 'RAD53',
    prev_name:
      'CHK2 (checkpoint, S.pombe) homolog|CHK2 checkpoint homolog (S. pombe)',
    gene_family: null,
    gene_family_id: null,
    date_approved_reserved: '2001-09-19',
    date_symbol_changed: '2001-09-27',
    date_name_changed: '2011-11-11',
    date_modified: '2018-12-24',
    entrez_id: '11200',
    ensembl_gene_id: 'ENSG00000183765',
    vega_id: 'OTTHUMG00000151023',
    ucsc_id: 'uc003adu.2',
    ucsc_id_novers: 'uc003adu',
    ena: 'AF086904',
    refseq_accession: 'NM_001005735',
    ccds_id: 'CCDS13843|CCDS13844|CCDS33629',
    uniprot_ids: 'O96017',
    pubmed_id: '9836640|10097108',
    mgd_id: 'MGI:1355321',
    rgd_id: 'RGD:621543',
    lsdb: 'LRG_302|http://ftp.ebi.ac.uk/pub/databases/lrgex/pending/LRG_302.xml',
    cosmic: 'CHEK2',
    omim_id: '604373',
    mirbase: null,
    homeodb: null,
    snornabase: null,
    bioparadigms_slc: null,
    orphanet: '119394',
    pseudogene_org: null,
    horde_id: null,
    merops: null,
    imgt: null,
    iuphar: 'objectId:1988',
    kznf_gene_catalog: null,
    mamit_trnadb: null,
    cd: null,
    lncrnadb: null,
    enzyme_id: null,
    intermediate_filament_db: null,
    rna_central_ids: null,
    gtrnadb: null,
    lncipedia: null,
    agr: null,
    mane_select: null,
  },
  ncbiSummary: {
    entrez_id: '11200',
    summary:
      'In response to DNA damage and replication blocks, cell cycle progression is halted through the control of critical cell cycle regulators. The protein encoded by this gene is a cell cycle checkpoint regulator and putative tumor suppressor. It contains a forkhead-associated protein interaction domain essential for activation in response to DNA damage and is rapidly phosphorylated in response to replication blocks and DNA damage. When activated, the encoded protein is known to inhibit CDC25C phosphatase, preventing entry into mitosis, and has been shown to stabilize the tumor suppressor protein p53, leading to cell cycle arrest in G1. In addition, this protein interacts with and phosphorylates BRCA1, allowing BRCA1 to restore survival after DNA damage. Mutations in this gene have been linked with Li-Fraumeni syndrome, a highly penetrant familial cancer phenotype usually associated with inherited mutations in TP53. Also, mutations in this gene are thought to confer a predisposition to sarcomas, breast cancer, and brain tumors. This nuclear protein is a member of the CDS1 subfamily of serine/threonine protein kinases. Several transcript variants encoding different isoforms have been found for this gene. [provided by RefSeq, Apr 2012]',
  },
  ncbiGeneRifs: [
    {
      entrez_id: '11200',
      rif_text: 'All 14 exons of CHEK2 were amplified.',
      pubmed_ids: ['27039729'],
    },
    {
      entrez_id: '11200',
      rif_text:
        '[Cell Cycle Checkpoint Kinase and Drug Resistance of Lung Cancer].',
      pubmed_ids: ['33910274'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Gluconeogenic enzyme PCK1 deficiency promotes CHK2 O-GlcNAcylation and hepatocellular carcinoma growth upon glucose deprivation.',
      pubmed_ids: ['33690219'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Sustained CHK2 activity, but not ATM activity, is critical to maintain a G1 arrest after DNA damage in untransformed cells.',
      pubmed_ids: ['33607997'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'An ATM-Chk2-INCENP pathway activates the abscission checkpoint.',
      pubmed_ids: ['33355621'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Clinicopathologic Profile of Breast Cancer in Germline ATM and CHEK2 Mutation Carriers.',
      pubmed_ids: ['33919281'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Bilateral Disease Common Among Slovenian CHEK2-Positive Breast Cancer Patients.',
      pubmed_ids: ['33030641'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 Germline Variants in Cancer Predisposition: Stalemate Rather than Checkmate.',
      pubmed_ids: ['33322746'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Skin cancer risk in CHEK2 mutation carriers.',
      pubmed_ids: ['32531112'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Homozygosity for CHEK2 p.Gly167Arg leads to a unique cancer syndrome with multiple complex chromosomal translocations in peripheral blood karyotype.',
      pubmed_ids: ['30858171'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'FadA promotes DNA damage and progression of Fusobacterium nucleatum-induced colorectal cancer through up-regulation of chk2.',
      pubmed_ids: ['32993749'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Clinicopathological Features and Outcomes in Individuals with Breast Cancer and ATM, CHEK2, or PALB2 Mutations.',
      pubmed_ids: ['32996020'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Clustering of known low and moderate risk alleles rather than a novel recessive high-risk gene in non-BRCA1/2 sib trios affected with breast cancer.',
      pubmed_ids: ['32383162'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Oncogene PRR14 promotes breast cancer through activation of PI3K signal pathway and inhibition of CHEK2 pathway.',
      pubmed_ids: ['32541902'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Rotavirus activates a noncanonical ATM-Chk2 branch of DNA damage response during infection to positively regulate viroplasm dynamics.',
      pubmed_ids: ['31845505'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Abnormal expression of p-ATM/CHK2 in nasal extranodal NK/T cell lymphoma, nasal type, is correlated with poor prognosis.',
      pubmed_ids: ['32220941'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Loss of CHEK2 Predicts Progression in Stage pT1 Non-Muscle-Invasive Bladder Cancer (NMIBC).',
      pubmed_ids: ['31506803'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Epigenetic changes in FOXO3 and CHEK2 genes and their correlation with clinicopathological findings in myelodysplastic syndromes.',
      pubmed_ids: ['32217071'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High CHK2 protein expression is a strong and independent prognostic feature in ERG negative prostate cancer.',
      pubmed_ids: ['32317175'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Differences in cancer prevalence among CHEK2 carriers identified via multi-gene panel testing.',
      pubmed_ids: ['32805687'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Validation of a next generation sequencing assay for BRCA1, BRCA2, CHEK2 and PALB2 genetic testing.',
      pubmed_ids: ['32531196'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'ATM-CHK2-Beclin 1 axis promotes autophagy to maintain ROS homeostasis under oxidative stress.',
      pubmed_ids: ['32187724'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High risk of breast cancer in women with biallelic pathogenic variants in CHEK2.',
      pubmed_ids: ['31993860'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Breast cancer screening implications of risk modeling among female relatives of ATM and CHEK2 carriers.',
      pubmed_ids: ['31967672'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High Expression of p21 as a Potential Therapeutic Target in Ovarian Clear-cell Carcinoma.',
      pubmed_ids: ['32988887'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2-FOXK axis promotes transcriptional control of autophagy programs.',
      pubmed_ids: ['31911943'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This study establishes the groundwork for the development of Dovitinib as a therapeutic agent for high-grade Aggressive Meningioma with either frequent codeletion or mutated CHEK2 and NF2, an avenue with high translational potential.',
      pubmed_ids: ['32441531'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'SIRT1, a metabolic sensor, protects cells from oxidative stress-dependent DNA damage response by the deacetylation of CHK2.',
      pubmed_ids: ['30902968'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 pathogenic variants in the BRCA-negative Hispanic women with breast cancer.',
      pubmed_ids: ['31206626'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Study suggests that structure and function of CHK2 can be distributed by various nsSNPs. In native protein of CHK2 gene, out of 79 SNPs, seven major variants found were: p.Arg160Gly, p.Arg188Trp, p.Ile203Thr, p.Gly210Arg, p.Arg223Cys, p.Pro225His and p.Ser415Phe. Among seven most significant SNPs, 3 were highly conserved and 4 SNPs were averaged conserved residues.',
      pubmed_ids: ['31398194'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The authors report a BRCA negative family with multiple affected women having breast cancer, with a novel, missense, likely pathogenic variant in the CHEK2 gene (c.1376T>G; p.Ile459Ser) that segregated with subjects with breast cancer.',
      pubmed_ids: ['31296309'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Hereditary CHEK2 mutations contribute to the development of hereditary Breast Cancer.',
      pubmed_ids: ['31409080'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'A single nucleotide polymorphism in the CHEK2 gene, rs1033667, was significantly associated with OSCC.',
      pubmed_ids: ['30753320'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This multicenter case-control analysis of men with or without in Checkpoint Kinase 2 (CHEK2) With Susceptibility to Testicular Germ Cell Tumors (TGCTs) provides evidence for CHEK2 as a novel moderate-penetrance TGCT susceptibility gene.',
      pubmed_ids: ['30676620'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations c.1100delC and I157T can distinguish which patients with breast cancer are susceptible to metastasis (Review).',
      pubmed_ids: ['31220302'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results demonstrate that CHK2 is deubiquitinated by USP39 enhancing its stability. CHK2 regulates cell cycle checkpoint, cell apoptosis and chemo-radiation response. Furthermore, USP39 and CHK2 expression are correlatively downregulated in lung cancer samples.',
      pubmed_ids: ['30771428'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Study identified germline CHEK2 variants in high-risk breast and ovarian cancer patients in addition to two types of large intragenic rearrangements of unknown significance.',
      pubmed_ids: ['31050813'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our results demonstrated that germline BRCA2 and CHEK2 mutations are independent unfavorable predictors in patients with mPCa which are associated with decreased time to castration resistance (HR 3.04, 95% CI 1.63-5.66, p<0.001), particularly in subgroup with low volume metastatic disease (HR 4.59, 95% CI 2.06-10.22, p<0,001).',
      pubmed_ids: ['31808637'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Germline BRCA2 K3326X and CHEK2 I157T mutations increase risk for sporadic pancreatic ductal adenocarcinoma',
      pubmed_ids: ['30672594'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 is involved in the DNA damage repair response Fanconi anemia (FA)-BRCA pathway. An increased risk for breast and other cancers has been documented in individuals who carry a single pathogenic CHEK2 variant. CHEK2 splicing variant c.793-1G > A is a deleterious variant.',
      pubmed_ids: ['31349801'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Study shows a low impact of CHEK2 on breast cancer in men predisposition in an Italian population.',
      pubmed_ids: ['30613976'],
    },
    {
      entrez_id: '11200',
      rif_text: 'a newly identified CHEK2 variant is described.',
      pubmed_ids: ['30633282'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2*1100delC is associated with an increased risk of both female and male breast cancer.',
      pubmed_ids: ['29909568'],
    },
    {
      entrez_id: '11200',
      rif_text:
        "Theaflavin-3,3'-digallate (TF3) up-regulated the expression of p27 to induce G0/G1 cell cycle arrest in OVCAR-3 cells. Our study indicated that Chk2 and p27 were vital anticancer targets of TF3 and provided more evidence that TF3 might be a potent agent to be applied as adjuvant treatment for ovarian cancer",
      pubmed_ids: ['30769778'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'somatic mutations in EIF1AX, PPM1D, and CHEK2 were absent in this large series of patients with Thyroid Cancer from a different racial group',
      pubmed_ids: ['30269267'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the congenital CHEK2 inactivation is strongly associated with the risk of MDS and with a poorer prognosis of the disease. However, the chromosomal instability in AML is not correlated with the hereditary dysfunction of CHEK2.',
      pubmed_ids: ['29902706'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 c.1100delC mutation appears to uniquely contribute to the risk of lethal prostate cancer in European American men.',
      pubmed_ids: ['29520813'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The ATR-Chk1 and ATM-Chk2 signalings in male breast cancer (MBC).',
      pubmed_ids: ['28808232'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'we showed that CHK2-dependent phosphorylation of PARP1 not only regulates its cellular localization but also promotes its catalytic activity and its interaction with XRCC1. These findings indicate that CHK2 exerts a multifaceted impact on PARP1 in response to oxidative stress to facilitate DNA repair and to maintain cell survival.',
      pubmed_ids: ['30254210'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'mong Chinese breast cancer patients, the CHEK2 germline mutation rate is approximately 0.34% and two specific mutations (Y139X and R137X) are recurrent. Patients with CHEK2 mutations are significantly more likely to have family histories of cancer, and to develop lymph node-positive and/or PR-positive breast cancers.',
      pubmed_ids: ['29356917'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'In Russia, CHEK2 mutations hold second position in the list of BC-predisposing gene defects after BRCAl, and include CHEK2 1100deIC, de15395, and IVS2+lG>A gene-inactivating alleles.',
      pubmed_ids: ['30695561'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Among 13 early-onset breast cancer, Cowden-like and Li-Fraumeni-like syndromes Norwegian patients, gene panel sequencing identified a potentially pathogenic variant in CHEK2 that affects a canonical RNA splicing signal.',
      pubmed_ids: ['28608266'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEK2 mutation is associated with Pancreatic Cancer.',
      pubmed_ids: ['26483394'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'present study aimed to molecularly define and determine the contribution of two rare, apparently novel CHEK2 Large Genomic Rearrangements, among Greek breast cancer patients.',
      pubmed_ids: ['29785007'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 Y390C mutation induced the drug resistance of triple negative breast cancer cells to chemotherapeutic drugs.',
      pubmed_ids: ['29761796'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 Germ Line Mutation is not associated with Familial and Sporadic Breast Cancer.',
      pubmed_ids: ['29479983'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk1 and Chk2 are significantly expressed in human sperm. In case of sperm DNA damage, up-regulated Chk1 expression may enhance sperm apoptosis and lead to asthenospermia, while increased Chk2 expression may inhibit spermatogenesis and result in oligospermia.',
      pubmed_ids: ['29658237'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK1 and CHK2 and their activated forms are frequently expressed in HGSC effusions, with higher expression following exposure to chemotherapy, and their expression is related to survival.',
      pubmed_ids: ['29804637'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'first article to report that identical germline mutation of CHEK2 gene, p.R180C, exists in both NF1 and NF2 patients.',
      pubmed_ids: ['29879026'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results suggested that there was a correlation between mutation of the CHEK2 gene and gastric cancer.',
      pubmed_ids: ['29067458'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Truncating variants in PALB2, ATM and CHEK2 , but not XRCC2 were associated with increased breast cancer risk.',
      pubmed_ids: ['28779002'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'our results identify a novel link between XRRA1 and the ATM/CHK1/2 pathway and suggest that XRRA1 is involved in a DNA damage response that drives radio- and chemoresistance by regulating the ATM/CHK1/2 pathway.',
      pubmed_ids: ['29082250'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'BRCA2 and CHEK2 play an important role in the genetic susceptibility to urinary tract cancers.',
      pubmed_ids: ['27632928'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Checkpoint kinase 2 (Chk2) inhibition suppressed C-terminal acetylation of p53 and delayed the induction of p53-target genes under heat stress (HS). Chk2 inhibition failed to inhibit apoptosis induced by HS, indicating that Chk2 was dispensable for p53-dependent apoptosis under HS. Chk2 inhibition abrogated G2/M arrest and promoted cell death induced by HS in cells with p53 defects.',
      pubmed_ids: ['28733865'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The inhibition CHK2 expression reduced detachment-induced apoptosis but did not influence the ability of cells to migrate and invade, which illustrates that CHK2 could inhibit tumor progression and metastatic potential by enhancing anoikis.',
      pubmed_ids: ['29486482'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These data suggest that the CHEK2 c.1100delC mutation is associated with an increased risk for MBC in the Finnish population.',
      pubmed_ids: ['28874143'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that mediator complex subunit 1 (Med1/TRAP220) is a target for checkpoint kinase 2 (Chk2)-mediated phosphorylation and may play a role in cellular DNA damage responses by mediating proper induction of gene transcription upon DNA damage.',
      pubmed_ids: ['28430840'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'this report conceives a novel strategy of Twist1 suppression through Chk2 induction, which prevents metastatic dissemination and promotes premature senescence in p53-defective invasive cancer cells.',
      pubmed_ids: ['28498365'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'we have provided evidence in this study that hepatocarcinogenesis with lagging chromosomes elicits the expression of DNA damage response protein Chk2. Thus, the overexpression of Chk2 and its mislocalisation within structures of the mitotic spindle contribute to sustain cell division and chromosomes missegregation.',
      pubmed_ids: ['28360097'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'PI3K kinase activity is necessary for maintaining 4E-BP1 stability. Our results also suggest 4E-BP1 a novel biological role of regulating cell cycle G2 checkpoint in responding to IR stress in association with controlling CHK2 phosphorylation',
      pubmed_ids: ['28539821'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data show that the checkpoint kinase 1/2 (Chk1/Chk2) inhibitor prexasertib (LY2606368) inhibits cell viability in B-/T-ALL cell lines.',
      pubmed_ids: ['27438145'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results confirm the predicted multiplicative relationship between CHEK2*1100delC and the common low-penetrance susceptibility variants for breast cancer.',
      pubmed_ids: ['27711073'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results show that Chk2 expression is regulated by 14-3-3s in G2-M arrest for non-homologous end joining repair probably via PARP1.',
      pubmed_ids: ['28087741'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results indicate that CHEK2 possesses non-cell-autonomous tumor suppressor functions, and present the Chk2 protein as an important mediator in the functional interplay between breast carcinomas and their stromal fibroblasts through repressing the expression/secretion of SDF-1 and IL-6.',
      pubmed_ids: ['27484185'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'variants in CHEK2 were associated with moderate risks of breast cancer.',
      pubmed_ids: ['28418444'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'In this paper, we describe an extension to the BOADICEA model to incorporate the effects of intermediate risk variants for breast cancer, specifically loss of function mutations in the three genes for which the evidence for association is clearest and the risk estimates most precise: PALB2, CHEK2 and ATM',
      pubmed_ids: ['27464310'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'SIAH2 regulates CHK2 basal turnover, with important consequences on cell-cycle control and on the ability of hypoxia to alter the DNA damage-response pathway in cancer cells.',
      pubmed_ids: ['26751770'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHECK2 rare variants were associated with an increased risk of breast cancer and prostate cancer.',
      pubmed_ids: ['27595995'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'MCM2-MCM6 complex is required for CHK2 chromatin loading and its phosphorylation to DNA damage response in squamous cell carcinoma cells.',
      pubmed_ids: ['27964702'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'On the basis of analyses of approximately 87,000 controls and patients with breast cancer from population- and hospital-based studies, our best estimate for the relative risk of invasive breast cancer for carriers of the 1100delC mutation in CHEK2, compared with noncarriers, was 2.26 (95% CI, 1.90 to 2.69).',
      pubmed_ids: ['27269948'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the G2 damage checkpoint prevents stable recruitment of the chromosome-packaging-machinery components condensin complex I and II onto the chromatin even in the presence of an active Cdk1.',
      pubmed_ids: ['27792460'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'data suggest that cancer risks reported for founder mutations may be generalizable to all CHEK2 + s, particularly for breast cancer',
      pubmed_ids: ['27751358'],
    },
    {
      entrez_id: '11200',
      rif_text: 'K373E mutation of CHK2 in tumorigenesis',
      pubmed_ids: ['27716909'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Checkpoint kinase 1 and 2 signaling is important for apoptin regulation.',
      pubmed_ids: ['27512067'],
    },
    {
      entrez_id: '11200',
      rif_text: 'High CHEK2 expression is associated with Lung Adenocarcinoma.',
      pubmed_ids: ['28373435'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High expression of pCHK2-Thr68 was associated with decreased patient survival (p = 0.001), but was not an independent prognostic factor. Our results suggest that pCHK2-Thr68 and pCDC25C-Ser216 play important roles in breast cancer and may be potential treatment targets',
      pubmed_ids: ['27801830'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our study reports the first case of Li-Fraumeni syndrome-like in Chinese patients and demonstrates the important contribution of de novo mutations in this type of rare disease.',
      pubmed_ids: ['27442652'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'hese findings confirmed that 53BP1 loss might be a negative factor for chemotherapy efficacy, promoting cell proliferation and inhibiting apoptosis by suppressing ATM-CHK2-P53 signaling, and finally inducing 5-FU resistance.',
      pubmed_ids: ['27838786'],
    },
    {
      entrez_id: '11200',
      rif_text: 'All 14 exons of CHEK2 were amplified and sequenced.',
      pubmed_ids: ['27510020'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that nitroxoline induces anticancer activity through AMP-activated kinase (AMPK)/mTOR serine-threonine kinase (mTOR) signaling pathway via checkpoint kinase 2 (Chk2) activation.',
      pubmed_ids: ['26447757'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mutation carriers were characterized by older age, a history of gastric cancer in the family, locally advanced disease, lower histologic grade and luminal B type breast cancer.',
      pubmed_ids: ['26991782'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The germline mutations of the CHEK2 gene are associated with an increased risk of polycythaemia vera.',
      pubmed_ids: ['26084796'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'loss of CHK2 or PP6C-SAPS3 promotes Aurora-A activity associated with BRCA1 in mitosis',
      pubmed_ids: ['26831064'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'we observed a great degree of heterogeneity amongst the CHEK2*1100delC breast cancers, comparable to the BRCAX breast cancers.  copy number aberrations were mostly seen at low frequencies in both the CHEK2*1100delC and BRCAX group of breast cancers.',
      pubmed_ids: ['26553136'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The aim of this study was to determine the frequency and spectrum of germline mutations in BRCA1, BRCA2 and PALB2 and to evaluate the presence of the CHEK2 c.1100delC allele in these patients.',
      pubmed_ids: ['26577449'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'germ-line CHEK2 mutations affecting protein coding sequence confer a moderately-increased risk of NHL, they are associated with an unfavorable NHL prognosis, and they may represent a valuable predictive biomarker for patients with DLBCL.',
      pubmed_ids: ['26506619'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations in CHEK2 were most frequent in patients with hereditary non-triple-negative breast cancers.',
      pubmed_ids: ['26083025'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Authors propose that CHK2 is a negative regulator of androgen sensitivity and prostate cancer growth, and that CHK2 signaling is lost during prostate cancer progression to castration resistance.',
      pubmed_ids: ['26573794'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These data provide a rationale for further evaluation of the combination of Wee1 and Chk1/2 inhibitors in malignant melanoma.',
      pubmed_ids: ['26054341'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Variants at the CHEK2 locus are associated with risk of invasive epithelial ovarian cancer. [meta-analysis]',
      pubmed_ids: ['26424751'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 H371Y mutation carriers are more likely to respond to neoadjuvant chemotherapy than are non-carriers',
      pubmed_ids: ['25884806'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Phosphorylation of ATR and CHK1 did not show significant differences in the three cell groups. Overexpression of SHP-1 in the CNE-2 cells led to radioresistance and the radioresistance was related to enhanced DNA DSB repair.',
      pubmed_ids: ['25962492'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The results of this study suggest that CHEK2 mutations are rare among high-risk breast cancer patients and may play a minor contributing role in breast carcinogenesis among Malaysian population.',
      pubmed_ids: ['25629968'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'our results not only identified a novel CHEK2 allele that is associated with cancer families and confers increased breast cancer risk, but also showed that this allele significantly impairs CHEK2 function during DNA damage response',
      pubmed_ids: ['25619829'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mutations were observed with high intensity and associated with poor therapy response and overall survival in high grade serous ovarian cancer.',
      pubmed_ids: ['24879340'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'HBx-induced reactive oxygen species accumulation induces DNA damage that activates the ATM-Chk2 pathway.',
      pubmed_ids: ['25872745'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Via activation of the ATM/ATR-Chk1/Chk2 check point pathway.',
      pubmed_ids: ['26061604'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'our results further revealed that expression of tumor suppressor gene, checkpoint kinase 2, was negatively regulated by miR-191',
      pubmed_ids: ['25773391'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2 participates in several molecular processes involved in DNA structure modification and cell cycle progression',
      pubmed_ids: ['25404613'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 and non-CHEK2 patients had a comparable objective response rate.',
      pubmed_ids: ['25958056'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Role of Chk2 protein in the DNA damage response through the base excision repair pathway',
      pubmed_ids: ['26025911'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 inactivation in B cells leads to decreased immunoglobulin hypermutation and increased conversion activity.',
      pubmed_ids: ['25483076'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This report demonstrates the critical role of Chk2 kinase in the establishment of HSV-1 corneal epithelial infection.',
      pubmed_ids: ['25531207'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The Russian carriers of BRCA1, BRCA2 and CHEK2 germline mutations have genetic predisposition to breast, ovarian, and colorectal cancer.',
      pubmed_ids: ['25850293'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The study indicates that the CHEK2 c.1100delC mutation does not contribute substantially to hereditary breast cancer in patients of Greek descent.',
      pubmed_ids: ['25835597'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These results suggest that CHEK2 mutations predispose to thyroid cancer, familial aggregations of breast and thyroid cancer and to double primary cancers of the breast and thyroid.',
      pubmed_ids: ['25583358'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that ataxia telangiectasia mutated protein (ATM)-checkpoint kinase 2 (Chk2) levels in sporadic breast cancer may have prognostic and predictive significance.',
      pubmed_ids: ['25425972'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Inherited mutations in the CHEK2 gene have been identified in some cases of breast cancer',
      pubmed_ids: ['25355026'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This study provides evidence for distinct sensitivity of BRCA1 and CHEK2 mutation-driven breast carcinomas to standard chemotherapeutic schemes.',
      pubmed_ids: ['25414026'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'DNA-PK/Chk2 signaling induces centrosome amplification upon long-term HU treatment, therefore increasing our insight into tumor recurrence after initial chemotherapy.',
      pubmed_ids: ['24662822'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Frequency of CHEK2 gene mutations in patients with breast cancer from the Republic of Bashkortostan',
      pubmed_ids: ['25842825'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 gene mutations are not associated with differentiated thyroid carcinoma.',
      pubmed_ids: ['24998580'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High CHEK2 expression is associated with trastuzumab-resistant breast cancer.',
      pubmed_ids: ['25449779'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'REsults indicate that CHEK2 rare variants, such as duplications, can confer a high susceptibility to cancer development.',
      pubmed_ids: ['24986639'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The results link Chk2 and REGgamma to the mechanism underlying the DBC1-dependent SIRT1 inhibition.',
      pubmed_ids: ['25361978'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'selective targeting of Chk1 and Chk2 by oncolytic adenovirus mutants was chosen to treat resistant tumor xenograft mice, and the maximum antitumoral efficacy was achieved with the combined co-abrogation of Chk1 and Chk2',
      pubmed_ids: ['24853623'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chromosomal instability is induced by overexpression of the oncogene AURKA or by loss of the tumour suppressor gene CHK2, a genetic constitution found in colorectal cancers.',
      pubmed_ids: ['24976383'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The adjusted hazard ratio associated with a CHEK2 mutation was 1.31.',
      pubmed_ids: ['24557336'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2-1100delC and BRCA2- Met784Val mutation haplotype is associated with breast cancer.',
      pubmed_ids: ['23803109'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'No significant interaction between CHEK2 and adjuvant chemotherapy was observed.',
      pubmed_ids: ['24918820'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our results provide evidence of a newly identified hMps1 phosphorylation site that is involved in the mitotic checkpoint and that CHK2 contributes to chromosomal stability through hMps1.',
      pubmed_ids: ['24764296'],
    },
    {
      entrez_id: '11200',
      rif_text: 'liink between mitosis and dna damage',
      pubmed_ids: ['20442702'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The findings implicate an important role of variants in the ATM- CHEK2- BRCA1 axis in modification of the genetic predisposition to papillary thyroid carcinoma and its clinical manifestations.',
      pubmed_ids: ['24599715'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'To our knowledge, this is first mutation scanning study of gene CHEK2 from Balochistan population.',
      pubmed_ids: ['24390236'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'There was no conspicuous activation of Chk2 kinase in 0.1 or 0.2 Gy group.',
      pubmed_ids: ['23073808'],
    },
    {
      entrez_id: '11200',
      rif_text: 'As evidenced by release through Chk2 inhibition.',
      pubmed_ids: ['24498068'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEK2 p.Ile157Thr is associated with lung cancer.',
      pubmed_ids: ['24880342'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Development of breast tumors in CHEK2, NBN/NBS1 and BLM mutation carriers does not commonly involve somatic inactivation of the wild-type allele.',
      pubmed_ids: ['24415413'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2-depleted ovarian cancer cell lines have diminished platinum sensitivity.',
      pubmed_ids: ['24657486'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The gene polymorphisms in CHEK2, GSTP1, and ERCC1 may be involved in glioblastoma in the Han Chinese population.',
      pubmed_ids: ['24532427'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 stabilizes Mps1 and phosphorylates Aurora B-serine 331 to prevent mitotic exit when most kinetochores are unattached.',
      pubmed_ids: ['24798733'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'we elucidated the prognostic implications of the expressions of ATM, Chk2, and p53, in gastric carcinoma',
      pubmed_ids: ['23969480'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEK2 mutations are associated with gastric cancer.',
      pubmed_ids: ['23296741'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'data provide strong evidences that Aurora-A and BRCA1/2 inversely control the sensitivity of cancer cells to radio- and chemotherapy through the ATM/Chk2-mediated DNA repair networks',
      pubmed_ids: ['24480460'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The recurrent mutation, p.H371Y of CHEK2, confers a moderate risk of breast cancer in Chinese women.',
      pubmed_ids: ['21618645'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These findings indicate that DHM inhibits the growth of hepatocellular carcinoma (HCC) cells via G2/M phase cell cycle arrest through Chk1/Chk2/Cdc25C pathway.',
      pubmed_ids: ['24002546'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 harbors many rare sequence variants that confer increased risk of breast cancer.',
      pubmed_ids: ['21244692'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHEK2 gene was screened for mutations in well-characterized, Finnish, high-risk hereditary breast and/or ovarian cancer individuals.',
      pubmed_ids: ['21356067'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2 kinase constitutively phosphorylates CDK11(p110) in a DNA damage-independent manner.',
      pubmed_ids: ['23178491'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The results show increased phosphorylation of H2AX, ATM, and Chk2 after exposure, and that nano-TiO2 inhibited the overall rate of DNA synthesis and frequency of replicon initiation events.',
      pubmed_ids: ['22770119'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 Del5395bp mutation is associated with breast cancer susceptibility.',
      pubmed_ids: ['24065469'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the DNA-PKcs/CHK2 pathway mediates the mitotic phosphorylation of H2AX in the absence of DNA damage.',
      pubmed_ids: ['24021642'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Studies indicate that autophosphorylation of Nek7 and Plk4 occurred through an intermolecular mechanism, the kinases Aurora-A and Chk2 followed an intramolecular mechanism.',
      pubmed_ids: ['23821772'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our findings suggest that CHEK2 mutations may not contribute significantly to breast/ovarian cancer risk in Pakistani women.',
      pubmed_ids: ['23806170'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 interacts with SMRT and regulates different transcription factors, acting as a repressor.',
      pubmed_ids: ['23690919'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Findings indicate that PIRH2 has central roles in the ubiquitylation of Chk2 and its turnover and in the regulation of its function.',
      pubmed_ids: ['23449389'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 I157T variant increases cancer risk, especially in breast and colorectal cancer in Caucasian population.',
      pubmed_ids: ['23713947'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'In our study, we demonstrate the presence of c.1100delC mutation in Galician (Northwest Spain) hereditary breast cancer families',
      pubmed_ids: ['23150219'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data indicate that genotyping for the CHEK2 1100delC mutation in a familial breast cancer setting contributes to optimal clinical surveillance in countries in which this mutation is prevalent.',
      pubmed_ids: ['23415889'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The 1100delC mutation was encountered in the germline of one (1.7%) individual in this high risk cohort which indicates that the CHEK2 1100delC is not commonly encountered in Brazilian families with multiple diagnoses of breast and colorectal cancer.',
      pubmed_ids: ['23329222'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'A significant association was found between CHEK2 1100delC heterozygote and breast cancer risk.',
      pubmed_ids: ['22994785'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Among women with estrogen receptor-positive breast cancer, CHEK2*1100delC heterozygosity was associated with a 1.4-fold risk of early death, a 1.6-fold risk of breast cancer-specific death, and a 3.5-fold risk of a second breast cancer.',
      pubmed_ids: ['23109706'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Higher phosphorylation levels of CHK2 is associated with poor treatment response in rectal cancer.',
      pubmed_ids: ['22658458'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'HIF-2alpha is involved in the blocking effects of arsenite on activation of the ATM/Chk-2 pathway and in repair of DNA damage induced by BaP in HBE cells.',
      pubmed_ids: ['23333640'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'loss of function of the ATM-Chek2-p53 cascade is strongly associated with resistance to anthracycline/mitomycin-containing chemotherapy in breast cancer',
      pubmed_ids: ['22420423'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'MYC regulation of CHK1 and CHK2 promotes radioresistance in a stem cell-like population of nasopharyngeal carcinoma cells.',
      pubmed_ids: ['23269272'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Five percent of women with uterine serous carcinoma have germline mutations the tumor suppressor genes BRCA1, CHEK2, and TP53.',
      pubmed_ids: ['22811390'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our research indicates that the CHEK2 I157T variant may be another important genetic mutation which increases risk of breast cancer, especially the lobular type.',
      pubmed_ids: ['22799331'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2 1100delC, IVS2+1G>A and I157T mutations are not present in hepatocellular cancer cases from a Turkish population.',
      pubmed_ids: ['23107771'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'data indicate the significance of CHEK2 gene alterations in contrast to promoter hypermethylation in breast cancerogenesis',
      pubmed_ids: ['22862163'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHEK2 I157T variant is associated with colorectal cancer susceptibility.',
      pubmed_ids: ['22901170'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Knockdown of the human DNA helicase RRM3 enhances phosphorylation of the cell cycle arrest kinase Chk2, indicating activation of the checkpoint via the ATM/Chk2 pathway.',
      pubmed_ids: ['22808196'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 1100delC, IVS2+1G>A and I157T mutations have not been agenetic susceptibility factor for Colorectal cancer in the Turkish population.',
      pubmed_ids: ['22521562'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that in vivo assay of cellular response to DNA damage by mutant CHEK2 alleles may complement and extend epidemiologic and genetic assessment of their clinical consequences.',
      pubmed_ids: ['22419737'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Higher frequencies of these mutations in the patient group compared to the control sample (1.95 versus 0.25% for BRCA1 5382insC, and 1.78 versus 0.40% for CHEK2 1100delC) were observed, pointing to their association with susceptibility to breast cancer',
      pubmed_ids: ['22946335'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Checkpoint kinase-2 (Chk2) binds to the beta-domain of pVHL and phosphorylates Ser 111 on DNA damage.',
      pubmed_ids: ['22071692'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations and CHEK2 protein levels were analyzed in prostatic neoplasms.  CHEK2 mutations contributed to prostate cancer risk.',
      pubmed_ids: ['12533788'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'findings suggest that Chk2-mediated phosphorylation of survivin-DeltaEx3 contributes to a DNA damage-sensing checkpoint that may affect cancer cell sensitivity to genotoxic therapies',
      pubmed_ids: ['22586065'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 gene may act as a factor contributing to individual tumor development in peculiar familial backgrounds.',
      pubmed_ids: ['21562711'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The Chk2 protein is as an essential mediator of the cellular responses to RITA.',
      pubmed_ids: ['22158418'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2-I157T variant was associated with the luminal A subtype, whereas CHEK2-truncating mutations were associated with the luminal B subtype.',
      pubmed_ids: ['21701879'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mutations could potentially contribute to the susceptibility to essential thrombocythemia. The germline inactivation of CHEK2, as it seems, has no direct impact on the development of disease.',
      pubmed_ids: ['22058216'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CT allele of single nucleotide polymorphisms (SNP) rs738722 and the GC allele of SNP rs2236142 might be a protective factor of the risk for lymph node metastasis of esophageal cancer.',
      pubmed_ids: ['22201027'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'report of four interactions between mutations in the breast cancer susceptibility genes ATM and CHEK2 with BRCA1 and BRCA2',
      pubmed_ids: ['22072393'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Widdrol breaks DNA directly in HT29 cells, resulting in checkpoint activation via Chk2-p53-Cdc25A-p21-MCM4 pathway and finally cells go to G1-phase cell cycle arrest and apoptosis.',
      pubmed_ids: ['22160829'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'a variety of deleterious CHEK2 alleles make an appreciable contribution to breast cancer susceptibility, and their identification could help in the clinical management of patients carrying a CHEK2 mutation.',
      pubmed_ids: ['22114986'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The identification of a CHEK2 gene signature implies an unexpected biological homogeneity among the CHEK2 1100delC breast cancers. All CHEK2 1100delC tumors classified as luminal intrinsic subtype breast cancers.',
      pubmed_ids: ['21614566'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2-induced phosphorylation enables TR3 to bind to its response elements on the promoters of the BRE and RNF-7 genes.',
      pubmed_ids: ['22159226'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'alternative splicing and frequent codeletion of CHEK2 and NF2 contribute to the genomic instability and associated development of aggressive biologic behavior in meningiomas.',
      pubmed_ids: ['22355270'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 gene polymorphisms are assciated with colorectal cancer.',
      pubmed_ids: ['22294770'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'high heterogeneity of Chk2 levels in cancer cells is primarily due to its inactivation (owing to low gene expression, alternative splicing, point mutations, copy-number alterations and premature truncation) or reduction of protein levels.',
      pubmed_ids: ['21765476'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations in CHEK2 gene confer a moderately increased risk of breast cancer in women from non-BRCA1/2 families.',
      pubmed_ids: ['22058428'],
    },
    {
      entrez_id: '11200',
      rif_text: 'structural insight into MDC1-CHK2 interaction',
      pubmed_ids: ['22211259'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'findings demonstrated that ethanol metabolism activates ataxia telangiectasia mutated (ATM) which can activate checkpoint kinase 2 (Chk2)',
      pubmed_ids: ['21924579'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2*1100delC heterozygotes have a twofold risk of malignant melanoma compared with noncarriers.',
      pubmed_ids: ['21956126'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mutation screening detects a clinically meaningful risk of breast cancer and should be considered in all women with a family history of breast cancer.',
      pubmed_ids: ['21876083'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that combination treatment with radiation and uPAR knock down or Chk2 inhibitor resulting in non-reversible G2/M arrest may be beneficial in the management of meningiomas.',
      pubmed_ids: ['21945852'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This meta-analysis demonstrates that the CHEK2 1100delC variant may be an important colorectal cancer-predisposing gene, which increases colorectal cancer risk.',
      pubmed_ids: ['21807500'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'X-ray structures of checkpoint kinase 2 in complex with inhibitors that target its gatekeeper-dependent hydrophobic pocket.',
      pubmed_ids: ['21907711'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Functional and molecular interactions between ERK and CHK2 in diffuse large B-cell lymphoma.',
      pubmed_ids: ['21772273'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEK2 polymorphisms are associated with endometrial cancer.',
      pubmed_ids: ['21787115'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Mutations in CHEK2 gene is associated with Hodgkin lymphoma.',
      pubmed_ids: ['21744992'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 centrosomal binding does not require DNA damage, but varies according to cell cycle progression.',
      pubmed_ids: ['20581449'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'In response to ultraviolet radiation, Lats2 is phosphorylated by Chk1 and Chk2 at S408.',
      pubmed_ids: ['21118956'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The authors propose that the release of HuR-bound mRNAs via an ionizing radiation-Chk2-HuR regulatory axis improves cell outcome following ionizing radiation.',
      pubmed_ids: ['21317874'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 variant, rs4035540, was associated with an increased risk of type 2 diabetes.',
      pubmed_ids: ['19855918'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The germ line CHK2 1100delC variant does not seem to have a major impact on the development of squamous cell carcinoma of the head and neck.',
      pubmed_ids: ['21184685'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'ATM-Chk2 and ATR-Chk1 pathways have roles in DNA damage signaling and cancer [review]',
      pubmed_ids: ['21034966'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Loss of ATM/Chk2/p53 pathway components accelerates tumor development and contributes to radiation resistance in gliomas.',
      pubmed_ids: ['21156285'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Per3 is a checkpoint protein that plays important roles in checkpoint activation, cell proliferation and apoptosis.',
      pubmed_ids: ['21070773'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2, STK11, and PALB2 mutations or large genomic rearrangements of either STK11 or PALB2 are rare, and do not contribute to a substantial fraction of breast cancer susceptibility in high-risk French Canadian breast cancer families.',
      pubmed_ids: ['20722467'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The I157T, other alterations in its proximity, del5395 and c.1100delC in CHEK2 do not predispose to pancreatic cancer risk in the Czech population.',
      pubmed_ids: ['20643596'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'complex interdependent network of phosphorylation events within the T-loop exchange region regulates dimerization/autophosphorylation, kinase activation, and chromatin targeting/egress of Chk2.',
      pubmed_ids: ['20713355'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This study assessed the pathological mutation detection rates for BRCA1, BRCA2 and the CHEK2c.1100 delC mutation in 2022 women with breast cancer, including 100 with breast/ovary double primary and 255 with bilateral breast cancer.',
      pubmed_ids: ['20472656'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data indicate a novel mechanism in undamaged cells where PPs function to maintain the balance between ATM and its direct substrate Chk2 through a regulatory circuit.',
      pubmed_ids: ['20599567'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Study show that siRNA-silencing of the ATM downstream effector, the protein kinase checkpoint kinase 2 (Chk2), significantly impacted CDT-mediated apoptosis of gingival epithelial cells.',
      pubmed_ids: ['20668524'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These data are consistent with the reported very low frequency of CHEK2*1100delC mutations in North American populations.',
      pubmed_ids: ['20875877'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Down-regulating Chk1 and Chk2 may increase the apoptotic sensitivity to irradiation due to changes of the pattern of cell cycle specific apoptosis.',
      pubmed_ids: ['19615254'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 single nucleotide polymorphism is not relevant for colorectal cancer risk in Bulgaria.',
      pubmed_ids: ['20658728'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Ron overexpression on a Chk2*1100 deletion background accelerates the development of mammary tumors.',
      pubmed_ids: ['20434834'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'report a function of Chk2, independent of p53 and DNA damage, that is required for proper progression of mitosis, and for the maintenance of chromosomal stability in human somatic cells',
      pubmed_ids: ['20364141'],
    },
    {
      entrez_id: '11200',
      rif_text:
        "The DNA damage-activated kinases Chk1 and Chk2 may be involved in tau phosphorylation and toxicity in the pathogenesis of Alzheimer's disease.",
      pubmed_ids: ['20159774'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 rs2236141 variant modifies lung cancer susceptibility in the Chinese population by affecting CHEK2 expression.',
      pubmed_ids: ['20462940'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2_1100delC and BRIP1 mutations incidence in Ireland is similar to that found in other unselected breast cancer cohorts from northern European countries.',
      pubmed_ids: ['19763819'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Observational study of genetic testing. (HuGE Navigator)',
      pubmed_ids: ['20417869'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The water extract of the lettuce Lactuca sativa activated checkpoint kinase 2, induced the tumour suppressor p21, and downregulated the proto-oncogene cyclin D1 in HL-60 leukaemia cells and MCF-7 breast cancer cells',
      pubmed_ids: ['20204303'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Increased CHK2 expression is associated with colorectal tumor progression.',
      pubmed_ids: ['20023412'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data show that coralyne treatment photosensitizes DNA, leading to p53- and Chk2-dependent apoptosis in tumor cell lines.',
      pubmed_ids: ['19922265'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest alternative splicing as a possible novel mechanism for repression of the Chk2 wild-type function.',
      pubmed_ids: ['20080130'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The I157T variant of CHEK2 is associated with colorectal cancer.',
      pubmed_ids: ['19876921'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The authors suggest that the Chk2 phosphorylation of TRF2 is important for coordinating origin recognition complex binding to OriP of Epstein-Barr virus and that a failure to execute these events leads to virus replication defects.',
      pubmed_ids: ['20200249'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The I157T single nucleotide polymorphism is overrepresented in endometrial cancer patients diagnosed at 75 or more years of age (9.09%, p = 0.05) and in those with deep myometrial invasion (3.85%, p = 0.06).',
      pubmed_ids: ['18834326'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The checkpoint kinase 2 appears to have a conserved function in control of mitotic progression following G(2)/M transition with DNA damage.',
      pubmed_ids: ['20023427'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'our study reveals the presence of CHEK2 exon 10 truncated mutations in two of 392 high-risk breast/ovarian cancer family probands',
      pubmed_ids: ['19768534'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'TIMELESS is required for ATM-dependent CHK2 activation and G2/M checkpoint control',
      pubmed_ids: ['19996108'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'a predisposing mutation in CHEk2,is present in approximately 6% of French-Canadian women with early-onset breast cancer',
      pubmed_ids: ['19863560'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Suppression of the Chk1/Chk2 protein by shRNA constructs inhibited the growth of oral pulp cells, which indicates that these checkpoint proteins may be essential for normal cell growth.',
      pubmed_ids: ['19453842'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mitochondrial DNA damage initiates a cell cycle arrest by a Chk2-associated mechanism in mammalian cells.',
      pubmed_ids: ['19840931'],
    },
    {
      entrez_id: '11200',
      rif_text:
        '*1100delC is unlikely to contribute significantly to risk to breast cancer among the Malay, Chinese and Indian ethnic groups in Malaysia',
      pubmed_ids: ['19399639'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2*I157T missense mutation is a founder mutation in ethnically diverse populations, but may also be a mutational hotspot.',
      pubmed_ids: ['19609724'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'ATM relays the DNA DSBs signaling triggered by the naphthalimides to the checkpoint kinases, predominantly to Chk2',
      pubmed_ids: ['19881958'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'caspase cleavage is induced upon differentiation of HPV positive cells through the action of the DNA damage protein kinase CHK2, which may be activated as a result of E7 binding to the ATM kinase.',
      pubmed_ids: ['19798429'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Patients with CHEK2 mutation may present poorer clinical course with several recurrences of Superficial Bladder Cancer. It also suggests a possible prognostic significance of CHEK2 analysis',
      pubmed_ids: ['19839522'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the BRCA2 T1915M polymorphism alone might be associated with a reduced risk of breast cancer, but among CHEK2 mutation carriers, it may lead to an unexpectedly high risk.',
      pubmed_ids: ['19030985'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 functions to maintain genome integrity after radiation-induced damage',
      pubmed_ids: ['19772467'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The structure, regulation, and functions of Chk1 and Chk2 in the DNA damage response, as well as their potential roles in human disease, is discussed.',
      pubmed_ids: ['19473886'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Report structure and activation mechanism of the CHK2 DNA damage checkpoint kinase.',
      pubmed_ids: ['19782031'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data show that initiation and maintenance of the IL-6 secretion required the DDR proteins ATM, NBS1 and CHK2.',
      pubmed_ids: ['19597488'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'in the Netherlands, CHEK2 1100delC is associated with an increased risk for male breast cancer',
      pubmed_ids: ['18759107'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'down-regulation of CHK2 gene via distal promoter CpG islands methylation may play a role in the pathogenesis of non-small cell lung cancers',
      pubmed_ids: ['19362748'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that TRF2 repression of Chk2 provides an additional level of control by which shelterin prevents unwanted DNA damage responses, and may explain why TRF2 overexpression acts as a telomerase-independent oncogenic stimulus.',
      pubmed_ids: ['19375317'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Cdc25A degradation depended on Ser75-Cdc25A phosphorylation caused by p38MAPK and Chk2.',
      pubmed_ids: ['19289404'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'RAD51C is required for activation of the checkpoint kinase CHK2 and cell cycle arrest in response to DNA damage.',
      pubmed_ids: ['19451272'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Recurrent loss, but lack of mutations, of the SMARCB1 tumor suppressor gene in T-cell prolymphocytic leukemia with TCL1A-TCRAD juxtaposition.',
      pubmed_ids: ['19480937'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'It was shown that the presence of the mutations in the BRCA1/2 genes among patients with bilateral breast cancer is associated with an earlier occurrence of the first and the second breast cancer than in patients without hereditary mutations.',
      pubmed_ids: ['19372713'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'a polymorphism of the CHEK2 gene is associated with measures of kidney function. These results suggest that CHEK2, a protein involved in cell cycle regulatory pathways, may influence kidney function in the context of hypertension.',
      pubmed_ids: ['19265784'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Zalypsis provoked DNA double-strand breaks (DSBs), evidenced by an increase in phospho-histone-H2AX and phospho-CHK2, followed by a striking overexpression of p53 in p53 wild-type cell lines',
      pubmed_ids: ['19020308'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Risk of cancer in a carrier of a CHEK2 mutation is dependent on the family history of cancer.',
      pubmed_ids: ['19401704'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHEK2 gene I157T mutation and other alterations in its proximity increase the risk of sporadic colorectal cancer in the Czech population.',
      pubmed_ids: ['18996005'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results indicate that Chk2 (but not Chk1) participates in the DNA damage-elicited pro-apoptotic cascade that leads to the demise of Env-elicited syncytia.',
      pubmed_ids: ['19177012'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results suggest that Mdm2 and PCAF may function as part of a multi-subunit E3 complex in their regulation of Chk2 turnover.',
      pubmed_ids: ['19176998'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 c.1100delC is rare variant for Chinese population and may not contribute to predisposition for hereditary breast cancer in Shanghai.',
      pubmed_ids: ['16883537'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'a regulatory loop between TTK/hMps1 and CHK2 whereby DNA damage-activated CHK2 may facilitate the stabilization of TTK/hMps1, therefore maintaining the checkpoint control.',
      pubmed_ids: ['19151762'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our study suggests that the risk of breast cancer in carriers of a deleterious CHEK2 mutation is increased if the second allele is the I157T missense variant.  the presence of a CHEK2 mutation in women with a BRCA1 mutation may not increase their risk',
      pubmed_ids: ['18930998'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'MT-2A could plausibly modulate cell cycle progression from G1- to S-phase via the ATM/Chk2/cdc25A pathway.',
      pubmed_ids: ['19062161'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Tax binds to and stabilizes a protein complex with DNA-PK and Chk2, resulting in a saturation of DNA-PK-mediated damage repair response',
      pubmed_ids: ['18957425'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Life time risks for CHEK2 1100delC carrier and noncarrier daughters of bilateral breast cancer cases of 37% and 18%, respectively.',
      pubmed_ids: ['19124502'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Women with a CHEK2 mutation face a fourfold increase in the risk of estrogen receptor-positive breast cancer',
      pubmed_ids: ['19021634'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHEK2 1100delC mutation is not present in Korean patients with breast cancer cases tested for BRCA1 and BRCA2 mutation',
      pubmed_ids: ['18175216'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations L303X & 1100delC cause a premature termination codon preventing CHEK2 & P-Thr68 CHEK2 protein expression. CHEK2 & p53 operate in the same tumor suppressor pathway.A main CHEK2 oncogenic function involves p53-mediated G1 cell-cycle arrest.',
      pubmed_ids: ['18297428'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'autophosphorylation of the FHA domain at the highly conserved Ser-140 position, a major pThr contact in all FHA-phosphopeptide complex structures, revealing a mechanism of Chk2 dimer dissociation following kinase domain activation.',
      pubmed_ids: ['18948271'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2.1100delC mutation may be a rare variant in Chinese, may be an association between genetic susceptibility to breast cancer in China and the variant 1111C>T.',
      pubmed_ids: ['18484200'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Strap regulation reflects the coordinated interplay between different DNA damage-activated protein kinases, ATM and Chk2 (Checkpoint kinase 2), where phosphorylation by each kinase provides a distinct functional consequence on the activity of Strap.',
      pubmed_ids: ['18833288'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These findings suggest that nuclear activation of Chk2 by TRAIL acts as a positive feedback loop involving the mitochondrion-dependent activation of caspases, independently of p53.',
      pubmed_ids: ['18955500'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The intramolecular phosphorylation sites in CHK2 are explored.',
      pubmed_ids: ['18812180'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 formed a complex with XRCC1, the BER scaffold protein, and phosphorylated XRCC1 in vivo and in vitro at Thr(284).',
      pubmed_ids: ['18971944'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'maximum expression of p53-Ser15(P) coincided in time with the peak of Chk2 activation',
      pubmed_ids: ['18802408'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Germline CHEK2 mutations are associated resistance to drug therapy in breast cancer paatients.',
      pubmed_ids: ['18725978'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'analysis of a novel CHEK2 missense variant, R406H, that is found to be unlikely to contribute to breast cancer risk in French Canadian women',
      pubmed_ids: ['18706089'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'analysis of how the breast cancer genes ATM, BRIP1, PALB2 and CHEK2 affect risk for women with strong family histories [review]',
      pubmed_ids: ['18557994'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'germline CHEK2 mutations have a minor role in, if any, prostatic cancer susceptibility in Ashkenazi Jewish men.',
      pubmed_ids: ['18571837'],
    },
    {
      entrez_id: '11200',
      rif_text: 'a link between CHEK2 and BRCA2 pathways',
      pubmed_ids: ['18797466'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Auto-/transphosphorylation of Serine 379 is required for Chk2 ubiquitination and effector function.',
      pubmed_ids: ['18644861'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Novel missense variants of CHEK2 is associated with breast cancer.',
      pubmed_ids: ['18058223'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the ATM-Chk2 signaling pathway is critical for HCV RNA replication',
      pubmed_ids: ['18667510'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The findings suggest that the CHEK2 100delC mutation is not present or is present at an extremely low frequency in Chilean families with familial breast cancer.',
      pubmed_ids: ['17876702'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the 1100delC variant of CHEK2 confers a colorectal cancer risk in HNPCC/HNPCC-related families',
      pubmed_ids: ['18676774'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study of gene-disease association, gene-environment interaction, and pharmacogenomic / toxicogenomic. (HuGE Navigator)',
      pubmed_ids: ['20644561', '19536092', '18725978'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'A quantitative cell-based assay using a high-content analysis platform was developed in an effort to identify small-molecule activators of CHK2.',
      pubmed_ids: ['18566483'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'ATO-induced activation of Chk2/p53 and p38 MAPK/p53 apoptotic pathways can be enhanced by siRNA-mediated suppression of Wip1 expression, further indicating that ATO inhibits Wip1 phosphatase in vivo',
      pubmed_ids: ['18482988'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These findings systematically dissect the differential roles of Chk1 and Chk2 in a favorable model pursuing camptothecin-driven DNA damage responses.',
      pubmed_ids: ['18566216'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'BRCA1/2 rearrangements is not advantageous in male breast neoplasm (MBC) cases not belonging to high-risk breast cancer families and that common CHEK2 mutations play an irrelevant role in MBC predisposition in Italy.',
      pubmed_ids: ['17661168'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk1 and Chk2 regulate the functional associations between hBRCA2 and Rad51 in response to DNA damage',
      pubmed_ids: ['18317453'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Autophosphorylated residues involved in the regulation of CHEK2 in vitro are described.',
      pubmed_ids: ['18538787'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 deficiency diminished the growth of wild-type HSV-1, but not the growth of an ICP0-deleted recombinant virus.',
      pubmed_ids: ['18321553'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'an important role for the DNA damage response mediated by ATR-Chk2 in p53 activation and renal cell apoptosis during cisplatin nephrotoxicity.',
      pubmed_ids: ['18162465'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Lung cancer cells from people with impaired CHEK2 function undergo increased rates of cell death.',
      pubmed_ids: ['18281249'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The frequency of the CHEK2 founder allele was measured in 3,882 breast cancer patients and 8,609 controls from various countries.',
      pubmed_ids: ['18381420'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'No significant associations was found between the CHEK2*1100delC mutation and contralateral breast cancer',
      pubmed_ids: ['18253122'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study and meta-analysis of gene-disease association. (HuGE Navigator)',
      pubmed_ids: ['19116388', '19064572', '18270339'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Meta-analysis of gene-disease association. (HuGE Navigator)',
      pubmed_ids: ['19124502', '18172190'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study of gene-disease association and gene-gene interaction. (HuGE Navigator)',
      pubmed_ids: [
        '20731661',
        '20496165',
        '20306497',
        '19714462',
        '19030985',
        '18930998',
        '18415014',
        '18381943',
        '17409195',
        '17372254',
        '17341484',
      ],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study of gene-disease association, gene-gene interaction, and gene-environment interaction. (HuGE Navigator)',
      pubmed_ids: ['19789190', '17333333'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study of gene-disease association and gene-environment interaction. (HuGE Navigator)',
      pubmed_ids: [
        '19401704',
        '19265784',
        '18253122',
        '17428320',
        '17164260',
        '16816021',
        '16492927',
        '16257342',
      ],
    },
    {
      entrez_id: '11200',
      rif_text: 'Observational study of genotype prevalence. (HuGE Navigator)',
      pubmed_ids: [
        '18175216',
        '17380889',
        '17333477',
        '17113724',
        '16858628',
        '16830057',
        '15488637',
        '11967536',
      ],
    },
    {
      entrez_id: '11200',
      rif_text: 'function and regulation of Cds1 - review',
      pubmed_ids: ['12111733'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Observational study of gene-disease association. (HuGE Navigator)',
      pubmed_ids: [
        '20875877',
        '20722467',
        '20658728',
        '20472656',
        '20462940',
        '20453000',
        '19876921',
        '19863560',
        '19763819',
        '19656415',
        '19548527',
        '19399639',
        '19372713',
        '19338683',
        '19338682',
        '19124506',
        '19021634',
        '18996005',
        '18950845',
        '18834326',
        '18759107',
        '18706089',
        '18676774',
        '18571837',
        '18484200',
        '18381420',
        '18281249',
        '18086781',
        '18058223',
        '18024013',
        '17918154',
        '17721994',
        '17705858',
        '17684142',
        '17661168',
        '17517688',
        '17428325',
        '17250914',
        '17214356',
        '17164383',
        '17132695',
        '17132159',
        '17106448',
        '17085682',
        '17040931',
        '17010071',
        '16914568',
        '16883537',
        '16880452',
        '16828850',
        '16758118',
        '16671833',
        '16574953',
        '16539695',
        '16452051',
        '16239104',
        '16043347',
        '15987456',
        '15980987',
        '15852425',
        '15818573',
        '15810020',
        '15803363',
        '15649950',
        '15535844',
        '15492928',
        '15472904',
        '15466005',
        '15385111',
        '15239132',
        '15122511',
        '15095295',
        '15087378',
        '15057041',
        '14997059',
        '14970869',
        '14678969',
        '14648717',
        '14612911',
        '14568168',
        '14507240',
        '12917215',
        '12529183',
        '12454775',
        '11751432',
        '11461078',
      ],
    },
    {
      entrez_id: '11200',
      rif_text:
        'pChk2 merits further investigation as a promising biomarker that can discriminate those lesions at risk for developing SCC, regardless of histologic evidence for atypia.',
      pubmed_ids: ['18086786'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Since risk of breast cancer at age 70 years among familial patient cases for CHEK2*1100delC heterozygotes is almost as high as for BRCA1 and BRCA2 mutation heterozygotes, genotyping should be considered in women with a family history of breast cancer.',
      pubmed_ids: ['18172190'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHK2 mutation in colorectal cancer is a low frequency event.',
      pubmed_ids: ['18167186'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2 truncated protein could not be detected, even when nonsense-mediated mRNA decay (NMD) mechanism was inhibited. This suggests that CHK2 truncated protein is unstable',
      pubmed_ids: ['17694537'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Germline mutations in the CHEK2 kinase gene are associated with bladder cancer',
      pubmed_ids: ['17918154'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'We believe that CHEK2 mutations are not associated with the cancer types seen in the LFS or LFL (other than breast cancer) and it is no longer reasonable to consider CHEK2 mutations to be a cause of LFS (Li-Fraumeni syndrome).',
      pubmed_ids: ['18178638'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 missense mutations may contribute to breast cancer susceptibility in Ashkenazi Jews.',
      pubmed_ids: ['18085035'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Parallel studies of the human CHEK2 gene have also highlighted its role as a candidate multiorgan tumour susceptibility gene rather than a highly penetrant predisposition gene for Li-Fraumeni syndrome.',
      pubmed_ids: ['18004398'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mis-sense variant and reduced risk of tobacco-related cancers',
      pubmed_ids: ['17517688'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The results indicate a critical role for Chk2 in methylglyoxal-induced G(2)/M cell-cycle checkpoint arrest.',
      pubmed_ids: ['17663721'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Loss of heterozygosity (LOH) across the CHEK2 locus is common in sporadic breast, ovarian, and colorectal cancers, but point mutation or epigenetic inactivation of the retained allele is uncommon.',
      pubmed_ids: ['17145815'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'clinical testing for rare missense mutations within CHEK2 may have limited value in predicting breast cancer risk, but that testing for the 1100delC variant may be valuable in phenotypically- and geographically-selected populations.',
      pubmed_ids: ['17721994'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'checkpoint kinase 2 stability is regulated via phosphorylation at serine 456',
      pubmed_ids: ['17715138'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Notwithstanding the involvement of the CHEK2 gene in breast cancer aetiology, we show that common polymorphisms do not influence postmenopausal breast cancer risk.',
      pubmed_ids: ['16671833'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'In total 2.2% of the patients with a family history of breast cancer carried the variant compared to 0.7% of the controls.',
      pubmed_ids: ['17705858'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Tax binding via the Chk2 kinase domain sequesters phosphorylated Chk2 within chromatin, thus hindering chromatin egress and appropriate response to DNA damage',
      pubmed_ids: ['17698850'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 inactivation is associated with intraductal papillary mucinous neoplasms of the pancreas',
      pubmed_ids: ['17671118'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'no significant association between CHEK2*1100delC and familial or sporadic chronic lymphocytic leukemia',
      pubmed_ids: ['17169815'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Given the low expected mutation rate of up to 1.4% for CHEK2 * 1100delC in the European population the data are suggestive for possible contribution of CHEK2 mutations to a small subset of Familial pancreatic cancer.',
      pubmed_ids: ['16858628'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'This is the first report of high ATM-Chk2 kinase activation and its linkage to replication defects in a Bloom syndrome model.',
      pubmed_ids: ['17634426'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'possible interplay between tumor protein p53 C-terminal phosphorylation and acetylation, and they provide an additional mechanism for the control of the activity of p53 by Checkpoint kinase 1 and Checkpoint kinase 2',
      pubmed_ids: ['15659650'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'some splice variants lack CHK2 function and/or localize aberrantly',
      pubmed_ids: ['15361853'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the otherwise dormant Chk2 is aberrantly and constitutively activated in invasive urinary bladder carcinomas',
      pubmed_ids: ['15361851'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Variations in this enzyme other than 1100delC do not make a major contribution to breast cancer susceptibility.',
      pubmed_ids: ['12610780'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'the NLS-3 motif located at amino acids 515-522 acts indeed as Nuclear Localization Signal for Chk2',
      pubmed_ids: ['12909615'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 1100delC is not a major cause of double primary breast and colorectal cancer in Sweden.',
      pubmed_ids: ['16539695'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These results demonstrate a sophisticated control by ATM of a target protein, Hdmx, which itself is one of several ATM targets in the ATM-p53 axis of the DNA damage response.',
      pubmed_ids: ['16943424'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These results identify a novel role for FoxM1 in the transcriptional response during DNA damage/checkpoint signaling and show a novel mechanism by which Chk2 protein regulates expression of DNA repair enzymes.',
      pubmed_ids: ['17101782'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'results suggest that aberrations of the CHK2 gene are rare in pediatric solid tumors',
      pubmed_ids: ['15942682'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 correlated with reduced expression of h-TERT and p27, but not with angiogenic factors in breast cancer; Chk2 expression also did not interfere in the outcome of the patients',
      pubmed_ids: ['16437383'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data suggest that the CHEK2 and TP53 mutations can substitute each other in at least 25% (21/84) of prostate cancers and that DNA damage-signaling pathway plays an important role in prostate cancer tumorigenesis.',
      pubmed_ids: ['16941491'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'These results indicate that Wip1 is one of the phosphatases regulating the activity of Chk2 in response to DNA damage.',
      pubmed_ids: ['16936775'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'A large deletion of exons 9 and 10 of CHEK2 confers an increased risk of prostate cancer.',
      pubmed_ids: ['17085682'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'carrying the CHEK2*1100delC mutation is an adverse prognostic indicator for breast cancer',
      pubmed_ids: ['15466005'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'there is a limited relevance for CHEK2 mutations in familial breast cancer',
      pubmed_ids: ['15095295'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'A functionally defective CHEK2 variant associates with an increased risk of colorectal cancer.',
      pubmed_ids: ['16816021'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'p53 negatively regulates Chk2 gene transcription through modulation of NF-Y function and that this regulation may be important for reentry of cells into the cell cycle after DNA damage is repaired.',
      pubmed_ids: ['15044452'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'genetic changes in CHK2 occur in small proportion of vulval squamous cell carcinomas',
      pubmed_ids: ['11875739'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 variants are low-penetrance prostate cancer predisposition alleles that contribute significantly to familial clustering of prostate cancer at the population level',
      pubmed_ids: ['14612911'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Determination of substrate specificity and putative substrates of Chk2 kinase.',
      pubmed_ids: ['12711320'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'determination as to the role of CHEK2 1100delC mutation in enhanced chromosomal radiosensitivity in breast cancer patients',
      pubmed_ids: ['16337852'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations in proline 82 of p53 impair its activation by PIN1 and CHK2 in response to DNA damage.',
      pubmed_ids: ['15964795'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Germ-line and somatic mutations that affect the kinase activity of CHEK2 are associated with the development of prostate cancer.',
      pubmed_ids: ['16835864'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'phosphorylation of Thr-68 may be required for initial oligomerization and activation of Chk2, but it is not needed for maintenance of dimerization or kinase activity',
      pubmed_ids: ['12386164'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Phosphorylation of threonine 68 promotes oligomerization and autophosphorylation of the Chk2 protein kinase via the forkhead-associated domain',
      pubmed_ids: ['11901158'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'MDC1 is recruited through its FHA domain to the activated CHK2, and has a critical role in CHK2-mediated DNA damage responses',
      pubmed_ids: ['12607004'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'functional link between recombination control and breast cancer predisposition in carriers of Chk2 and BRCA1 germ line mutations',
      pubmed_ids: ['14701743'],
    },
    {
      entrez_id: '11200',
      rif_text: 'TTK functions upstream from CHK2 in response to DNA damage',
      pubmed_ids: ['15618221'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'HDM2 negatively affects the Chk2-mediated phosphorylation of p53.',
      pubmed_ids: ['15862297'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'in the human orthologue of Cds1, CHK2, differential splicing of a cryptic exon leads to a frame shift and premature termination producing a short variant (SvCHK2).',
      pubmed_ids: ['15467464'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'p53-independent role for Chk2 in p21 induction and senescence that may contribute to tumor suppression',
      pubmed_ids: ['16317088'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 mutations may be associated with specific histologic subtypes of breast cancer in Polish women.  I157T missense mutation was strongly associated with lobular carcinoma.',
      pubmed_ids: ['15803365'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 germline mutation rarely contributes to breast cancer development in the Czech Republic',
      pubmed_ids: ['15803363'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results suggest that E2F1 plays a central role in signaling disturbances in the retinoblastoma growth control pathway and, by upregulation of Chk2 by Atm and Nbs1, may sensitize cells to undergo apoptosis.',
      pubmed_ids: ['15024084'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Therefore, these results are the first to indicate a novel mechanism of regulating Chk2 in cisplatin-induced resistance of cancer cells.',
      pubmed_ids: ['15694385'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk1 and Chk2 control the induction of the p53 related transcription factor p73 in response to DNA damage.',
      pubmed_ids: ['15601819'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 autophosphorylation is critical for Chk2 function following DNA damage',
      pubmed_ids: ['12855706'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 germ line mutation is associated with bilateral breast cancer',
      pubmed_ids: ['15472904'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'a role of CHEK2 in the pathway of alternative TP53 inactivation in primary glioblastoma.',
      pubmed_ids: ['16078115'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'DNA-PK augments ATM and ATR in activation of Chk2 by DNA damage.',
      pubmed_ids: ['15668230'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Our results support the hypothesis that carrier status for CHEK2*1100delC is associated with increased breast cancer risk and suggest that this relationship may be modified by other factors, such as radiation exposure.',
      pubmed_ids: ['16492927'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Preeminent associations were identified in SNPs mapping to genes pivotal in the DNA damage-response and cell-cycle pathways, including ATM F858L and P1054R, CHEK2 I157T, BRCA2 N372H, and BUB1B Q349R.',
      pubmed_ids: ['16574953'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'High relevance of the 1100delC variant for breast cancer predisposition in Russia',
      pubmed_ids: ['16758118'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'an intrinsic kinase activity of Chk2, but not phosphatase activity of Wip1, is required for the association of fulllength Chk2 and Wip1',
      pubmed_ids: ['16798742'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'deregulation of CHEK2 and/or PPP2R2A is of pathogenetic importance in at least a subset of germ cell tumors',
      pubmed_ids: ['16790090'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Results underscore the critical roles of S19, S33, and S35 and argue that these phosphoresidues may serve to fine-tune the ATM-dependent response of Chk2 to increasing amounts of DNA damage.',
      pubmed_ids: ['16940182'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Germ line mutation in checkpoint kinase 2 is associated with breast cancer patients with a positive estrogen receptor status',
      pubmed_ids: ['17010071'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2*1100delC carriers have an increased risk of second breast cancer and a worse long-term recurrence-free survival rate',
      pubmed_ids: ['17132695'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Heterozygosity for a germline CHEK2 mutation appears to represent an adverse prognostic factor in patients with early-stage breast cancer.',
      pubmed_ids: ['17250914'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2 alterations are uncommon in malignant lymphomas but occur in a subset of aggressive tumors.  The high number of chromosomal imbalances in tumors with complete absence of CHK2 protein suggests a role in chromosomal instability in human lymphomas.',
      pubmed_ids: ['12393693'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The 1100delC variant of the CHEK2 gene was present in 18% of 55 families with hereditary breast and colorectal cancer (HBCC) as compared with 4% of 380 families with non-HBCC and may act in synergy with unknown susceptibility gene(s)',
      pubmed_ids: ['12690581'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Increased phosphate incorporation into serine residues generated by the combined action of CHK1 and CHK2 kinases correlated with the ionizing radiation-induced acceleration of Cdc25A proteolysis.',
      pubmed_ids: ['12676583'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEKs and balances: accounting for breast cancer.',
      pubmed_ids: ['11984555'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Compensation of the 1100delC defect in CHEK2 might explain the rather low breast cancer risk associated with the CHEK2 variant, compared to that associated with truncating mutations in BRCA1 or BRCA2',
      pubmed_ids: ['15700044'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'results are consistent with a low-penetrance effect (OR 1.5-2.0) of the CHEK2 1100delC on CRC risk.',
      pubmed_ids: ['15852425'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Chk2 kinase was regualted by the oncogenic Wip1 phosphatase.',
      pubmed_ids: ['16311512'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'tumor cells exposed to DNA damage counteract cell death by releasing the antiapoptotic protein, survivin, from mitochondria, which reauires activated checkpoint kinase 2 (Chk2.',
      pubmed_ids: ['17178848'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'common polymorphisms in the ATM, BRCA1, BRCA2, CHEK2 and TP53 cancer susceptibility genes are not shown to increase breast cancer risk',
      pubmed_ids: ['17428325'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'utilization of peptide library analyses to develop specific, highly preferred substrate motifs for hCds1/Chk2 and Chk1',
      pubmed_ids: ['11821419'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Low-penetrance susceptibility to breast cancer due to CHEK2(*)1100delC in noncarriers of BRCA1 or BRCA2 mutations.',
      pubmed_ids: ['11967536'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'interaction with polo-like kinase 1 and localization to centrosomes and midbody',
      pubmed_ids: ['12493754'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Plk3 is rapidly activated by reactive oxygen species fibroblasts cells, correlating with increased p53 protein levels. Plk3 physically interacts with Chk2 and the interaction is enhanced upon DNA damage.',
      pubmed_ids: ['12548019'],
    },
    {
      entrez_id: '11200',
      rif_text: 'mutation is associated with familial breast cancer',
      pubmed_ids: ['12094328'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 activity is triggered by a greater number of double strand breaks, implying that, below a certain threshold level of lesions, DNA repair can occur through ATM, without enforcing Chk2-dependent checkpoints.',
      pubmed_ids: ['15361830'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'chk2 is recruited into the PML nuclear bodies by PML along with p53',
      pubmed_ids: ['12810724'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Mutations in CHEK2 is associated with breast cancer',
      pubmed_ids: ['15649950'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'evidence that CHK2 can be activated allosterically towards some substrates by a novel docking interaction; identifed a potential regulatory switch that may channel CHK2 into distinct signalling pathways in vivo',
      pubmed_ids: ['12897801'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Destabilization of CHK2 by a missense mutation associated with Li-Fraumeni Syndrome.',
      pubmed_ids: ['11719428'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk1 and Chk2 have roles in mismatch repair-dependent G2 arrest',
      pubmed_ids: ['15647386'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The activation of ATM/ATR/CHK signaling pathways contributes to this G2 checkpoint and highlight the interrelated roles of p14ARF and the Tip60 protein in the initiation of this DNA damage-signaling cascade.',
      pubmed_ids: ['16705183'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Data demonstrate that PML (promyelocytic leukemia)interacts with Chk2 and activates Chk2 by mediating its autophosphorylation step.',
      pubmed_ids: ['16835227'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mre11 stabilizes Nbs1 and Rad50 and MRN activates Chk2 downstream from ATM in response to replication-mediated DNA double strand breaks',
      pubmed_ids: ['16905549'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'hereditary breast and colorectal cancer syndrome, if it exists as a separate entity, is not likely to be due to CHEK2 mutations',
      pubmed_ids: ['17026620'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'EBNA3C can directly regulate the G2/M component of the host cell cycle machinery through ATM/ATR and Chk2, allowing for the release of the checkpoint block',
      pubmed_ids: ['17409144'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Phosphorylation of p53 (Ser15), Chk1 (Ser345), and Chk2 (Thr68) was also observed, suggesting that H/R activates p53 through checkpoint signals.',
      pubmed_ids: ['17544403'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Mutations of the CHK2 gene are found in some osteosarcomas, but are rare in breast, lung, and ovarian tumors.',
      pubmed_ids: ['11746983'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Chk2 kinase is not required for p53 activation in human cells and explain why CHK2 and TP53 mutations can jointly occur in human tumors.',
      pubmed_ids: ['12654917'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'although Chk2 purified from DNA damage sustaining cells has dramatically increased ability to phosphorylate Cdc25C when compared with untreated cells, its ability to phosphorylate p53 is weak',
      pubmed_ids: ['12654916'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Down regulation of Cdk1/cyclin B is secondary to the activation of Chk2. A conflict in cell cycle progression or DNA damage can lead to mitotic catastrophe, provided that the checkpoint kinase Chk2 is inhibited.',
      pubmed_ids: ['15048074'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The CHEK2 1100delC allele was not over-represented in cases suggesting that this variant is not associated with an increased risk of colorectal disease.',
      pubmed_ids: ['14568168'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Two truncating mutations of CHEK2 confer a moderate risk of prostate cancer in Polish men and that the missense change appears to confer a modest risk.',
      pubmed_ids: ['15087378'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Plk3 is in a pathway linking ATM, Plk3, Chk2, Cdc25C and Cdc2 in cellular response to DNA damage.',
      pubmed_ids: ['16481012'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'ATR is one of the kinases that is likely involved in phosphorylation of Chk2 in response to ionizing radiation when ATM is deficient.',
      pubmed_ids: ['16741947'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2*1100delC heterozygosity is associated with a three-fold risk of breast cancer in women in the general population',
      pubmed_ids: ['16880452'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Defects may predispose to tumors, with particular emphasis on familial breast cancer. [REVIEW]',
      pubmed_ids: ['16998506'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Breast tumors carrying a mutation in CHEK2 are rare and show contradictory results, probably due to the low number of these cases. [REVIEW]',
      pubmed_ids: ['16998498'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'I157T mutation increases the risk of colorectal cancer in the population; truncating mutations may confer a lower risk or no increase in risk.',
      pubmed_ids: ['17106448'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'HuR regulates SIRT1 expression, underscore functional links between the two stress-response proteins, and implicate Chk2 in these processes.',
      pubmed_ids: ['17317627'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'study from South India, on BRCA1, BRCA2 & CHEK2 mutations in patients with a family history of breast and/or ovarian cancer and early onset breast/ovarian cancer',
      pubmed_ids: ['14507240'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHK2 triggers replicative senescence.',
      pubmed_ids: ['15192702'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Plk1 Polo box domain mediates a cell cycle and DNA damage regulated interaction with Chk2',
      pubmed_ids: ['15876876'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Although phospho-dependent binding is important for Chk2 activity, previously uncharacterized phospho-independent FHA domain interactions appear to be the primary target of oncogenic lesions.',
      pubmed_ids: ['12049740'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'robust method for detecting CHK2/RAD53 mutations in genomic DNA',
      pubmed_ids: ['11793476'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'data reveal the very different mode of regulation between CHK1 and CHK2',
      pubmed_ids: ['14681223'],
    },
    {
      entrez_id: '11200',
      rif_text: 'CHEK2*1100delC confers an increased risk of breast cancer',
      pubmed_ids: ['15122511'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHK2-depleted cells do not exhibit chromosome instability or common fragile site breaks.',
      pubmed_ids: ['16732333'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'The response of promyelocytic leukemia nuclear bodies to DNA double-strand breaks is regulated by NBS1, ATM, Chk2, and ATR.',
      pubmed_ids: ['17030982'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Novel substrates for Chk1 and Chk2 were screened using substrate target motifs determined previously by an oriented peptide library approach.',
      pubmed_ids: ['17464182'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'checkpoint kinase hCds1/Chk2 has a role in regulating PML-dependent apoptosis after DNA damage',
      pubmed_ids: ['12402044'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Expression of a dominant-negative Chk2 mutant blocks induction of E2F-1 and prevents E2F-1-dependent apoptosis. Moreover, E2F-1 is resistant to induction by etoposide in tumour cells expressing mutant chk2.',
      pubmed_ids: ['12717439'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Zinc-finger protein transcription factors bind an 18-bp recognition sequence within the promoter of the endogenous CHK2 gene, giving a >10-fold reduction in CHK2 mRNA and protein',
      pubmed_ids: ['14514889'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'autophosphorylation of Chk2 can occur both in cis and in trans and suggest that oligomerization may regulate Chk2 activation by promoting these cis- and trans-phosphorylation events',
      pubmed_ids: ['12805407'],
    },
    {
      entrez_id: '11200',
      rif_text: 'Chk2 is regulated by NFBD1 and 53BP1 in human tumor cells',
      pubmed_ids: ['12551934'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'CHEK2 protein mutation is not clinically important high risk gene for hereditary prostate cancer susceptibility in the population of Southern Sweden.',
      pubmed_ids: ['16452051'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Gene repair directed by oligonucleotides activates a pathway that prevents corrected cells from proliferating in cell culture through the activation of Chk1 and Chk2.',
      pubmed_ids: ['16414312'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Three founder alleles in CHEK2 contribute to early-onset breast cancer in Poland. Breast tumors which arise in carriers of CHEK2 mutations seem to be similar to those of breast cancers in the population at large.',
      pubmed_ids: ['16914568'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'Common variants in the ATM and CHEK2 genes, in interaction with oestrogen-related exposures, are involved in endometrial cancer aetiology.',
      pubmed_ids: ['17164260'],
    },
    {
      entrez_id: '11200',
      rif_text:
        'results suggest that Chk2 oligomerization regulates Chk2 activation, signal amplification, and transduction in DNA damage checkpoint pathways',
      pubmed_ids: ['12024051'],
    },
  ],
  smallVariant: {
    release: 'GRCh37',
    chromosome: '22',
    chromosome_no: 22,
    start: 29118327,
    end: 29118327,
    bin: 807,
    reference: 'G',
    alternative: 'A',
    var_type: 'snv',
    info: {},
    genotype: {
      'NA12878-N1-DNA1-WES1': { ad: 1, dp: 1, gq: 3, gt: '1/1' },
      'NA12891-N1-DNA1-WES1': { ad: 4, dp: 4, gq: 12, gt: '1/1' },
      'NA12892-N1-DNA1-WES1': { ad: -1, dp: -1, gq: -1, gt: './.' },
    },
    num_hom_alt: 0,
    num_hom_ref: 0,
    num_het: 0,
    num_hemi_alt: 0,
    num_hemi_ref: 0,
    in_clinvar: false,
    exac_frequency: 0,
    exac_homozygous: 0,
    exac_heterozygous: 0,
    exac_hemizygous: null,
    thousand_genomes_frequency: 0,
    thousand_genomes_homozygous: 0,
    thousand_genomes_heterozygous: 0,
    thousand_genomes_hemizygous: null,
    gnomad_exomes_frequency: 0,
    gnomad_exomes_homozygous: 0,
    gnomad_exomes_heterozygous: 0,
    gnomad_exomes_hemizygous: null,
    gnomad_genomes_frequency: 0.583426,
    gnomad_genomes_homozygous: 5427,
    gnomad_genomes_heterozygous: 6986,
    gnomad_genomes_hemizygous: null,
    refseq_gene_id: null,
    refseq_transcript_id: 'NM_001005735.1',
    ensembl_gene_id: 'ENSG00000183765',
    ensembl_transcript_id: 'ENST00000328354.6',
    gene_id: '11200',
    transcript_id: 'NM_001005735.1',
    transcript_coding: true,
    hgvs_c: 'c.721+2638C>T',
    hgvs_p: 'p.=',
    effect: ['coding_transcript_intron_variant'],
    effect_ambiguity: false,
    exon_dist: 2638,
    case_uuid: '3b22fce8-9be8-4387-8e6e-3be73f4228fb',
    family_name: 'NA12878',
    mtdb_count: 0,
    mtdb_frequency: 0,
    mtdb_dloop: false,
    helixmtdb_het_count: 0,
    helixmtdb_hom_count: 0,
    helixmtdb_frequency: 0,
    helixmtdb_is_triallelic: false,
    mitomap_count: 0,
    mitomap_frequency: 0,
    rsid: null,
    symbol: 'CHEK2',
    gene_name: 'checkpoint kinase 2',
    gene_family: '',
    pubmed_id: '9836640|10097108',
    hgnc_id: 'HGNC:16627',
    uniprot_ids: 'O96017',
    gene_symbol: '',
    acmg_symbol: null,
    mgi_id: null,
    flag_count: null,
    flag_bookmarked: null,
    flag_candidate: null,
    flag_segregates: null,
    flag_doesnt_segregate: null,
    flag_final_causative: null,
    flag_for_validation: null,
    flag_no_disease_association: null,
    flag_molecular: null,
    flag_visual: null,
    flag_validation: null,
    flag_phenotype_match: null,
    flag_summary: null,
    comment_count: null,
    extra_annos: null,
    acmg_class_auto: null,
    acmg_class_override: null,
    modes_of_inheritance: ['AD'],
    disease_gene: 'True',
    gnomad_pLI: 1.2103e-24,
    gnomad_mis_z: -0.45001,
    gnomad_syn_z: 1.1405,
    gnomad_oe_lof: 1.1499,
    gnomad_oe_lof_upper: 1.53,
    gnomad_oe_lof_lower: 0.874,
    gnomad_loeuf: 1.531,
    exac_pLI: null,
    exac_mis_z: null,
    exac_syn_z: null,
    inhouse_hom_ref: 0,
    inhouse_het: 0,
    inhouse_hom_alt: 0,
    inhouse_hemi_ref: 0,
    inhouse_hemi_alt: 0,
    inhouse_carriers: 0,
    variation_type: '',
    vcv: '',
    summary_review_status_label: '',
    summary_pathogenicity_label: '',
    summary_pathogenicity: [],
    summary_gold_stars: 0,
    details: [],
  },
}

export const Mitochondrial = Template.bind({})
Mitochondrial.args = {
  gene: {
    omim: {
      604364: [
        'EPILEPSY, FAMILIAL FOCAL, WITH VARIABLE FOCI',
        ['EPILEPSY, PARTIAL, WITH VARIABLE FOCI'],
      ],
    },
    omim_genes: [614191],
    hpo_inheritance: [['HP:0000006', 'AD']],
    hpo_terms: [
      ['HP:0000729', 'Autistic behavior'],
      ['HP:0032046', 'Focal cortical dysplasia'],
      ['HP:0032047', 'Focal cortical dysplasia type I'],
      ['HP:0032051', 'Focal cortical dysplasia type II'],
      ['HP:0032052', 'Focal cortical dysplasia type IIa'],
      ['HP:0007206', 'Hemimegalencephaly'],
      ['HP:0003829', 'Incomplete penetrance'],
      ['HP:0001249', 'Intellectual disability'],
      ['HP:0031951', 'Nocturnal seizures'],
      ['HP:0003812', 'Phenotypic variability'],
      ['HP:0001250', 'Seizures'],
    ],
    clinvar_pathogenicity: {
      symbol: 'DEPDC5',
      entrez_id: '9681',
      ensembl_gene_id: 'ENSG00000100150',
      pathogenic_count: 122,
      likely_pathogenic_count: 49,
    },
    gnomad_constraints: {
      symbol: 'DEPDC5',
      ensembl_transcript_id: 'ENST00000382112',
      obs_mis: 713,
      exp_mis: 941.88,
      oe_mis: 0.757,
      mu_mis: 0.000056764,
      possible_mis: 10514,
      obs_mis_pphen: 258,
      exp_mis_pphen: 395.16,
      oe_mis_pphen: 0.65289,
      possible_mis_pphen: 4348,
      obs_syn: 338,
      exp_syn: 358.1,
      oe_syn: 0.94386,
      mu_syn: 0.000022536,
      possible_syn: 3024,
      obs_lof: 24,
      mu_lof: 0.0000059951,
      possible_lof: 1045,
      exp_lof: 101.96,
      pLI: 0.1165,
      pNull: 6.8626e-17,
      pRec: 0.8835,
      oe_lof: 0.23539,
      oe_syn_lower: 0.863,
      oe_syn_upper: 1.033,
      oe_mis_lower: 0.711,
      oe_mis_upper: 0.805,
      oe_lof_lower: 0.169,
      oe_lof_upper: 0.331,
      constraint_flag: null,
      syn_z: 0.83513,
      mis_z: 2.6501,
      lof_z: 7.1543,
      oe_lof_upper_rank: 2748,
      oe_lof_upper_bin: 1,
      oe_lof_upper_bin_6: 0,
      n_sites: 33,
      classic_caf: 0.00017837,
      max_af: 0.000024103,
      no_lofs: 124867,
      obs_het_lof: 43,
      obs_hom_lof: 0,
      defined: 124910,
      p: 0.00017214,
      exp_hom_lof: 0.0037013,
      classic_caf_afr: 0.0003877,
      classic_caf_amr: 0.00020706,
      classic_caf_asj: 0.000099325,
      classic_caf_eas: 0.00028483,
      classic_caf_fin: 0.00027866,
      classic_caf_nfe: 0.00012511,
      classic_caf_oth: 0,
      classic_caf_sas: 0.00016402,
      p_afr: 0.00032205,
      p_amr: 0.00020272,
      p_asj: 0.00009929,
      p_eas: 0.00027695,
      p_fin: 0.00027807,
      p_nfe: 0.0001235,
      p_oth: 0,
      p_sas: 0.00016337,
      transcript_type: 'protein_coding',
      ensembl_gene_id: 'ENSG00000100150',
      transcript_level: 2,
      cds_length: 4782,
      num_coding_exons: 42,
      gene_type: 'protein_coding',
      gene_length: 153069,
      exac_pLI: 1,
      exac_obs_lof: 7,
      exac_exp_lof: 76.346,
      exac_oe_lof: 0.091688,
      brain_expression: null,
      chromosome: '22',
      start_position: 32149944,
      end_position: 32303012,
    },
    exac_constraints: null,
    hgnc_id: 'HGNC:18423',
    symbol: 'DEPDC5',
    name: 'DEP domain containing 5',
    locus_group: 'protein-coding gene',
    locus_type: 'gene with protein product',
    status: 'Approved',
    location: '22q12.2-q12.3',
    location_sortable: '22q12.2-q12.3',
    alias_symbol: 'KIAA0645|DEP.5',
    alias_name: null,
    prev_symbol: null,
    prev_name: null,
    gene_family: 'GATOR1 subcomplex',
    gene_family_id: '1394',
    date_approved_reserved: '2004-05-05',
    date_symbol_changed: null,
    date_name_changed: null,
    date_modified: '2018-02-13',
    entrez_id: '9681',
    ensembl_gene_id: 'ENSG00000100150',
    vega_id: 'OTTHUMG00000030926',
    ucsc_id: 'uc003alt.4',
    ucsc_id_novers: 'uc003alt',
    ena: 'AB014545',
    refseq_accession: 'NM_014662',
    ccds_id:
      'CCDS43006|CCDS43007|CCDS46692|CCDS56229|CCDS74849|CCDS87017|CCDS87018',
    uniprot_ids: 'O75140',
    pubmed_id: '23542697|23542701',
    mgd_id: 'MGI:2141101',
    rgd_id: 'RGD:1311535',
    lsdb: null,
    cosmic: 'DEPDC5',
    omim_id: '614191',
    mirbase: null,
    homeodb: null,
    snornabase: null,
    bioparadigms_slc: null,
    orphanet: '353372',
    pseudogene_org: null,
    horde_id: null,
    merops: null,
    imgt: null,
    iuphar: null,
    kznf_gene_catalog: null,
    mamit_trnadb: null,
    cd: null,
    lncrnadb: null,
    enzyme_id: null,
    intermediate_filament_db: null,
    rna_central_ids: null,
    gtrnadb: null,
    lncipedia: null,
    agr: null,
    mane_select: null,
  },
  ncbiSummary: null,
  ncbiGeneRifs: [],
  smallVariant: {
    release: 'GRCh37',
    chromosome: '22',
    chromosome_no: 22,
    start: 32150850,
    end: 32150850,
    bin: 830,
    reference: 'A',
    alternative: 'G',
    var_type: 'snv',
    info: {},
    genotype: {
      'NA12878-N1-DNA1-WES1': { ad: 26, dp: 42, gq: 99, gt: '0/1' },
      'NA12891-N1-DNA1-WES1': { ad: 18, dp: 45, gq: 99, gt: '0/1' },
      'NA12892-N1-DNA1-WES1': { ad: 9, dp: 78, gq: 99, gt: '0/0' },
    },
    num_hom_alt: 0,
    num_hom_ref: 0,
    num_het: 0,
    num_hemi_alt: 0,
    num_hemi_ref: 0,
    in_clinvar: false,
    exac_frequency: 0,
    exac_homozygous: 0,
    exac_heterozygous: 0,
    exac_hemizygous: null,
    thousand_genomes_frequency: 0,
    thousand_genomes_homozygous: 0,
    thousand_genomes_heterozygous: 0,
    thousand_genomes_hemizygous: null,
    gnomad_exomes_frequency: 0,
    gnomad_exomes_homozygous: 0,
    gnomad_exomes_heterozygous: 0,
    gnomad_exomes_hemizygous: null,
    gnomad_genomes_frequency: 0,
    gnomad_genomes_homozygous: 0,
    gnomad_genomes_heterozygous: 0,
    gnomad_genomes_hemizygous: null,
    refseq_gene_id: null,
    refseq_transcript_id: 'NM_001007188.2',
    ensembl_gene_id: 'ENSG00000100150',
    ensembl_transcript_id: 'ENST00000266091.3',
    gene_id: '9681',
    transcript_id: 'NM_001007188.2',
    transcript_coding: true,
    hgvs_c: 'c.-58A>G',
    hgvs_p: 'p.=',
    effect: ['splice_region_variant', '5_prime_UTR_exon_variant'],
    effect_ambiguity: false,
    exon_dist: 0,
    case_uuid: '3b22fce8-9be8-4387-8e6e-3be73f4228fb',
    family_name: 'NA12878',
    mtdb_count: 0,
    mtdb_frequency: 0,
    mtdb_dloop: false,
    helixmtdb_het_count: 0,
    helixmtdb_hom_count: 0,
    helixmtdb_frequency: 0,
    helixmtdb_is_triallelic: false,
    mitomap_count: 0,
    mitomap_frequency: 0,
    rsid: null,
    symbol: 'DEPDC5',
    gene_name: 'DEP domain containing 5',
    gene_family: 'GATOR1 subcomplex',
    pubmed_id: '23542697|23542701',
    hgnc_id: 'HGNC:18423',
    uniprot_ids: 'O75140',
    gene_symbol: '',
    acmg_symbol: null,
    mgi_id: null,
    flag_count: null,
    flag_bookmarked: null,
    flag_candidate: null,
    flag_segregates: null,
    flag_doesnt_segregate: null,
    flag_final_causative: null,
    flag_for_validation: null,
    flag_no_disease_association: null,
    flag_molecular: null,
    flag_visual: null,
    flag_validation: null,
    flag_phenotype_match: null,
    flag_summary: null,
    comment_count: null,
    extra_annos: null,
    acmg_class_auto: null,
    acmg_class_override: null,
    modes_of_inheritance: ['AD'],
    disease_gene: 'True',
    gnomad_pLI: 0.1165,
    gnomad_mis_z: 2.6501,
    gnomad_syn_z: 0.83513,
    gnomad_oe_lof: 0.23539,
    gnomad_oe_lof_upper: 0.331,
    gnomad_oe_lof_lower: 0.169,
    gnomad_loeuf: 0.332,
    exac_pLI: null,
    exac_mis_z: null,
    exac_syn_z: null,
    inhouse_hom_ref: 0,
    inhouse_het: 0,
    inhouse_hom_alt: 0,
    inhouse_hemi_ref: 0,
    inhouse_hemi_alt: 0,
    inhouse_carriers: 0,
    variation_type: '',
    vcv: '',
    summary_review_status_label: '',
    summary_pathogenicity_label: '',
    summary_pathogenicity: [],
    summary_gold_stars: 0,
    details: [],
  },
}
