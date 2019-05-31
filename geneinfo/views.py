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


def get_gene_infos(database, gene_id):
    if database == "refseq":
        # Get HGNC entry via intermediate table as HGNC is badly equipped with refseq IDs.
        hgnc = RefseqToHgnc.objects.filter(entrez_id=gene_id).first()
        gene = None
        if hgnc:
            gene = Hgnc.objects.filter(hgnc_id=hgnc.hgnc_id).first()
    else:
        # We could also go via EnsemblToRefseq -> RefseqToHgnc -> Hgnc ???
        gene = Hgnc.objects.filter(ensembl_gene_id=gene_id).first()
    if not gene:
        return {"entrez_id" if database == "refseq" else "ensembl_gene_id": gene_id}
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
        hpoterms, hpoinheritance, omim = _handle_hpo_omim(gene["entrez_id"])
        gene["omim"] = omim
        gene["hpo_inheritance"] = list(hpoinheritance)
        gene["hpo_terms"] = list(hpoterms)
        gene["clinvar_pathogenicity"] = ClinvarPathogenicGenes.objects.filter(
            entrez_id=gene["entrez_id"]
        ).first()
        if ensembl_gene_id:
            gene["exac_constraints"] = _get_exac_constraints(ensembl_gene_id)
            gene["gnomad_constraints"] = GnomadConstraints.objects.filter(
                ensembl_gene_id=ensembl_gene_id
            ).first()
        return gene


def _get_exac_constraints(ensembl_gene_id):
    results = EnsemblToRefseq.objects.filter(ensembl_gene_id=ensembl_gene_id)
    ensembl_transcripts = [record.ensembl_transcript_id for record in results]
    return ExacConstraints.objects.filter(ensembl_transcript_id__in=ensembl_transcripts).first()


def _handle_hpo_omim(entrez_id):
    if entrez_id is None:
        return [], [], None
    mim2gene = Mim2geneMedgen.objects.filter(entrez_id=entrez_id)
    omim = dict()
    hpoterms = set()
    hpointeritance = set()
    for mim in mim2gene:
        mapping = _get_hpo_mapping(mim)
        for record in mapping:
            if record is not None:
                if record[0] in HPO_INHERITANCE_MAPPING:
                    hpointeritance.add((record[0], HPO_INHERITANCE_MAPPING[record[0]]))
                else:
                    hpoterms.add(record)
            omim_type, omim_id, omim_name = next(mapping)
            if omim_type == "phenotype":
                if omim_id in omim:
                    if len(omim[omim_id]) < len(omim_name):
                        omim[omim_id] = omim_name
                else:
                    omim[omim_id] = omim_name
    omim = {key: (value[0], value[1:]) for key, value in omim.items() if value}
    return hpoterms, hpointeritance, omim


def _get_hpo_mapping(mim):
    for h in Hpo.objects.filter(database_id="OMIM:{}".format(mim.omim_id)):
        hponame = HpoName.objects.filter(hpo_id=h.hpo_id).first()
        yield h.hpo_id, hponame.name if hponame else None
        yield mim.omim_type, mim.omim_id, list(_parse_omim_name(h.name))


def _parse_omim_name(name):
    if name:
        for s in name.split(";;"):
            m = re.search(RE_OMIM_PARSER, s.split(";")[0])
            yield m.group(1)
