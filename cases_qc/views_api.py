import typing

from django.http import Http404
from projectroles.views_api import SODARAPIBaseProjectMixin
from rest_framework.generics import RetrieveAPIView

from cases.views_api import CasesApiPermission
from cases_qc.models import CaseQc
from cases_qc.models.dragen import (
    DragenFragmentLengthHistogram,
    DragenMappingMetrics,
    DragenRegionCoverageMetrics,
    DragenSvMetrics,
    DragenVcMetrics,
    DragenWgsCoverageMetrics,
)
from cases_qc.models.varfish import (
    DetailedAlignmentCounts,
    InsertSizeStats,
    RegionCoverageStats,
    RegionVariantStats,
    SampleAlignmentStats,
    SampleReadStats,
    SampleSeqvarStats,
    SampleStrucvarStats,
    VarfishStats,
)
from cases_qc.serializers import CaseQcSerializer, VarfishStatsSerializer
from varfish.api_utils import VarfishApiRenderer, VarfishApiVersioning
from variants.models.case import Case


class CaseQcRetrieveApiView(SODARAPIBaseProjectMixin, RetrieveAPIView):
    """
    Retrieve the latest ``CaseQc`` for the given case.

    This corresponds to the raw QC values imported into VarFish.  See
    ``VarfishStatsRetrieveApiView`` for the information used by the UI.

    **URL:** ``/cases_qc/api/caseqc/retrieve/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** serialized ``CaseQc`` if any, HTTP 404 if not found
    """

    lookup_field = "case"

    permission_classes = [CasesApiPermission]
    permission_required = "cases_qc.view_data"

    renderer_classes = [VarfishApiRenderer]
    versioning_class = VarfishApiVersioning
    serializer_class = CaseQcSerializer

    def get_project(self, request=None, kwargs=None):
        _ = request
        casephenotypeterms = CaseQc.objects.get(sodar_uuid=kwargs["case"])
        return casephenotypeterms.case.project

    def get_queryset(self):
        case = Case.objects.get(sodar_uuid=self.kwargs["case"])
        qs = CaseQc.objects.filter(case=case)
        qs = qs.prefetch_related("dragencnvmetrics_set")
        return qs

    def get_object(self):
        result = self.get_queryset().filter(state=CaseQc.STATE_ACTIVE).first()
        if not result:
            raise Http404()
        return result


class VarfishStatsRetrieveApiView(CaseQcRetrieveApiView):
    """
    Retrieve the latest statistics to display in the UI for a case.

    **URL:** ``/cases_qc/api/varfishstats/retrieve/{case.sodar_uuid}/``

    **Methods:** ``GET``

    **Returns:** serialized ``CaseQc`` if any, HTTP 404 if not found
    """

    serializer_class = VarfishStatsSerializer

    def get_object(self):
        caseqc = super().get_object()
        result = VarfishStats(
            samples=[],
            readstats=[],
            alignmentstats=[],
            seqvarstats=[],
            strucvarstats=[],
        )

        self._handle_dragen_readstats(
            result.samples, result.readstats, caseqc.dragenmappingmetrics_set.all()
        )
        self._handle_dragen_alignmentstats(
            result.samples,
            result.alignmentstats,
            caseqc.dragenmappingmetrics_set.all(),
            caseqc.dragenfragmentlengthhistogram_set.all(),
            caseqc.dragenwgscoveragemetrics_set.all(),
            caseqc.dragenregioncoveragemetrics_set.all(),
        )
        self._handle_dragen_vcmetrics(
            result.samples,
            result.seqvarstats,
            caseqc.dragenvcmetrics_set.all(),
        )
        self._handle_dragen_svmetrics(
            result.samples,
            result.strucvarstats,
            caseqc.dragensvmetrics_set.all(),
        )

        return result

    def _handle_dragen_readstats(
        self,
        samples: list[str],
        readstats_list: list[SampleReadStats],
        dragenmappingmetrics: typing.Iterable[DragenMappingMetrics],
    ):
        section, entry = "MAPPING/ALIGNING SUMMARY", None

        for dmm in dragenmappingmetrics:
            if dmm.sample not in samples:
                samples.append(dmm.sample)

            readstats = None
            for metrics in dmm.metrics:
                if metrics.section != section or metrics.entry != entry:
                    continue  # skip
                elif not readstats:
                    readstats = SampleReadStats(
                        sample=dmm.sample,
                        read_length_n50=0,
                        read_length_histogram=[],
                        total_reads=0,
                        total_yield=0,
                        fragment_first=None,
                        fragment_last=None,
                    )

                if metrics.name == "Total input reads":
                    readstats.total_reads = int(metrics.value)
                elif metrics.name == "Total bases":
                    readstats.total_yield = int(metrics.value)
                elif metrics.name == "Estimated read length":
                    readstats.read_length_n50 = int(metrics.value)

            readstats.read_length_histogram = [[readstats.read_length_n50, readstats.total_reads]]
            readstats_list.append(readstats)

    def _handle_dragen_alignmentstats(  # noqa: C901
        self,
        samples: list[str],
        readstats: list[SampleReadStats],
        dragenmappingmetrics: typing.Iterable[DragenMappingMetrics],
        dragenfragmentlengthistogram: typing.Iterable[DragenFragmentLengthHistogram],
        dragenwgscoveragemetrics: typing.Iterable[DragenWgsCoverageMetrics],
        dragenregioncoveragemetrics: typing.Iterable[DragenRegionCoverageMetrics],
    ):
        # get histograms by sample name
        histograms = {hist.sample: hist for hist in dragenfragmentlengthistogram}
        # get coverage by sample name
        cov_wgs: dict[str, DragenWgsCoverageMetrics] = {}
        for cov in dragenwgscoveragemetrics:
            cov_wgs[cov.sample] = cov
        cov_reg: dict[str, list[DragenRegionCoverageMetrics]] = {}
        for cov in dragenregioncoveragemetrics:
            cov_reg.setdefault(cov.sample, []).append(cov)

        # process the mapping metrics for most of the data
        section, entry = "MAPPING/ALIGNING SUMMARY", None
        for dmm in dragenmappingmetrics:
            if dmm.sample not in samples:
                samples.append(dmm.sample)

            total_bases = None
            mismatched_bases = 0
            alignmentstats = None
            for metrics in dmm.metrics:
                if metrics.section != section or metrics.entry != entry:
                    continue  # skip
                elif not alignmentstats:
                    alignmentstats = SampleAlignmentStats(
                        sample=dmm.sample,
                        detailed_counts=DetailedAlignmentCounts(
                            primary=0,
                            secondary=0,
                            supplementary=0,
                            duplicates=0,
                            mapped=0,
                            properly_paired=0,
                            with_itself_and_mate_mapped=0,
                            singletons=0,
                            with_mate_mapped_to_different_chr=0,
                            with_mate_mapped_to_different_chr_mapq=0,
                            mismatch_rate=0.0,
                            mapq=[],
                        ),
                        per_chromosome_counts=[],
                        insert_size_stats=InsertSizeStats(
                            insert_size_mean=0,
                            insert_size_median=None,
                            insert_size_stddev=0,
                            insert_size_histogram=[],
                        ),
                        region_coverage_stats=[],
                    )

                if metrics.name == "Total bases":
                    total_bases = int(metrics.value)
                elif metrics.name in (
                    "Mismatched bases R1 (excl. indels)",
                    "Mismatched bases R2 (excl. indels)",
                ):
                    mismatched_bases += int(metrics.value)
                elif metrics.name == "Total alignments":
                    alignmentstats.detailed_counts.mapped = int(metrics.value)
                elif metrics.name == "Supplementary (chimeric) alignments":
                    alignmentstats.detailed_counts.supplementary = int(metrics.value)
                elif metrics.name == "Secondary alignments":
                    alignmentstats.detailed_counts.secondary = int(metrics.value)
                elif metrics.name == "Number of duplicate marked reads":
                    alignmentstats.detailed_counts.duplicates = int(metrics.value)
                elif metrics.name == "Insert length: mean":
                    alignmentstats.insert_size_stats.insert_size_mean = float(metrics.value)
                elif metrics.name == "Insert length: median":
                    alignmentstats.insert_size_stats.insert_size_median = float(metrics.value)
                elif metrics.name == "Insert length: standard deviation":
                    alignmentstats.insert_size_stats.insert_size_stddev = float(metrics.value)
                elif metrics.name == "Singleton reads (itself mapped; mate unmapped)":
                    alignmentstats.detailed_counts.singletons = int(metrics.value)
                elif metrics.name == "Properly paired reads":
                    alignmentstats.detailed_counts.properly_paired = int(metrics.value)
                elif metrics.name == "Paired reads (itself & mate mapped)":
                    alignmentstats.detailed_counts.with_itself_and_mate_mapped = int(metrics.value)
                elif metrics.name == "Paired reads mapped to different chromosomes":
                    alignmentstats.detailed_counts.with_mate_mapped_to_different_chr = int(
                        metrics.value
                    )
                elif metrics.name == "Paired reads mapped to different chromosomes (MAPQ>=10)":
                    alignmentstats.detailed_counts.with_mate_mapped_to_different_chr_mapq = int(
                        metrics.value
                    )

            # fill in some derived values for which we need to have seen all data
            alignmentstats.detailed_counts.primary = (
                alignmentstats.detailed_counts.mapped
                - alignmentstats.detailed_counts.secondary
                - alignmentstats.detailed_counts.supplementary
            )
            if mismatched_bases > 0:
                alignmentstats.detailed_counts.mismatch_rate = mismatched_bases / total_bases

            # copy over the histogram in a binned fashion
            if dmm.sample in histograms:
                histogram = histograms[dmm.sample]
                bin_width = 10
                max_bin = 2000
                histo = {}
                for key, value in zip(histogram.keys, histogram.values):
                    bin = min(int(key / bin_width) * bin_width, max_bin)
                    histo[bin] = histo.get(bin, 0) + value
                alignmentstats.insert_size_stats.insert_size_histogram = list(histo.items())

            # finally, add the region coverage stats
            if dmm.sample in cov_wgs:
                alignmentstats.region_coverage_stats.append(
                    self._dragen_cov_metrics_to_regioncoveragestats("WGS", cov_wgs[dmm.sample])
                )
            for cov in cov_reg.get(dmm.sample, []):
                alignmentstats.region_coverage_stats.append(
                    self._dragen_cov_metrics_to_regioncoveragestats(
                        cov.region_name, cov_wgs[dmm.sample]
                    )
                )

            readstats.append(alignmentstats)

    def _dragen_cov_metrics_to_regioncoveragestats(
        self,
        region_name: str,
        cov: DragenWgsCoverageMetrics | DragenRegionCoverageMetrics,
    ):
        mean_rd: None | float = None
        min_rd_fraction: list[list[int, float]] = []
        for metric in cov.metrics:
            if metric.section != "COVERAGE SUMMARY" or metric.entry is not None:
                continue
            if metric.name == "Average alignment coverage over genome":
                mean_rd = float(metric.value)
            elif metric.name.startswith("PCT of genome with coverage [") and metric.name.endswith(
                ": inf)"
            ):
                depth_str = metric.name[metric.name.find("[") + 1 : metric.name.find("x:")]
                min_rd_fraction.append([int(depth_str), float(metric.value)])
        min_rd_fraction.sort()
        return RegionCoverageStats(
            region_name=region_name,
            mean_rd=mean_rd,
            min_rd_fraction=min_rd_fraction,
        )

    def _handle_dragen_vcmetrics(
        self,
        samples: list[str],
        seqvarstats_list: list[SampleSeqvarStats],
        dragenvcmetrics: typing.Iterable[DragenVcMetrics],
    ):
        section = "VARIANT CALLER POSTFILTER"

        for dss in dragenvcmetrics:
            seqvarstats = None
            for metrics in dss.metrics:
                if metrics.section != section:
                    continue  # skip
                else:
                    # TODO: sample mapping with phenopackets info
                    if metrics.entry not in samples:
                        samples.append(metrics.entry)
                    if not seqvarstats:
                        seqvarstats = SampleSeqvarStats(
                            sample=metrics.entry,
                            genome_wide=RegionVariantStats(
                                region_name="WGS",
                                snv_count=0,
                                indel_count=0,
                                multiallelic_count=0,
                                transition_count=0,
                                transversion_count=0,
                                tstv_ratio=0.0,
                            ),
                            per_region=[],
                        )

                if metrics.name == "SNPs":
                    seqvarstats.genome_wide.snv_count = int(metrics.value)
                elif metrics.name in (
                    "Insertions (Hom)",
                    "Insertions (Het)",
                    "Deletions (Hom)",
                    "Deletions (Het)",
                    "Indels (Het)",
                ):
                    seqvarstats.genome_wide.indel_count = int(metrics.value)
                elif metrics.name == "SNP Transitions":
                    seqvarstats.genome_wide.transition_count = int(metrics.value)
                elif metrics.name == "SNP Transversions":
                    seqvarstats.genome_wide.transversion_count = int(metrics.value)
                elif metrics.name == "Ti/Tv ratio":
                    seqvarstats.genome_wide.tstv_ratio = float(metrics.value)
                elif metrics.name == "Multiallelic":
                    seqvarstats.genome_wide.multiallelic_count = int(metrics.value)

            seqvarstats_list.append(seqvarstats)

    def _handle_dragen_svmetrics(
        self,
        samples: list[str],
        strucvarstats_list: list[SampleStrucvarStats],
        dragensvmetrics: typing.Iterable[DragenSvMetrics],
    ):
        section = "SV SUMMARY"

        for dss in dragensvmetrics:
            strucvarstats = None
            for metrics in dss.metrics:
                if metrics.section != section:
                    continue  # skip
                else:
                    # TODO: sample mapping with phenopackets info
                    if metrics.entry not in samples:
                        samples.append(metrics.entry)
                    if not strucvarstats:
                        strucvarstats = SampleStrucvarStats(
                            sample=metrics.entry,
                            deletion_count=0,
                            duplication_count=0,
                            insertion_count=0,
                            inversion_count=0,
                            breakend_count=0,
                        )

                if metrics.name == "Number of deletions (PASS)":
                    strucvarstats.deletion_count = int(metrics.value)
                elif metrics.name == "Number of insertions (PASS)":
                    strucvarstats.insertion_count = int(metrics.value)
                elif metrics.name == "Number of duplications (PASS)":
                    strucvarstats.duplication_count = int(metrics.value)
                elif metrics.name == "Number of breakend pairs (PASS)":
                    strucvarstats.breakend_count = int(metrics.value)

            strucvarstats_list.append(strucvarstats)
