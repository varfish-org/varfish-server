import re

from django.forms import model_to_dict

from clinvar.models import ClinvarPathogenicGenes
from geneinfo.models import (
    RefseqToHgnc,
    EnsemblToRefseq,
    Hgnc,
    GnomadConstraints,
    ExacConstraints,
    Mim2geneMedgen,
    Hpo,
    HpoName,
    RefseqToEnsembl,
    RefseqToGeneSymbol,
    EnsemblToGeneSymbol,
)


RE_OMIM_PARSER = re.compile("^(?:#\d+ )?(.+)$")


# Modes of inheritance in HPO: https://hpo.jax.org/app/browse/term/HP:0000005
HPO_INHERITANCE_MAPPING = {
    "HP:0000006": "AD",
    "HP:0000007": "AR",
    "HP:0010985": "Gonosomal",
    "HP:0001417": "X-linked",
    "HP:0001419": "XR",
    "HP:0001423": "XD",
}


def get_gene_infos(database, gene_id, ensembl_transcript_id):
    if database == "refseq":
        # Get HGNC entry via intermediate table as HGNC is badly equipped with refseq IDs.
        hgnc = RefseqToHgnc.objects.filter(entrez_id=gene_id).first()
        gene = None
        gene_symbol = None
        if hgnc:
            gene = Hgnc.objects.filter(hgnc_id=hgnc.hgnc_id).first()
        gene_symbol_mapping = RefseqToGeneSymbol.objects.filter(entrez_id=gene_id).first()
        if gene_symbol_mapping:
            gene_symbol = gene_symbol_mapping.gene_symbol
    else:
        # We could also go via EnsemblToRefseq -> RefseqToHgnc -> Hgnc ???
        gene = Hgnc.objects.filter(ensembl_gene_id=gene_id).first()
        gene_symbol_mapping = EnsemblToGeneSymbol.objects.filter(ensembl_gene_id=gene_id).first()
        gene_symbol = None
        if gene_symbol_mapping:
            gene_symbol = gene_symbol_mapping.gene_symbol
    if not gene:
        return {
            "entrez_id" if database == "refseq" else "ensembl_gene_id": gene_id,
            "symbol": gene_symbol,
        }
    else:
        gene = model_to_dict(gene)
        if database == "refseq":
            refseq_to_ensembl = RefseqToEnsembl.objects.filter(entrez_id=gene_id).first()
            ensembl_gene_id = getattr(refseq_to_ensembl, "ensembl_gene_id", None)
            gene["entrez_id"] = gene_id
        else:
            ensembl_gene_id = gene_id
            hgnc = RefseqToHgnc.objects.filter(hgnc_id=gene["hgnc_id"]).first()
            gene["entrez_id"] = getattr(hgnc, "entrez_id", None)
        hpoterms, hpoinheritance, omim, omim_genes = _handle_hpo_omim(gene["entrez_id"])
        gene["omim"] = omim
        # Overwrite symbol from HGNC with the one derived directly from ncbi/ensembl.
        if not gene["symbol"]:
            gene["symbol"] = gene_symbol
        gene["omim_genes"] = omim_genes
        gene["hpo_inheritance"] = list(hpoinheritance)
        gene["hpo_terms"] = list(hpoterms)
        gene["clinvar_pathogenicity"] = ClinvarPathogenicGenes.objects.filter(
            entrez_id=gene["entrez_id"]
        ).first()
        if ensembl_gene_id:
            gene["gnomad_constraints"] = GnomadConstraints.objects.filter(
                ensembl_gene_id=ensembl_gene_id
            ).first()
        if ensembl_transcript_id:
            gene["exac_constraints"] = ExacConstraints.objects.filter(
                ensembl_transcript_id=ensembl_transcript_id.split(".")[0]
            ).first()
        return gene


def _handle_hpo_omim(entrez_id):
    if entrez_id is None:
        return [], [], {}, []
    # Obtain type (``phenotype`` or ``gene``) and omim ID via entrez ID.
    # Multiple entries for one entrez ID are possible (also mutiple genes for one entrez ID!).
    mim2gene = Mim2geneMedgen.objects.filter(entrez_id=entrez_id)
    omim = dict()
    hpoterms = set()
    hpoinheritance = set()
    omim_genes = set()
    for mim in mim2gene:
        # Collect omim genes
        if mim.omim_type == "gene":
            omim_genes.add(mim.omim_id)
        # Handle omim phenotypes
        else:
            # Get HPO info for the current omim ID
            for hpo_id, hpo_name, omim_name in _get_hpo_mapping(mim):
                if hpo_id in HPO_INHERITANCE_MAPPING:
                    hpoinheritance.add((hpo_id, HPO_INHERITANCE_MAPPING[hpo_id]))
                else:
                    hpoterms.add((hpo_id, hpo_name))
                # Replace omim name if we encountered a longer name for the same ID.
                # The longer name likely contains the shorter name.
                if mim.omim_id in omim:
                    if len(omim[mim.omim_id]) < len(omim_name):
                        omim[mim.omim_id] = omim_name
                else:
                    omim[mim.omim_id] = omim_name
    omim = {key: (value[0], value[1:]) for key, value in omim.items() if value}
    hpoterms = sorted(hpoterms, key=lambda tup: tup[1])
    return hpoterms, hpoinheritance, omim, omim_genes


def _get_hpo_mapping(mim):
    """Given one omim ID, obtain HPO entries with the associated HPO name and parsed OMIM name."""
    for h in Hpo.objects.filter(database_id="OMIM:{}".format(mim.omim_id)):
        hponame = HpoName.objects.filter(hpo_id=h.hpo_id).first()
        yield h.hpo_id, hponame.name if hponame else None, list(_parse_omim_name(h.name))


def _parse_omim_name(name):
    if name:
        for s in name.split(";;"):
            m = re.search(RE_OMIM_PARSER, s.split(";")[0])
            yield m.group(1)
