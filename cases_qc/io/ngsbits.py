"""Code for reading ngs-bits output files."""

import typing

from cases_qc import models
from cases_qc.io.utils import try_cast


class MappingqcParser:
    """Helper datastructure for parsing MappingQC output files"""

    def __init__(self):
        self.records: list[models.NgsbitsMappingqcRecord] = []

    def run(self, input_file: typing.TextIO):
        for line in input_file:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            record = line.split(": ", 1)
            self.records.append(
                models.NgsbitsMappingqcRecord(
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
) -> models.NgsbitsMappingqcMetrics:
    """Load a ngs-bits MappingQC output file into a ``cases_qc.models.NgsbitsMappingqcMetrics``
    record"""

    parser = MappingqcParser()
    parser.run(input_file)

    return models.NgsbitsMappingqcMetrics.objects.create(
        caseqc=caseqc,
        sample=sample,
        region_name=region_name,
        records=parser.records,
    )
