"""Code for reading Dragen-style CSV QC files into ``cases_qc.models`` records."""

import csv
import typing

from cases_qc import models
from cases_qc.io.utils import try_cast
import cases_qc.models.dragen as models_dragen


def load_metrics_generic(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    model: typing.Type,
    sample: str | None = None,
    region_name: str | None = None,
    fieldnames: typing.Iterable[str] | None = None,
    file_identifier_to_individual: typing.Dict[str, str] | None = None,
):
    file_identifier_to_individual = file_identifier_to_individual or {}
    if fieldnames is None:
        fieldnames = ("section", "entry", "name", "value", "value_float")
    if any(k not in fieldnames for k in ("entry", "value")):
        raise ValueError(f"fieldnames must contain at least {fieldnames}")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    metrics = []
    for record in reader:
        entry = try_cast(record["entry"], (str, None))
        name = record.get("name")
        metrics.append(
            models_dragen.DragenStyleMetric(
                section=record.get("section"),
                entry=file_identifier_to_individual.get(entry, entry),
                name=file_identifier_to_individual.get(name, name),
                value=try_cast(record["value"], (int, float, str, None)),
                value_float=try_cast(record.get("value_float", ""), (float, None)),
            )
        )

    model_kwargs = {}
    if region_name is not None:
        model_kwargs["region_name"] = region_name
    if sample is not None:
        model_kwargs["sample"] = file_identifier_to_individual.get(sample, sample)

    return model.objects.create(
        caseqc=caseqc,
        metrics=metrics,
        **model_kwargs,
    )


def load_fragment_length_hist(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenFragmentLengthHistogram:
    # skip first line
    input_file.readline()

    keys: list[int] = []
    values: list[int] = []
    reader = csv.DictReader(f=input_file, delimiter=",")
    for record in reader:
        if record["Count"] != "0":
            keys.append(int(record["FragmentLength"]))
            values.append(int(record["Count"]))

    return models_dragen.DragenFragmentLengthHistogram.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
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
    file_identifier_to_individual: typing.Dict[str, str] = None,
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
        sample=file_identifier_to_individual.get(sample, sample),
        keys=keys,
        values=values,
        **model_kwargs,
    )


def load_wgs_fine_hist(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenWgsFineHist:
    return load_fine_hist_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenWgsFineHist,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_vc_hethom_ratio_metrics(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenVcHethomRatioMetrics:
    """Load contig het./hom. metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenVcHethomRatioMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_cnv_metrics(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenCnvMetrics:
    """Load CNV metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenCnvMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_mapping_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenMappingMetrics:
    """Load mapping metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenMappingMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_ploidy_estimation_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenPloidyEstimationMetrics:
    """Load ploidy estimation metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenPloidyEstimationMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_roh_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenRohMetrics:
    """Load ROH metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenRohMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_sv_metrics(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenSvMetrics:
    """Load SV calling metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenSvMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_time_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenTimeMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenTimeMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_trimmer_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenTrimmerMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenTrimmerMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_vc_metrics(
    *,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenTrimmerMetrics:
    """Load variant caller metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenVcMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_wgs_contig_mean_cov(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenWgsContigMeanCovMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    fieldnames = ("contig_name", "contig_len", "cov")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    metrics = []
    for record in reader:
        metrics.append(
            models_dragen.DragenStyleCoverage(
                contig_name=record["contig_name"],
                contig_len=int(record["contig_len"]),
                cov=float(record["cov"]),
            )
        )

    return models_dragen.DragenWgsContigMeanCovMetrics.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        metrics=metrics,
    )


def load_wgs_coverage_metrics(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenWgsCoverageMetrics:
    """Load time metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenWgsCoverageMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_wgs_hist(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenWgsHist:
    """Load WGS histogram metrics from ``input_file`` into ``caseqc``."""
    fieldnames = ("key", "value")
    reader = csv.DictReader(f=input_file, fieldnames=fieldnames, delimiter=",")

    keys: list[str] = []
    values: list[float] = []
    for record in reader:
        keys.append(record["key"])
        values.append(float(record["value"]))

    return models_dragen.DragenWgsHist.objects.create(
        caseqc=caseqc,
        sample=file_identifier_to_individual.get(sample, sample),
        keys=keys,
        values=values,
    )


def load_wgs_overall_mean_cov(
    *,
    sample: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenWgsOverallMeanCov:
    """Load overall mean coverage metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenWgsOverallMeanCov,
        fieldnames=("entry", "value"),
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_region_coverage_metrics(
    *,
    sample: str,
    region_name: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenRegionCoverageMetrics:
    """Load region coverage metrics from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenRegionCoverageMetrics,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_region_fine_hist(
    *,
    sample: str,
    region_name: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenRegionFineHist:
    """Load region fine histogram from ``input_file`` into ``caseqc``"""
    return load_fine_hist_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenRegionFineHist,
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_region_hist(
    *,
    sample: str,
    region_name: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenRegionHist:
    """Load region histogram from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenRegionHist,
        fieldnames=("entry", "value"),
        file_identifier_to_individual=file_identifier_to_individual,
    )


def load_region_overall_mean_cov(
    *,
    sample: str,
    region_name: str,
    input_file: typing.TextIO,
    caseqc: models.CaseQc,
    file_identifier_to_individual: typing.Dict[str, str],
) -> models_dragen.DragenRegionOverallMeanCov:
    """Load region histogram from ``input_file`` into ``caseqc``"""
    return load_metrics_generic(
        sample=sample,
        region_name=region_name,
        input_file=input_file,
        caseqc=caseqc,
        model=models_dragen.DragenRegionOverallMeanCov,
        file_identifier_to_individual=file_identifier_to_individual,
    )
