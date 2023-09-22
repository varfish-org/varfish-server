"""Code for reading Dragen-style CSV QC files into ``cases_qc.models`` records."""

import csv
import typing

from cases_qc import models
from cases_qc.io.utils import try_cast


def load_metrics_generic(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    model: typing.Type,
    sample: str | None = None,
    region_name: str | None = None,
    fieldnames: typing.Iterable[str] | None = None,
):
    if fieldnames is None:
        fieldnames = ("section", "entry", "name", "value", "value_float")
    if any(k not in fieldnames for k in ("entry", "value")):
        raise ValueError(f"fieldnames must contain at least {fieldnames}")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    metrics = []
    for record in reader:
        metrics.append(
            models.DragenStyleMetric(
                section=record.get("section"),
                entry=try_cast(record["entry"], (str, None)),
                name=record.get("name"),
                value=try_cast(record["value"], (int, float, str, None)),
                value_float=try_cast(record.get("value_float", ""), (float, None)),
            )
        )

    model_kwargs = {}
    if region_name is not None:
        model_kwargs["region_name"] = region_name
    if sample is not None:
        model_kwargs["sample"] = sample

    return model.objects.create(
        caseqc=caseqc,
        metrics=metrics,
        **model_kwargs,
    )


def load_fragment_length_hist(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenFragmentLengthHistogram:
    # skip first line
    input_file.readline()

    keys: list[int] = []
    values: list[int] = []
    reader = csv.DictReader(f=input_file, delimiter=",")
    for record in reader:
        if record["Count"] != "0":
            keys.append(int(record["FragmentLength"]))
            values.append(int(record["Count"]))

    return models.DragenFragmentLengthHistogram.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
    )


def load_fine_hist_generic(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    model: typing.Type,
    region_name: str | None = None,
):
    keys: list[int] = []
    values: list[int] = []
    reader = csv.DictReader(f=input_file, delimiter=",")
    for record in reader:
        if record["Overall"] != "0":
            keys.append(int(record["Depth"].replace("+", "")))
            values.append(int(record["Overall"]))

    model_kwargs = {}
    if region_name is not None:
        model_kwargs["region_name"] = region_name

    return model.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
        **model_kwargs,
    )


def load_wgs_fine_hist(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenWgsFineHist:
    return load_fine_hist_generic(
        sample=sample, input_file=input_file, caseqc=caseqc, model=models.DragenWgsFineHist
    )


def load_vc_hethom_ratio_metrics(
    *, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenVcHethomRatioMetrics:
    """Load contig het./hom. metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenVcHethomRatioMetrics,
    )


def load_cnv_metrics(
    *, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenCnvMetrics:
    """Load CNV metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenCnvMetrics,
    )


def load_mapping_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenMappingMetrics:
    """Load mapping metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenMappingMetrics,
    )


def load_ploidy_estimation_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenPloidyEstimationMetrics:
    """Load ploidy estimation metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenPloidyEstimationMetrics,
    )


def load_roh_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenRohMetrics:
    """Load ROH metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenRohMetrics,
    )


def load_sv_metrics(*, input_file: typing.TextIO, caseqc: models.CaseQc) -> models.DragenSvMetrics:
    """Load SV calling metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenSvMetrics,
    )


def load_time_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenTimeMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenTimeMetrics,
    )


def load_trimmer_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenTrimmerMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenTrimmerMetrics,
    )


def load_vc_metrics(
    *, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenTrimmerMetrics:
    """Load variant caller metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenVcMetrics,
    )


def load_wgs_contig_mean_cov(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenWgsContigMeanCovMetrics:
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

    return models.DragenWgsContigMeanCovMetrics.objects.create(
        caseqc=caseqc,
        sample=sample,
        metrics=metrics,
    )


def load_wgs_coverage_metrics(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenWgsCoverageMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenWgsCoverageMetrics,
    )


def load_wgs_hist(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenWgsHist:
    """Load WGS histogram metrics from ``input_file`` into ``caseqc``."""
    fieldnames = ("key", "value")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    keys: list[str] = []
    values: list[float] = []
    for record in reader:
        keys.append(record["key"])
        values.append(float(record["value"]))

    return models.DragenWgsHist.objects.create(
        caseqc=caseqc,
        sample=sample,
        keys=keys,
        values=values,
    )


def load_wgs_overall_mean_cov(
    *, sample: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenWgsOverallMeanCov:
    """Load overall mean coverage metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenWgsOverallMeanCov,
        fieldnames=("entry", "value"),
    )


def load_region_coverage_metrics(
    *, sample: str, region_name: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenRegionCoverageMetrics:
    """Load region coverage metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenRegionCoverageMetrics,
    )


def load_region_fine_hist(
    *, sample: str, region_name: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenRegionFineHist:
    """Load region fine histogram from ``input_file`` into ``caseqc``"""
    return load_fine_hist_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenRegionFineHist,
    )


def load_region_hist(
    *, sample: str, region_name: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenRegionHist:
    """Load region histogram from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenRegionHist,
        fieldnames=("entry", "value"),
    )


def load_region_overall_mean_cov(
    *, sample: str, region_name: str, input_file: typing.TextIO, caseqc: models.CaseQc
) -> models.DragenRegionOverallMeanCov:
    """Load region histogram from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models.DragenRegionOverallMeanCov,
    )
