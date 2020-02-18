"""QC metric computation contained in this package."""

from itertools import chain

import numpy as np
from sqlalchemy import or_
from sqlalchemy.sql import select, and_, not_, func

from .models import ReferenceSite


def _compute_het_hom_chrx_stmt(variant_model, variant_set):
    """Build SQL Alchemy statement given the variant model class and the case object."""
    return (
        select([variant_model.sa.genotype])
        .select_from(variant_model.sa.table)
        .where(
            and_(
                variant_model.sa.case_id == variant_set.case.id,
                variant_model.sa.set_id == variant_set.id,
                variant_model.sa.chromosome == "X",
                # Exclude pseudoautosomal regions on chrX; works for both GRCh37 and GRCh38.
                not_(and_(variant_model.sa.start >= 10000, variant_model.sa.start <= 2_781_479)),
                not_(
                    and_(
                        variant_model.sa.start >= 154_931_044, variant_model.sa.start <= 156_030_895
                    )
                ),
            )
        )
    )


def compute_het_hom_chrx(connection, variant_model, variant_set, min_depth=7, n_sites=10000):
    """Compute het/hom ratio on chromosome X from the given ``variant_model``."""
    # Obtain the genotypes.
    stmt = _compute_het_hom_chrx_stmt(variant_model, variant_set)
    result = connection.execute(stmt)

    # Count hom. ref., het., and hom. alt. genotypes for each sample.
    samples = variant_set.case.get_members_with_samples()
    hom_ref = np.zeros(len(samples), dtype=int)
    het = np.zeros(len(samples), dtype=int)
    hom_alt = np.zeros(len(samples), dtype=int)
    kept = 0

    # Iterate over genotypes of chrX.
    for row in result.fetchall():
        # Skip if too few samples are called.
        gts = [row.genotype[sample]["gt"] for sample in samples]
        nocalls = [gt for gt in gts if gt == "./."]
        if not gts or len(nocalls) / len(gts) > 0.5:
            continue  # skip, too few calls
        # Skip if depth not sufficient.
        # TODO: will fail without depth annotation
        gt_depths = np.asarray([row.genotype[sample]["dp"] for sample in samples])
        if any(gt_depths < min_depth):
            continue  # skip, coverage too low
        depth_filter = gt_depths >= min_depth
        # Count genotypes
        hom_ref += np.asarray([gt == "0/0" for gt in gts]) & depth_filter
        hom_alt += np.asarray([gt == "1/1" for gt in gts]) & depth_filter
        het += np.asarray([gt in ("0/1", "1/0") for gt in gts]) & depth_filter
        # Stop if sufficient site count reached.
        kept += 1
        if kept >= n_sites:
            break

    # Build result.
    hom_alt[hom_alt == 0] = 1
    het_ratios = het.astype(float) / hom_alt
    return {sample: het_ratios[i] for i, sample in enumerate(samples)}


def _compute_relatedness_stmt(variant_model, variant_set):
    """Build SQL Alchemy statement given the variant model class and the case object."""
    return (
        select([variant_model.sa.genotype])
        .select_from(
            variant_model.sa.table.join(
                ReferenceSite.sa.table,
                and_(
                    ReferenceSite.sa.release == variant_model.sa.release,
                    ReferenceSite.sa.chromosome == variant_model.sa.chromosome,
                    ReferenceSite.sa.start == variant_model.sa.start,
                ),
            )
        )
        .where(
            and_(
                variant_model.sa.set_id == variant_set.id,
                variant_model.sa.case_id == variant_set.case.id,
                not_(variant_model.sa.chromosome.in_(("X", "Y"))),
            )
        )
    )


def _normalize_gt(gt):
    if gt == "1/0":
        return "0/1"
    else:
        return gt


def compute_relatedness(connection, variant_model, variant_set, min_depth=7, n_sites=10000):
    """Compute relatedness between pairs following Pedersen & Quinlan (2017).

    Return ``het, het_shared, ibs0, ibs1, ibs2``.
    """
    # Obtain the genotypes.
    stmt = _compute_relatedness_stmt(variant_model, variant_set)
    result = connection.execute(stmt)

    # Compute sample pairs to consider.
    samples = variant_set.case.get_members_with_samples()
    sample_pairs = [(s, t) for i, s in enumerate(samples) for j, t in enumerate(samples) if i > j]
    # Statistics.
    het = {s: 0 for s in samples}
    het_shared = {p: 0 for p in sample_pairs}
    ibs0 = {p: 0 for p in sample_pairs}
    ibs1 = {p: 0 for p in sample_pairs}
    ibs2 = {p: 0 for p in sample_pairs}

    # Iterate over genotypes of pseudo-autosomal regions on chrX.
    kept = 0
    for row in result.fetchall():
        # Skip if too few samples are called.
        gts = {sample: _normalize_gt(row.genotype[sample]["gt"]) for sample in samples}
        nocalls = [gt for gt in gts if gt == "./."]
        if len(nocalls) / len(gts) > 0.5:
            continue  # skip, too few calls
        # Skip if depth not sufficient.
        # TODO: will fail without depth annotation
        gt_depths = np.asarray([row.genotype[sample]["dp"] for sample in samples])
        if any(gt_depths < min_depth):
            continue  # skip, coverage too low
        # Compute statistics
        for sample in samples:
            het[sample] += gts[sample] in ("0/1", "1/0")
        for s, t in sample_pairs:
            gt1 = gts[s]
            gt2 = gts[t]
            gt_set = {gt1, gt2}
            if len(gt_set) == 1:
                ibs2[(s, t)] += 1
                if gt1 == "0/1":
                    het_shared[(s, t)] += 1
            elif gt_set == {"0/0", "1/1"}:
                ibs0[(s, t)] += 1
            else:
                ibs1[(s, t)] += 1
        kept += 1
        if kept > n_sites:
            break

    # Return result.
    return het, het_shared, ibs0, ibs1, ibs2


def _compute_relatedness_stmt_many(variant_model, cases):
    """Build SQL Alchemy statement given the variant model class and multiple case objects."""
    variant_set_conditions = []
    for case in cases:
        variant_set = case.latest_variant_set()
        if variant_set:
            variant_set_conditions.append(
                and_(
                    variant_model.sa.set_id == variant_set.id,
                    variant_model.sa.case_id == variant_set.case.id,
                )
            )

    return (
        select([func.jsonb_agg(variant_model.sa.genotype).label("genotype")])
        .select_from(
            variant_model.sa.table.join(
                ReferenceSite.sa.table,
                and_(
                    ReferenceSite.sa.release == variant_model.sa.release,
                    ReferenceSite.sa.chromosome == variant_model.sa.chromosome,
                    ReferenceSite.sa.start == variant_model.sa.start,
                ),
            )
        )
        .where(
            and_(or_(*variant_set_conditions), not_(variant_model.sa.chromosome.in_(("X", "Y"))))
        )
        .group_by(
            variant_model.sa.chromosome,
            variant_model.sa.start,
            variant_model.sa.end,
            variant_model.sa.reference,
            variant_model.sa.alternative,
        )
    )


def compute_relatedness_many(connection, variant_model, cases, min_depth=7, n_sites=10000):
    """Compute relatedness between pairs over a set of cases.

    Return ``het, het_shared, ibs0, ibs1, ibs2``.
    """
    # Obtain the genotypes.
    stmt = _compute_relatedness_stmt_many(variant_model, cases)
    result = connection.execute(stmt)

    # Collect project-wide samples and sample pairs.
    samples = set(chain(*(case.get_members_with_samples() for case in cases)))
    sample_pairs = [(s, t) for i, s in enumerate(samples) for j, t in enumerate(samples) if i > j]

    # Statistics.
    het = {s: 0 for s in samples}
    het_shared = {p: 0 for p in sample_pairs}
    ibs0 = {p: 0 for p in sample_pairs}
    ibs1 = {p: 0 for p in sample_pairs}
    ibs2 = {p: 0 for p in sample_pairs}

    # Return defaults if project is empty
    if result.rowcount == 0:
        return het, het_shared, ibs0, ibs1, ibs2

    # Iterate over genotypes of pseudo-autosomal regions on chrX.
    kept = 0
    for row in result.fetchall():
        # Merge the genotype dictionaries.
        genotype = {}
        for part in row.genotype:
            genotype = {**genotype, **part}
        # Skip if too few samples are called.
        gts = {
            sample: _normalize_gt(genotype.get(sample, {}).get("gt", "./.")) for sample in samples
        }
        nocalls = [gt for gt in gts if gt == "./."]
        if not gts:
            continue
        if len(nocalls) / len(gts) > 0.1 and len(gts) - len(nocalls) < 5:
            continue  # skip, too few calls
        # Skip if depth not sufficient.
        # TODO: will fail without depth annotation
        gt_depths = np.asarray([genotype.get(sample, {}).get("dp", -1) for sample in samples])
        # Compute statistics
        for sample in samples:
            if gts[sample] == "1/0":
                gts[sample] = "0/1"
            het[sample] += gts[sample] == "0/1"
        for s, t in sample_pairs:
            gt1 = gts[s]
            gt2 = gts[t]
            if gt1 == "./." and gt2 == "./.":
                continue  # skip if both no-call
            if gt1 == "./.":  # assume HOM_REF
                gt1 = "0/0"
            if gt2 == "./.":  # assume HOM_REF
                gt2 = "0/0"
            gt_set = {gt1, gt2}
            if len(gt_set) == 1:
                ibs2[(s, t)] += 1
                if gt1 == "0/1":
                    het_shared[(s, t)] += 1
            elif gt_set in ({"0/0", "0/1"}, {"1/1", "0/1"}):
                ibs1[(s, t)] += 1
            else:
                ibs0[(s, t)] += 1
        kept += 1
        if kept > n_sites:
            break

    # Return result.
    return het, het_shared, ibs0, ibs1, ibs2
