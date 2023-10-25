"""Code for reading samtoools-style QC files into ``cases_qc.models`` records.

This includes support for bcftools stats files as well.
"""

import csv
import typing

from cases_qc import models
from cases_qc.io.utils import try_cast
import cases_qc.models.samtools as models_samtools


class ParserRunMixin:
    """Shared code for parser helper classes."""

    def run(self, input_file: typing.TextIO):
        reader = csv.reader(input_file, delimiter="\t")
        for record in reader:
            if record[0].startswith("#"):
                continue  # skip comment

            if len(record) < 2:
                raise ValueError(f"record {record} has less than 2 fields")
            token = record[0].lower()
            if hasattr(self, f"_handle_{token}"):
                getattr(self, f"_handle_{token}")(record)
            else:
                raise ValueError(f"do not know how to handle line with id {record[0]}")


class BcftoolsStatsParser(ParserRunMixin):
    """Helper class for parsing ``bcftools stats`` output."""

    def __init__(self, file_identifier_to_individual: typing.Dict[str, str]):
        self.file_identifier_to_individual = file_identifier_to_individual
        self.sn: list[models_samtools.BcftoolsStatsSnRecord] = []
        self.tstv: list[models_samtools.BcftoolsStatsTstvRecord] = []
        self.sis: list[models_samtools.BcftoolsStatsSisRecord] = []
        self.af: list[models_samtools.BcftoolsStatsAfRecord] = []
        self.qual: list[models_samtools.BcftoolsStatsQualRecord] = []
        self.idd: list[models_samtools.BcftoolsStatsIddRecord] = []
        self.st: list[models_samtools.BcftoolsStatsStRecord] = []
        self.dp: list[models_samtools.BcftoolsStatsDpRecord] = []

    def _handle_id(self, record: list[str]):
        """Skip ``ID`` lines."""
        if record[1] != "0":
            raise ValueError(
                f"at the moment, only single-sample VCFs are supported (ID={record[1]})"
            )

    def _handle_sn(self, record: list[str]):
        """Handle parsing of ``SN`` lines."""
        self.sn.append(
            models_samtools.BcftoolsStatsSnRecord(
                key=record[2],
                value=int(record[3]),
            )
        )

    def _handle_tstv(self, record: list[str]):
        """Handle parsing of ``TSV`` lines."""
        self.tstv.append(
            models_samtools.BcftoolsStatsTstvRecord(
                ts=int(record[2]),
                tv=int(record[3]),
                tstv=float(record[4]),
                ts_1st_alt=int(record[5]),
                tv_1st_alt=int(record[6]),
                tstv_1st_alt=float(record[7]),
            )
        )

    def _handle_sis(self, record: list[str]):
        """Handle parsing of ``SiS`` lines."""
        self.sis.append(
            models_samtools.BcftoolsStatsSisRecord(
                total=int(record[2]),
                snps=int(record[3]),
                ts=int(record[4]),
                tv=int(record[5]),
                indels=int(record[6]),
                repeat_consistent=int(record[7]),
                repeat_inconsistent=int(record[8]),
            )
        )

    def _handle_af(self, record: list[str]):
        """Handle parsing of ``AF`` lines."""
        self.af.append(
            models_samtools.BcftoolsStatsAfRecord(
                af=float(record[2]),
                snps=int(record[3]),
                ts=int(record[4]),
                tv=int(record[5]),
                indels=int(record[6]),
                repeat_consistent=int(record[7]),
                repeat_inconsistent=int(record[8]),
                na=int(record[9]),
            )
        )

    def _handle_qual(self, record: list[str]):
        """Handle parsing of ``QUAL`` lines."""
        self.qual.append(
            models_samtools.BcftoolsStatsQualRecord(
                qual=try_cast(record[2], (float, None)),
                snps=int(record[3]),
                ts=int(record[4]),
                tv=int(record[5]),
                indels=int(record[6]),
            )
        )

    def _handle_idd(self, record: list[str]):
        """Handle parsing of ``IDD`` lines."""
        self.idd.append(
            models_samtools.BcftoolsStatsIddRecord(
                length=int(record[2]),
                sites=int(record[3]),
                gts=int(record[4]),
                mean_vaf=try_cast(record[5], (float, None)),
            )
        )

    def _handle_st(self, record: list[str]):
        """Handle parsing of ``ST`` lines."""
        self.st.append(
            models_samtools.BcftoolsStatsStRecord(
                type=record[2],
                count=int(record[3]),
            )
        )

    def _handle_dp(self, record: list[str]):
        """Handle parsing of ``DP`` lines."""
        self.dp.append(
            models_samtools.BcftoolsStatsDpRecord(
                bin=int(record[2].replace(">", "")),
                gts=int(record[3]),
                gts_frac=float(record[4]),
                sites=int(record[5]),
                sites_frac=float(record[6]),
            )
        )


def load_bcftools_stats(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_samtools.BcftoolsStatsMetrics:
    """Load a ``bcftools stats`` file into a ``cases_qc.models_samtools.BcftoolsStats`` record."""
    parser = BcftoolsStatsParser(file_identifier_to_individual)
    parser.run(input_file)

    return models_samtools.BcftoolsStatsMetrics.objects.create(
        caseqc=caseqc,
        sn=parser.sn,
        tstv=parser.tstv,
        sis=parser.sis,
        af=parser.af,
        qual=parser.qual,
        idd=parser.idd,
        st=parser.st,
        dp=parser.dp,
    )


def load_samtools_flagstat(  # noqa: C901
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_samtools.SamtoolsFlagstatMetrics:
    """Load the output of ``samtools idxstats``"""
    qc_pass = models_samtools.SamtoolsFlagstatRecord()
    qc_fail = models_samtools.SamtoolsFlagstatRecord()

    for line in input_file:
        line = line.strip()
        if line.count(" ") < 3:
            continue
        str_pass, _, str_fail, suffix = line.split(" ", 3)
        count_pass = int(str_pass)
        count_fail = int(str_fail)

        if suffix == "in total (QC-passed reads + QC-failed reads)":
            qc_pass.total = count_pass
            qc_fail.total = count_fail
        elif suffix == "primary":
            qc_pass.primary = count_pass
            qc_fail.primary = count_fail
        elif suffix == "secondary":
            qc_pass.secondary = count_pass
            qc_fail.secondary = count_fail
        elif suffix == "supplementary":
            qc_pass.supplementary = count_pass
            qc_fail.supplementary = count_fail
        elif suffix == "duplicates":
            qc_pass.duplicates = count_pass
            qc_fail.duplicates = count_fail
        elif suffix == "primary duplicates":
            qc_pass.duplicates_primary = count_pass
            qc_fail.duplicates_primary = count_fail
        elif suffix.startswith("mapped ("):
            qc_pass.mapped = count_pass
            qc_fail.mapped = count_fail
        elif suffix.startswith("primary mapped ("):
            qc_pass.mapped_primary = count_pass
            qc_fail.mapped_primary = count_fail
        elif suffix == "paired in sequencing":
            qc_pass.paired = count_pass
            qc_fail.paired = count_fail
        elif suffix == "read1":
            qc_pass.fragment_first = count_pass
            qc_fail.fragment_first = count_fail
        elif suffix == "read2":
            qc_pass.fragment_last = count_pass
            qc_fail.fragment_last = count_fail
        elif suffix.startswith("properly paired ("):
            qc_pass.properly_paired = count_pass
            qc_fail.properly_paired = count_fail
        elif suffix == "with itself and mate mapped":
            qc_pass.with_itself_and_mate_mapped = count_pass
            qc_fail.with_itself_and_mate_mapped = count_fail
        elif suffix.startswith("singletons ("):
            qc_pass.singletons = count_pass
            qc_fail.singletons = count_fail
        elif suffix == "with mate mapped to a different chr":
            qc_pass.with_mate_mapped_to_different_chr = count_pass
            qc_fail.with_mate_mapped_to_different_chr = count_fail
        elif suffix == "with mate mapped to a different chr (mapQ>=5)":
            qc_pass.with_mate_mapped_to_different_chr_mapq5 = count_pass
            qc_fail.with_mate_mapped_to_different_chr_mapq5 = count_fail
        else:
            raise ValueError("cannot interpret line {line}")

    return models_samtools.SamtoolsFlagstatMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        qc_pass=qc_pass,
        qc_fail=qc_fail,
    )


class SamtoolsStatsParser(ParserRunMixin):
    """Helper class for parsing ``samtools stats`` output."""

    def __init__(self):
        self.sn: list[models_samtools.BcftoolsStatsSnRecord] = []
        self.chk: list[models_samtools.SamtoolsStatsChkRecord] = []
        self.ffq: list[models_samtools.SamtoolsStatsFqRecord] = []
        self.lfq: list[models_samtools.SamtoolsStatsFqRecord] = []
        self.gcf: list[models_samtools.SamtoolsStatsGcRecord] = []
        self.gcl: list[models_samtools.SamtoolsStatsGcRecord] = []
        self.gcc: list[models_samtools.SamtoolsStatsBasePercentagesRecord] = []
        self.gct: list[models_samtools.SamtoolsStatsBasePercentagesRecord] = []
        self.fbc: list[models_samtools.SamtoolsStatsBasePercentagesRecord] = []
        self.lbc: list[models_samtools.SamtoolsStatsBasePercentagesRecord] = []
        self.isize: list[models_samtools.SamtoolsStatsIsRecord] = []
        self.rl: list[models_samtools.SamtoolsStatsHistoRecord] = []
        self.frl: list[models_samtools.SamtoolsStatsHistoRecord] = []
        self.lrl: list[models_samtools.SamtoolsStatsHistoRecord] = []
        self.mapq: list[models_samtools.SamtoolsStatsHistoRecord] = []

        self.cov: list[models_samtools.SamtoolsStatsHistoRecord] = []
        self.gcd: list[models_samtools.SamtoolsStatsGcdRecord] = []
        self.idd: list[models_samtools.SamtoolsStatsIdRecord] = []
        self.ic: list[models_samtools.SamtoolsStatsIcRecord] = []

    def _handle_chk(self, record: list[str]):
        """Handle parsing of ``CHK`` lines."""
        self.chk.append(
            models_samtools.SamtoolsStatsChkRecord(
                read_names_crc32=record[1],
                sequences_crc32=record[2],
                qualities_crc32=record[3],
            )
        )

    def _handle_sn(self, record: list[str]):
        """Handle parsing of ``SN`` lines."""
        self.sn.append(
            models_samtools.BcftoolsStatsSnRecord(
                key=record[1],
                value=try_cast(record[2], (int, float, str, None)),
            )
        )

    def _handle_ffq(self, record: list[str]):
        """Handle parsing of ``FFQ`` lines."""
        self.ffq.append(
            models_samtools.SamtoolsStatsFqRecord(
                cycle=int(record[1]),
                counts=[int(x) for x in record[2:]],
            )
        )

    def _handle_lfq(self, record: list[str]):
        """Handle parsing of ``LFQ`` lines."""
        self.lfq.append(
            models_samtools.SamtoolsStatsFqRecord(
                cycle=int(record[1]),
                counts=[int(x) for x in record[2:]],
            )
        )

    def _handle_gcf(self, record: list[str]):
        """Handle parsing of ``GCF`` lines."""
        self.gcf.append(
            models_samtools.SamtoolsStatsGcRecord(
                gc_content=float(record[1]),
                count=int(record[2]),
            )
        )

    def _handle_gcl(self, record: list[str]):
        """Handle parsing of ``GCL`` lines."""
        self.gcl.append(
            models_samtools.SamtoolsStatsGcRecord(
                gc_content=float(record[1]),
                count=int(record[2]),
            )
        )

    def _handle_base_percentage_record(
        self,
        lst: list[models_samtools.SamtoolsStatsBasePercentagesRecord],
        record: list[str],
    ):
        """Generic handler for GCC, GCT, FBC, LBC lines."""
        lst.append(
            models_samtools.SamtoolsStatsBasePercentagesRecord(
                cycle=int(record[1]),
                percentages=[float(x) for x in record[2:]],
            )
        )

    def _handle_gcc(self, record: list[str]):
        """Handle parsing of ``GCC`` lines."""
        self._handle_base_percentage_record(self.gcc, record)

    def _handle_gct(self, record: list[str]):
        """Handle parsing of ``GCT`` lines."""
        self._handle_base_percentage_record(self.gct, record)

    def _handle_fbc(self, record: list[str]):
        """Handle parsing of ``FBC`` lines."""
        self._handle_base_percentage_record(self.fbc, record)

    def _handle_ftc(self, record: list[str]):
        """Skip ``FTC`` lines."""

    def _handle_lbc(self, record: list[str]):
        """Handle parsing of ``LBC`` lines."""
        self._handle_base_percentage_record(self.lbc, record)

    def _handle_ltc(self, _record: list[str]):
        """Skip ``LTC`` lines."""

    def _handle_is(self, record: list[str]):
        """Handle parsing of ``IS`` lines."""
        self.isize.append(
            models_samtools.SamtoolsStatsIsRecord(
                insert_size=int(record[1]),
                pairs_total=int(record[2]),
                pairs_inward=int(record[3]),
                pairs_outward=int(record[4]),
                pairs_other=int(record[5]),
            )
        )

    def _handle_histo_record(
        self,
        lst: list[models_samtools.SamtoolsStatsHistoRecord],
        record: list[str],
        idx_value: int = 1,
        idx_count: int = 2,
    ):
        """Generic handler for RL, COV, GCD, FRL, LRL, MAPQ lines."""
        lst.append(
            models_samtools.SamtoolsStatsHistoRecord(
                value=int(record[idx_value]),
                count=int(record[idx_count]),
            )
        )

    def _handle_rl(self, record: list[str]):
        """Handle parsing of ``RL`` lines."""
        self._handle_histo_record(self.rl, record)

    def _handle_frl(self, record: list[str]):
        """Handle parsing of ``FRL`` lines."""
        self._handle_histo_record(self.frl, record)

    def _handle_lrl(self, record: list[str]):
        """Handle parsing of ``LRL`` lines."""
        self._handle_histo_record(self.lrl, record)

    def _handle_mapq(self, record: list[str]):
        """Handle parsing of ``MAPQ`` lines."""
        self._handle_histo_record(self.mapq, record)

    def _handle_id(self, record: list[str]):
        """Handle ID lines."""
        self.idd.append(
            models_samtools.SamtoolsStatsIdRecord(
                length=int(record[1]),
                ins=int(record[2]),
                dels=float(record[3]),
            )
        )

    def _handle_ic(self, record: list[str]):
        """Handle IC lines."""
        self.ic.append(
            models_samtools.SamtoolsStatsIcRecord(
                cycle=int(record[1]),
                ins_fwd=int(record[2]),
                dels_fwd=int(record[3]),
                ins_rev=int(record[4]),
                dels_rev=int(record[5]),
            )
        )

    def _handle_cov(self, record: list[str]):
        """Handle parsing of ``COV`` lines."""
        self._handle_histo_record(self.cov, record, idx_value=2, idx_count=3)

    def _handle_gcd(self, record: list[str]):
        """Handle parsing of ``GCD`` lines."""
        self.gcd.append(
            models_samtools.SamtoolsStatsGcdRecord(
                gc_content=float(record[1]),
                unique_seq_percentiles=float(record[2]),
                dp_percentile_10=float(record[3]),
                dp_percentile_25=float(record[4]),
                dp_percentile_50=float(record[5]),
                dp_percentile_75=float(record[6]),
                dp_percentile_90=float(record[7]),
            )
        )


def load_samtools_stats(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> tuple[
    models_samtools.SamtoolsStatsMainMetrics,
    models_samtools.SamtoolsStatsSupplementaryMetrics,
]:
    """Load the output of ``samtools stats`"""
    parser = SamtoolsStatsParser()
    parser.run(input_file)

    main = models_samtools.SamtoolsStatsMainMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        sn=parser.sn,
        chk=parser.chk,
        isize=parser.isize,
        cov=parser.cov,
        gcd=parser.gcd,
        frl=parser.frl,
        lrl=parser.lrl,
        idd=parser.idd,
        ffq=parser.ffq,
        lfq=parser.lfq,
        fbc=parser.fbc,
        lbc=parser.lbc,
    )
    supplementary = models_samtools.SamtoolsStatsSupplementaryMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        gcf=parser.gcf,
        gcl=parser.gcl,
        gcc=parser.gcc,
        gct=parser.gct,
        rl=parser.rl,
        mapq=parser.mapq,
        ic=parser.ic,
    )

    return (main, supplementary)


def load_samtools_idxstats(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_samtools.SamtoolsIdxstatsMetrics:
    """Load the output of ``samtools idxstats`"""
    reader = csv.reader(input_file, delimiter="\t")
    records = []
    for record in reader:
        records.append(
            models_samtools.SamtoolsIdxstatsRecord(
                contig_name=record[0],
                contig_len=int(record[1]),
                mapped=int(record[2]),
                unmapped=int(record[3]),
            )
        )

    return models_samtools.SamtoolsIdxstatsMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        records=records,
    )
