"""Code supporting scoring of variants by pathogenicity or phenotype."""

import json
import re
import time

import binning
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import model_to_dict
from django.utils.html import strip_tags
import pandas as pd
from projectroles.app_settings import AppSettingAPI
import requests
import wrapt

from ext_gestaltmatcher.models import SmallVariantQueryGestaltMatcherScores
from varfish.utils import JSONField

_app_settings = AppSettingAPI()


def load_molecular_impact(kwargs):
    """Load molecular impact from Jannovar REST API if configured."""
    if not settings.VARFISH_ENABLE_JANNOVAR:
        return []

    url_tpl = (
        "%(base_url)sannotate-var/%(database)s/%(genome)s/%(chromosome)s/%(position)s/%(reference)s/"
        "%(alternative)s"
    )
    genome = {"GRCh37": "hg19", "GRCh38": "hg38"}.get(kwargs["release"], "hg19")
    url = url_tpl % {
        "base_url": settings.VARFISH_JANNOVAR_REST_API_URL,
        "database": kwargs["database"],
        "genome": genome,
        "chromosome": kwargs["chromosome"],
        "position": kwargs["start"],
        "reference": kwargs["reference"],
        "alternative": kwargs["alternative"],
    }
    try:
        res = requests.request(method="get", url=url)
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )
        else:
            return res.json()
    except requests.ConnectionError as e:
        raise ConnectionError(
            "ERROR: Server at {} not responding.".format(settings.VARFISH_JANNOVAR_REST_API_URL)
        ) from e


class SmallVariantQueryGeneScores(models.Model):
    """Annotate ``SmallVariantQuery`` with gene scores (if configured to do so)."""

    #: The query to annotate.
    query = models.ForeignKey("SmallVariantQuery", on_delete=models.CASCADE)

    #: The Entrez gene ID.
    gene_id = models.CharField(max_length=64, null=False, blank=False, help_text="Entrez gene ID")

    #: The gene symbol.
    gene_symbol = models.CharField(
        max_length=128, null=False, blank=False, help_text="The gene symbol"
    )

    #: The priority type.
    priority_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The priority type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The gene score")


class SmallVariantQueryVariantScores(models.Model):
    """Annotate ``SmallVariantQuery`` with pathogenicity score."""

    #: The query to annotate.
    query = models.ForeignKey("SmallVariantQuery", on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - 1-based start position.
    start = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - end position.
    end = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - UCSC bin.
    bin = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - reference
    reference = models.CharField(max_length=512, null=False, blank=False)

    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512, null=False, blank=False)

    #: The score type.
    score_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The score type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The variant score")

    #: Further information.
    info = JSONField(default=dict)

    def variant_key(self):
        return "-".join(
            map(str, [self.release, self.chromosome, self.start, self.reference, self.alternative])
        )


class ProjectCasesSmallVariantQueryVariantScores(models.Model):
    """Annotate ``ProjectCasesSmallVariantQuery`` with pathogenicity score."""

    #: The query to annotate.
    query = models.ForeignKey("ProjectCasesSmallVariantQuery", on_delete=models.CASCADE)

    #: Genome build
    release = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32, null=False, blank=False)

    #: Variant coordinates - 1-based start position.
    start = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - end position.
    end = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - UCSC bin.
    bin = models.IntegerField(null=False, blank=False)

    #: Variant coordinates - reference
    reference = models.CharField(max_length=512, null=False, blank=False)

    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512, null=False, blank=False)

    #: The score type.
    score_type = models.CharField(
        max_length=64, null=False, blank=False, help_text="The score type"
    )

    #: The score.
    score = models.FloatField(null=False, blank=False, help_text="The variant score")

    #: Further information.
    info = JSONField(default=dict)

    def variant_key(self):
        return "-".join(
            map(str, [self.release, self.chromosome, self.start, self.reference, self.alternative])
        )


class PathogenicityScoreCacheBase(models.Model):
    """Base model class for the pathogenicity scoring caches to store the API results."""

    #: Date of last retrieval
    last_retrieved = models.DateTimeField(auto_now=True, help_text="DateTime of last modification")
    #: Genome build
    release = models.CharField(max_length=32)
    #: Variant coordinates - chromosome
    chromosome = models.CharField(max_length=32)
    #: Variant coordinates - 1-based start position
    start = models.IntegerField()
    #: Variant coordinates - end position
    end = models.IntegerField()
    #: Variant coordinates - UCSC bin
    bin = models.IntegerField()
    #: Variant coordinates - reference
    reference = models.CharField(max_length=512)
    #: Variant coordinates - alternative
    alternative = models.CharField(max_length=512)

    class Meta:
        abstract = True


class CaddPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the CADD pathogenicity API results."""

    #: Info dictionary
    info = JSONField()
    #: Tuple of returned scores
    scores = ArrayField(models.FloatField(), size=2)


class UmdPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the UMD predictor API results."""

    #: Amino acid wildtype
    aa_wildtype = models.CharField(max_length=512)
    #: Amino acid mutant
    aa_mutant = models.CharField(max_length=512)
    #: Gene symbol
    gene_name = models.CharField(max_length=512)
    #: Conclusion
    conclusion = models.CharField(max_length=512)
    #: EnsEMBL gene ID
    ensembl_gene_id = models.CharField(max_length=16)
    #: EnsEMBL transcript ID
    ensembl_transcript_id = models.CharField(max_length=32)
    #: Pathogenicity score
    pathogenicity_score = models.IntegerField()
    #: Transcript position
    transcript_position = models.IntegerField()


class MutationTasterPathogenicityScoreCache(PathogenicityScoreCacheBase):
    """Model to cache the MutationTaster API results."""

    #: Ensembl transcript id
    transcript_stable = models.CharField(max_length=32, null=True)
    #: Entrez ID
    ncbi_geneid = models.CharField(max_length=16, null=True)
    #: Pathogenicity prediction
    prediction = models.CharField(max_length=32, null=True)
    #: Model used for predicition
    model = models.CharField(max_length=32, null=True)
    #: Probability from bayes classifier
    bayes_prob_dc = models.IntegerField(null=True)
    #: Further information
    note = models.CharField(max_length=512, null=True)
    #: Splicesite
    splicesite = models.CharField(max_length=32, null=True)
    #: Distance from splicesite
    distance_from_splicesite = models.IntegerField(null=True)
    #: Disease database this mutation is registered in (e.g. ClinVar)
    disease_mutation = models.CharField(max_length=32, null=True)
    #: Polymorphism database this mutation is registered in (e.g. ExAC)
    polymorphism = models.CharField(max_length=32, null=True)


# TODO: Improve wrapper so we can assign obj.phenotype_rank and score
class RowWithPhenotypeScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for phenotype score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_phenotype_rank = None
        self._self_phenotype_score = -1

    @property
    def phenotype_rank(self):
        return self._self_phenotype_rank

    @property
    def phenotype_score(self):
        return self._self_phenotype_score

    def __getitem__(self, key):
        if key == "phenotype_rank":
            return self.phenotype_rank
        elif key == "phenotype_score":
            return self.phenotype_score
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithGestaltMatcherScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for Gestalt Matcher score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_gm_rank = None
        self._self_gm_score = -1

    @property
    def gm_rank(self):
        return self._self_gm_rank

    @property
    def gm_score(self):
        return self._self_gm_score

    def __getitem__(self, key):
        if key == "gm_rank":
            return self.gm_rank
        elif key == "gm_score":
            return self.gm_score
        elif key == "pedia_score":
            return
        elif key == "pedia_rank":
            return
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithPediaScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for PEDIA score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_pedia_rank = None
        self._self_pedia_score = -1

    @property
    def pedia_rank(self):
        return self._self_pedia_rank

    @property
    def pedia_score(self):
        return self._self_pedia_score

    def __getitem__(self, key):
        if key == "pedia_rank":
            return self.pedia_rank
        elif key == "pedia_score":
            return self.pedia_score
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithTranscripts(wrapt.ObjectProxy):
    """Wrap a result row and add members for phenotype score and rank."""

    def __init__(self, obj, database):
        super().__init__(obj)
        self._self_transcripts = None
        self._self_database = database

    @property
    def transcripts(self):
        return self._self_transcripts

    @property
    def database(self):
        return self._self_database

    @transcripts.setter
    def transcripts(self, value):
        self._self_transcripts = value

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, key):
        if key == "transcripts":
            return self.transcripts
        elif key == "database":
            return self.database
        else:
            return self.__wrapped__.__getitem__(key)


def annotate_with_phenotype_scores(rows, gene_scores):
    """Annotate the results in ``rows`` with phenotype scores stored in ``small_variant_query``.

    Variants are ranked by the gene scors, automatically ranking them by gene.
    """
    rows = [RowWithPhenotypeScore(row) for row in rows]
    for row in rows:
        row._self_phenotype_score = gene_scores.get(row.entrez_id, -1)
    rows.sort(key=lambda row: (row._self_phenotype_score, row.entrez_id or ""), reverse=True)
    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].phenotype_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.phenotype_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_gene_score = row.phenotype_score
            prev_gene = row.entrez_id
        row._self_phenotype_rank = rank
    return rows


def annotate_with_gm_scores(rows, gm_scores):
    """Annotate the results in ``rows`` with Gestalt Matcher scores stored in ``small_variant_query``.

    Variants are ranked by the Gestalt Matcher scores, automatically ranking them by gene.
    """
    rows = [RowWithGestaltMatcherScore(row) for row in rows]
    for row in rows:
        row._self_gm_score = gm_scores.get(row.entrez_id, 0)
    rows.sort(key=lambda row: (row._self_gm_score, row.entrez_id or ""), reverse=True)
    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gm_score = rows[0].gm_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gm_score == row.gm_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_gm_score = row.gm_score
            prev_gene = row.entrez_id
        row._self_gm_rank = rank
    return rows


def annotate_with_pedia_scores(rows, pedia_scores):
    """Annotate the results in ``rows`` with PEDIA scores stored in ``small_variant_query``.

    Variants are ranked by the PEDIA scores, automatically ranking them by gene.
    """
    rows = [RowWithPediaScore(row) for row in rows]
    for row in rows:
        row._self_pedia_score = pedia_scores.get(row.entrez_id, -1)
    rows.sort(key=lambda row: (row._self_pedia_score, row.entrez_id or ""), reverse=True)
    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_pedia_score = rows[0].pedia_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_pedia_score == row.pedia_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_pedia_score = row.pedia_score
            prev_gene = row.entrez_id
        row._self_pedia_rank = rank
    return rows


def annotate_with_transcripts(rows, database):
    """Annotate the results in ``rows`` with transcripts (RefSeq or Ensembl)"""
    rows = [RowWithTranscripts(row, database) for row in rows]
    for row in rows:
        transcripts = load_molecular_impact(row)
        row.transcripts = "\n".join(
            [
                t["transcriptId"]
                + ";"
                + ",".join(t["variantEffects"])
                + ";"
                + t["hgvsProtein"]
                + ";"
                + t["hgvsNucleotides"]
                for t in transcripts
            ]
        )

    return rows


# TODO: Improve wrapper so we can assign obj.pathogenicity_rank and score
class RowWithPathogenicityScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for pathogenicity score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_pathogenicity_rank = None
        self._self_pathogenicity_score = -1
        self._self_pathogenicity_score_info = {}

    @property
    def pathogenicity_rank(self):
        return self._self_pathogenicity_rank

    @property
    def pathogenicity_score(self):
        return self._self_pathogenicity_score

    @property
    def pathogenicity_score_info(self):
        return self._self_pathogenicity_score_info

    def __getitem__(self, key):
        if key == "pathogenicity_rank":
            return self.pathogenicity_rank
        elif key == "pathogenicity_score":
            return self.pathogenicity_score
        elif key == "pathogenicity_score_info":
            return self.pathogenicity_score_info
        else:
            return self.__wrapped__.__getitem__(key)

    def variant_key(self):
        return "-".join(
            map(str, (self.release, self.chromosome, self.start, self.reference, self.alternative))
        )


def annotate_with_pathogenicity_scores(rows, variant_scores):
    """Annotate the results in ``rows`` with pathogenicity scores stored in ``small_variant_query``.

    Variants are score independently but grouped by gene (the highest score of each variant in
    each gene is used for ranking).
    """
    # Get list of rows and assign pathogenicity scores.
    rows = [RowWithPathogenicityScore(row) for row in rows]
    if variant_scores:
        for row in rows:
            key = row.variant_key()
            score = variant_scores.get(key)
            if score:
                row._self_pathogenicity_score = score[0]
                row._self_pathogenicity_score_info = score[1]
    # Get highest score for each gene.
    gene_scores = {}
    for row in rows:
        gene_scores[row.entrez_id] = max(
            gene_scores.get(row.entrez_id, 0), row.pathogenicity_score or 0.0
        )

    # Sort variant by gene score now.
    def gene_score(row):
        if row.entrez_id:
            return (gene_scores[row.entrez_id], row.pathogenicity_score or 0.0)
        else:
            return (0.0, 0.0)  # no gene => lowest score

    rows.sort(key=gene_score, reverse=True)

    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].pathogenicity_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.pathogenicity_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            # We get the score of the first variant of a gene, they are ordered by score and thus the first variant is
            # the highest, representing the gene score.
            prev_gene_score = row.pathogenicity_score
            prev_gene = row.entrez_id
        row._self_pathogenicity_rank = rank
    return rows


# TODO: Improve wrapper so we can assign obj.pathogenicity_rank and score
class RowWithJointScore(wrapt.ObjectProxy):
    """Wrap a result row and add members for joint score and rank."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_joint_rank = None
        self._self_joint_score = -1

    @property
    def joint_rank(self):
        return self._self_joint_rank

    @property
    def joint_score(self):
        return self._self_joint_score

    def __getitem__(self, key):
        if key == "joint_rank":
            return self.joint_rank
        elif key == "joint_score":
            return self.joint_score
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithExtraAnno(wrapt.ObjectProxy):
    """Wrap a result row with extra annotations"""

    def __init__(self, obj, fields, datas):
        super().__init__(obj)
        self._self_anno_fields = fields
        if datas is not None:
            self._self_anno_data = datas[0]
        else:
            self._self_anno_data = None

    def find_id(self, key):
        return self._self_anno_fields.get(key, -1)

    def __getattr__(self, item):
        return self.__getitem__(item)

    def __getitem__(self, key):
        id = self.find_id(key)
        if id != -1:
            if self._self_anno_data is None:
                return None
            return self._self_anno_data[id]
        else:
            return self.__wrapped__.__getitem__(key)


def annotate_with_joint_scores(rows):
    """Annotate the results in ``rows`` with joint scores stored in ``small_variant_query``.

    Variants are score independently but grouped by gene (the highest score of each variant in
    each gene is used for ranking).
    """
    # Get list of rows and assign joint scores.
    rows = [RowWithJointScore(row) for row in rows]
    for row in rows:
        # TODO: cleanup
        # key = "-".join(
        #     map(str, [row["chromosome"], row["start"], row["reference"], row["alternative"]])
        # )
        row._self_joint_score = (row.phenotype_score or 0) * (row.pathogenicity_score or 0)
    # Get highest score for each gene.
    gene_scores = {}
    for row in rows:
        gene_scores[row.entrez_id] = max(gene_scores.get(row.entrez_id, 0), row.joint_score or 0)

    # Sort variant by gene score now.
    def gene_score(row):
        if row.entrez_id:
            return gene_scores[row.entrez_id]
        else:
            return 0.0  # no gene => lowest score

    rows.sort(key=gene_score, reverse=True)

    # Re-compute ranks
    prev_gene = rows[0].entrez_id if rows else None
    prev_gene_score = rows[0].joint_score if rows else None
    rank = 1
    same_score_count = 1
    for row in rows:
        if row.entrez_id != prev_gene:
            if prev_gene_score == row.joint_score:
                same_score_count += 1
            else:
                rank += same_score_count
                same_score_count = 1
            prev_gene_score = row.joint_score
            prev_gene = row.entrez_id
        row._self_joint_rank = rank
    return rows


def unroll_extra_annos_result(rows, fields):
    """unroll the extra annotation results in columns in such a way that all writer can operate on extra annotations."""
    # Get list of rows with extra annotations
    rows_ = [RowWithExtraAnno(row, fields, getattr(row, "extra_annos")) for row in rows]

    return rows_


def generate_pedia_input(self, pathoEnabled, prioEnabled, gmEnabled, queryId, case_name, results):
    pathogenicity_scores = None
    if pathoEnabled:
        pathogenicity_scores = {
            (row.chromosome, row.start, row.reference, row.alternative): row.score
            for row in SmallVariantQueryVariantScores.objects.filter(query__sodar_uuid=queryId)
        }
    phenotype_scores = None
    if prioEnabled:
        phenotype_scores = {
            row.gene_id: row.score
            for row in SmallVariantQueryGeneScores.objects.filter(query__sodar_uuid=queryId)
            if row.gene_id
        }
    gm_scores = None
    if gmEnabled:
        gm_scores = {
            row.gene_id: 0 if row.score == 0 else row.score
            for row in SmallVariantQueryGestaltMatcherScores.objects.filter(
                query__sodar_uuid=queryId
            )
            if row.gene_id
        }

    payloadList = []
    """Read and json object by reading ``results`` ."""
    for line in results:
        payload = dict()

        if line["entrez_id"]:
            if line["symbol"]:
                payload["gene_name"] = line["symbol"]
            else:
                payload["gene_name"] = " "
            payload["gene_id"] = line["entrez_id"]

        if phenotype_scores and line.entrez_id:
            payload["cada_score"] = phenotype_scores.get(line.entrez_id, -1)

        if pathogenicity_scores:
            payload["cadd_score"] = pathogenicity_scores.get(
                (line.chromosome, line.start, line.reference, line.alternative), 0.0
            )

        if gm_scores and line.entrez_id:
            payload["gestalt_score"] = (
                0
                if gm_scores.get(line.entrez_id, 0) == float("nan")
                else gm_scores.get(line.entrez_id, 0)
            )

        payload["label"] = False

        payloadList.append(payload)

    df = pd.DataFrame(payloadList)

    if "cadd_score" in df:
        # Sort the DataFrame based on the 'cadd_score' column in descending order
        df_sorted = df.sort_values(by="cadd_score", ascending=False)

        # Drop duplicates in the 'gene_name' column, keeping the first occurrence (highest CADD score)
        df_no_duplicates = df_sorted.drop_duplicates(subset="gene_name", keep="first")

        if case_name.startswith("F_"):
            name = case_name[2:]  # Remove the first two characters ("F_")
        else:
            name = case_name

        scores = {"case_name": name, "genes": df_no_duplicates.to_dict(orient="records")}
        return scores

    return {"case_name": "case", "genes": df.to_dict(orient="records")}


def prioritize_genes(entrez_ids, hpo_terms, prio_algorithm, logging=lambda text: True):
    """Perform gene prioritization query.

    Yield quadruples (gene id, gene symbol, score, priority type) for the given gene list and query settings.
    """
    # TODO: properly test

    if prio_algorithm == "CADA":
        logging("Prioritize genes with CADA ...")
        yield from prio_cada(hpo_terms)

    else:
        logging("Prioritize genes with Exomiser ...")
        yield from prio_exomiser(entrez_ids, hpo_terms, prio_algorithm)


def prioritize_genes_gm(gm_response, logging=lambda text: True):
    """Perform gene prioritization query.

    Yield quadruples (gene id, gene symbol, score, priority type) for the given gene list and query settings.
    """
    try:
        res = json.loads(gm_response)
    except requests.ConnectionError:
        raise ConnectionError("ERROR: GestaltMatcher Server not responding.")
    for entry in res:
        yield entry["gene_entrez_id"], entry["gene_name"], (
            1.3 - entry["distance"]
        ), "GestaltMatcher"


def prio_exomiser(entrez_ids, hpo_terms, prio_algorithm):
    if not settings.VARFISH_ENABLE_EXOMISER_PRIORITISER or not entrez_ids or not hpo_terms:
        return

    try:
        algo_params = {
            "hiphive": ("hiphive", ["human", "mouse", "fish", "ppi"]),
            "hiphive-human": ("hiphive", ["human"]),
            "hiphive-mouse": ("hiphive", ["human", "mouse"]),
        }
        prio_algorithm, prio_params = algo_params.get(prio_algorithm, (prio_algorithm, []))
        res = requests.post(
            settings.VARFISH_EXOMISER_PRIORITISER_API_URL,
            json={
                "phenotypes": sorted(set(hpo_terms)),
                "genes": sorted(set(entrez_ids)),
                "prioritiser": prio_algorithm,
                "prioritiserParams": ",".join(prio_params),
            },
        )
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, strip_tags(re.sub("<head>.*</head>", "", res.text))
                )
            )
    except requests.ConnectionError:
        raise ConnectionError(
            "ERROR: Server {} not responding.".format(settings.VARFISH_EXOMISER_PRIORITISER_API_URL)
        )

    for entry in res.json().get("results", ()):
        yield entry["geneId"], entry["geneSymbol"], entry["score"], entry["priorityType"]


def prio_cada(hpo_terms):
    if not settings.VARFISH_ENABLE_CADA or not hpo_terms:
        return
    try:
        res = requests.post(
            settings.VARFISH_CADA_REST_API_URL,
            json=sorted(set(hpo_terms)),
        )

        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, strip_tags(re.sub("<head>.*</head>", "", res.text))
                )
            )
    except requests.ConnectionError:
        raise ConnectionError(
            "ERROR: Server {} not responding.".format(settings.VARFISH_CADA_REST_API_URL)
        )
    for entry in res.json():
        yield entry["geneId"].split(":")[1], entry["geneSymbol"], entry["score"], "CADA"


def prioritize_genes_pedia(
    self, pathoEnabled, prioEnabled, gmEnabled, caseId, case_name, result, logging
):
    inputJson = generate_pedia_input(
        self, pathoEnabled, prioEnabled, gmEnabled, caseId, case_name, result
    )
    yield from get_pedia_scores(inputJson)


def get_pedia_scores(inputJson):
    try:
        res = requests.post(
            settings.VARFISH_PEDIA_REST_API_URL,
            json=inputJson,
        )

        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}. ".format(
                    res.status_code,
                    strip_tags(
                        re.sub("<head>.*</head>", "", res.text),
                    ),
                )
            )
    except requests.ConnectionError:
        raise ConnectionError(
            "ERROR: Server {} not responding.".format(settings.VARFISH_PEDIA_REST_API_URL)
        )

    for entry in res.json():
        gene_name = entry["gene_name"] if entry["gene_name"] else ""
        yield entry["gene_id"], gene_name, entry["pedia_score"]


class VariantScoresFactory:
    """Factory class for variant scorers."""

    def get_scorer(self, genomebuild, score_type, variants, user=None):
        if score_type == "umd":
            return VariantScoresUmd(genomebuild, variants, score_type, user)
        elif score_type == "cadd":
            return VariantScoresCadd(genomebuild, variants, score_type)
        elif score_type == "mutationtaster":
            return VariantScoresMutationTaster(genomebuild, variants, score_type)


class VariantScoresBase:
    """Variant scoring base class."""

    #: Set PathogenicityCache model (required in child classes)
    cache_model = None

    def __init__(self, genomebuild, variants, score_type, user=None):
        self.genomebuild = genomebuild
        self.variants = list(set(variants))
        self.superuser = user
        self.score_type = score_type

    def score(self):
        raise NotImplementedError("Implement me!")

    def get_cache_model(self):
        if not self.cache_model:
            raise NotImplementedError("Please set ``cache_model``")
        return self.cache_model

    def _get_cached_and_uncached_variants(self):
        cached = []
        uncached = []
        for variant in self.variants:
            res = self.get_cache_model().objects.filter(
                chromosome=variant[0],
                start=variant[1],
                reference=variant[2],
                alternative=variant[3],
            )
            if res:
                cached.append(res.first())
            else:
                uncached.append(variant)
        return cached, uncached

    def _cache_results(self, results):
        self.get_cache_model().objects.bulk_create(results)

    def _build_yield_dict(self, record, score, info):
        yield_dict = {
            k: record[k]
            for k in ("release", "chromosome", "start", "end", "bin", "reference", "alternative")
        }
        yield_dict["score"] = score
        yield_dict["info"] = info
        yield_dict["score_type"] = self.score_type
        return yield_dict


class VariantScoresUmd(VariantScoresBase):
    """Variant scoring class for UMD Predictor."""

    #: Set PathogenicityCache model (required)
    cache_model = UmdPathogenicityScoreCache

    def score(self):
        if not self.variants or not self.superuser:
            return

        token = _app_settings.get("variants", "umd_predictor_api_token", user=self.superuser)

        if not token:
            return

        cached, uncached = self._get_cached_and_uncached_variants()

        try:
            res = requests.get(
                settings.VARFISH_UMD_REST_API_URL,
                params=dict(
                    batch=",".join(["_".join(map(str, var)) for var in uncached]), token=token
                ),
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(settings.VARFISH_UMD_REST_API_URL)
            )

        # Exit if error is reported
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )

        # UMD API results do not contain header, so manually assign header information from their web page legend.
        header = [
            "chromosome",
            "position",
            "gene_name",
            "ensembl_gene_id",
            "ensembl_transcript_id",
            "transcript_position",
            "reference",
            "alternative",
            "aa_wildtype",
            "aa_mutant",
            "pathogenicity_score",
            "conclusion",
        ]
        # Yield cached results
        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(item, item["pathogenicity_score"], {})
        # Yield API results
        result = []
        for line in res.text.split("\n"):
            if not line:
                continue
            if not line.startswith("chr"):
                continue
            record = dict(zip(header, line.split("\t")))
            record["release"] = "GRCh37"
            record["chromosome"] = record["chromosome"][3:]
            record["start"] = int(record.pop("position"))
            record["end"] = record["start"] + len(record["reference"]) - 1
            record["bin"] = binning.assign_bin(record["start"] - 1, record["end"])
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(record, record["pathogenicity_score"], {})
        # Store API results in cache
        self._cache_results(result)


class VariantScoresMutationTaster(VariantScoresBase):
    """Variant scoring class for Mutation Taster."""

    #: Set PathogenicityCache model (required)
    cache_model = MutationTasterPathogenicityScoreCache

    def score(self):
        if not self.variants:
            return

        cached, uncached = self._get_cached_and_uncached_variants()

        if len(uncached) > settings.VARFISH_MUTATIONTASTER_MAX_VARS:
            raise ConnectionError(
                "ERROR: Too many variants to score. Got {}, limit is {}.".format(
                    len(uncached), settings.VARFISH_MUTATIONTASTER_MAX_VARS
                )
            )

        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(
                item,
                _variant_scores_mutationtaster_score(item),
                _variant_scores_mutationtaster_info(item),
            )

        for i in range(len(uncached)):
            if i % settings.VARFISH_MUTATIONTASTER_BATCH_VARS == 0:
                yield from self._variant_scores_mutationtaster_loop(
                    uncached[i : i + settings.VARFISH_MUTATIONTASTER_BATCH_VARS]
                )

    def _variant_scores_mutationtaster_loop(self, batch):
        batch_str = ",".join("{}:{}{}>{}".format(*var) for var in batch)
        try:
            res = requests.post(
                settings.VARFISH_MUTATIONTASTER_REST_API_URL,
                dict(format="tsv", debug="0", variants=batch_str),
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(
                    settings.VARFISH_MUTATIONTASTER_REST_API_URL
                )
            )

        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )

        error_response = "Content-Type: text/plain\n\nERROR: "
        if res.text.startswith(error_response):
            raise ConnectionError(
                "ERROR: Server responded with: {}".format(res.text[len(error_response) :])
            )

        result = []
        lines = res.text.split("\n")
        if not lines or len(lines) < 2:
            return
        head = lines.pop(0).lower().split("\t")
        for line in lines:
            if not line:
                continue
            line = line.split("\t")
            record = dict(zip(head, line))
            # Remove id column as it would collide with the postgres id column. It's not required anyway.
            if "id" in record:
                record.pop("id")
            # Convert chromosome identifiers
            record["chromosome"] = record.pop("chr")
            if record["chromosome"] == "23":
                record["chromosome"] = "X"
            elif record["chromosome"] == "24":
                record["chromosome"] = "Y"
            elif record["chromosome"] == "0":
                record["chromosome"] = "MT"
            # Re-label columns and convert data types to match postgres columns.
            record["release"] = "GRCh37"
            record["start"] = int(record.pop("pos"))
            record["end"] = record["start"] + len(record["ref"]) - 1
            record["bin"] = binning.assign_bin(record["start"] - 1, record["end"])
            record["reference"] = record.pop("ref")
            record["alternative"] = record.pop("alt")
            # This looks a bit complicated but is required as int() can't be casted on an empty string.
            record["bayes_prob_dc"] = (
                int(record["bayes_prob_dc"]) if record["bayes_prob_dc"] else None
            )
            record["distance_from_splicesite"] = (
                int(record["distance_from_splicesite"])
                if record["distance_from_splicesite"]
                else None
            )
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(
                record,
                _variant_scores_mutationtaster_score(record),
                _variant_scores_mutationtaster_info(record),
            )
        result_ = [(r.chromosome, r.start, r.reference, r.alternative) for r in result]
        # Create empty record for variants that weren't scored by mutationtaster
        # (and thus do not show up in the results and would be queried all over again)
        for variant in batch:
            if variant not in result_:
                chromosome, start, reference, alternative = variant
                record = {
                    "release": "GRCh37",
                    "chromosome": chromosome,
                    "start": start,
                    "end": start + len(reference) - 1,
                    "bin": binning.assign_bin(start - 1, start + len(reference) - 1),
                    "reference": reference,
                    "alternative": alternative,
                    "transcript_stable": None,
                    "ncbi_geneid": None,
                    "prediction": None,
                    "model": None,
                    "bayes_prob_dc": None,
                    "note": "error",
                    "splicesite": None,
                    "distance_from_splicesite": None,
                    "disease_mutation": None,
                    "polymorphism": None,
                }
                result.append(self.get_cache_model()(**record))
                yield self._build_yield_dict(
                    record,
                    _variant_scores_mutationtaster_score(record),
                    _variant_scores_mutationtaster_info(record),
                )

        # Store API results in cache
        self._cache_results(result)


def _variant_scores_mutationtaster_score(record):
    if record.get("note") == "error":
        return -1
    model_rank = variant_scores_mutationtaster_rank_model(record)
    return model_rank + int(record.get("bayes_prob_dc")) / 10000


def _variant_scores_mutationtaster_info(record):
    return {
        "model": record["model"],
        "prediction": record["prediction"],
        "splicesite": record["splicesite"],
        "bayes_prob_dc": record["bayes_prob_dc"],
        "note": record["note"],
    }


def variant_scores_mutationtaster_rank_model(record):
    model_rank = 0
    if record.get("prediction") == "disease causing (automatic)":
        model_rank = 4
    elif record.get("prediction") in ("disease causing", "disease causing - long InDel"):
        if record.get("model") in ("simple_aae", "complex_aae"):
            model_rank = 3
        elif record.get("model") == "without_aae":
            if record.get("splicesite") in ("splice site", "splicing impaired"):
                model_rank = 2
            else:
                model_rank = 1
    return model_rank


class VariantScoresCadd(VariantScoresBase):
    """Variant scoring class for CADD."""

    #: Set PathogenicityCache model (required)
    cache_model = CaddPathogenicityScoreCache

    def score(self):
        if not settings.VARFISH_ENABLE_CADD or not self.variants:
            return

        cached, uncached = self._get_cached_and_uncached_variants()
        uncached = uncached[: settings.VARFISH_CADD_MAX_VARS]

        # TODO: properly test
        try:
            res = requests.post(
                settings.VARFISH_CADD_REST_API_URL + "/annotate/",
                json={
                    "genome_build": self.genomebuild,
                    "cadd_release": settings.VARFISH_CADD_REST_API_CADD_VERSION,
                    "variant": ["-".join(map(str, var)) for var in uncached],
                },
            )
        except requests.ConnectionError:
            raise ConnectionError(
                "ERROR: Server {} not responding.".format(settings.VARFISH_CADD_REST_API_URL)
            )

        # Exit if error is reported
        if not res.status_code == 200:
            raise ConnectionError(
                "ERROR: Server responded with status {} and message {}".format(
                    res.status_code, res.text
                )
            )
        bgjob_uuid = res.json().get("uuid")
        while True:
            try:
                res = requests.post(
                    settings.VARFISH_CADD_REST_API_URL + "/result/", json={"bgjob_uuid": bgjob_uuid}
                )
            except requests.ConnectionError:
                raise ConnectionError(
                    "ERROR: Server {} not responding.".format(settings.VARFISH_CADD_REST_API_URL)
                )

            if not res.status_code == 200:
                raise ConnectionError(
                    "ERROR: Server responded with status {} and message {}".format(
                        res.status_code, res.text
                    )
                )
            if res.json().get("status") == "active":
                time.sleep(2)
            elif res.json().get("status") == "failed":
                raise ConnectionError(
                    "Job failed, leaving the following message: {}".format(res.json().get("result"))
                )
            else:  # status == finished
                break

        # Yield cached results
        for item in cached:
            item = model_to_dict(item)
            yield self._build_yield_dict(item, item["scores"][1], {})

        result = []
        for var, scores in res.json().get("scores", {}).items():
            chrom, pos, ref, alt = var.split("-")
            start = int(pos)
            end = start + len(ref) - 1
            record = {
                "release": "GRCh37",
                "chromosome": chrom,
                "start": start,
                "end": end,
                "bin": binning.assign_bin(start - 1, end),
                "reference": ref,
                "alternative": alt,
                "info": res.json().get("info"),
                "scores": scores,
            }
            result.append(self.get_cache_model()(**record))
            yield self._build_yield_dict(record, record["scores"][1], {})
        self._cache_results(result)


# TODO: Improve wrapper
class RowWithClinvarMax(wrapt.ObjectProxy):
    """Wrap a result row and add members for clinvar max status and max significance."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_max_clinvar_status = None
        self._self_max_significance = None
        self._self_max_all_traits = None

    @property
    def max_clinvar_status(self):
        return self._self_max_clinvar_status

    @property
    def max_significance(self):
        return self._self_max_significance

    @property
    def max_all_traits(self):
        return self._self_max_all_traits

    def __getitem__(self, key):
        if key == "max_clinvar_status":
            return self.max_clinvar_status
        elif key == "max_significance":
            return self.max_significance
        elif key == "max_all_traits":
            return self.max_all_traits
        else:
            return self.__wrapped__.__getitem__(key)


class RowWithAffectedCasesPerGene(wrapt.ObjectProxy):
    """Wrap a result row and add number of families per gene."""

    def __init__(self, obj):
        super().__init__(obj)
        self._self_affected_cases_per_gene = None

    @property
    def affected_cases_per_gene(self):
        return self._self_affected_cases_per_gene

    def __getitem__(self, key):
        if key == "affected_cases_per_gene":
            return self.affected_cases_per_gene
        else:
            return self.__wrapped__.__getitem__(key)
