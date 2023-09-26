"""Code for reading ngs-bits output files."""

import typing

from cases_qc import models
from cases_qc.io.utils import try_cast
import cases_qc.models.ngsbits


class MappingqcParser:
    """Helper datastructure for parsing MappingQC output files"""

    def __init__(self):
        self.records: list[cases_qc.models.ngsbits.NgsbitsMappingqcRecord] = []

    def run(self, input_file: typing.TextIO):
        for line in input_file:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            record = line.split(": ", 1)
            self.records.append(
                cases_qc.models.ngsbits.NgsbitsMappingqcRecord(
                    key=record[0],
                    value=try_cast(record[1], (int, float, str, None)),
                )
            )


def load_mappingqc(
    *,
    sample: str,
    region_name: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: dict[str, str],
) -> cases_qc.models.ngsbits.NgsbitsMappingqcMetrics:
    """Load a ngs-bits MappingQC output file into a ``cases_qc.models.NgsbitsMappingqcMetrics``
    record"""
    parser = MappingqcParser()
    parser.run(input_file)

    return cases_qc.models.ngsbits.NgsbitsMappingqcMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        region_name=region_name,
        records=parser.records,
    )
