"""Helper code for creating/updating ``CaseVariantStats`` and related records."""

from django.db import transaction
import numpy as np

from projectroles.plugins import get_backend_api
from var_stats_qc.qc import compute_het_hom_chrx, compute_relatedness, compute_relatedness_many

from .forms import FILTER_FORM_TRANSLATE_EFFECTS
from .models import SmallVariant, CaseVariantStats, ProjectVariantStats


#: Effects to ignore when computing stats.
IGNORE_EFFECTS = (
    "downstream",
    "upstream",
    "intergenic",
    "non_coding_transcript_exon_variant",
    "non_coding_transcript_intron_variant",
)

#: Transition pairs
TRANSITIONS = (("A", "G"), ("G", "A"), ("C", "T"), ("T", "C"))


def _get_dp_bin(dp):
    """Returns lower bin width for the given depth.

    Bin width

    - 0..19: 1bp
    - 20..49: 5bp
    - 50..199: 10bp
    - 200..: = 200
    """
    if dp < 20:
        return dp
    elif dp < 50:
        return (dp // 2) * 2
    elif dp < 200:
        return (dp // 5) * 5
    else:
        return 200


def gather_variant_stats(variant_set):
    """Iterate over ``SmallVariant`` objects of ``variant_set`` and collect various statistics."""
    # TODO: could be refactored into class with multiple smaller, easier-to-read functions
    samples = variant_set.case.get_members_with_samples()
    transitions = {name: 0 for name in samples}
    transversions = {name: 0 for name in samples}
    snvs = {name: 0 for name in samples}
    indels = {name: 0 for name in samples}
    mnvs = {name: 0 for name in samples}
    effect_counts = {
        name: {effect: 0 for effect in FILTER_FORM_TRANSLATE_EFFECTS.values()} for name in samples
    }
    max_indel_size = 10
    indel_sizes = {name: {} for name in samples}
    read_depths = {name: {} for name in samples}
    dps = {name: [] for name in samples}
    hets = {name: 0 for name in samples}
    homs = {name: 0 for name in samples}

    ignore_set = set(IGNORE_EFFECTS)
    for small_var in SmallVariant.objects.filter(
        set_id=variant_set.pk, case_id=variant_set.case.pk
    ):
        if not (set(small_var.ensembl_effect) & ignore_set):
            for sample in samples:
                if small_var.genotype[sample]["gt"].count("1") == 1:
                    hets[sample] += 1
                else:
                    homs[sample] += 1
                dps[sample].append(small_var.genotype[sample]["dp"])
                bin = _get_dp_bin(small_var.genotype[sample]["dp"])
                read_depths[sample].setdefault(bin, 0)
                read_depths[sample][bin] += 1
                for effect in small_var.ensembl_effect:
                    effect_counts[sample][effect] += small_var.genotype[sample]["gt"].count("1")
            if small_var.var_type == "snv":
                for sample in samples:
                    snvs[sample] += small_var.genotype[sample]["gt"].count("1")
                if (small_var.reference, small_var.alternative) in TRANSITIONS:
                    for sample in samples:
                        transitions[sample] += small_var.genotype[sample]["gt"].count("1")
                else:
                    for sample in samples:
                        transversions[sample] += small_var.genotype[sample]["gt"].count("1")
            elif small_var.var_type == "mnvs":
                for sample in samples:
                    mnvs[sample] += small_var.genotype[sample]["gt"].count("1")
            elif small_var.var_type == "indel":
                for sample in samples:
                    count = small_var.genotype[sample]["gt"].count("1")
                    indels[sample] += count
                    delta = len(small_var.reference) - len(small_var.alternative)
                    if delta > max_indel_size:
                        delta = max_indel_size
                    elif delta < -max_indel_size:
                        delta = -max_indel_size
                    indel_sizes[sample].setdefault(delta, 0)
                    indel_sizes[sample][delta] += count

    dp_quantiles = {}
    for sample in samples:
        if dps[sample]:
            arr = np.asarray(dps[sample])
            dp_quantiles[sample] = list(np.percentile(arr, [0, 25, 50, 75, 100]))
        else:
            dp_quantiles[sample] = [0] * 5

    het_ratio = {}
    for sample in samples:
        if hets[sample] + homs[sample]:
            het_ratio[sample] = hets[sample] / (hets[sample] + homs[sample])
        else:
            het_ratio[sample] = 0.0

    return (
        transitions,
        transversions,
        snvs,
        indels,
        mnvs,
        effect_counts,
        indel_sizes,
        read_depths,
        dp_quantiles,
        het_ratio,
    )


def rebuild_case_variant_stats(engine, variant_set, logger=lambda _: None):
    """Rebuild the ``CaseVariantStats`` for the given ``SmallVariantSet`` using the SQL Alchemy ``connection``."""
    # Compute statistics.
    logger("... compute relatedness")
    het, het_shared, ibs0, ibs1, ibs2 = compute_relatedness(engine, SmallVariant, variant_set)
    logger("... compute het hom ratio on chromosome X")
    chrx_het_hom = compute_het_hom_chrx(engine, SmallVariant, variant_set)
    logger("... gather variant stats")
    (
        transitions,
        transversions,
        snvs,
        indels,
        mnvs,
        effect_counts,
        indel_sizes,
        read_depths,
        dp_quantiles,
        het_ratio,
    ) = gather_variant_stats(variant_set)

    # Rebuild the case variant statistics atomically.
    with transaction.atomic():
        # Remove existing record if any.
        logger("... delete old case variant stats if available")
        try:
            variant_set.variant_stats.delete()
            logger("... (deletion successful)")
        except CaseVariantStats.DoesNotExist:
            logger("... (none found)")
            pass  # swallow, nothing to delete

        # Create statistics object.
        logger("... create new case variant stats object")
        stats = CaseVariantStats.objects.create(variant_set=variant_set)
        # Insert basic information.
        for sample in variant_set.case.get_members_with_samples():
            logger("... creating sample variant stats object for sample %s" % sample)
            stats.sample_variant_stats.create(
                sample_name=sample,
                ontarget_transitions=transitions[sample],
                ontarget_transversions=transversions[sample],
                ontarget_snvs=snvs[sample],
                ontarget_indels=indels[sample],
                ontarget_mnvs=mnvs[sample],
                ontarget_effect_counts=effect_counts[sample],
                chrx_het_hom=chrx_het_hom[sample],
                ontarget_indel_sizes=indel_sizes[sample],
                ontarget_dps=read_depths[sample],
                ontarget_dp_quantiles=dp_quantiles[sample],
                het_ratio=het_ratio[sample],
            )
        # Insert relatedness information
        for pair in het_shared.keys():
            logger("... create relatedness object for samples %s and %s" % (pair[0], pair[1]))
            stats.relatedness.create(
                sample1=pair[0],
                sample2=pair[1],
                het_1_2=het_shared[pair],
                het_1=het[pair[0]],
                het_2=het[pair[1]],
                n_ibs0=ibs0[pair],
                n_ibs1=ibs1[pair],
                n_ibs2=ibs2[pair],
            )
        return stats


def rebuild_project_variant_stats(engine, project, user, logger=lambda _: None):
    timeline = get_backend_api("timeline_backend")
    if timeline:
        tl_event = timeline.add_event(
            project=project,
            app_name="variants",
            user=user,
            event_name="project_stats_build",
            description="build project-wide variant statistics",
            status_type="INIT",
        )
    cases = project.case_set.all()
    with transaction.atomic():
        het, het_shared, ibs0, ibs1, ibs2 = compute_relatedness_many(engine, SmallVariant, cases)
    logger("Done computing relatedness, now saving to DB")
    try:
        with transaction.atomic():
            # Remove existing record if any.
            try:
                project.variant_stats.delete()
            except ProjectVariantStats.DoesNotExist:
                pass  # swallow, nothing to delete
            else:
                logger("Done removing old statistics")

            # Create statistics object.
            stats = ProjectVariantStats.objects.create(project=project)
            # Insert relatedness information
            for pair in het_shared.keys():
                stats.relatedness.create(
                    sample1=pair[0],
                    sample2=pair[1],
                    het_1_2=het_shared[pair],
                    het_1=het[pair[0]],
                    het_2=het[pair[1]],
                    n_ibs0=ibs0[pair],
                    n_ibs1=ibs1[pair],
                    n_ibs2=ibs2[pair],
                )
            if timeline:
                tl_event.set_status("OK", "finished storing new project-wide variant statistics")
            return stats
    except Exception as e:
        if timeline:
            tl_event.set_status(
                "FAILED", "could not update project-wide variant statistics: {}".format(e)
            )
        raise


def execute_rebuild_project_variant_stats_job(engine, stats_job):
    """Rebuild the ``ProjectVariantStats`` for the given ``project"""
    stats_job.mark_start()
    try:
        stats = rebuild_project_variant_stats(
            engine, stats_job.project, stats_job.bg_job.user, stats_job.add_log_entry
        )
        stats_job.mark_success()
        return stats
    except Exception as e:
        stats_job.mark_error("problem updating project-wide variant statistics: {}".format(e))
        raise
