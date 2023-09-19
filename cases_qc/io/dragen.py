"""Code for reading Dragen-style CSV QC files into ``cases_qc.models`` records."""

import csv
import typing

from cases_qc import models


def try_cast(
    value: str,
    types: typing.Iterable[typing.Type],
    none_values: typing.Iterable[typing.Any] = (None, "", "NA", "inf"),
) -> typing.Union[str, int, float, None]:
    if value in none_values and None in types:
        return None

    for type in types:
        if type is not None:
            try:
                return type(value)
            except ValueError:
                continue
    if None in types:
        return None
    else:
        raise ValueError(f"could not cast value {value} to any of {types}")


def load_metrics_generic(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc, model: typing.Type
):
    fieldnames = ("section", "entry", "name", "value", "value_float")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    metrics = []
    for record in reader:
        metrics.append(
            models.DragenStyleMetric(
                section=record["section"],
                entry=try_cast(record["entry"], (str, None)),
                name=record["name"],
                value=try_cast(record["value"], (int, float, str, None)),
                value_float=try_cast(record["value_float"], (float, None)),
            )
        )

    return model.objects.create(
        caseqc=caseqc,
        sample=sample,
        metrics=metrics,
    )


def load_fragment_length_hist(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.FragmentLengthHistogram:
    # skip first line
    input_file.readline()

    keys: list[int] = []
    values: list[int] = []
    reader = csv.DictReader(f=input_file, delimiter=",")
    for record in reader:
        if record["Count"] != "0":
            keys.append(int(record["FragmentLength"]))
            values.append(int(record["Count"]))

    return models.FragmentLengthHistogram.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
    )


def load_wgs_fine_hist(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.WgsFineHist:
    keys: list[int] = []
    values: list[int] = []
    reader = csv.DictReader(f=input_file, delimiter=",")
    for record in reader:
        if record["Overall"] != "0":
            keys.append(int(record["Depth"].replace("+", "")))
            values.append(int(record["Overall"]))

    return models.WgsFineHist.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
    )


def load_contig_het_hom_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.ContigHetHomMetrics:
    """Load contig het./hom. metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.ContigHetHomMetrics,
    )


def load_cnv_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.CnvMetrics:
    """Load CNV metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.CnvMetrics,
    )


def load_mapping_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.MappingMetrics:
    """Load mapping metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.MappingMetrics,
    )


def load_ploidy_estimation_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.PloidyEstimationMetrics:
    """Load ploidy estimation metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.PloidyEstimationMetrics,
    )


def load_roh_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.RohMetrics:
    """Load ROH metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.RohMetrics,
    )


def load_seqvar_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.RohMetrics:
    """Load sequence variant metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.SeqvarMetrics,
    )


def load_strucvar_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.StrucvarMetrics:
    """Load SV calling metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.StrucvarMetrics,
    )


def load_time_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.TimeMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.TimeMetrics,
    )


def load_trimmer_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.TrimmerMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.TrimmerMetrics,
    )


def load_wgs_contig_mean_cov_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.WgsContigMeanCovMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    fieldnames = ("contig_name", "contig_len", "cov")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    metrics = []
    for record in reader:
        metrics.append(
            models.DragenStyleCoverage(
                contig_name=record["contig_name"],
                contig_len=int(record["contig_len"]),
                cov=float(record["cov"]),
            )
        )

    return models.WgsContigMeanCovMetrics.objects.create(
        caseqc=caseqc,
        sample=sample,
        metrics=metrics,
    )


def load_wgs_coverage_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.WgsCoverageMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.WgsCoverageMetrics,
    )


def load_wgs_hist_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.WgsHistMetrics:
    """Load WGS histogram metrics from ``input_file`` into ``caseqc``."""
    fieldnames = ("key", "value")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    keys: list[str] = []
    values: list[float] = []
    for record in reader:
        keys.append(record["key"])
        values.append(float(record["value"]))

    return models.WgsHistMetrics.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
    )
