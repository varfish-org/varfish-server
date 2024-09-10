#!/usr/bin/env python

import gzip
import os
import re
import sys
import typing

import binning
from clinvar_data.pbs import clinvar_public
from clinvar_data.pbs.extracted_vars import ExtractedVcvRecord
from google.protobuf.json_format import Parse
import pydantic
import requests

FULL_SET_PATH = "/tmp/varfish-hgnc_complete_set.txt"
FULL_SET_URL = (
    "https://g-a8b222.dd271.03c0.data.globus.org/pub/"
    "databases/genenames/hgnc/tsv/hgnc_complete_set.txt"
)


class Clinvar(pydantic.BaseModel):
    release: str
    chromosome: str
    start: int
    end: int
    bin: int
    reference: str
    alternative: str
    clinvar_version: str
    set_type: str
    variation_type: str
    symbols: typing.List[str]
    hgnc_ids: typing.List[str]
    vcv: str
    summary_clinvar_review_status_label: str
    summary_clinvar_pathogenicity_label: str
    summary_clinvar_pathogenicity: typing.List[str]
    summary_clinvar_gold_stars: int
    summary_paranoid_review_status_label: str
    summary_paranoid_pathogenicity_label: str
    summary_paranoid_pathogenicity: typing.List[str]
    summary_paranoid_gold_stars: int
    details: typing.Dict[str, typing.Any]

    def print_for_postgres(self, file: typing.TextIO = sys.stdout):
        result = [
            self.release,
            self.chromosome,
            str(self.start),
            str(self.end),
            str(self.bin),
            self.reference,
            self.alternative,
            self.clinvar_version,
            self.set_type,
            self.variation_type,
            "{%s}" % ",".join(self.symbols),
            "{%s}" % ",".join(self.hgnc_ids),
            self.vcv,
            self.summary_clinvar_review_status_label,
            self.summary_clinvar_pathogenicity_label,
            "{%s}"
            % ",".join(
                [
                    '"%s"' % label if " " in label else label
                    for label in self.summary_clinvar_pathogenicity
                ]
            ),
            str(self.summary_clinvar_gold_stars),
            self.summary_paranoid_review_status_label,
            self.summary_paranoid_pathogenicity_label,
            "{%s}"
            % ",".join(
                [
                    '"%s"' % label if " " in label else label
                    for label in self.summary_paranoid_pathogenicity
                ]
            ),
            str(self.summary_paranoid_gold_stars),
            "{}",
        ]
        print("\t".join(result), file=file)


PATHOGENICITIES: dict[str, 1] = {
    "likely pathogenic": 1,
    "pathogenic": 2,
    "uncertain significance": 0,
    "likely benign": -1,
    "benign": -2,
}
PATHOGENICITIES_INV = {v: k for k, v in PATHOGENICITIES.items()}
REVIEW_STATUS_LABELS: dict[clinvar_public.AggregateGermlineReviewStatus.ValueType, str] = {
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_CONFLICTING_CLASSIFICATIONS: "criteria provided, conflicting classifications	",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS: "criteria provided, multiple submitters, no conflicts",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_SINGLE_SUBMITTER: "criteria provided, single submitter",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED: "no assertion criteria provided",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATION_PROVIDED: "no classifications provided",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATIONS_FROM_UNFLAGGED_RECORDS: "no classifications from unflagged records",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_PRACTICE_GUIDELINE: "practice guideline",
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_REVIEWED_BY_EXPERT_PANEL: "reviewed by expert panel",
}
REVIEW_STATUS_STARS: dict[clinvar_public.AggregateGermlineReviewStatus.ValueType, int] = {
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_CONFLICTING_CLASSIFICATIONS: 1,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_MULTIPLE_SUBMITTERS_NO_CONFLICTS: 2,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_CRITERIA_PROVIDED_SINGLE_SUBMITTER: 1,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED: 0,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATION_PROVIDED: 0,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATIONS_FROM_UNFLAGGED_RECORDS: 0,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_PRACTICE_GUIDELINE: 4,
    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_REVIEWED_BY_EXPERT_PANEL: 3,
}


def extracted_var_to_clinvar_record(
    hgnc_map: typing.Dict[str, str],
    clinvar_version: str,
    release: typing.Literal["GRCh37", "GRCh38"],
    record: ExtractedVcvRecord,
) -> typing.Optional[Clinvar]:
    if not record.sequence_location.position_vcf:
        return None
    if not record.classifications.HasField("germline_classification"):
        return None
    germline_classification = record.classifications.germline_classification

    chromosome = clinvar_public.Chromosome.Name(record.sequence_location.chr)[len("CHROMOSOME_") :]
    end = (
        record.sequence_location.position_vcf
        + len(record.sequence_location.reference_allele_vcf)
        - 1
    )
    if (
        len(record.sequence_location.reference_allele_vcf) == 1
        and len(record.sequence_location.alternate_allele_vcf) == 1
    ):
        variation_type = "snv"
    else:
        variation_type = "indel"
    symbols = list(filter(lambda x: bool(x), map(hgnc_map.get, record.hgnc_ids)))

    if "conflicting" in germline_classification.description.lower():
        summary_clinvar_pathogenicity = ["uncertain significance"]
        summary_clinvar_pathogenicity_label = "conflicting interpretations of pathogenicity"
        summary_clinvar_review_status_label = "criteria provided, conflicting classifications"
        summary_clinvar_gold_stars = 0
    else:
        description_tokens = (
            token.strip().lower()
            for token in re.split(r"[/,;]", germline_classification.description)
        )
        summary_clinvar_pathogenicity = []
        summary_clinvar_pathogenicity_label = "uncertain significance"
        for token in description_tokens:
            for key in PATHOGENICITIES.keys():
                if key == token:
                    summary_clinvar_pathogenicity.append(key)
        if summary_clinvar_pathogenicity:
            summary_clinvar_pathogenicity_label = "/".join(summary_clinvar_pathogenicity)
        else:
            summary_clinvar_pathogenicity = ["uncertain significance"]
            summary_clinvar_pathogenicity_label = "uncertain significance"
        summary_clinvar_review_status_label = REVIEW_STATUS_LABELS[
            germline_classification.review_status
        ]
        summary_clinvar_gold_stars = REVIEW_STATUS_STARS[germline_classification.review_status]

    summary_paranoid_review_status_label = summary_clinvar_review_status_label
    summary_paranoid_pathogenicity_label = summary_clinvar_pathogenicity_label
    summary_paranoid_pathogenicity = summary_clinvar_pathogenicity
    summary_paranoid_gold_stars = summary_clinvar_gold_stars
    if "conflicting" in summary_clinvar_pathogenicity_label:
        # look through the SCVs
        worst = None
        for clinical_assertion in record.clinical_assertions:
            if clinical_assertion.HasField(
                "classifications"
            ) and clinical_assertion.classifications.HasField("germline_classification"):
                if clinical_assertion.classifications.review_status not in (
                    clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_CLASSIFICATION_PROVIDED,
                    # clinvar_public.AggregateGermlineReviewStatus.AGGREGATE_GERMLINE_REVIEW_STATUS_NO_ASSERTION_CRITERIA_PROVIDED,
                ):
                    description_tokens = [
                        token.strip().lower()
                        for token in re.split(
                            r"[/,;]", clinical_assertion.classifications.germline_classification
                        )
                    ]
                    for token in description_tokens:
                        for key in PATHOGENICITIES.keys():
                            if PATHOGENICITIES[key] is not None and (
                                worst is None or PATHOGENICITIES[key] > worst
                            ):
                                worst = PATHOGENICITIES[key]
        if worst is not None and PATHOGENICITIES.get(summary_clinvar_pathogenicity[0], 0) < worst:
            # override paranoid
            summary_paranoid_pathogenicity_label = PATHOGENICITIES_INV[worst]
            summary_paranoid_pathogenicity = [PATHOGENICITIES_INV[worst]]
            summary_paranoid_gold_stars = 0

    return Clinvar(
        release=release,
        chromosome=chromosome,
        start=record.sequence_location.position_vcf,
        end=end,
        bin=binning.assign_bin(record.sequence_location.position_vcf - 1, end),
        reference=record.sequence_location.reference_allele_vcf,
        alternative=record.sequence_location.alternate_allele_vcf,
        clinvar_version=clinvar_version,
        set_type="variant",
        variation_type=variation_type,
        symbols=symbols,
        hgnc_ids=list(record.hgnc_ids),
        vcv=f"{record.accession.accession}.{record.accession.version}",
        summary_clinvar_review_status_label=summary_clinvar_review_status_label,
        summary_clinvar_pathogenicity_label=summary_clinvar_pathogenicity_label,
        summary_clinvar_pathogenicity=summary_clinvar_pathogenicity,
        summary_clinvar_gold_stars=summary_clinvar_gold_stars,
        summary_paranoid_review_status_label=summary_paranoid_review_status_label,
        summary_paranoid_pathogenicity_label=summary_paranoid_pathogenicity_label,
        summary_paranoid_pathogenicity=summary_paranoid_pathogenicity,
        summary_paranoid_gold_stars=summary_paranoid_gold_stars,
        details={},
    )


HEADER = [
    "release",
    "chromosome",
    "start",
    "end",
    "bin",
    "reference",
    "alternative",
    "clinvar_version",
    "set_type",
    "variation_type",
    "symbols",
    "hgnc_ids",
    "vcv",
    "summary_clinvar_review_status_label",
    "summary_clinvar_pathogenicity_label",
    "summary_clinvar_pathogenicity",
    "summary_clinvar_gold_stars",
    "summary_paranoid_review_status_label",
    "summary_paranoid_pathogenicity_label",
    "summary_paranoid_pathogenicity",
    "summary_paranoid_gold_stars",
    "details",
]


def run_conversion(
    hgnc_map: typing.Dict[str, str],
    clinvar_version: str,
    release: typing.Literal["GRCh37", "GRCh38"],
    path_jsonl: str,
):
    if path_jsonl.endswith(".gz"):
        inputf = gzip.open(path_jsonl, "rt")
    else:
        inputf = open(path_jsonl, "rt")
    print("\t".join(HEADER))
    with inputf:
        for line in inputf:
            extracted_vars = Parse(line, ExtractedVcvRecord())
            clinvar_record = extracted_var_to_clinvar_record(
                hgnc_map, clinvar_version, release, extracted_vars
            )
            if clinvar_record:
                clinvar_record.print_for_postgres()


def download_full_set():
    """Cached download of HGNC full set."""
    if os.path.exists(FULL_SET_PATH):
        with open(FULL_SET_PATH, "rt") as inputf:
            return inputf.read()
    else:
        response = requests.get(FULL_SET_URL)
        response.raise_for_status()
        with open(FULL_SET_PATH, "wb") as outputf:
            outputf.write(response.content)
        return response.text


def full_set_to_hgnc_map(full_set_tsv: str) -> typing.Dict[str, str]:
    hgnc_map = {}
    header = None
    for line in full_set_tsv.split("\n"):
        if not line:
            continue
        if not header:
            header = line.split("\t")
            continue
        else:
            fields = dict(zip(header, line.split("\t")))
            hgnc_map[fields["hgnc_id"]] = fields["symbol"]
    return hgnc_map


if __name__ == "__main__":
    full_set_tsv = download_full_set()
    hgnc_map = full_set_to_hgnc_map(full_set_tsv)
    run_conversion(hgnc_map, sys.argv[1], sys.argv[2], sys.argv[3])
