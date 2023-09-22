"""Code for reading cramino output files."""

import csv
import enum
import typing

from cases_qc import models
from cases_qc.io.utils import try_cast
import cases_qc.models.cramino


class CraminoParserState(enum.Enum):
    INITIAL = "initial"
    COUNTS_PER_CHROM = "counts_per_chrom"


class CraminoParser:
    """Helper datastructure for parsing Cramino output files"""

    def __init__(self):
        self.state = CraminoParserState.INITIAL
        self.summary: list[cases_qc.models.cramino.CraminoSummaryRecord] = []
        self.chrom_counts: list[cases_qc.models.cramino.CraminoChromNormalizedCountsRecord] = []

    def run(self, input_file: typing.TextIO):
        reader = csv.reader(input_file, delimiter="\t")
        for record in reader:
            if not record:
                continue  # skip empty lines
            elif record[0] == "# Normalized read count per chromosome":
                self.state = CraminoParserState.COUNTS_PER_CHROM
            else:
                func = getattr(self, f"_handle_state_{self.state.value}")
                func(record)

    def _handle_state_initial(self, record: list[str]):
        self.summary.append(
            cases_qc.models.cramino.CraminoSummaryRecord(
                key=record[0],
                value=try_cast(record[1], (int, float, str)),
            )
        )

    def _handle_state_counts_per_chrom(self, record: list[str]):
        self.chrom_counts.append(
            cases_qc.models.cramino.CraminoChromNormalizedCountsRecord(
                chrom_name=record[0],
                normalized_counts=float(record[1]),
            )
        )


def load_cramino(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
) -> cases_qc.models.cramino.CraminoMetrics:
    """Load a ``cramino`` output file into a ``cases_qc.models.CraminoMetrics`` record."""

    parser = CraminoParser()
    parser.run(input_file)

    return cases_qc.models.cramino.CraminoMetrics.objects.create(
        caseqc=caseqc,
        sample=sample,
        summary=parser.summary,
        chrom_counts=parser.chrom_counts,
    )
