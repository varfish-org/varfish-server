"""Code that supports building the structural variant background database."""

from contextlib import contextmanager
import enum
import gc
import itertools
import json
import logging
import os
import pathlib
import random
import re
import tempfile
import typing

import attrs
import binning
import cattr
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from intervaltree import Interval, IntervalTree
from projectroles.plugins import get_backend_api
from projectroles.templatetags.projectroles_common_tags import get
import psutil
from sqlalchemy import delete

from svs.models import (
    BackgroundSv,
    BackgroundSvSet,
    BuildBackgroundSvSetJob,
    CleanupBackgroundSvSetJob,
    StructuralVariant,
)
from svs.models import SV_SUB_TYPE_BND as _SV_SUB_TYPE_BND
from svs.models import SV_SUB_TYPE_CHOICES as _SV_SUB_TYPE_CHOICES
from svs.models import SV_SUB_TYPE_INS as _SV_SUB_TYPE_INS
from varfish import __version__ as varfish_version

#: Logger to use in this module.
from variants.helpers import get_engine, get_meta
from variants.models import CHROMOSOME_NAMES, CHROMOSOME_STR_TO_CHROMOSOME_INT, Case

LOGGER = logging.getLogger(__name__)

#: The SV types to be used in ``SvRecord``.
SV_TYPES = [t[0] for t in _SV_SUB_TYPE_CHOICES]


@attrs.define
class ClusterAlgoParams:
    """Parameters for the clustering algorithm"""

    #: Seed to use for random numbers.
    seed: int = 42
    #: Maximal size of a cluster before subsampling.
    cluster_max_size: int = 500
    #: Maximal size of a cluster after subsampling.
    cluster_size_sample_to: int = 100
    #: Minimal reciprocal overlap.
    min_reciprocal_overlap: float = 0.85
    #: Slack to allow around breakend or insertion
    bnd_slack: int = 50


def _file_name_safe(s: str) -> str:
    """Make the given string file name safe.

    This is done by making all not explicitely allowed character underscores.
    """
    return re.sub(r"[^a-zA-Z]", "_", s)


class PairedEndOrientation(enum.Enum):
    """Enumeration type for SV connectivity (important for deciding for merge compatibility)."""

    #: Indicate 3' to 5' connection.
    THREE_TO_FIVE = "3to5"
    #: Indicate 5' to 3' connection.
    FIVE_TO_THREE = "5to3"
    #: Indicate 3' to 3' connection.
    THREE_TO_THREE = "3to3"
    #: Indicate 5' to 5' connection.
    FIVE_TO_FIVE = "5to5"


@attrs.define(frozen=True)
class GenotypeCounts:
    """Represents genotype counts for an SV record."""

    #: Number of source records (families) this record was built from
    src_count: int = 0
    #: Number of carriers
    carriers: int = 0
    #: Number of heterozygous carriers
    carriers_het: int = 0
    #: Number of homozygous carriers
    carriers_hom: int = 0
    #: Number of hemizygous carriers
    carriers_hemi: int = 0

    def plus(self, other: "GenotypeCounts") -> "GenotypeCounts":
        """Add ``self`` and ``other``."""
        return GenotypeCounts(
            src_count=self.src_count + other.src_count,
            carriers=self.carriers + other.carriers,
            carriers_het=self.carriers_het + other.carriers_het,
            carriers_hom=self.carriers_hom + other.carriers_hom,
            carriers_hemi=self.carriers_hemi + other.carriers_hemi,
        )


@attrs.define(frozen=True)
class SvRecord:
    """Represents a structural variant record as used in the SV clustering algorithm.

    The clustering algorithm currently ignores the uncertainty specification of variants (IOW: ci_*).
    """

    #: Genome build version
    release: str
    #: The structural variant type
    sv_type: str
    #: The chromosome of the left chromosomal position
    chrom: str
    #: 1-based start position
    pos: int
    #: The chromosome of the right chromosomal position
    chrom2: str
    #: 1-based end position of the variant
    end: int
    #: Paired-end connectivity type
    orientation: typing.Optional[PairedEndOrientation] = None
    #: Genotype counds
    counts: GenotypeCounts = attrs.field(factory=GenotypeCounts)

    def does_overlap(self, other: "SvRecord", *, bnd_slack: typing.Optional[int] = None) -> bool:
        """Returns whether the two records overlap."""
        if self.release != other.release:  # pragma: nocover
            raise ValueError(f"Incompatible release values: {self.release} vs {other.release}")
        if self.sv_type != other.sv_type:  # pragma: nocover
            raise ValueError(f"Incompatible sv_type values: {self.sv_type} vs {other.sv_type}")
        if (bnd_slack is None) == (self.is_bnd() or self.is_ins()):
            raise ValueError("Should specify bnd_slack if and only if SV is a breakend (or INS)")
        if self.is_bnd():  # break-end, potentially non-linear SV
            return (
                self.chrom == other.chrom
                and abs(self.pos - other.pos) <= bnd_slack
                and self.chrom2 == other.chrom2
                and abs(self.end - other.end) <= bnd_slack
            )
        elif self.is_ins():  # insertion / "point SV"
            return self.chrom == other.chrom and abs(self.pos - other.pos) <= bnd_slack
        else:  # linear SV
            return self.chrom == other.chrom and self.pos <= other.end and self.end >= other.pos

    def reciprocal_overlap(self, other: "SvRecord") -> typing.Optional[float]:
        """Return reciprocal overlap of overlap between ``self`` and ``other``.

        Raises an ``ValueError` if ``release`` or ``sv_type`` are not the same.
        """
        if self.is_bnd() or other.is_bnd() or self.is_ins() or other.is_ins():
            raise ValueError("Cannot compute reciprocal overlap for break-ends and INS!")
        if self.does_overlap(other):
            len_self = self.end - self.pos + 1
            len_other = other.end - other.pos + 1
            len_intersect = min(self.end, other.end) + 1 - max(self.pos, other.pos)
            ovl_self = len_intersect / len_self
            ovl_other = len_intersect / len_other
            return min(ovl_self, ovl_other)
        else:
            return 0.0

    def is_compatible(self, other: "SvRecord", *, bnd_slack: int) -> bool:
        """Determine whether the two records ``self`` and ``other`` are compatible to be merged in principle.

        That is, they must be of the same SV type and overlap.
        """
        if self.sv_type != other.sv_type:
            return False
        if self.is_bnd():  # => other.is_bnd() is True
            return (
                self.does_overlap(other, bnd_slack=bnd_slack)
                and self.orientation == other.orientation
            )
        elif self.is_ins():  # => other.is_ins() is True
            return self.does_overlap(other, bnd_slack=bnd_slack)
        else:
            return self.does_overlap(other)

    def is_bnd(self) -> bool:
        """Returns whether the record is a breakend."""
        return self.sv_type == _SV_SUB_TYPE_BND

    def is_ins(self) -> bool:
        """Returns whether the record is an insertion."""
        return self.sv_type.startswith(_SV_SUB_TYPE_INS)

    def build_interval(
        self, *, data: typing.Optional[typing.Any] = None, bnd_slack: int = 0
    ) -> Interval:
        if self.is_bnd() or self.is_ins():
            return Interval(self.pos - bnd_slack, self.end + bnd_slack, data)
        else:
            return Interval(self.pos, self.end, data)

    def sort_key(self):
        return (self.chrom, self.pos)


@attrs.define
class SvCluster:
    """Define one SV cluster by a median representation and backing records"""

    #: The clustering algorithm parameters.
    params: ClusterAlgoParams
    #: The random number generator to use
    rng: random.Random = attrs.field(repr=False)
    #: The representing ``SvRecord``
    representant: typing.Optional[SvRecord] = None
    #: The list of records backing the cluster
    records: typing.List[SvRecord] = attrs.field(default=attrs.Factory(list))
    #: The overall genotype counts
    counts: GenotypeCounts = attrs.field(factory=GenotypeCounts)

    def augment(self, record: SvRecord) -> bool:
        """Augment the given cluster

        Return whether the representant changed.

        Raises ``ValueError`` if record incompatible with representant (if exists) by release,
        sv_type, chrom, or chrom2.
        """
        orig_representant = self.representant
        if self.representant:
            for key in ("release", "sv_type", "chrom", "chrom2"):
                if getattr(record, key) != getattr(self.representant, key):  # pragma: nocover
                    raise ValueError(
                        f"Incompatible record ({record}) vs representant ({self.representant}"
                    )
            if not self.representant.is_compatible(record, bnd_slack=self.params.bnd_slack):
                raise ValueError(
                    f"Incompatible record ({record}) vs representant ({self.representant}"
                )
        else:
            self.representant = record
        self._augment(record)
        if len(self.records) > self.params.cluster_max_size:
            self._sub_sample()
        self.counts = self.counts.plus(record.counts)
        return self.representant != orig_representant

    def is_compatible(self, record: SvRecord, *, bnd_slack: int) -> bool:
        """Return whether record is compatible with all records in cluster"""
        return all(entry.is_compatible(record, bnd_slack=bnd_slack) for entry in self.records)

    def _augment(self, record: SvRecord) -> None:
        """Augment cluster with the given ``record``"""
        self.records.append(record)

    def _sub_sample(self) -> None:
        """Sub sample the records of this cluster and assign new representant"""
        self.records = self.rng.choices(self.records, k=self.params.cluster_size_sample_to)
        self.representant = self.records[0]

    def sort_key(self):
        if self.representant is None:
            return ("", -1000)
        else:
            return self.representant.sort_key()

    def normalized(self):
        """Normalized output (e.g., for tests)"""
        return attrs.evolve(self, records=list(sorted(self.records, key=SvRecord.sort_key)))


class ClusterSvAlgorithm:
    """This class encapsulates the state of the SV clustering algorithm using ``attrs`` based data structures.

    Data is processed per ``(variant_type, chromosome)`` in memory and stored.

    Protocol is:

    .. code-block:: python

        params = ClusterAlgoParams()
        algo = ClusterSvAlgorithm(params)
        for chrom in ["chr1", "chr2"]:
            db_records = DATABASE_QUERY()
            with algo.on_chrom(chrom):  # accept pushes in block
                for db_record in db_records:
                    sv_record: SvRecord = BUILD_SV_RECORD(db_record)
                    algo.push(sv_record)
            clusters = algo.cluster()
            # ...

    """

    def __init__(self, params: ClusterAlgoParams):
        self.params = params
        #: Which chromosome the algorithm is on, if any.
        self.current_chrom: typing.Optional[str] = None
        #: Clusters on the current chromosome, if any
        self.clusters: typing.List[SvRecord] = None
        #: Chromosomes that the algorithm has seen so far.
        self.seen_chroms: typing.Set[str] = set()
        #: Temporary directory to write to.
        self.tmp_dir: typing.Optional[pathlib.Path] = None
        #: Temporary storage file per SV type.
        self.tmp_files: typing.Dict[str, typing.IO[str]] = {}
        #: The random number generator to use
        self.rng: random.Random = random.Random(self.params.seed)

    @contextmanager
    def on_chrom(self, chrom: str):
        """Start clustering for a new chromosome used as a context manager.

        On exiting the context manager, all temporary files will be closed.
        """
        LOGGER.info("Starting collection of SV records for chromosome %s", chrom)
        if chrom in self.seen_chroms:  # pragma: nocover
            raise RuntimeError(f"Seen chromosome {chrom} already!")
        else:
            self.seen_chroms.add(chrom)
        self.current_chrom = chrom
        self.clusters = None
        with tempfile.TemporaryDirectory() as tmp_dir:
            pass
        os.makedirs(str(tmp_dir))
        LOGGER.info("Opening temporary files for chrom %s - %s", chrom, tmp_dir)
        self.tmp_dir = pathlib.Path(tmp_dir)
        for sv_type in SV_TYPES:
            self.tmp_files[sv_type] = (self.tmp_dir / _file_name_safe(sv_type)).open("wt+")
        yield
        LOGGER.info("Closing temporary files again for chrom %s", chrom)
        for tmp_file in self.tmp_files.values():
            tmp_file.close()
        self.tmp_dir = None
        self.tmp_files = {}
        LOGGER.info("Done with collecting SV records for chromosome %s", chrom)

    def push(self, record: SvRecord) -> None:
        """Push the ``record`` on the current chromosome to the appropriate file in ``self.tmp_dir``."""
        if not self.tmp_files:  # pragma: nocover
            raise RuntimeError("Invalid state, for push(), no temporary files open!")
        LOGGER.debug("Writing record %s", record)
        print(json.dumps(cattr.unstructure(record)), file=self.tmp_files[record.sv_type])

    def cluster(self) -> typing.List[SvCluster]:
        """Execute the clustering for the current chromosome and return clusters.

        The resulting clusters will be sorted by start position (empty clusters first)
        """
        if not self.tmp_files:  # pragma: nocover
            raise RuntimeError("Invalid state, for cluster(), no temporary files open!")
        if self.clusters is None:
            LOGGER.info("Starting clustering on chromosome %s", self.current_chrom)
            self.clusters = []
            for sv_type, tmp_file in self.tmp_files.items():
                process = psutil.Process(os.getpid())
                rss_mb = process.memory_info().rss // 1024 // 1024
                LOGGER.info(f"... clustering SV type {sv_type} with RSS {rss_mb} MB")
                tmp_file.flush()
                tmp_file.seek(0)
                self.clusters += self._cluster_impl(sv_type, tmp_file)
            self.clusters.sort(key=SvCluster.sort_key)
            LOGGER.info("Done with clustering on chromosome %s", self.current_chrom)
        return self.clusters

    def _cluster_impl(self, sv_type: str, tmp_file: typing.IO[str]) -> typing.List[SvCluster]:
        """Implementation of the clustering step for a given SV type and with a given temporary file"""
        #: Load records from disk and shuffle
        sv_records = []
        for line in tmp_file:
            LOGGER.debug("Read line %s", repr(line))
            sv_record = cattr.structure(json.loads(line), SvRecord)
            if sv_record.sv_type != sv_type:  # pragma: nocover
                raise ValueError(
                    f"Unexpected SV type. Is: {sv_record.sv_type}, expected {sv_type}."
                )
            sv_records.append(sv_record)
        self.rng.shuffle(sv_records)

        # Maintain an interval tree of clusters (interval is cluster representant).  Go over the SV records in random
        # order (implied after shuffling above) and assign to best fitting compatible cluster.
        tree = IntervalTree()
        clusters: typing.List[SvCluster] = []
        for sv_record in sv_records:
            # Find all overlapping clusters from the interval tree
            sv_interval = sv_record.build_interval(bnd_slack=self.params.bnd_slack)
            ovl_intervals: typing.Set[Interval] = tree.overlap(sv_interval.begin, sv_interval.end)
            ovl_indices: typing.List[int] = [interval.data for interval in ovl_intervals]
            best_index: typing.Optional[int] = None
            best_overlap: typing.Optional[float] = None

            # Identify the best overlapping cluster, if any
            for curr_index in ovl_indices:
                curr_cluster = clusters[curr_index]
                curr_representant = curr_cluster.representant
                if curr_cluster.is_compatible(sv_record, bnd_slack=self.params.bnd_slack):
                    if sv_record.is_bnd() or sv_record.is_ins():
                        best_index = curr_index
                        break  # pick first
                    else:
                        curr_overlap = curr_representant.reciprocal_overlap(sv_record)
                        if best_index is None or curr_overlap > best_overlap:
                            best_index = curr_index
                            best_overlap = curr_overlap

            # Create new cluster or update existing one
            if best_index is None or (
                best_overlap and best_overlap < self.params.min_reciprocal_overlap
            ):
                LOGGER.debug("Found no cluster for SV record %s (create new one)", sv_record)
                # Create new cluster and add it to the tree with representant.
                best_index = len(clusters)
                sv_cluster = SvCluster(params=self.params, rng=self.rng)
                sv_cluster.augment(sv_record)
                clusters.append(sv_cluster)
                tree.add(sv_cluster.representant.build_interval(data=best_index))
            else:
                LOGGER.debug(
                    "Found cluster %s for SV record %s with overlap %f (will update)",
                    clusters[best_index],
                    sv_record,
                    best_overlap,
                )
                # Update cluster, remove from tree and add back if representant changed.
                sv_cluster = clusters[best_index]
                old_itv = sv_cluster.representant.build_interval(data=best_index)
                representant_changed = sv_cluster.augment(sv_record)
                if representant_changed:
                    tree.remove(old_itv)
                    tree.add(sv_cluster.representant.build_interval(data=best_index))

        return clusters


def _fixup_sv_type(sv_type: str) -> str:
    return sv_type.replace("_", ":")


def _fill_null_counts(record, sex=None):
    """Helper to fill NULL ``num_*`` fields in ``record`` based on genotype and optionally a mapping of
    sample name to PED sex.
    """
    sex = sex or {}
    record.num_hom_alt = 0
    record.num_hom_ref = 0
    record.num_het = 0
    record.num_hemi_alt = 0
    record.num_hemi_ref = 0
    for k, v in record.genotype.items():
        gt = v["gt"]
        k_sex = sex.get(record.case_id, {}).get(k, 0)
        if gt == "1":
            record.num_hemi_alt += 1
        elif gt == "0":
            record.num_hemi_ref += 1
        elif gt in ("0/1", "1/0", "0|1", "1|0"):
            record.num_het += 1
        elif gt in ("0/0", "0|0"):
            if "x" in record.chromosome.lower() and k_sex == 1:
                record.num_hemi_ref += 1
            else:
                record.num_hom_ref += 1
        elif gt in ("1|1", "1|1"):
            if "x" in record.chromosome.lower() and k_sex == 1:
                record.num_hemi_alt += 1
            else:
                record.num_hom_alt += 1


def sv_model_to_attrs(model_record: StructuralVariant) -> SvRecord:
    """Conversion from ``StructuralVariant`` to ``SvRecord`` for use in clustering."""
    _fill_null_counts(model_record)
    counts = GenotypeCounts(
        src_count=1,
        carriers=(model_record.num_het or 0)
        + (model_record.num_hom_alt or 0)
        + (model_record.num_hemi_alt or 0),
        carriers_het=model_record.num_het or 0,
        carriers_hom=model_record.num_hom_alt or 0,
        carriers_hemi=model_record.num_hemi_alt or 0,
    )
    # We write out chrom2=chrom1 etc. to work around NULL values left-over from old SVs
    return SvRecord(
        release=model_record.release,
        sv_type=_fixup_sv_type(model_record.sv_type),
        chrom=model_record.chromosome,
        pos=model_record.start,
        chrom2=model_record.chromosome2 or model_record.chromosome,
        end=model_record.end,
        orientation=model_record.pe_orientation,
        counts=counts,
    )


def sv_cluster_to_model_args(sv_cluster: SvCluster) -> typing.Dict[str, typing.Any]:
    """Conversion from ``SvCluster`` to args for creation of ``BackgroundSv``."""
    chrom_nochr = (
        sv_cluster.representant.chrom
        if not sv_cluster.representant.chrom.startswith("chrm")
        else sv_cluster.representant.chrom[3:]
    )
    chrom2_nochr = (
        sv_cluster.representant.chrom2
        if not sv_cluster.representant.chrom.startswith("chrm")
        else sv_cluster.representant.chrom2[3:]
    )
    mean = sv_cluster.representant
    if mean.chrom == mean.chrom2:
        bin = binning.assign_bin(mean.pos, mean.end)
    else:
        bin = binning.assign_bin(mean.pos, mean.pos + 1)
    return {
        "release": mean.release,
        "chromosome": mean.chrom,
        "chromosome_no": CHROMOSOME_STR_TO_CHROMOSOME_INT.get(chrom_nochr, 0),
        "start": mean.pos,
        "chromosome2": mean.chrom2,
        "chromosome_no2": CHROMOSOME_STR_TO_CHROMOSOME_INT.get(chrom2_nochr, 0),
        "end": mean.end,
        "pe_orientation": mean.orientation.value if mean.orientation else None,
        "bin": bin,
        "sv_type": sv_cluster.representant.sv_type,
        **cattr.unstructure(sv_cluster.counts),
    }


def _build_bg_sv_set_impl(
    job: BuildBackgroundSvSetJob, *, chromosomes: typing.Optional[typing.List[str]] = None
) -> BackgroundSvSet:
    genomebuild = job.genomebuild
    chrom_pat = "%s" if genomebuild == "GRCh37" else "chr%s"

    def log(msg: str):
        job.add_log_entry(msg)
        LOGGER.info(msg)

    log("Creating new bg_db_set in state 'initial'")
    bg_sv_set = BackgroundSvSet.objects.create(
        genomebuild=job.genomebuild, varfish_version=varfish_version, state="building"
    )

    log("Obtain IDs of cases marked for exclusion")
    excluded_case_ids = set([])
    for case in Case.objects.prefetch_related("project").iterator():
        if get("variants", "exclude_from_inhouse_db", project=case.project):
            excluded_case_ids.add(case.id)

    log("Starting actual clustering")
    params = ClusterAlgoParams()
    algo = ClusterSvAlgorithm(params)
    record_count = 0

    for chrom_name in chromosomes or CHROMOSOME_NAMES:
        chrom = chrom_pat % chrom_name
        log("Starting with chromosome %s for genome build %s" % (chrom, genomebuild))
        chunk_size = 10_000
        with algo.on_chrom(chrom):  # accept pushes in block
            log("Creating database cursor ...")
            cursor = enumerate(
                StructuralVariant.objects.filter(release=genomebuild, chromosome=chrom).iterator(
                    chunk_size=chunk_size
                )
            )
            first = list(itertools.islice(cursor, 1))  # everything is lazy, force cursor creation
            log("Retrieving records ...")
            for num, db_record in itertools.chain(first, cursor):
                if db_record.case_id in excluded_case_ids:
                    continue  # skip excluded cases
                sv_record = sv_model_to_attrs(db_record)
                if sv_record.pos >= sv_record.end:  # fix 0-length INS/BND
                    sv_record = attrs.evolve(sv_record, end=sv_record.pos + 1)
                algo.push(sv_record)
                record_count += 1
                if num % 10_000 == 0:
                    process = psutil.Process(os.getpid())
                    rss_mb = process.memory_info().rss // 1024 // 1024
                    LOGGER.info("... at record %d with RSS %d MB", num, rss_mb)
                    gc.collect()
            log("Creating clusters ...")
            clusters = algo.cluster()
        log("Built %d clusters from %d records" % (len(clusters), record_count))

        with open("/tmp/clusters.txt", "wt") as outputf:
            for cluster in clusters:
                print(str(cluster), file=outputf)

        log("Constructing background SV set records...")
        for cluster in clusters:
            BackgroundSv.objects.create(bg_sv_set=bg_sv_set, **sv_cluster_to_model_args(cluster))

        log("... done constructing background SV set records.")
        log("Done with chromosome %s for genome build %s" % (chrom, genomebuild))

    with transaction.atomic():
        bg_sv_set.refresh_from_db()
        bg_sv_set.state = "active"
        bg_sv_set.save()
    return bg_sv_set


def build_bg_sv_set(
    job: BuildBackgroundSvSetJob, *, chromosomes: typing.Optional[typing.List[str]] = None
) -> BackgroundSvSet:
    """Construct a new ``BackgroundSvSet``"""
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=None,
            app_name="svs",
            user=None,
            event_name="svs_build_bg_sv_set",
            description="build background sv set",
            status_type="INIT",
        )
    try:
        job.add_log_entry("Starting creation of background SV set...")
        result = _build_bg_sv_set_impl(job, chromosomes=chromosomes)
        job.add_log_entry("... done creating background SV set.")
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "failed to build background sv set")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "building background sv set complete")
        return result


def _cleanup_bg_sv_sets(
    job: CleanupBackgroundSvSetJob, *, timeout_hours: typing.Optional[int] = None
) -> None:
    meta = get_meta()
    sa_table_set = meta.tables[BackgroundSvSet._meta.db_table]
    query_set = delete(sa_table_set)

    # Keep latest two active
    active_sets = BackgroundSvSet.objects.filter(state="active").order_by("-date_created")
    keep_ids = []
    if active_sets.count():
        keep_ids += [s.id for s in active_sets[:2]]
    # Keep building ones that are younger than ``build_timeout_hours``
    if timeout_hours >= 0:
        hours_ago = timezone.now() - timezone.timedelta(hours=timeout_hours)
        young_sets = BackgroundSvSet.objects.filter(
            (~Q(state="active")) & Q(date_created__lt=hours_ago)
        )
        keep_ids += [s.id for s in young_sets]

    sa_table_sv = meta.tables[BackgroundSv._meta.db_table]
    query_sv = delete(sa_table_sv)
    if keep_ids:
        query_sv = query_sv.where(sa_table_sv.c.bg_sv_set_id.not_in(keep_ids))
    get_engine().execute(query_sv)

    if keep_ids:
        query_set = query_set.where(sa_table_set.c.id.not_in(keep_ids))
    else:
        query_set = query_set.where(True)
    get_engine().execute(query_set)


def cleanup_bg_sv_sets(
    job: CleanupBackgroundSvSetJob, *, timeout_hours: typing.Optional[int] = None
) -> None:
    """Cleanup old background SV sets"""
    timeout_hours = timeout_hours or settings.SV_CLEANUP_BUILDING_SV_SETS
    job.mark_start()
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=None,
            app_name="svs",
            user=None,
            event_name="svs_cleanup_bg_sv_sets",
            description="cleanup background sv set",
            status_type="INIT",
        )
    try:
        job.add_log_entry("Starting cleanup of background SVs...")
        _cleanup_bg_sv_sets(job, timeout_hours=timeout_hours)
        job.add_log_entry("... done cleaning up background SVs.")
    except Exception as e:
        job.mark_error(e)
        if timeline:
            tl_event.set_status("FAILED", "failed to clean up background SVs")
        raise
    else:
        job.mark_success()
        if timeline:
            tl_event.set_status("OK", "cleaning up background SVs complete")
